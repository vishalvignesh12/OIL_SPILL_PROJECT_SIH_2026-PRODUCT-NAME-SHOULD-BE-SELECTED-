import torch
from torch.utils.data import DataLoader, TensorDataset

from src.models.unet import UNet
from src.training.losses import BCEDiceLoss
from src.training.train import (
    get_device,
    create_dataloaders,
    train_one_epoch,
    validate,
)


def create_synthetic_loader():
    """Create a small synthetic segmentation dataset."""

    images = torch.rand(
        4,
        1,
        64,
        64,
    )

    masks = (
        torch.rand(
            4,
            1,
            64,
            64,
        ) > 0.8
    ).float()

    dataset = TensorDataset(
        images,
        masks,
    )

    return DataLoader(
        dataset,
        batch_size=2,
        shuffle=False,
    )


def test_get_device():

    device = get_device()

    assert device.type in {
        "cpu",
        "cuda",
    }


def test_train_one_epoch():

    loader = create_synthetic_loader()

    model = UNet(
        in_channels=1,
        out_channels=1,
    )

    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=1e-4,
    )

    criterion = BCEDiceLoss()

    device = torch.device("cpu")

    loss = train_one_epoch(
        model,
        loader,
        optimizer,
        criterion,
        device,
    )

    assert loss > 0


def test_validate():

    loader = create_synthetic_loader()

    model = UNet(
        in_channels=1,
        out_channels=1,
    )

    criterion = BCEDiceLoss()

    device = torch.device("cpu")

    results = validate(
        model,
        loader,
        criterion,
        device,
    )

    assert "loss" in results
    assert "dice" in results
    assert "iou" in results
    assert "precision" in results
    assert "recall" in results

    assert results["loss"] >= 0

    for metric in [
        "dice",
        "iou",
        "precision",
        "recall",
    ]:
        assert 0 <= results[metric] <= 1


def test_create_dataloaders():

    images = torch.rand(
        10,
        1,
        32,
        32,
    )

    masks = (
        torch.rand(
            10,
            1,
            32,
            32,
        ) > 0.5
    ).float()

    dataset = TensorDataset(
        images,
        masks,
    )

    train_loader, validation_loader = (
        create_dataloaders(
            dataset,
            batch_size=2,
            validation_split=0.2,
            seed=42,
        )
    )

    assert len(
        train_loader.dataset
    ) == 8

    assert len(
        validation_loader.dataset
    ) == 2