from pathlib import Path
import shutil
import tempfile

import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile

from src.config import MODELS_DIR
from src.inference.predictor import OilSpillPredictor


app = FastAPI(
    title="Oil Spill Detection AI",
    version="1.0.0",
    description="API for Sentinel-1 SAR oil spill detection",
)


@app.get("/")
def root():

    return {
        "message": "Oil Spill AI API is running",
        "status": "healthy",
    }


@app.get("/health")
def health_check():

    model_path = (
        MODELS_DIR
        / "best_model.pt"
    )

    return {
        "status": "healthy",
        "model_loaded": model_path.exists(),
    }


def make_json_serializable(value):

    if isinstance(value, np.ndarray):
        return value.tolist()

    if isinstance(value, np.generic):
        return value.item()

    if isinstance(value, tuple):
        return list(value)

    if isinstance(value, list):
        return [
            make_json_serializable(item)
            for item in value
        ]

    if isinstance(value, dict):
        return {
            key: make_json_serializable(item)
            for key, item in value.items()
        }

    return value


@app.post("/predict")
async def predict(
    file: UploadFile = File(...)
):
    """
    Upload a SAR TIFF image and run
    oil spill prediction.
    """

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file was provided.",
        )

    allowed_extensions = {
        ".tif",
        ".tiff",
    }

    file_extension = (
        Path(file.filename)
        .suffix
        .lower()
    )

    if file_extension not in allowed_extensions:

        raise HTTPException(
            status_code=400,
            detail=(
                "Only .tif and .tiff "
                "SAR images are supported."
            ),
        )

    model_path = (
        MODELS_DIR
        / "best_model.pt"
    )

    if not model_path.exists():

        raise HTTPException(
            status_code=503,
            detail=(
                "Model is not available yet. "
                "Train the model before prediction."
            ),
        )

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=file_extension,
        ) as temp_file:

            shutil.copyfileobj(
                file.file,
                temp_file,
            )

            temp_path = Path(
                temp_file.name
            )

        predictor = OilSpillPredictor(
            model_path=model_path,
        )

        result = predictor.predict(
            temp_path
        )

        return make_json_serializable(
            result
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error),
        )

    finally:

        if (
            temp_path is not None
            and temp_path.exists()
        ):

            temp_path.unlink()

        await file.close()