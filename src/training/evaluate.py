"""
Phase 4 (metrics) + Phase 5 (U-Net vs DeepLabv3+ comparison) + interpretation.

Produces, for a given checkpoint on the held-out Part III test set:
  - pixel-level IoU / Dice / Precision / Recall / F1
  - scene-level confusion matrix + AUC-ROC (oil-present vs oil-absent)
  - side-by-side visualization: SAR image | ground truth | predicted
    probability heatmap (the segmentation equivalent of Grad-CAM — it shows
    directly, per-pixel, where the model is looking, which is a stronger
    interpretability signal here than a classifier's Grad-CAM would be)

Usage:
    python -m src.training.evaluate --checkpoint models/oilspill-v1/best.pt --data-root data/raw
"""
from __future__ import annotations

import argparse
import json
import os

import matplotlib.pyplot as plt
import numpy as np
import torch
from torch.utils.data import DataLoader

from src.inference.predictor import OilSpillPredictor
from src.models.unet import UNet
from src.preprocessing.dataset import OilSpillTileDataset
from src.preprocessing.loader import build_dataset_index
from src.training.metrics import aggregate_epoch_metrics, pixel_metrics, scene_level_confusion_and_auc


def evaluate_pixel_metrics(checkpoint_path: str, test_samples, tile_size=512, batch_size=8, device=None):
    device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
    ckpt = torch.load(checkpoint_path, map_location=device)
    model = UNet(in_channels=2, num_classes=1).to(device)
    model.load_state_dict(ckpt["model_state"])
    model.eval()

    ds = OilSpillTileDataset(test_samples, tile_size=tile_size, train=False, tiles_per_scene_cap=None)
    loader = DataLoader(ds, batch_size=batch_size, shuffle=False, num_workers=4)

    batch_metrics = []
    with torch.no_grad():
        for images, masks in loader:
            images, masks = images.to(device), masks.to(device)
            logits = model(images)
            batch_metrics.append(pixel_metrics(logits, masks))
    return aggregate_epoch_metrics(batch_metrics)


def evaluate_scene_level(checkpoint_path: str, test_samples, threshold=0.5):
    predictor = OilSpillPredictor(checkpoint_path)
    probs, labels = [], []
    for s in test_samples:
        result = predictor.predict(s.image_path, threshold=threshold)
        probs.append(result.max_confidence)
        labels.append(1 if s.category == "oil" else 0)
    cm, auc = scene_level_confusion_and_auc(probs, labels, threshold)
    return cm, auc


def plot_interpretation(checkpoint_path: str, sample, out_path: str, tile_size=512):
    from src.preprocessing.loader import read_mask, read_sar_image
    from src.preprocessing.normalize import normalize_sar

    predictor = OilSpillPredictor(checkpoint_path, tile_size=tile_size)
    result = predictor.predict(sample.image_path)

    raw = read_sar_image(sample.image_path)
    gt_mask = read_mask(sample.mask_path)
    normed = normalize_sar(raw)

    from src.preprocessing.tiling import make_tiles, stitch_predictions
    tiles, offsets = make_tiles(normed, tile_size)
    probs = []
    for t in tiles:
        x = torch.from_numpy(t).unsqueeze(0).float().to(predictor.device)
        with torch.no_grad():
            p = torch.sigmoid(predictor.model(x))[0, 0].cpu().numpy()
        probs.append(p)
    full_prob = stitch_predictions(probs, offsets, raw.shape[1:], tile_size)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    axes[0].imshow(raw[0], cmap="gray")
    axes[0].set_title("SAR (VV)")
    axes[1].imshow(gt_mask, cmap="Reds")
    axes[1].set_title("Ground truth mask")
    axes[2].imshow(raw[0], cmap="gray")
    axes[2].imshow(full_prob, cmap="jet", alpha=0.5)
    axes[2].set_title("Predicted probability heatmap")
    for ax in axes:
        ax.axis("off")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close(fig)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--checkpoint", required=True)
    p.add_argument("--data-root", default="data/raw")
    p.add_argument("--out-dir", default="reports/eval")
    args = p.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)

    samples = build_dataset_index(args.data_root)
    test_samples = [s for s in samples if s.part == "part3"]
    if not test_samples:
        raise SystemExit("No Part III test samples found under data-root — check your download.")

    pixel_results = evaluate_pixel_metrics(args.checkpoint, test_samples)
    cm, auc = evaluate_scene_level(args.checkpoint, test_samples)

    report = {"pixel_metrics": pixel_results, "confusion_matrix": cm.tolist(), "auc_roc": auc}
    with open(os.path.join(args.out_dir, "report.json"), "w") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report, indent=2))

    oil_sample = next((s for s in test_samples if s.category == "oil"), None)
    if oil_sample:
        plot_interpretation(args.checkpoint, oil_sample, os.path.join(args.out_dir, "interpretation_example.png"))
        print(f"Interpretation plot saved to {args.out_dir}/interpretation_example.png")


if __name__ == "__main__":
    main()
