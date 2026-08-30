"""
Oil spill segmentation inference pipeline.
"""

from pathlib import Path

import numpy as np
import rasterio
import torch

from src.models.unet import UNet
from src.postprocessing.mask import logits_to_probability
from src.postprocessing.regions import (
    remove_small_regions,
    extract_regions,
)


class OilSpillPredictor:
    """
    Load a trained U-Net model and run oil spill prediction.
    """

    def __init__(
        self,
        model_path: str | Path,
        device: str | None = None,
        image_size: int = 256,
        threshold: float = 0.5,
        min_pixels: int = 100,
    ):

        if device is None:

            if torch.cuda.is_available():
                device = "cuda"
            else:
                device = "cpu"

        self.device = torch.device(device)

        self.image_size = image_size
        self.threshold = threshold
        self.min_pixels = min_pixels

        self.model = UNet(
            in_channels=1,
            out_channels=1,
        )

        checkpoint = torch.load(
            model_path,
            map_location=self.device,
        )

        self.model.load_state_dict(
            checkpoint["model_state_dict"]
        )

        self.model.to(self.device)

        self.model.eval()

    def load_image(
        self,
        image_path: str | Path,
    ) -> np.ndarray:
        """
        Load a single-band SAR TIFF image.
        """

        with rasterio.open(image_path) as src:

            image = src.read(1).astype(
                np.float32
            )

        return image

    def preprocess(
        self,
        image: np.ndarray,
    ) -> tuple[torch.Tensor, tuple[int, int]]:
        """
        Normalize and resize an image for the model.
        """

        original_shape = image.shape

        mean = image.mean()
        std = image.std()

        if std > 0:
            image = (
                image - mean
            ) / std

        image_tensor = torch.from_numpy(
            image
        ).float()

        image_tensor = image_tensor.unsqueeze(
            0
        ).unsqueeze(0)

        image_tensor = torch.nn.functional.interpolate(
            image_tensor,
            size=(
                self.image_size,
                self.image_size,
            ),
            mode="bilinear",
            align_corners=False,
        )

        return image_tensor, original_shape

    def predict(
        self,
        image_path: str | Path,
    ) -> dict:
        """
        Run the complete prediction pipeline.
        """

        image = self.load_image(
            image_path
        )

        image_tensor, original_shape = (
            self.preprocess(image)
        )

        image_tensor = image_tensor.to(
            self.device
        )

        with torch.no_grad():

            logits = self.model(
                image_tensor
            )

            probabilities = (
                logits_to_probability(
                    logits
                )
            )

        probability_map = (
            probabilities
            .squeeze()
            .cpu()
            .numpy()
        )

        binary_mask = (
            probability_map >= self.threshold
        ).astype(np.uint8)

        binary_mask = remove_small_regions(
            binary_mask,
            min_pixels=self.min_pixels,
        )

        regions = extract_regions(
            binary_mask
        )

        return {
            "mask": binary_mask,
            "probability_map": probability_map,
            "regions": regions,
            "original_shape": original_shape,
            "oil_spill_detected": (
                len(regions) > 0
            ),
        }