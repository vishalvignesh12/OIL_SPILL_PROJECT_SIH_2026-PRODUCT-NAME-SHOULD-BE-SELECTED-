"""
PyTorch dataset for Sentinel-1 SAR oil spill segmentation.
"""

from pathlib import Path
from typing import List, Tuple

import numpy as np
import rasterio
import torch
from torch.utils.data import Dataset

from src.config import IMAGES_DIR, MASKS_DIR


SUPPORTED_EXTENSIONS = {".tif", ".tiff"}


def get_tiff_files(directory: Path) -> List[Path]:
    """Return sorted TIFF files from a directory."""

    if not directory.exists():
        return []

    return sorted(
        path
        for path in directory.iterdir()
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def create_image_mask_pairs(
    images_dir: Path,
    masks_dir: Path,
) -> List[Tuple[Path, Path]]:
    """
    Match images and masks using their filename.

    Example:
        images/00000.tif
        masks/00000.tif
    """

    image_files = get_tiff_files(images_dir)
    mask_files = get_tiff_files(masks_dir)

    mask_map = {
        mask.stem: mask
        for mask in mask_files
    }

    pairs = []

    for image_path in image_files:
        mask_path = mask_map.get(image_path.stem)

        if mask_path is not None:
            pairs.append(
                (image_path, mask_path)
            )

    return pairs


class OilSpillDataset(Dataset):
    """
    Dataset for binary oil spill semantic segmentation.

    Returns:
        image: Tensor [C, H, W]
        mask:  Tensor [1, H, W]
    """

    def __init__(
        self,
        images_dir: Path = IMAGES_DIR,
        masks_dir: Path = MASKS_DIR,
        image_size: int = 256,
    ):
        self.image_size = image_size

        self.pairs = create_image_mask_pairs(
            images_dir,
            masks_dir,
        )

        if not self.pairs:
            raise ValueError(
                "No image-mask pairs found. "
                "Check the dataset paths and filenames."
            )

    def __len__(self) -> int:
        return len(self.pairs)

    @staticmethod
    def _normalize_image(
        image: np.ndarray,
    ) -> np.ndarray:
        """
        Normalize each channel independently.

        Uses percentile clipping to reduce the
        influence of extreme SAR pixel values.
        """

        normalized_channels = []

        for channel in image:
            lower = np.percentile(
                channel,
                1,
            )

            upper = np.percentile(
                channel,
                99,
            )

            channel = np.clip(
                channel,
                lower,
                upper,
            )

            denominator = upper - lower

            if denominator > 0:
                channel = (
                    channel - lower
                ) / denominator
            else:
                channel = np.zeros_like(
                    channel,
                    dtype=np.float32,
                )

            normalized_channels.append(
                channel.astype(np.float32)
            )

        return np.stack(
            normalized_channels,
            axis=0,
        )

    def __getitem__(
        self,
        index: int,
    ) -> Tuple[torch.Tensor, torch.Tensor]:

        image_path, mask_path = self.pairs[index]

        # Read SAR image.
        with rasterio.open(
            image_path
        ) as src:

            image = src.read().astype(
                np.float32
            )

        # Read binary mask.
        with rasterio.open(
            mask_path
        ) as src:

            mask = src.read(1).astype(
                np.float32
            )

        # Normalize SAR image.
        image = self._normalize_image(
            image
        )

        # Convert to PyTorch tensors.
        image_tensor = torch.from_numpy(
            image
        )

        mask_tensor = torch.from_numpy(
            mask
        ).unsqueeze(0)

        # Resize image and mask.
        image_tensor = torch.nn.functional.interpolate(
            image_tensor.unsqueeze(0),
            size=(
                self.image_size,
                self.image_size,
            ),
            mode="bilinear",
            align_corners=False,
        ).squeeze(0)

        mask_tensor = torch.nn.functional.interpolate(
            mask_tensor.unsqueeze(0),
            size=(
                self.image_size,
                self.image_size,
            ),
            mode="nearest",
        ).squeeze(0)

        # Ensure mask remains binary.
        mask_tensor = (
            mask_tensor > 0.5
        ).float()

        return (
            image_tensor,
            mask_tensor,
        )