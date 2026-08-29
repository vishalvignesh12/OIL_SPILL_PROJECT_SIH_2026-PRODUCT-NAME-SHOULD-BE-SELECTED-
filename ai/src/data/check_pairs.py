"""
Check image-mask pairing for the oil spill dataset.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import IMAGES_DIR, MASKS_DIR
from src.data.dataset import (
    create_image_mask_pairs,
    get_tiff_files,
    get_unmatched_files,
)


def main() -> None:
    print("\n=== IMAGE-MASK PAIR CHECK ===\n")

    image_files = get_tiff_files(IMAGES_DIR)
    mask_files = get_tiff_files(MASKS_DIR)

    print(f"Images found: {len(image_files)}")
    print(f"Masks found:  {len(mask_files)}")

    pairs = create_image_mask_pairs(
        IMAGES_DIR,
        MASKS_DIR,
    )

    unmatched_images, unmatched_masks = get_unmatched_files(
        IMAGES_DIR,
        MASKS_DIR,
    )

    print(f"Valid pairs:  {len(pairs)}")
    print(f"Images without masks: {len(unmatched_images)}")
    print(f"Masks without images: {len(unmatched_masks)}")

    if not image_files:
        print("\nSAR images have not been added yet.")
        print("The pairing system is ready and will automatically")
        print("match files when images are placed in:")
        print(IMAGES_DIR)

    elif pairs:
        print("\nSample pairs:")

        for image_path, mask_path in pairs[:5]:
            print(
                f"{image_path.name}  <->  {mask_path.name}"
            )


if __name__ == "__main__":
    main()