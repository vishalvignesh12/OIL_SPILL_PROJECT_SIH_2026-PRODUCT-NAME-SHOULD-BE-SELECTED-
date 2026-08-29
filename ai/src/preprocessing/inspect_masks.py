"""
Inspect oil spill segmentation masks.

Usage:
    python src/preprocessing/inspect_masks.py <mask_directory>
"""

import sys
from pathlib import Path

import numpy as np
import rasterio


def inspect_masks(mask_dir: Path, sample_count: int = 5) -> None:
    """Inspect oil spill mask files in the given directory."""

    if not mask_dir.exists():
        print(f"ERROR: Directory does not exist:\n{mask_dir}")
        return

    mask_files = sorted(
        list(mask_dir.glob("*.tif")) +
        list(mask_dir.glob("*.tiff"))
    )

    print("\n=== OIL SPILL MASK INSPECTION ===")
    print(f"Mask directory: {mask_dir.resolve()}")
    print(f"Total masks found: {len(mask_files)}\n")

    if not mask_files:
        print("No TIFF mask files found.")
        return

    for mask_path in mask_files[:sample_count]:
        with rasterio.open(mask_path) as dataset:
            mask = dataset.read(1)

        unique_values = np.unique(mask)
        positive_pixels = int(np.sum(mask > 0))
        total_pixels = mask.size

        print(f"File: {mask_path.name}")
        print(f"Size: {mask.shape[1]} x {mask.shape[0]}")
        print(f"Data type: {mask.dtype}")
        print(f"Min / Max: {mask.min()} / {mask.max()}")
        print(f"Unique values: {unique_values.tolist()}")
        print(f"Positive pixels: {positive_pixels} / {total_pixels}")
        print("-" * 50)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage:")
        print("python src/preprocessing/inspect_masks.py <mask_directory>")
        sys.exit(1)

    mask_directory = Path(sys.argv[1])
    inspect_masks(mask_directory)


if __name__ == "__main__":
    main()