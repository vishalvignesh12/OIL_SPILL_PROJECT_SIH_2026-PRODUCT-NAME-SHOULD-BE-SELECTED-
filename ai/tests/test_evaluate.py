import torch
from torch.utils.data import TensorDataset

from src.models.unet import UNet
from src.training.evaluate import evaluate_model


def create_test_checkpoint(path):

    model = UNet(
        in_channels=1,
        out_channels=1,
    )

    torch.save(
        {
            "model_state_dict":
                model.state_dict()
        },
        path,
    )


def test_evaluate_model(tmp_path):

    checkpoint_path = (
        tmp_path / "model.pt"
    )

    create_test_checkpoint(
        checkpoint_path
    )

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
        ) > 0.5
    ).float()

    dataset = TensorDataset(
        images,
        masks,
    )

    results = evaluate_model(
        model_path=checkpoint_path,
        dataset=dataset,
        batch_size=2,
        device="cpu",
    )

    expected_metrics = [
        "loss",
        "dice",
        "iou",
        "precision",
        "recall",
    ]

    for metric in expected_metrics:

        assert metric in results

        assert isinstance(
            results[metric],
            float,
        )

    assert results["loss"] >= 0

    for metric in [
        "dice",
        "iou",
        "precision",
        "recall",
    ]:

        assert 0 <= results[metric] <= 1


def test_empty_dataset_raises_error(
    tmp_path,
):

    checkpoint_path = (
        tmp_path / "model.pt"
    )

    create_test_checkpoint(
        checkpoint_path
    )

    images = torch.empty(
        0,
        1,
        64,
        64,
    )

    masks = torch.empty(
        0,
        1,
        64,
        64,
    )

    dataset = TensorDataset(
        images,
        masks,
    )

    try:

        evaluate_model(
            model_path=checkpoint_path,
            dataset=dataset,
            device="cpu",
        )

    except ValueError as error:

        assert (
            "empty"
            in str(error).lower()
        )

    else:

        raise AssertionError(
            "Expected ValueError "
            "for empty dataset."
        )