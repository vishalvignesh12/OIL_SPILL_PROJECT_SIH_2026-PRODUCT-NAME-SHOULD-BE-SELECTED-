"""
Central configuration for the oil spill ML pipeline.
"""

from pathlib import Path


# Root directory for large datasets stored outside the Git repository.
DATA_ROOT = Path(r"D:\oil_spill_data")

# Raw / input Sentinel-1 SAR images.
IMAGES_DIR = DATA_ROOT / "images"

# Ground-truth oil spill segmentation masks.
MASKS_DIR = (
    DATA_ROOT
    / "masks"
    / "01_Train_Val_Oil_Spill_mask"
    / "Mask_oil"
)

# Directory for generated processed data.
PROCESSED_DIR = DATA_ROOT / "processed"

# Model artifacts.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = PROJECT_ROOT / "models"