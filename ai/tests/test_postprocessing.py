import numpy as np
import torch

from src.postprocessing.mask import (
    logits_to_probability,
    probability_to_mask,
    logits_to_mask,
)

from src.postprocessing.regions import (
    remove_small_regions,
    extract_regions,
)


def test_logits_to_probability():

    logits = torch.tensor([
        [[[0.0, 10.0, -10.0]]]
    ])

    probabilities = logits_to_probability(
        logits
    )

    assert probabilities.shape == logits.shape

    assert probabilities[0, 0, 0, 0].item() == 0.5
    assert probabilities[0, 0, 0, 1].item() > 0.99
    assert probabilities[0, 0, 0, 2].item() < 0.01


def test_probability_to_mask():

    probabilities = torch.tensor([
        [[[0.2, 0.5, 0.8]]]
    ])

    mask = probability_to_mask(
        probabilities,
        threshold=0.5,
    )

    expected = torch.tensor([
        [[[0, 1, 1]]]
    ], dtype=torch.uint8)

    assert torch.equal(
        mask,
        expected,
    )


def test_logits_to_mask():

    logits = torch.tensor([
        [[[-10.0, 10.0]]]
    ])

    mask = logits_to_mask(logits)

    expected = torch.tensor([
        [[[0, 1]]]
    ], dtype=torch.uint8)

    assert torch.equal(
        mask,
        expected,
    )


def test_remove_small_regions():

    mask = np.zeros(
        (20, 20),
        dtype=np.uint8,
    )

    # Large region: 25 pixels.
    mask[2:7, 2:7] = 1

    # Small noise region: 4 pixels.
    mask[15:17, 15:17] = 1

    cleaned = remove_small_regions(
        mask,
        min_pixels=10,
    )

    assert cleaned.sum() == 25


def test_extract_regions():

    mask = np.zeros(
        (20, 20),
        dtype=np.uint8,
    )

    # Region 1: 4 x 4 = 16 pixels.
    mask[2:6, 2:6] = 1

    # Region 2: 3 x 3 = 9 pixels.
    mask[10:13, 10:13] = 1

    regions = extract_regions(mask)

    assert len(regions) == 2

    assert regions[0]["pixel_count"] == 16
    assert regions[1]["pixel_count"] == 9

    assert regions[0]["centroid_x"] == 3.5
    assert regions[0]["centroid_y"] == 3.5