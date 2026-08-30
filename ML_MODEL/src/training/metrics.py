"""
Pixel-level metrics (PRD §14 / Phase 4): IoU, Dice, precision, recall, F1.
Also exposes a scene-level confusion matrix and AUC-ROC (treating each
scene as oil-present / oil-absent based on predicted foreground fraction),
which is what a hackathon evaluator will actually want to see plotted.
"""
from __future__ import annotations

import numpy as np
import torch
from sklearn.metrics import confusion_matrix, roc_auc_score


@torch.no_grad()
def pixel_metrics(logits: torch.Tensor, targets: torch.Tensor, threshold: float = 0.5, eps: float = 1e-7):
    probs = torch.sigmoid(logits).squeeze(1)  # (B, H, W)
    preds = (probs > threshold).float()
    targets = targets.float()

    tp = (preds * targets).sum().item()
    fp = (preds * (1 - targets)).sum().item()
    fn = ((1 - preds) * targets).sum().item()
    tn = ((1 - preds) * (1 - targets)).sum().item()

    iou = tp / (tp + fp + fn + eps)
    dice = 2 * tp / (2 * tp + fp + fn + eps)
    precision = tp / (tp + fp + eps)
    recall = tp / (tp + fn + eps)
    f1 = 2 * precision * recall / (precision + recall + eps)

    return {
        "iou": iou, "dice": dice, "precision": precision,
        "recall": recall, "f1": f1,
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
    }


def scene_level_confusion_and_auc(
    scene_probs: list[float], scene_labels: list[int], threshold: float = 0.5
):
    """
    scene_probs: max (or mean) predicted foreground probability per scene.
    scene_labels: 1 if scene truly contains oil, else 0.
    Returns confusion matrix (2x2) and AUC-ROC.
    """
    preds = [1 if p > threshold else 0 for p in scene_probs]
    cm = confusion_matrix(scene_labels, preds, labels=[0, 1])
    auc = roc_auc_score(scene_labels, scene_probs) if len(set(scene_labels)) > 1 else float("nan")
    return cm, auc


def aggregate_epoch_metrics(batch_metrics: list[dict]) -> dict:
    """Micro-averages TP/FP/FN/TN across batches, then recomputes derived metrics
    (more correct than macro-averaging per-batch ratios for imbalanced data)."""
    tp = sum(m["tp"] for m in batch_metrics)
    fp = sum(m["fp"] for m in batch_metrics)
    fn = sum(m["fn"] for m in batch_metrics)
    tn = sum(m["tn"] for m in batch_metrics)
    eps = 1e-7
    iou = tp / (tp + fp + fn + eps)
    dice = 2 * tp / (2 * tp + fp + fn + eps)
    precision = tp / (tp + fp + eps)
    recall = tp / (tp + fn + eps)
    f1 = 2 * precision * recall / (precision + recall + eps)
    return {"iou": iou, "dice": dice, "precision": precision, "recall": recall, "f1": f1}
