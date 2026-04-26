#!/usr/bin/env python3
"""
Skin Classifier — Inference Test Script
=========================================
Picks one sample image per class from HAM10000 and runs inference
through the SkinDiseaseClassifier to validate end-to-end functionality.

Usage:
    python src/training/test_inference.py
"""

import sys
import os
import json
import pandas as pd
from pathlib import Path

# Ensure project root is on path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from src.ai_models.skin_classifier import SkinDiseaseClassifier


def find_sample_images(csv_path: str, image_dirs: list) -> dict:
    """Pick one image per class from the dataset."""
    df = pd.read_csv(csv_path)

    # Build image lookup
    image_lookup = {}
    for img_dir in image_dirs:
        img_dir_path = Path(img_dir)
        if img_dir_path.is_dir():
            for fpath in img_dir_path.glob("*.jpg"):
                image_lookup[fpath.stem] = str(fpath)

    # Pick one per class
    samples = {}
    classes = ["akiec", "bcc", "bkl", "df", "mel", "nv", "vasc"]
    for cls in classes:
        cls_rows = df[df["dx"] == cls]
        for _, row in cls_rows.iterrows():
            iid = row["image_id"]
            if iid in image_lookup:
                samples[cls] = {
                    "image_id": iid,
                    "path": image_lookup[iid],
                    "ground_truth": cls,
                }
                break

    return samples


def main():
    print("\n" + "=" * 70)
    print("  SKIN CLASSIFIER — INFERENCE TEST")
    print("=" * 70)

    # --- Paths ---
    csv_path = "data/HAM10000/dataverse_files/HAM10000_metadata.csv"
    image_dirs = [
        "data/HAM10000/dataverse_files/HAM10000_images_part_1",
        "data/HAM10000/dataverse_files/HAM10000_images_part_2",
    ]
    model_path = "models/skin_model.pth"

    # --- Check model exists ---
    if not Path(model_path).exists():
        print(f"\n❌ Model not found at {model_path}")
        print("   Train the model first: python -m src.training.train_skin_model")
        return

    # --- Load classifier ---
    print("\n📦 Loading SkinDiseaseClassifier...")
    classifier = SkinDiseaseClassifier(model_path=model_path)

    if not classifier.is_ready():
        print("❌ Classifier not ready!")
        return

    # --- Model info ---
    info = classifier.get_model_info()
    print(f"\n✅ Model loaded successfully")
    print(f"   Device: {info['device']}")
    print(f"   Parameters: {info.get('total_parameters_human', 'N/A')}")
    print(f"   Image size: {info['image_size']}×{info['image_size']}")
    print(f"   Classes: {info['num_classes']}")

    # --- Find sample images ---
    print("\n🔍 Finding sample images (one per class)...")
    samples = find_sample_images(csv_path, image_dirs)
    print(f"   Found {len(samples)} / 7 class samples")

    if not samples:
        print("❌ No sample images found!")
        return

    # --- Run inference on each sample ---
    print("\n" + "─" * 70)
    print(f"  {'Class':<8} {'Image ID':<18} {'Predicted':<8} {'Conf':>8} {'Severity':>10} {'Match':>6}")
    print("─" * 70)

    correct = 0
    total = 0

    for cls_name, sample in samples.items():
        result = classifier.predict_from_file(sample["path"])

        top = result["top_prediction"]
        pred_code = top["condition_code"]
        confidence = top["confidence"]
        severity = result["severity"]

        match = "✅" if pred_code == cls_name else "❌"
        if pred_code == cls_name:
            correct += 1
        total += 1

        print(
            f"  {cls_name:<8} {sample['image_id']:<18} {pred_code:<8} "
            f"{confidence:>7.1%} {severity:>10} {match:>6}"
        )

    print("─" * 70)
    print(f"\n📊 Accuracy on sample images: {correct}/{total} ({correct/total:.0%})")

    # --- Detailed output for ONE sample ---
    print("\n" + "=" * 70)
    print("  DETAILED PREDICTION — Sample Melanoma Image")
    print("=" * 70)

    # Pick melanoma or first available
    detail_cls = "mel" if "mel" in samples else list(samples.keys())[0]
    detail_sample = samples[detail_cls]

    result = classifier.predict_from_file(detail_sample["path"])

    print(f"\n  Ground Truth: {detail_cls}")
    print(f"  Image: {detail_sample['image_id']}")
    print(f"\n  🎯 Top Prediction: {result['top_prediction']['condition']}")
    print(f"  📊 Confidence: {result['top_prediction']['confidence']:.1%}")
    print(f"  ⚡ Severity: {result['severity']}")

    print(f"\n  📋 All Predictions:")
    for pred in result["all_predictions"]:
        bar_len = int(pred["confidence"] * 30)
        bar = "█" * bar_len + "░" * (30 - bar_len)
        print(f"     {pred['condition_code']:<6} {bar} {pred['confidence']:>7.2%}")

    print(f"\n  📝 Confidence Interpretation:")
    print(f"     {result['confidence_interpretation']}")

    print(f"\n  💡 Recommendations:")
    for i, rec in enumerate(result["recommendations"][:3], 1):
        print(f"     {i}. {rec[:100]}{'...' if len(rec) > 100 else ''}")

    print(f"\n  ⚕️  Disclaimer:")
    print(f"     {result['disclaimer'][:120]}...")

    print("\n" + "=" * 70)
    print("  ✅ INFERENCE TEST COMPLETE")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
