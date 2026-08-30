"""
Loss functions for oil spill segmentation.
"""

import torch
import torch.nn as nn


class DiceLoss(nn.Module):
    """Dice loss for binary image segmentation."""

    def __init__(self, smooth: float = 1.0):
        super().__init__()
        self.smooth = smooth

    def forward(
        self,
        logits: torch.Tensor,
        targets: torch.Tensor,
    ) -> torch.Tensor:

        probabilities = torch.sigmoid(logits)

        probabilities = probabilities.contiguous().view(-1)
        targets = targets.contiguous().view(-1)

        intersection = (probabilities * targets).sum()

        dice_score = (
            (2.0 * intersection + self.smooth)
            / (
                probabilities.sum()
                + targets.sum()
                + self.smooth
            )
        )

        return 1.0 - dice_score


class BCEDiceLoss(nn.Module):
    """
    Combined Binary Cross Entropy and Dice loss.
    """

    def __init__(
        self,
        bce_weight: float = 0.5,
        dice_weight: float = 0.5,
    ):
        super().__init__()

        self.bce_weight = bce_weight
        self.dice_weight = dice_weight

        self.bce = nn.BCEWithLogitsLoss()
        self.dice = DiceLoss()

    def forward(
        self,
        logits: torch.Tensor,
        targets: torch.Tensor,
    ) -> torch.Tensor:

        bce_loss = self.bce(logits, targets)
        dice_loss = self.dice(logits, targets)

        return (
            self.bce_weight * bce_loss
            + self.dice_weight * dice_loss
        )