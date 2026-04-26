#!/usr/bin/env python3
"""
Skin Lesion Classification Training Pipeline
=============================================
EfficientNet-B3 fine-tuned on HAM10000 dataset for 7-class dermoscopic
lesion classification.

Dataset: 10,015 dermoscopic images across 7 diagnostic categories
Model:   EfficientNet-B3 (timm) with custom classification head
Loss:    Focal Loss (gamma=2) for class imbalance
Metrics: Per-class F1, macro AUC (OvR)

MEDICAL DISCLAIMER: This model is intended for research and educational
purposes only. It is NOT a substitute for professional medical diagnosis.
Always consult a qualified dermatologist for skin lesion evaluation.
"""

import os
import sys
import logging
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR

import timm
from PIL import Image
import albumentations as A
from albumentations.pytorch import ToTensorV2

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix,
)

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
# Constants
# ---------------------------------------------------------------------------
CLASS_NAMES: List[str] = [
    "akiec",   # Actinic Keratoses & Intraepithelial Carcinoma
    "bcc",     # Basal Cell Carcinoma
    "bkl",     # Benign Keratosis-like Lesions
    "df",      # Dermatofibroma
    "mel",     # Melanoma
    "nv",      # Melanocytic Nevi
    "vasc",    # Vascular Lesions
]

CLASS_DISPLAY_NAMES: Dict[str, str] = {
    "akiec": "Actinic Keratoses / Intraepithelial Carcinoma",
    "bcc":   "Basal Cell Carcinoma",
    "bkl":   "Benign Keratosis-like Lesions",
    "df":    "Dermatofibroma",
    "mel":   "Melanoma",
    "nv":    "Melanocytic Nevi",
    "vasc":  "Vascular Lesions",
}

NUM_CLASSES: int = len(CLASS_NAMES)
IMAGE_SIZE: int = 224  # Reduced from 300 to fit 4GB VRAM GPUs
IMAGENET_MEAN: Tuple[float, ...] = (0.485, 0.456, 0.406)
IMAGENET_STD: Tuple[float, ...] = (0.229, 0.224, 0.225)


# ===================================================================
# 1. HAM10000Dataset
# ===================================================================
class HAM10000Dataset(Dataset):
    """
    PyTorch Dataset for HAM10000 dermoscopic skin lesion images.

    Expects:
        csv_path  : Path to HAM10000_metadata.csv
        image_dir : Directory (or list of directories) containing the ISIC .jpg images
        transform : Albumentations Compose pipeline

    The CSV must contain at minimum:
        - image_id : filename stem (e.g. "ISIC_0024306")
        - dx       : diagnosis label string (one of CLASS_NAMES)
    """

    def __init__(
        self,
        csv_path: str,
        image_dirs: List[str],
        transform: Optional[A.Compose] = None,
        class_names: List[str] = CLASS_NAMES,
    ):
        super().__init__()
        self.transform = transform
        self.class_names = class_names
        self.label_to_idx = {name: idx for idx, name in enumerate(class_names)}

        # ---- Load metadata ------------------------------------------------
        df = pd.read_csv(csv_path)
        if "image_id" not in df.columns or "dx" not in df.columns:
            raise ValueError(
                "CSV must contain 'image_id' and 'dx' columns. "
                f"Found columns: {list(df.columns)}"
            )

        # Build a fast lookup: image_id -> full path
        image_lookup: Dict[str, str] = {}
        for img_dir in image_dirs:
            img_dir_path = Path(img_dir)
            if not img_dir_path.is_dir():
                logger.warning(f"Image directory not found, skipping: {img_dir}")
                continue
            for fpath in img_dir_path.glob("*.jpg"):
                image_lookup[fpath.stem] = str(fpath)

        # ---- Filter to images we actually have on disk --------------------
        valid_rows = []
        for _, row in df.iterrows():
            iid = row["image_id"]
            dx = row["dx"]
            if iid in image_lookup and dx in self.label_to_idx:
                valid_rows.append(
                    {
                        "image_id": iid,
                        "path": image_lookup[iid],
                        "label": self.label_to_idx[dx],
                        "dx": dx,
                    }
                )

        self.samples = pd.DataFrame(valid_rows)
        if len(self.samples) == 0:
            raise RuntimeError(
                "No valid image-label pairs found. Check csv_path and image_dirs."
            )
        logger.info(
            f"HAM10000Dataset initialized — {len(self.samples)} images, "
            f"{NUM_CLASSES} classes"
        )
        self._log_class_distribution()

    # ---- helpers ----------------------------------------------------------
    def _log_class_distribution(self) -> None:
        counts = self.samples["dx"].value_counts()
        for cls_name in self.class_names:
            cnt = counts.get(cls_name, 0)
            logger.info(f"  {cls_name:>6s}: {cnt:>5d} images")

    @property
    def labels(self) -> np.ndarray:
        """Return integer labels array (needed for WeightedRandomSampler)."""
        return self.samples["label"].values

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        row = self.samples.iloc[idx]
        image = np.array(Image.open(row["path"]).convert("RGB"))

        if self.transform is not None:
            augmented = self.transform(image=image)
            image = augmented["image"]  # already a torch Tensor
        else:
            # Fallback: simple resize + to tensor
            image = torch.from_numpy(image).permute(2, 0, 1).float() / 255.0

        return image, int(row["label"])


# ===================================================================
# 2. Albumentations Augmentation Pipelines
# ===================================================================
def get_train_transforms(image_size: int = IMAGE_SIZE) -> A.Compose:
    """Training augmentation pipeline with geometric + colour augmentations."""
    return A.Compose(
        [
            A.Resize(image_size, image_size),
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.5),
            A.RandomRotate90(p=0.5),
            A.ColorJitter(
                brightness=0.2,
                contrast=0.2,
                saturation=0.2,
                hue=0.1,
                p=0.5,
            ),
            A.Affine(
                translate_percent={"x": (-0.1, 0.1), "y": (-0.1, 0.1)},
                scale=(0.85, 1.15),
                rotate=(-30, 30),
                mode=0,
                p=0.5,
            ),
            A.CoarseDropout(
                num_holes_range=(1, 8),
                hole_height_range=(image_size // 25, image_size // 15),
                hole_width_range=(image_size // 25, image_size // 15),
                fill=0,
                p=0.3,
            ),
            A.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
            ToTensorV2(),
        ]
    )


def get_val_transforms(image_size: int = IMAGE_SIZE) -> A.Compose:
    """Validation / inference pipeline — deterministic resize + normalise."""
    return A.Compose(
        [
            A.Resize(image_size, image_size),
            A.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
            ToTensorV2(),
        ]
    )


# ===================================================================
# 3. WeightedRandomSampler builder
# ===================================================================
def build_weighted_sampler(labels: np.ndarray) -> WeightedRandomSampler:
    """
    Build a WeightedRandomSampler that oversamples minority classes so
    each class is seen roughly equally during training.
    """
    class_counts = np.bincount(labels, minlength=NUM_CLASSES).astype(np.float64)
    class_weights = 1.0 / (class_counts + 1e-6)  # inverse frequency
    sample_weights = class_weights[labels]
    sample_weights = torch.from_numpy(sample_weights).double()

    sampler = WeightedRandomSampler(
        weights=sample_weights,
        num_samples=len(sample_weights),
        replacement=True,
    )
    logger.info(
        f"WeightedRandomSampler created — class weights: "
        f"{dict(zip(CLASS_NAMES, class_weights.round(4)))}"
    )
    return sampler


# ===================================================================
# 4. SkinEfficientNet Model
# ===================================================================
class SkinEfficientNet(nn.Module):
    """
    EfficientNet-B3 backbone (pretrained on ImageNet) with a custom
    two-layer classification head for 7-class skin lesion classification.

    Architecture:
        EfficientNet-B3 backbone (first 3 blocks frozen)
        → AdaptiveAvgPool
        → Dropout(0.4)
        → Linear(1536, 512)
        → ReLU
        → Dropout(0.3)
        → Linear(512, 7)

    The backbone feature dimension for EfficientNet-B3 is 1536.
    """

    def __init__(
        self,
        num_classes: int = NUM_CLASSES,
        pretrained: bool = True,
        drop_head_1: float = 0.4,
        drop_head_2: float = 0.3,
        hidden_dim: int = 512,
    ):
        super().__init__()

        # ---- Backbone -----------------------------------------------------
        self.backbone = timm.create_model(
            "efficientnet_b3",
            pretrained=pretrained,
            num_classes=0,          # remove original classifier
            global_pool="avg",      # keep global average pooling
        )
        backbone_dim = self.backbone.num_features  # 1536 for B3

        # ---- Custom classification head -----------------------------------
        self.classifier = nn.Sequential(
            nn.Dropout(p=drop_head_1),
            nn.Linear(backbone_dim, hidden_dim),
            nn.ReLU(inplace=True),
            nn.Dropout(p=drop_head_2),
            nn.Linear(hidden_dim, num_classes),
        )

        # ---- Freeze first 3 blocks ---------------------------------------
        self._freeze_early_blocks(num_blocks_to_freeze=3)

        logger.info(
            f"SkinEfficientNet initialised — backbone_dim={backbone_dim}, "
            f"head=[{backbone_dim}→{hidden_dim}→{num_classes}], "
            f"frozen_blocks=3"
        )

    def _freeze_early_blocks(self, num_blocks_to_freeze: int = 3) -> None:
        """
        Freeze the first `num_blocks_to_freeze` blocks of the EfficientNet
        backbone to preserve low-level feature extractors and reduce
        overfitting on small datasets.
        """
        # EfficientNet in timm organises blocks under self.backbone.blocks
        if hasattr(self.backbone, "blocks"):
            for i, block in enumerate(self.backbone.blocks):
                if i < num_blocks_to_freeze:
                    for param in block.parameters():
                        param.requires_grad = False
            logger.info(
                f"Froze {num_blocks_to_freeze} / {len(self.backbone.blocks)} "
                f"backbone blocks"
            )
        else:
            # Fallback: freeze by named children
            children = list(self.backbone.children())
            for child in children[:num_blocks_to_freeze]:
                for param in child.parameters():
                    param.requires_grad = False
            logger.info(
                f"Froze first {num_blocks_to_freeze} backbone children "
                f"(fallback method)"
            )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        features = self.backbone(x)      # (B, 1536)
        logits = self.classifier(features)  # (B, num_classes)
        return logits

    def count_trainable_params(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)

    def count_total_params(self) -> int:
        return sum(p.numel() for p in self.parameters())


# ===================================================================
# 5. Focal Loss (implemented from scratch)
# ===================================================================
class FocalLoss(nn.Module):
    """
    Focal Loss for multi-class classification.

    FL(p_t) = -alpha_t * (1 - p_t)^gamma * log(p_t)

    Down-weights easy examples and focuses training on hard, misclassified
    samples — particularly effective for highly imbalanced datasets like
    HAM10000 where nevi dominate.

    Args:
        gamma:   Focusing parameter (default=2). Higher gamma → more focus
                 on hard examples.
        alpha:   Per-class weight tensor of shape (C,). If None, all classes
                 are weighted equally.
        reduction: 'mean' | 'sum' | 'none'
    """

    def __init__(
        self,
        gamma: float = 2.0,
        alpha: Optional[torch.Tensor] = None,
        reduction: str = "mean",
    ):
        super().__init__()
        self.gamma = gamma
        self.reduction = reduction

        if alpha is not None:
            if not isinstance(alpha, torch.Tensor):
                alpha = torch.tensor(alpha, dtype=torch.float32)
            self.register_buffer("alpha", alpha)
        else:
            self.alpha = None

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """
        Args:
            logits:  (B, C) raw class scores (before softmax)
            targets: (B,) integer class labels

        Returns:
            Scalar loss (if reduction='mean' or 'sum') or (B,) per-sample loss.
        """
        num_classes = logits.size(1)

        # Numerically stable log-softmax
        log_probs = F.log_softmax(logits, dim=1)       # (B, C)
        probs = torch.exp(log_probs)                     # (B, C)

        # Gather the probability of the correct class
        targets_one_hot = F.one_hot(targets, num_classes).float()  # (B, C)
        p_t = (probs * targets_one_hot).sum(dim=1)                 # (B,)
        log_p_t = (log_probs * targets_one_hot).sum(dim=1)         # (B,)

        # Focal modulating factor
        focal_weight = (1.0 - p_t) ** self.gamma  # (B,)

        # Per-class alpha weighting
        if self.alpha is not None:
            alpha_t = self.alpha.gather(0, targets)  # (B,)
            focal_weight = alpha_t * focal_weight

        # Focal loss
        loss = -focal_weight * log_p_t  # (B,)

        if self.reduction == "mean":
            return loss.mean()
        elif self.reduction == "sum":
            return loss.sum()
        return loss


# ===================================================================
# 6. Metric Helpers
# ===================================================================
def compute_metrics(
    all_labels: np.ndarray,
    all_preds: np.ndarray,
    all_probs: np.ndarray,
    class_names: List[str] = CLASS_NAMES,
) -> Dict:
    """
    Compute per-class F1 scores and macro AUC (one-vs-rest).

    Args:
        all_labels: (N,) ground-truth integer labels
        all_preds:  (N,) predicted integer labels
        all_probs:  (N, C) softmax probability matrix

    Returns:
        Dictionary with per-class F1, macro F1, per-class AUC, macro AUC.
    """
    # Per-class F1
    per_class_f1 = f1_score(
        all_labels, all_preds, labels=range(len(class_names)), average=None,
        zero_division=0.0,
    )
    macro_f1 = f1_score(all_labels, all_preds, average="macro", zero_division=0.0)

    # Per-class AUC (one-vs-rest)
    try:
        per_class_auc = roc_auc_score(
            all_labels, all_probs, multi_class="ovr", average=None,
            labels=range(len(class_names)),
        )
        macro_auc = roc_auc_score(
            all_labels, all_probs, multi_class="ovr", average="macro",
            labels=range(len(class_names)),
        )
    except ValueError:
        # Can happen if a class has zero samples in the batch
        per_class_auc = np.zeros(len(class_names))
        macro_auc = 0.0

    return {
        "per_class_f1": {
            name: round(float(f), 4)
            for name, f in zip(class_names, per_class_f1)
        },
        "macro_f1": round(float(macro_f1), 4),
        "per_class_auc": {
            name: round(float(a), 4)
            for name, a in zip(class_names, per_class_auc)
        },
        "macro_auc": round(float(macro_auc), 4),
    }


def print_epoch_metrics(epoch: int, total_epochs: int, metrics: Dict) -> None:
    """Pretty-print metrics for one epoch."""
    header = f"Epoch [{epoch + 1}/{total_epochs}]"
    logger.info(f"\n{'='*70}")
    logger.info(f"{header}  —  Macro F1: {metrics['macro_f1']:.4f}  |  "
                f"Macro AUC: {metrics['macro_auc']:.4f}")
    logger.info(f"{'-'*70}")
    logger.info(f"  {'Class':>8s}  {'F1':>8s}  {'AUC':>8s}")
    logger.info(f"  {'─'*8}  {'─'*8}  {'─'*8}")
    for cls_name in CLASS_NAMES:
        f1_val = metrics["per_class_f1"].get(cls_name, 0.0)
        auc_val = metrics["per_class_auc"].get(cls_name, 0.0)
        logger.info(f"  {cls_name:>8s}  {f1_val:>8.4f}  {auc_val:>8.4f}")
    logger.info(f"{'='*70}\n")


# ===================================================================
# 7. Training & Validation Loops
# ===================================================================
def train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    epoch: int,
    accum_steps: int = 4,
) -> Tuple[float, np.ndarray, np.ndarray, np.ndarray]:
    """
    Run one full training epoch with gradient accumulation.

    Gradient accumulation allows using a small batch_size (e.g. 8) while
    simulating a larger effective batch (8 * accum_steps = 32).

    Returns:
        avg_loss, all_labels, all_preds, all_probs
    """
    model.train()
    running_loss = 0.0
    all_labels, all_preds, all_probs = [], [], []
    num_batches = len(loader)

    optimizer.zero_grad(set_to_none=True)

    for batch_idx, (images, labels) in enumerate(loader):
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        # Forward
        logits = model(images)
        loss = criterion(logits, labels) / accum_steps  # Scale loss

        # Backward (accumulate gradients)
        loss.backward()

        # Step optimizer every accum_steps batches (or at end of epoch)
        if (batch_idx + 1) % accum_steps == 0 or (batch_idx + 1) == num_batches:
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            optimizer.zero_grad(set_to_none=True)

        # Accumulate metrics (use unscaled loss for logging)
        running_loss += loss.item() * accum_steps
        probs = F.softmax(logits.detach(), dim=1)
        preds = probs.argmax(dim=1)

        all_labels.append(labels.cpu().numpy())
        all_preds.append(preds.cpu().numpy())
        all_probs.append(probs.cpu().numpy())

        if (batch_idx + 1) % max(1, num_batches // 5) == 0:
            logger.info(
                f"  [Train] Epoch {epoch + 1} — Batch {batch_idx + 1}/{num_batches} "
                f"— Loss: {loss.item() * accum_steps:.4f}"
            )

    avg_loss = running_loss / num_batches
    return (
        avg_loss,
        np.concatenate(all_labels),
        np.concatenate(all_preds),
        np.concatenate(all_probs, axis=0),
    )


@torch.no_grad()
def validate(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
) -> Tuple[float, np.ndarray, np.ndarray, np.ndarray]:
    """
    Run validation pass.

    Returns:
        avg_loss, all_labels, all_preds, all_probs
    """
    model.eval()
    running_loss = 0.0
    all_labels, all_preds, all_probs = [], [], []

    for images, labels in loader:
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        logits = model(images)
        loss = criterion(logits, labels)
        running_loss += loss.item()

        probs = F.softmax(logits, dim=1)
        preds = probs.argmax(dim=1)

        all_labels.append(labels.cpu().numpy())
        all_preds.append(preds.cpu().numpy())
        all_probs.append(probs.cpu().numpy())

    avg_loss = running_loss / len(loader)
    return (
        avg_loss,
        np.concatenate(all_labels),
        np.concatenate(all_preds),
        np.concatenate(all_probs, axis=0),
    )


# ===================================================================
# 8. Main Training Orchestrator
# ===================================================================
def train(
    csv_path: str,
    image_dirs: List[str],
    output_dir: str = "models",
    num_epochs: int = 30,
    batch_size: int = 32,
    learning_rate: float = 1e-4,
    weight_decay: float = 1e-5,
    val_ratio: float = 0.2,
    seed: int = 42,
    num_workers: int = 4,
) -> None:
    """
    Full HAM10000 training pipeline.

    Steps:
        1. Load & split dataset (stratified)
        2. Build DataLoaders with WeightedRandomSampler
        3. Initialise SkinEfficientNet + FocalLoss + AdamW + CosineAnnealingLR
        4. Train for `num_epochs`, track per-class F1 and AUC each epoch
        5. Save best model by val macro AUC to `output_dir/skin_model.pth`
    """
    # ---- Seed everything --------------------------------------------------
    torch.manual_seed(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Device: {device}")
    if device.type == "cuda":
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")

    # ---- Output directory -------------------------------------------------
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    best_model_path = output_path / "skin_model.pth"

    # ---- Build full dataset for splitting ---------------------------------
    full_dataset = HAM10000Dataset(
        csv_path=csv_path,
        image_dirs=image_dirs,
        transform=None,  # transforms applied per-split below
    )

    # ---- Stratified train / val split -------------------------------------
    all_labels = full_dataset.labels
    train_indices, val_indices = train_test_split(
        np.arange(len(full_dataset)),
        test_size=val_ratio,
        stratify=all_labels,
        random_state=seed,
    )
    logger.info(
        f"Split: {len(train_indices)} train / {len(val_indices)} val "
        f"(ratio={val_ratio})"
    )

    # ---- Create split datasets with transforms ----------------------------
    train_dataset = HAM10000Subset(
        full_dataset, train_indices, transform=get_train_transforms()
    )
    val_dataset = HAM10000Subset(
        full_dataset, val_indices, transform=get_val_transforms()
    )

    # ---- WeightedRandomSampler for training set ---------------------------
    train_labels = all_labels[train_indices]
    sampler = build_weighted_sampler(train_labels)

    # ---- DataLoaders ------------------------------------------------------
    pin_memory = device.type == "cuda"
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        sampler=sampler,
        num_workers=num_workers,
        pin_memory=pin_memory,
        drop_last=True,
        persistent_workers=num_workers > 0,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory,
        persistent_workers=num_workers > 0,
    )

    # ---- Model ------------------------------------------------------------
    model = SkinEfficientNet(num_classes=NUM_CLASSES, pretrained=True)
    model = model.to(device)
    logger.info(
        f"Model params — Total: {model.count_total_params():,} | "
        f"Trainable: {model.count_trainable_params():,}"
    )

    # ---- Loss: FocalLoss with per-class alpha from inverse frequency ------
    class_counts = np.bincount(all_labels, minlength=NUM_CLASSES).astype(np.float64)
    alpha_weights = 1.0 / (class_counts + 1e-6)
    alpha_weights = alpha_weights / alpha_weights.sum() * NUM_CLASSES  # normalise
    alpha_tensor = torch.tensor(alpha_weights, dtype=torch.float32).to(device)

    criterion = FocalLoss(gamma=2.0, alpha=alpha_tensor, reduction="mean")
    logger.info(f"FocalLoss — gamma=2.0, alpha={dict(zip(CLASS_NAMES, alpha_weights.round(4)))}")

    # ---- Optimiser & Scheduler --------------------------------------------
    optimizer = AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=learning_rate,
        weight_decay=weight_decay,
    )
    scheduler = CosineAnnealingLR(optimizer, T_max=num_epochs, eta_min=1e-7)

    logger.info(f"Optimizer: AdamW(lr={learning_rate}, wd={weight_decay})")
    logger.info(f"Scheduler: CosineAnnealingLR(T_max={num_epochs})")

    # ---- Training loop ----------------------------------------------------
    best_val_auc = 0.0
    training_history: List[Dict] = []

    logger.info(f"\n{'#'*70}")
    logger.info(f"  Starting training — {num_epochs} epochs, batch_size={batch_size}")
    logger.info(f"{'#'*70}\n")

    for epoch in range(num_epochs):
        epoch_start = time.time()

        # ---- Train --------------------------------------------------------
        train_loss, train_labels_arr, train_preds, train_probs = train_one_epoch(
            model, train_loader, criterion, optimizer, device, epoch
        )
        train_metrics = compute_metrics(train_labels_arr, train_preds, train_probs)

        # ---- Validate -----------------------------------------------------
        val_loss, val_labels_arr, val_preds, val_probs = validate(
            model, val_loader, criterion, device
        )
        val_metrics = compute_metrics(val_labels_arr, val_preds, val_probs)

        # ---- Scheduler step -----------------------------------------------
        scheduler.step()
        current_lr = optimizer.param_groups[0]["lr"]

        epoch_time = time.time() - epoch_start

        # ---- Log ----------------------------------------------------------
        logger.info(
            f"Epoch [{epoch + 1}/{num_epochs}] — "
            f"Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | "
            f"LR: {current_lr:.2e} | Time: {epoch_time:.1f}s"
        )

        logger.info("--- Train Metrics ---")
        print_epoch_metrics(epoch, num_epochs, train_metrics)

        logger.info("--- Validation Metrics ---")
        print_epoch_metrics(epoch, num_epochs, val_metrics)

        # ---- Save best model by val AUC -----------------------------------
        if val_metrics["macro_auc"] > best_val_auc:
            best_val_auc = val_metrics["macro_auc"]
            checkpoint = {
                "epoch": epoch + 1,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "scheduler_state_dict": scheduler.state_dict(),
                "best_val_auc": best_val_auc,
                "val_metrics": val_metrics,
                "class_names": CLASS_NAMES,
                "class_display_names": CLASS_DISPLAY_NAMES,
                "image_size": IMAGE_SIZE,
                "imagenet_mean": IMAGENET_MEAN,
                "imagenet_std": IMAGENET_STD,
            }
            torch.save(checkpoint, best_model_path)
            logger.info(
                f"★ New best model saved — Val AUC: {best_val_auc:.4f} "
                f"→ {best_model_path}"
            )

        # ---- History ------------------------------------------------------
        training_history.append(
            {
                "epoch": epoch + 1,
                "train_loss": train_loss,
                "val_loss": val_loss,
                "train_macro_f1": train_metrics["macro_f1"],
                "val_macro_f1": val_metrics["macro_f1"],
                "train_macro_auc": train_metrics["macro_auc"],
                "val_macro_auc": val_metrics["macro_auc"],
                "lr": current_lr,
            }
        )

    # ---- Final summary ----------------------------------------------------
    logger.info(f"\n{'#'*70}")
    logger.info(f"  Training complete — Best Val AUC: {best_val_auc:.4f}")
    logger.info(f"  Best model saved to: {best_model_path}")
    logger.info(f"{'#'*70}")

    # Save training history as CSV
    history_df = pd.DataFrame(training_history)
    history_path = output_path / "skin_model_training_history.csv"
    history_df.to_csv(history_path, index=False)
    logger.info(f"Training history saved to: {history_path}")

    # Final classification report on validation set
    logger.info("\n--- Final Validation Classification Report ---")
    _, final_labels, final_preds, _ = validate(model, val_loader, criterion, device)
    report = classification_report(
        final_labels, final_preds,
        target_names=CLASS_NAMES,
        digits=4,
        zero_division=0.0,
    )
    logger.info(f"\n{report}")

    # Confusion matrix
    cm = confusion_matrix(final_labels, final_preds)
    logger.info("Confusion Matrix:")
    logger.info(f"\n{cm}")

    logger.info("\n" + "=" * 70)
    logger.info("MEDICAL DISCLAIMER: This model is for research/educational purposes")
    logger.info("only. It is NOT a substitute for professional dermatological diagnosis.")
    logger.info("Always consult a qualified dermatologist for skin lesion evaluation.")
    logger.info("=" * 70)


# ===================================================================
# Helper: Subset wrapper that applies per-split transforms
# ===================================================================
class HAM10000Subset(Dataset):
    """
    Wraps a HAM10000Dataset with specific indices and transform.
    This allows train/val splits to use different augmentation pipelines
    while sharing the same underlying metadata.
    """

    def __init__(
        self,
        parent_dataset: HAM10000Dataset,
        indices: np.ndarray,
        transform: Optional[A.Compose] = None,
    ):
        self.parent = parent_dataset
        self.indices = indices
        self.transform = transform

    def __len__(self) -> int:
        return len(self.indices)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        real_idx = self.indices[idx]
        row = self.parent.samples.iloc[real_idx]
        image = np.array(Image.open(row["path"]).convert("RGB"))

        if self.transform is not None:
            augmented = self.transform(image=image)
            image = augmented["image"]
        else:
            image = torch.from_numpy(image).permute(2, 0, 1).float() / 255.0

        return image, int(row["label"])


# ===================================================================
# 9. CLI Entry Point
# ===================================================================
if __name__ == "__main__":
    """
    Usage:
        python -m src.training.train_skin_model \
            --csv data/HAM10000/HAM10000_metadata.csv \
            --images data/HAM10000/HAM10000_images_part_1 \
                     data/HAM10000/HAM10000_images_part_2 \
            --epochs 30 \
            --batch-size 32 \
            --lr 1e-4

    Download HAM10000 from:
        https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/DBW86T
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Train EfficientNet-B3 on HAM10000 for skin lesion classification"
    )
    parser.add_argument(
        "--csv",
        type=str,
        default="data/HAM10000/dataverse_files/HAM10000_metadata.csv",
        help="Path to HAM10000_metadata.csv",
    )
    parser.add_argument(
        "--images",
        type=str,
        nargs="+",
        default=[
            "data/HAM10000/dataverse_files/HAM10000_images_part_1",
            "data/HAM10000/dataverse_files/HAM10000_images_part_2",
        ],
        help="Paths to image directories",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="models",
        help="Directory to save trained model",
    )
    parser.add_argument("--epochs", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--weight-decay", type=float, default=1e-5)
    parser.add_argument("--val-ratio", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--workers", type=int, default=2)

    args = parser.parse_args()

    train(
        csv_path=args.csv,
        image_dirs=args.images,
        output_dir=args.output_dir,
        num_epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        weight_decay=args.weight_decay,
        val_ratio=args.val_ratio,
        seed=args.seed,
        num_workers=args.workers,
    )
