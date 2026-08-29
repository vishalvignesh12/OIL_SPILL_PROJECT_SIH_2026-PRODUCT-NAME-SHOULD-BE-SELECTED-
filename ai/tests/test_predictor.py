import numpy as np
import rasterio
import torch

from rasterio.transform import from_origin

from src.models.unet import UNet
from src.inference.predictor import OilSpillPredictor


def create_test_checkpoint(path):

    model = UNet(
        in_channels=1,
        out_channels=1,
    )

    checkpoint = {
        "model_state_dict": model.state_dict(),
    }

    torch.save(
        checkpoint,
        path,
    )


def create_test_tiff(path):

    image = np.random.rand(
        64,
        64,
    ).astype(np.float32)

    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=image.shape[0],
        width=image.shape[1],
        count=1,
        dtype="float32",
        transform=from_origin(
            0,
            0,
            1,
            1,
        ),
    ) as dst:

        dst.write(
            image,
            1,
        )


def test_predictor_initialization(
    tmp_path,
):

    checkpoint_path = (
        tmp_path / "model.pt"
    )

    create_test_checkpoint(
        checkpoint_path
    )

    predictor = OilSpillPredictor(
        model_path=checkpoint_path,
        device="cpu",
    )

    assert predictor.device.type == "cpu"


def test_predictor_load_image(
    tmp_path,
):

    checkpoint_path = (
        tmp_path / "model.pt"
    )

    image_path = (
        tmp_path / "image.tif"
    )

    create_test_checkpoint(
        checkpoint_path
    )

    create_test_tiff(
        image_path
    )

    predictor = OilSpillPredictor(
        model_path=checkpoint_path,
        device="cpu",
    )

    image = predictor.load_image(
        image_path
    )

    assert image.shape == (
        64,
        64,
    )


def test_predictor_preprocess(
    tmp_path,
):

    checkpoint_path = (
        tmp_path / "model.pt"
    )

    create_test_checkpoint(
        checkpoint_path
    )

    predictor = OilSpillPredictor(
        model_path=checkpoint_path,
        device="cpu",
        image_size=128,
    )

    image = np.random.rand(
        64,
        64,
    ).astype(np.float32)

    tensor, original_shape = (
        predictor.preprocess(
            image
        )
    )

    assert tensor.shape == (
        1,
        1,
        128,
        128,
    )

    assert original_shape == (
        64,
        64,
    )


def test_predictor_complete_pipeline(
    tmp_path,
):

    checkpoint_path = (
        tmp_path / "model.pt"
    )

    image_path = (
        tmp_path / "image.tif"
    )

    create_test_checkpoint(
        checkpoint_path
    )

    create_test_tiff(
        image_path
    )

    predictor = OilSpillPredictor(
        model_path=checkpoint_path,
        device="cpu",
        image_size=64,
        min_pixels=1,
    )

    result = predictor.predict(
        image_path
    )

    assert "mask" in result
    assert "probability_map" in result
    assert "regions" in result
    assert "original_shape" in result
    assert "oil_spill_detected" in result

    assert result["mask"].shape == (
        64,
        64,
    )

    assert result[
        "probability_map"
    ].shape == (
        64,
        64,
    )

    assert result[
        "original_shape"
    ] == (
        64,
        64,
    )

    assert isinstance(
        result["regions"],
        list,
    )

    assert isinstance(
        result[
            "oil_spill_detected"
        ],
        bool,
    )