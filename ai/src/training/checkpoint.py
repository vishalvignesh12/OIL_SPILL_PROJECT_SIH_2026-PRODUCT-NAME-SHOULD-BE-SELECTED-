"""
Checkpoint utilities for saving and resuming model training.
"""

from pathlib import Path

import torch


def save_checkpoint(
    path: str | Path,
    model,
    optimizer,
    epoch: int,
    best_dice: float,
):
    """
    Save the current training state.
    """

    path = Path(path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    torch.save(
        {
            "epoch": epoch,
            "model_state_dict":
                model.state_dict(),
            "optimizer_state_dict":
                optimizer.state_dict(),
            "best_dice": best_dice,
        },
        path,
    )


def load_checkpoint(
    path: str | Path,
    model,
    optimizer=None,
    device: str | torch.device = "cpu",
):
    """
    Load a training checkpoint.

    Returns:
        checkpoint dictionary
    """

    device = torch.device(device)

    checkpoint = torch.load(
        path,
        map_location=device,
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    if (
        optimizer is not None
        and "optimizer_state_dict"
        in checkpoint
    ):
        optimizer.load_state_dict(
            checkpoint["optimizer_state_dict"]
        )

    return checkpoint