"""
Utilities for extracting individual oil spill regions
from binary segmentation masks.
"""

from typing import Dict, List

import numpy as np
from scipy import ndimage


def remove_small_regions(
    mask: np.ndarray,
    min_pixels: int = 100,
) -> np.ndarray:
    """
    Remove connected regions smaller than min_pixels.
    """

    mask = (mask > 0).astype(np.uint8)

    labeled_mask, num_regions = ndimage.label(
        mask
    )

    cleaned_mask = np.zeros_like(
        mask,
        dtype=np.uint8,
    )

    for region_id in range(
        1,
        num_regions + 1,
    ):

        region = (
            labeled_mask == region_id
        )

        pixel_count = region.sum()

        if pixel_count >= min_pixels:

            cleaned_mask[region] = 1

    return cleaned_mask


def extract_regions(
    mask: np.ndarray,
) -> List[Dict]:
    """
    Extract connected oil spill regions.

    Returns region information including:
    - region_id
    - pixel_count
    - centroid_x
    - centroid_y
    - bounding_box
    """

    mask = (mask > 0).astype(np.uint8)

    labeled_mask, num_regions = ndimage.label(
        mask
    )

    regions = []

    for region_id in range(
        1,
        num_regions + 1,
    ):

        region = (
            labeled_mask == region_id
        )

        pixel_count = int(
            region.sum()
        )

        if pixel_count == 0:
            continue

        coordinates = np.argwhere(
            region
        )

        centroid_y = float(
            coordinates[:, 0].mean()
        )

        centroid_x = float(
            coordinates[:, 1].mean()
        )

        min_y = int(
            coordinates[:, 0].min()
        )

        max_y = int(
            coordinates[:, 0].max()
        )

        min_x = int(
            coordinates[:, 1].min()
        )

        max_x = int(
            coordinates[:, 1].max()
        )

        regions.append(
            {
                "region_id": region_id,
                "pixel_count": pixel_count,
                "centroid_x": centroid_x,
                "centroid_y": centroid_y,
                "bounding_box": {
                    "min_x": min_x,
                    "min_y": min_y,
                    "max_x": max_x,
                    "max_y": max_y,
                },
            }
        )

    return regions