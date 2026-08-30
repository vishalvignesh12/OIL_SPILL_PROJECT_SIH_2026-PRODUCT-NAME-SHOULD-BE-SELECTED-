"""
Analyze oil spill mask distribution.

Calculates oil spill coverage across all binary masks.
"""

import sys
from pathlib import Path

import numpy as np
import rasterio


def analyze_masks(mask_dir: Path) -> None:
    if not mask_dir.exists():
        print(f"ERROR: Directory does not exist: {mask_dir}")
        return

    mask_files = sorted(mask_dir.glob("*.tif"))

    if not mask_files:
        print("No mask files found.")
        return

    coverages = []
    empty_masks = 0

    print("\n=== ANALYZING MASK DISTRIBUTION ===")
    print(f"Directory: {mask_dir}")
    print(f"Total masks: {len(mask_files)}\n")

    for index, mask_path in enumerate(mask_files, start=1):
        with rasterio.open(mask_path) as dataset:
            mask = dataset.read(1)

        positive_pixels = np.count_nonzero(mask > 0)
        total_pixels = mask.size
        coverage_percent = (positive_pixels / total_pixels) * 100

        coverages.append(coverage_percent)

        if positive_pixels == 0:
            empty_masks += 1

        if index % 100 == 0 or index == len(mask_files):
            print(f"Processed {index}/{len(mask_files)} masks")

    coverages = np.array(coverages)

    print("\n=== RESULTS ===")
    print(f"Total masks: {len(mask_files)}")
    print(f"Empty masks: {empty_masks}")
    print(f"Masks containing oil: {len(mask_files) - empty_masks}")
    print(f"Minimum oil coverage: {coverages.min():.6f}%")
    print(f"Maximum oil coverage: {coverages.max():.6f}%")
    print(f"Mean oil coverage: {coverages.mean():.6f}%")
    print(f"Median oil coverage: {np.median(coverages):.6f}%")

    print("\n=== COVERAGE GROUPS ===")

    groups = {
        "0%": coverages == 0,
        "0% - 1%": (coverages > 0) & (coverages <= 1),
        "1% - 5%": (coverages > 1) & (coverages <= 5),
        "5% - 20%": (coverages > 5) & (coverages <= 20),
        "> 20%": coverages > 20,
    }

    for name, condition in groups.items():
        print(f"{name}: {np.count_nonzero(condition)} masks")


def main() -> None:
    if len(sys.argv) < 2:
        print(
            "Usage: python src/preprocessing/analyze_mask_distribution.py "
            "<mask_directory>"
        )
        sys.exit(1)

    analyze_masks(Path(sys.argv[1]))


if __name__ == "__main__":
    main()