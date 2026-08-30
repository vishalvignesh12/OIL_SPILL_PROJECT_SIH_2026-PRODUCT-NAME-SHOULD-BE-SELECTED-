"""
Check availability of dataset directories.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.config import IMAGES_DIR, MASKS_DIR, PROCESSED_DIR


def count_tiff_files(directory: Path) -> int:
    if not directory.exists():
        return 0

    return len(list(directory.glob("*.tif"))) + len(
        list(directory.glob("*.tiff"))
    )


def main():
    print("\n=== OIL SPILL DATASET PATH CHECK ===\n")

    paths = {
        "Images": IMAGES_DIR,
        "Masks": MASKS_DIR,
        "Processed": PROCESSED_DIR,
    }

    for name, path in paths.items():
        exists = path.exists()
        print(f"{name}:")
        print(f"  Path: {path}")
        print(f"  Exists: {exists}")

        if exists and name != "Processed":
            print(f"  TIFF files: {count_tiff_files(path)}")

        print()

    if not MASKS_DIR.exists():
        print("ERROR: Mask directory was not found.")
    elif count_tiff_files(MASKS_DIR) != 1200:
        print("WARNING: Expected 1200 masks.")
    else:
        print("Mask dataset is ready.")

    if count_tiff_files(IMAGES_DIR) == 0:
        print("\nSAR images are not available yet.")
        print("We can continue building the ML pipeline until images arrive.")
    else:
        print("\nSAR images detected. Image-mask pairing can begin.")


if __name__ == "__main__":
    main()