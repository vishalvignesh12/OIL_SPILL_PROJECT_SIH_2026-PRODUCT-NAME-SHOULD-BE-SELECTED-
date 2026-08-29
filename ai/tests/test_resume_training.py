from pathlib import Path

import torch

from src.models.unet import UNet
from src.training.checkpoint import (
    save_checkpoint,
    load_checkpoint,
)


def test_resume_checkpoint_starts_after_saved_epoch(
    tmp_path,
):

    checkpoint_path = (
        tmp_path / "latest_checkpoint.pt"
    )

    model = UNet(
        in_channels=1,
        out_channels=1,
    )

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=1e-4,
    )

    save_checkpoint(
        path=checkpoint_path,
        model=model,
        optimizer=optimizer,
        epoch=3,
        best_dice=0.75,
    )

    new_model = UNet(
        in_channels=1,
        out_channels=1,
    )

    new_optimizer = torch.optim.Adam(
        new_model.parameters(),
        lr=1e-4,
    )

    checkpoint = load_checkpoint(
        path=checkpoint_path,
        model=new_model,
        optimizer=new_optimizer,
        device="cpu",
    )

    start_epoch = checkpoint["epoch"]

    assert start_epoch == 3
    assert start_epoch + 1 == 4


def test_resume_restores_best_dice(
    tmp_path,
):

    checkpoint_path = (
        tmp_path / "latest_checkpoint.pt"
    )

    model = UNet(
        in_channels=1,
        out_channels=1,
    )

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=1e-4,
    )

    save_checkpoint(
        path=checkpoint_path,
        model=model,
        optimizer=optimizer,
        epoch=7,
        best_dice=0.8432,
    )

    new_model = UNet(
        in_channels=1,
        out_channels=1,
    )

    checkpoint = load_checkpoint(
        path=checkpoint_path,
        model=new_model,
        device="cpu",
    )

    best_dice = checkpoint.get(
        "best_dice",
        0.0,
    )

    assert best_dice == 0.8432