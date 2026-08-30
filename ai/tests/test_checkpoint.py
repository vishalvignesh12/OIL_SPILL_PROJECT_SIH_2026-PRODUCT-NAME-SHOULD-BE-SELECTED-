import torch

from src.models.unet import UNet
from src.training.checkpoint import (
    save_checkpoint,
    load_checkpoint,
)


def test_save_and_load_checkpoint(
    tmp_path,
):

    checkpoint_path = (
        tmp_path / "checkpoint.pt"
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
        epoch=5,
        best_dice=0.82,
    )

    assert checkpoint_path.exists()

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

    assert checkpoint["epoch"] == 5
    assert checkpoint["best_dice"] == 0.82


def test_checkpoint_restores_weights(
    tmp_path,
):

    checkpoint_path = (
        tmp_path / "checkpoint.pt"
    )

    model = UNet(
        in_channels=1,
        out_channels=1,
    )

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=1e-4,
    )

    with torch.no_grad():

        for parameter in model.parameters():

            parameter.fill_(0.123)

    save_checkpoint(
        path=checkpoint_path,
        model=model,
        optimizer=optimizer,
        epoch=1,
        best_dice=0.5,
    )

    new_model = UNet(
        in_channels=1,
        out_channels=1,
    )

    load_checkpoint(
        path=checkpoint_path,
        model=new_model,
        device="cpu",
    )

    for parameter in new_model.parameters():

        assert torch.allclose(
            parameter,
            torch.full_like(
                parameter,
                0.123,
            ),
        )