import numpy as np

from src.postprocessing.mask import label_regions, threshold_and_clean
from src.postprocessing.polygon import mask_to_polygons


def _square_prob_map(size=100, sq_slice=slice(20, 60)):
    prob = np.zeros((size, size), dtype=np.float32)
    prob[sq_slice, sq_slice] = 0.9
    return prob


def test_threshold_and_clean_removes_noise():
    prob = _square_prob_map()
    prob[5, 5] = 0.8  # isolated 1px noise, should be removed
    mask = threshold_and_clean(prob, threshold=0.5, min_area_px=10)
    assert mask[5, 5] == 0
    assert mask[40, 40] == 1


def test_label_regions_counts_one_blob():
    prob = _square_prob_map()
    mask = threshold_and_clean(prob, threshold=0.5, min_area_px=10)
    _, props = label_regions(mask)
    assert len(props) == 1


def test_mask_to_polygons_area_roughly_matches():
    prob = _square_prob_map()
    mask = threshold_and_clean(prob, threshold=0.5, min_area_px=10)
    regions = mask_to_polygons(mask)
    assert len(regions) == 1
    # 40x40 square = 1600 px^2, contour-based polygon area should be close
    assert 1200 < regions[0]["area_px2"] < 1700
