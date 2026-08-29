"""
Training pipeline for oil spill segmentation.
"""

import torch
from torch.utils.data import DataLoader, random_split

from src.config import MODELS_DIR
from src.data.dataset import OilSpillDataset
from src.models.unet import UNet
from src.training.checkpoint import (
    save_checkpoint,
    load_checkpoint,
)
from src.training.losses import BCEDiceLoss
from src.training.metrics import (
    dice_score,
    iou_score,
    precision_score,
    recall_score,
)


def get_device() -> torch.device:
    """Select GPU if available, otherwise CPU."""

    if torch.cuda.is_available():
        return torch.device("cuda")

    return torch.device("cpu")


def create_dataloaders(
    dataset: OilSpillDataset,
    batch_size: int = 2,
    validation_split: float = 0.2,
    seed: int = 42,
):
    """Split the dataset into training and validation sets."""

    total_size = len(dataset)

    validation_size = int(
        total_size * validation_split
    )

    train_size = total_size - validation_size

    generator = torch.Generator().manual_seed(
        seed
    )

    train_dataset, validation_dataset = random_split(
        dataset,
        [train_size, validation_size],
        generator=generator,
    )

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
    )

    validation_loader = DataLoader(
        validation_dataset,
        batch_size=batch_size,
        shuffle=False,
    )

    return train_loader, validation_loader


def train_one_epoch(
    model,
    loader,
    optimizer,
    criterion,
    device,
):
    """Train the model for one epoch."""

    model.train()

    total_loss = 0.0

    for images, masks in loader:

        images = images.to(device)
        masks = masks.to(device)

        optimizer.zero_grad()

        outputs = model(images)

        loss = criterion(
            outputs,
            masks,
        )

        loss.backward()

        optimizer.step()

        total_loss += loss.item()

    return total_loss / len(loader)


def validate(
    model,
    loader,
    criterion,
    device,
):
    """Evaluate the model."""

    model.eval()

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

    return {
        "loss": total_loss / num_batches,
        "dice": total_dice / num_batches,
        "iou": total_iou / num_batches,
        "precision": total_precision / num_batches,
        "recall": total_recall / num_batches,
    }


def train(
    epochs: int = 10,
    batch_size: int = 2,
    learning_rate: float = 1e-4,
    resume: bool = True,
):
    """Run the complete training pipeline."""

    device = get_device()

    print(f"\nUsing device: {device}")

    dataset = OilSpillDataset(
        image_size=256,
    )

    print(
        f"Dataset pairs: {len(dataset)}"
    )

    train_loader, validation_loader = (
        create_dataloaders(
            dataset,
            batch_size=batch_size,
        )
    )

    model = UNet(
        in_channels=1,
        out_channels=1,
    ).to(device)

    criterion = BCEDiceLoss()

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=learning_rate,
    )

    MODELS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    latest_checkpoint_path = (
        MODELS_DIR
        / "latest_checkpoint.pt"
    )

    best_model_path = (
        MODELS_DIR
        / "best_model.pt"
    )

    start_epoch = 0
    best_dice = 0.0

    if (
        resume
        and latest_checkpoint_path.exists()
    ):

        print(
            "\nLoading latest checkpoint..."
        )

        checkpoint = load_checkpoint(
            path=latest_checkpoint_path,
            model=model,
            optimizer=optimizer,
            device=device,
        )

        start_epoch = (
            checkpoint["epoch"]
        )

        best_dice = (
            checkpoint.get(
                "best_dice",
                0.0,
            )
        )

        print(
            f"Resuming from epoch "
            f"{start_epoch + 1}"
        )

        print(
            f"Best Dice so far: "
            f"{best_dice:.4f}"
        )

    for epoch in range(
        start_epoch,
        epochs,
    ):

        print(
            f"\nEpoch "
            f"{epoch + 1}/{epochs}"
        )

        train_loss = train_one_epoch(
            model,
            train_loader,
            optimizer,
            criterion,
            device,
        )

        validation_results = validate(
            model,
            validation_loader,
            criterion,
            device,
        )

        print(
            f"Train Loss: "
            f"{train_loss:.4f}"
        )

        print(
            f"Validation Loss: "
            f"{validation_results['loss']:.4f}"
        )

        print(
            f"Dice: "
            f"{validation_results['dice']:.4f}"
        )

        print(
            f"IoU: "
            f"{validation_results['iou']:.4f}"
        )

        print(
            f"Precision: "
            f"{validation_results['precision']:.4f}"
        )

        print(
            f"Recall: "
            f"{validation_results['recall']:.4f}"
        )

        current_dice = (
            validation_results["dice"]
        )

        if current_dice > best_dice:

            best_dice = current_dice

            save_checkpoint(
                path=best_model_path,
                model=model,
                optimizer=optimizer,
                epoch=epoch + 1,
                best_dice=best_dice,
            )

            print(
                f"Best model saved: "
                f"{best_model_path}"
            )

        save_checkpoint(
            path=latest_checkpoint_path,
            model=model,
            optimizer=optimizer,
            epoch=epoch + 1,
            best_dice=best_dice,
        )

        print(
            f"Latest checkpoint saved: "
            f"{latest_checkpoint_path}"
        )

    print("\nTraining completed.")


if __name__ == "__main__":

    train()