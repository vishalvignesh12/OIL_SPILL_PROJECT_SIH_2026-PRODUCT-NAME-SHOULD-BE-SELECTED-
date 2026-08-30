"""
Probability map -> cleaned binary mask -> labeled connected components
(PRD §3.2 recommended objectives: multi-region, remove small noisy blobs).
"""
import numpy as np
from scipy import ndimage
from skimage import morphology, measure


def threshold_and_clean(
    prob_map: np.ndarray,
    threshold: float = 0.5,
    min_area_px: int = 50,
) -> np.ndarray:
    """prob_map: (H, W) float32 in [0,1]. Returns cleaned binary mask (H, W) uint8."""
    binary = (prob_map > threshold)
    binary = morphology.remove_small_objects(binary, min_size=min_area_px)
    binary = morphology.remove_small_holes(binary, area_threshold=min_area_px)
    return binary.astype(np.uint8)


def label_regions(binary_mask: np.ndarray):
    """Returns (labeled_array, list of skimage.measure.RegionProperties)."""
    labeled, num = ndimage.label(binary_mask)
    props = measure.regionprops(labeled)
    return labeled, props
