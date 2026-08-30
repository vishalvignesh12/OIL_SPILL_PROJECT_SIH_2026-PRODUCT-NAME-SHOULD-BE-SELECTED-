"""
Evaluation pipeline for oil spill segmentation.
"""

from pathlib import Path

import torch
from torch.utils.data import DataLoader

from src.data.dataset import OilSpillDataset
from src.models.unet import UNet
from src.training.losses import BCEDiceLoss
from src.training.metrics import (
    dice_score,
    iou_score,
    precision_score,
    recall_score,
)


def get_device() -> torch.device:
    """Use CUDA if available, otherwise CPU."""

    if torch.cuda.is_available():
        return torch.device("cuda")

    return torch.device("cpu")


def evaluate_model(
    model_path: str | Path,
    dataset,
    batch_size: int = 2,
    device: str | None = None,
):
    """
    Evaluate a trained model on a dataset.
    """

    if device is None:
        device = get_device()
    else:
        device = torch.device(device)

    checkpoint = torch.load(
        model_path,
        map_location=device,
    )

    model = UNet(
        in_channels=1,
        out_channels=1,
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model.to(device)
    model.eval()

    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,
    )

    criterion = BCEDiceLoss()

    total_loss = 0.0
    total_dice = 0.0
    total_iou = 0.0
    total_precision = 0.0
    total_recall = 0.0

    with torch.no_grad():

        for images, masks in loader:

            images = images.to(device)
            masks = masks.to(device)

            outputs = model(images)

            loss = criterion(
                outputs,
                masks,
            )

            total_loss += loss.item()

            total_dice += dice_score(
                outputs,
                masks,
            )

            total_iou += iou_score(
                outputs,
                masks,
            )

            total_precision += precision_score(
                outputs,
                masks,
            )

            total_recall += recall_score(
                outputs,
                masks,
            )

    num_batches = len(loader)

    if num_batches == 0:
        raise ValueError(
            "Evaluation dataset is empty."
        )

    results = {
        "loss": total_loss / num_batches,
        "dice": total_dice / num_batches,
        "iou": total_iou / num_batches,
        "precision": total_precision / num_batches,
        "recall": total_recall / num_batches,
    }

    return results


if __name__ == "__main__":

    device = get_device()

    print(f"\nUsing device: {device}")

    dataset = OilSpillDataset(
        image_size=256,
    )

    print(
        f"Evaluation dataset size: {len(dataset)}"
    )

    results = evaluate_model(
        model_path="models/best_model.pt",
        dataset=dataset,
        device=device,
    )

    print("\n=== EVALUATION RESULTS ===")

    for name, value in results.items():

        print(
            f"{name.capitalize()}: {value:.4f}"
        )