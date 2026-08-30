from pathlib import Path

import numpy as np
import rasterio
import torch

from src.data.dataset import (
    create_image_mask_pairs,
    OilSpillDataset,
)


def write_tiff(path, data):
    """Create a small test TIFF file."""

    height, width = data.shape[-2:]

    count = 1

    if data.ndim == 3:
        count = data.shape[0]

    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=count,
        dtype=data.dtype,
    ) as dst:

        if data.ndim == 2:
            dst.write(data, 1)
        else:
            dst.write(data)


def test_image_mask_pairing(tmp_path):

    images_dir = tmp_path / "images"
    masks_dir = tmp_path / "masks"

    images_dir.mkdir()
    masks_dir.mkdir()

    image = np.random.rand(
        1,
        32,
        32,
    ).astype(np.float32)

    mask = np.zeros(
        (32, 32),
        dtype=np.uint8,
    )

    mask[10:20, 10:20] = 1

    write_tiff(
        images_dir / "00001.tif",
        image,
    )

    write_tiff(
        masks_dir / "00001.tif",
        mask,
    )

    pairs = create_image_mask_pairs(
        images_dir,
        masks_dir,
    )

    assert len(pairs) == 1


def test_dataset_returns_correct_shapes(
    tmp_path,
):

    images_dir = tmp_path / "images"
    masks_dir = tmp_path / "masks"

    images_dir.mkdir()
    masks_dir.mkdir()

    image = np.random.rand(
        1,
        64,
        64,
    ).astype(np.float32)

    mask = np.zeros(
        (64, 64),
        dtype=np.uint8,
    )

    mask[20:40, 20:40] = 1

    write_tiff(
        images_dir / "00001.tif",
        image,
    )

    write_tiff(
        masks_dir / "00001.tif",
        mask,
    )

    dataset = OilSpillDataset(
        images_dir=images_dir,
        masks_dir=masks_dir,
        image_size=256,
    )

    image_tensor, mask_tensor = dataset[0]

    assert image_tensor.shape == (
        1,
        256,
        256,
    )

    assert mask_tensor.shape == (
        1,
        256,
        256,
    )

    assert image_tensor.dtype == torch.float32
    assert mask_tensor.dtype == torch.float32

    assert set(
        mask_tensor.unique().tolist()
    ).issubset({0.0, 1.0})