import torch

from src.training.losses import (
    DiceLoss,
    BCEDiceLoss,
)

from src.training.metrics import (
    dice_score,
    iou_score,
    precision_score,
    recall_score,
)


def test_dice_loss_perfect_prediction():

    logits = torch.tensor(
        [[[[10.0, -10.0],
           [-10.0, 10.0]]]]
    )

    targets = torch.tensor(
        [[[[1.0, 0.0],
           [0.0, 1.0]]]]
    )

    loss = DiceLoss()(logits, targets)

    assert loss.item() < 0.01


def test_bce_dice_loss_returns_value():

    logits = torch.randn(
        1, 1, 16, 16
    )

    targets = torch.randint(
        0,
        2,
        (1, 1, 16, 16),
    ).float()

    loss = BCEDiceLoss()(
        logits,
        targets,
    )

    assert loss.item() > 0


def test_perfect_segmentation_metrics():

    logits = torch.tensor(
        [[[[10.0, -10.0],
           [-10.0, 10.0]]]]
    )

    targets = torch.tensor(
        [[[[1.0, 0.0],
           [0.0, 1.0]]]]
    )

    assert dice_score(logits, targets) > 0.99
    assert iou_score(logits, targets) > 0.99
    assert precision_score(logits, targets) > 0.99
    assert recall_score(logits, targets) > 0.99