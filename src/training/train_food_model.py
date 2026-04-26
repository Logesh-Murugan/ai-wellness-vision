#!/usr/bin/env python3
"""
Food Recognition Model Training Pipeline
=========================================
Trains an EfficientNet-B0 model on the Food-101 dataset using a 2-stage
fine-tuning approach with advanced augmentations (Mixup, RandomErasing,
and Label Smoothing).
"""

import json
import logging
import os
from pathlib import Path
from typing import Tuple

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import torchvision.transforms as transforms
import torchvision.transforms.v2 as v2
from torchvision.datasets import Food101
import timm

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DATA_DIR = "data"
MODELS_DIR = "models"
BATCH_SIZE = 32
IMAGE_SIZE = 224
NUM_WORKERS = min(4, os.cpu_count() or 1)

# Training Hyperparameters
STAGE1_EPOCHS = 5
STAGE2_EPOCHS = 10
STAGE1_LR = 1e-3
STAGE2_LR = 1e-4

MIXUP_ALPHA = 0.2
LABEL_SMOOTHING = 0.1


def setup_data() -> Tuple[DataLoader, DataLoader, list]:
    """Downloads (if necessary) and prepares Food-101 DataLoaders."""
    logger.info("Setting up Food-101 dataset...")

    # Data Augmentation & Transforms
    train_transform = v2.Compose([
        v2.ToImage(),
        v2.RandomResizedCrop(IMAGE_SIZE, scale=(0.8, 1.0)),
        v2.RandomHorizontalFlip(),
        v2.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        v2.ToDtype(torch.float32, scale=True),
        v2.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        v2.RandomErasing(p=0.5),
    ])

    val_transform = v2.Compose([
        v2.ToImage(),
        v2.Resize(256),
        v2.CenterCrop(IMAGE_SIZE),
        v2.ToDtype(torch.float32, scale=True),
        v2.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    Path(DATA_DIR).mkdir(parents=True, exist_ok=True)
    
    logger.info("Loading training data (this may take a moment if extracting)...")
    train_dataset = Food101(root=DATA_DIR, split="train", download=True)
    train_dataset.transform = train_transform

    logger.info("Loading validation data...")
    val_dataset = Food101(root=DATA_DIR, split="test", download=True)
    val_dataset.transform = val_transform

    train_loader = DataLoader(
        train_dataset, batch_size=BATCH_SIZE, shuffle=True, 
        num_workers=NUM_WORKERS, pin_memory=True, drop_last=True
    )
    val_loader = DataLoader(
        val_dataset, batch_size=BATCH_SIZE, shuffle=False, 
        num_workers=NUM_WORKERS, pin_memory=True
    )

    class_names = train_dataset.classes
    return train_loader, val_loader, class_names


def create_model(num_classes: int) -> nn.Module:
    """Creates a pretrained EfficientNet-B0 model."""
    logger.info(f"Creating EfficientNet-B0 model for {num_classes} classes...")
    model = timm.create_model("efficientnet_b0", pretrained=True, num_classes=num_classes)
    return model


def train_one_epoch(
    model: nn.Module, 
    loader: DataLoader, 
    criterion: nn.Module, 
    optimizer: optim.Optimizer, 
    device: torch.device,
    mixup_fn: v2.MixUp
) -> float:
    """Trains the model for one epoch."""
    model.train()
    total_loss = 0.0

    for i, (images, targets) in enumerate(loader):
        images, targets = images.to(device), targets.to(device)
        
        # Apply MixUp
        images, targets = mixup_fn(images, targets)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, targets)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        if (i + 1) % 100 == 0:
            logger.info(f"Batch [{i+1}/{len(loader)}] - Loss: {loss.item():.4f}")

    return total_loss / len(loader)


@torch.no_grad()
def evaluate(model: nn.Module, loader: DataLoader, device: torch.device) -> Tuple[float, float]:
    """Evaluates the model and returns Top-1 and Top-5 accuracy."""
    model.eval()
    top1_correct = 0
    top5_correct = 0
    total = 0

    for images, targets in loader:
        images, targets = images.to(device), targets.to(device)
        outputs = model(images)
        
        # Get top 5 predictions
        _, pred5 = outputs.topk(5, dim=1, largest=True, sorted=True)
        pred5 = pred5.t()
        correct = pred5.eq(targets.view(1, -1).expand_as(pred5))

        top1_correct += correct[:1].reshape(-1).float().sum(0, keepdim=True).item()
        top5_correct += correct[:5].reshape(-1).float().sum(0, keepdim=True).item()
        total += targets.size(0)

    top1_acc = (top1_correct / total) * 100
    top5_acc = (top5_correct / total) * 100
    return top1_acc, top5_acc


def save_metadata(class_names: list, output_dir: Path):
    """Saves class names mapping for inference."""
    output_dir.mkdir(parents=True, exist_ok=True)
    mapping = {i: name for i, name in enumerate(class_names)}
    with open(output_dir / "food_class_names.json", "w") as f:
        json.dump(mapping, f, indent=4)
    logger.info("Saved food_class_names.json")


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Using device: {device}")

    # 1. Setup Data
    train_loader, val_loader, class_names = setup_data()
    num_classes = len(class_names)
    
    # Save metadata immediately
    save_metadata(class_names, Path(MODELS_DIR))

    # 2. Setup Model & MixUp
    model = create_model(num_classes).to(device)
    mixup = v2.MixUp(alpha=MIXUP_ALPHA, num_classes=num_classes)
    
    # Criterion with Label Smoothing (using standard CrossEntropyLoss with smoothing)
    criterion = nn.CrossEntropyLoss(label_smoothing=LABEL_SMOOTHING)

    best_top1_acc = 0.0

    # =========================================================================
    # STAGE 1: Train Classifier Head Only
    # =========================================================================
    logger.info("=== STAGE 1: Freezing backbone, training classifier ===")
    for param in model.parameters():
        param.requires_grad = False
    for param in model.classifier.parameters():
        param.requires_grad = True

    optimizer1 = optim.AdamW(model.classifier.parameters(), lr=STAGE1_LR)

    for epoch in range(1, STAGE1_EPOCHS + 1):
        logger.info(f"Stage 1 - Epoch {epoch}/{STAGE1_EPOCHS}")
        train_loss = train_one_epoch(model, train_loader, criterion, optimizer1, device, mixup)
        top1, top5 = evaluate(model, val_loader, device)
        
        logger.info(f"Stage 1 - Epoch {epoch} Summary: Loss: {train_loss:.4f} | Top-1 Acc: {top1:.2f}% | Top-5 Acc: {top5:.2f}%")

    # =========================================================================
    # STAGE 2: Fine-tune Entire Model
    # =========================================================================
    logger.info("=== STAGE 2: Unfreezing all layers for fine-tuning ===")
    for param in model.parameters():
        param.requires_grad = True

    optimizer2 = optim.AdamW(model.parameters(), lr=STAGE2_LR, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer2, T_max=STAGE2_EPOCHS)

    for epoch in range(1, STAGE2_EPOCHS + 1):
        logger.info(f"Stage 2 - Epoch {epoch}/{STAGE2_EPOCHS}")
        train_loss = train_one_epoch(model, train_loader, criterion, optimizer2, device, mixup)
        top1, top5 = evaluate(model, val_loader, device)
        scheduler.step()
        
        logger.info(f"Stage 2 - Epoch {epoch} Summary: Loss: {train_loss:.4f} | Top-1 Acc: {top1:.2f}% | Top-5 Acc: {top5:.2f}%")

        # Save best model
        if top1 > best_top1_acc:
            best_top1_acc = top1
            save_path = Path(MODELS_DIR) / "food_model.pth"
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer2.state_dict(),
                'best_val_top1': best_top1_acc,
                'class_names': class_names
            }, save_path)
            logger.info(f"⭐️ New best model saved to {save_path} (Top-1: {best_top1_acc:.2f}%)")

    logger.info("🎉 Training complete!")


if __name__ == "__main__":
    main()
