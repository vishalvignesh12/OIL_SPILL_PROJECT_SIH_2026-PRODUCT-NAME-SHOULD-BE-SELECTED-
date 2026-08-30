"""
Combined BCE + Dice loss. Oil pixels are typically a small fraction of each
tile (class imbalance), so plain BCE alone under-weights the foreground —
Dice directly optimizes overlap and compensates for that.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F


class DiceLoss(nn.Module):
    def __init__(self, smooth: float = 1.0):
        super().__init__()
        self.smooth = smooth

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        probs = torch.sigmoid(logits).flatten(1)
        targets = targets.float().flatten(1)
        intersection = (probs * targets).sum(dim=1)
        union = probs.sum(dim=1) + targets.sum(dim=1)
        dice = (2 * intersection + self.smooth) / (union + self.smooth)
        return 1 - dice.mean()


class BCEDiceLoss(nn.Module):
    def __init__(self, bce_weight: float = 0.5, pos_weight: float | None = None):
        super().__init__()
        pw = torch.tensor([pos_weight]) if pos_weight else None
        self.bce = nn.BCEWithLogitsLoss(pos_weight=pw)
        self.dice = DiceLoss()
        self.bce_weight = bce_weight

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        # logits: (B, 1, H, W); targets: (B, H, W) long {0,1}
        targets_f = targets.unsqueeze(1).float()
        bce_loss = self.bce(logits, targets_f)
        dice_loss = self.dice(logits, targets_f)
        return self.bce_weight * bce_loss + (1 - self.bce_weight) * dice_loss
