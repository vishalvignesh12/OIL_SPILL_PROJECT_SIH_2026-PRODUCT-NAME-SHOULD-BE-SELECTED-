"""
Tests for the U-Net segmentation model.
"""

import sys
from pathlib import Path

import torch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.models.unet import UNet


def test_unet_output_shape():
    """
    The U-Net output should have the same height and width
    as the input image.
    """

    model = UNet(
        in_channels=1,
        out_channels=1,
    )

    x = torch.randn(
        1,
        1,
        256,
        256,
    )

    output = model(x)

    assert output.shape == (
        1,
        1,
        256,
        256,
    )


def test_unet_batch_output_shape():
    """The U-Net should support multiple images in a batch."""

    model = UNet()

    x = torch.randn(
        2,
        1,
        256,
        256,
    )

    output = model(x)

    assert output.shape == (
        2,
        1,
        256,
        256,
    )