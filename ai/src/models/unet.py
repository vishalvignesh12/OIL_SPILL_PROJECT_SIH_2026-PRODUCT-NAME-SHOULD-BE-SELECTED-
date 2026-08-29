"""
U-Net model for oil spill semantic segmentation.

The model accepts a satellite/SAR image tensor and produces
a single-channel segmentation logits map.
"""

import torch
import torch.nn as nn


class DoubleConv(nn.Module):
    """Two convolution blocks followed by BatchNorm and ReLU."""

    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()

        self.layers = nn.Sequential(
            nn.Conv2d(
                in_channels,
                out_channels,
                kernel_size=3,
                padding=1,
                bias=False,
            ),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),

            nn.Conv2d(
                out_channels,
                out_channels,
                kernel_size=3,
                padding=1,
                bias=False,
            ),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.layers(x)


class Down(nn.Module):
    """Downsampling block."""

    def __init__(self, in_channels: int, out_channels: int):
        super().__init__()

        self.layers = nn.Sequential(
            nn.MaxPool2d(kernel_size=2),
            DoubleConv(in_channels, out_channels),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.layers(x)


class Up(nn.Module):
    """Upsampling block with skip connection."""

    def __init__(
        self,
        in_channels: int,
        skip_channels: int,
        out_channels: int,
    ):
        super().__init__()

        self.up = nn.ConvTranspose2d(
            in_channels,
            out_channels,
            kernel_size=2,
            stride=2,
        )

        self.conv = DoubleConv(
            out_channels + skip_channels,
            out_channels,
        )

    def forward(
        self,
        x: torch.Tensor,
        skip: torch.Tensor,
    ) -> torch.Tensor:

        x = self.up(x)

        x = torch.cat(
            [skip, x],
            dim=1,
        )

        return self.conv(x)


class UNet(nn.Module):
    """
    U-Net for binary oil spill segmentation.

    Args:
        in_channels:
            Number of input image channels.
            This will be confirmed after inspecting
            the Sentinel-1 dataset.

        out_channels:
            Number of output segmentation channels.
            1 for binary oil spill segmentation.
    """

    def __init__(
        self,
        in_channels: int = 1,
        out_channels: int = 1,
    ):
        super().__init__()

        self.enc1 = DoubleConv(
            in_channels,
            64,
        )

        self.enc2 = Down(
            64,
            128,
        )

        self.enc3 = Down(
            128,
            256,
        )

        self.enc4 = Down(
            256,
            512,
        )

        self.bottleneck = Down(
            512,
            1024,
        )

        self.up4 = Up(
            1024,
            512,
            512,
        )

        self.up3 = Up(
            512,
            256,
            256,
        )

        self.up2 = Up(
            256,
            128,
            128,
        )

        self.up1 = Up(
            128,
            64,
            64,
        )

        self.output = nn.Conv2d(
            64,
            out_channels,
            kernel_size=1,
        )

    def forward(
        self,
        x: torch.Tensor,
    ) -> torch.Tensor:

        enc1 = self.enc1(x)
        enc2 = self.enc2(enc1)
        enc3 = self.enc3(enc2)
        enc4 = self.enc4(enc3)

        bottleneck = self.bottleneck(enc4)

        dec4 = self.up4(
            bottleneck,
            enc4,
        )

        dec3 = self.up3(
            dec4,
            enc3,
        )

        dec2 = self.up2(
            dec3,
            enc2,
        )

        dec1 = self.up1(
            dec2,
            enc1,
        )

        return self.output(dec1)