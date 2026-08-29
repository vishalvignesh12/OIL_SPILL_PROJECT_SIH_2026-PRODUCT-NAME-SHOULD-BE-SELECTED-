"""
Evaluation metrics for binary oil spill segmentation.
"""

import torch


def _prepare_predictions(
    logits: torch.Tensor,
    targets: torch.Tensor,
    threshold: float = 0.5,
):
    """Convert logits into binary predictions."""

    probabilities = torch.sigmoid(logits)

    predictions = (
        probabilities >= threshold
    ).float()

    targets = (targets > 0.5).float()

    return predictions, targets


def dice_score(
    logits: torch.Tensor,
    targets: torch.Tensor,
    threshold: float = 0.5,
    smooth: float = 1.0,
) -> float:

    predictions, targets = _prepare_predictions(
        logits,
        targets,
        threshold,
    )

    predictions = predictions.view(-1)
    targets = targets.view(-1)

    intersection = (
        predictions * targets
    ).sum()

    score = (
        2.0 * intersection + smooth
    ) / (
        predictions.sum()
        + targets.sum()
        + smooth
    )

    return score.item()


def iou_score(
    logits: torch.Tensor,
    targets: torch.Tensor,
    threshold: float = 0.5,
    smooth: float = 1.0,
) -> float:

    predictions, targets = _prepare_predictions(
        logits,
        targets,
        threshold,
    )

    predictions = predictions.view(-1)
    targets = targets.view(-1)

    intersection = (
        predictions * targets
    ).sum()

    union = (
        predictions.sum()
        + targets.sum()
        - intersection
    )

    score = (
        intersection + smooth
    ) / (
        union + smooth
    )

    return score.item()


def precision_score(
    logits: torch.Tensor,
    targets: torch.Tensor,
    threshold: float = 0.5,
    smooth: float = 1.0,
) -> float:

    predictions, targets = _prepare_predictions(
        logits,
        targets,
        threshold,
    )

    predictions = predictions.view(-1)
    targets = targets.view(-1)

    true_positive = (
        predictions * targets
    ).sum()

    predicted_positive = predictions.sum()

    score = (
        true_positive + smooth
    ) / (
        predicted_positive + smooth
    )

    return score.item()


def recall_score(
    logits: torch.Tensor,
    targets: torch.Tensor,
    threshold: float = 0.5,
    smooth: float = 1.0,
) -> float:

    predictions, targets = _prepare_predictions(
        logits,
        targets,
        threshold,
    )

    predictions = predictions.view(-1)
    targets = targets.view(-1)

    true_positive = (
        predictions * targets
    ).sum()

    actual_positive = targets.sum()

    score = (
        true_positive + smooth
    ) / (
        actual_positive + smooth
    )

    return score.item()