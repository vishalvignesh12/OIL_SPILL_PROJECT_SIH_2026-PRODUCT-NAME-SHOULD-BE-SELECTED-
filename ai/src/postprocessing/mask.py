"""
Utilities for converting model outputs into binary oil spill masks.
"""

import torch


def logits_to_probability(
    logits: torch.Tensor,
) -> torch.Tensor:
    """
    Convert raw model logits to probabilities.
    """

    return torch.sigmoid(logits)


def probability_to_mask(
    probabilities: torch.Tensor,
    threshold: float = 0.5,
) -> torch.Tensor:
    """
    Convert probability values into a binary mask.
    """

    return (
        probabilities >= threshold
    ).to(torch.uint8)


def logits_to_mask(
    logits: torch.Tensor,
    threshold: float = 0.5,
) -> torch.Tensor:
    """
    Convert model logits directly into a binary mask.
    """

    probabilities = logits_to_probability(
        logits
    )

    return probability_to_mask(
        probabilities,
        threshold,
    )