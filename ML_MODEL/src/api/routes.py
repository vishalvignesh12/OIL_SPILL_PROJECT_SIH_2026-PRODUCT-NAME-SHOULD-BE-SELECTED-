"""
Minimal inference API (PRD §6, Phase 7). Receives a scene reference (not the
raw image bytes), retrieves the image from local/mounted storage, runs the
predictor, and returns the structured result for the backend to persist.

Run: uvicorn src.api.routes:app --host 0.0.0.0 --port 8080
"""
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.inference.predictor import OilSpillPredictor

app = FastAPI(title="Oil Spill Segmentation Inference Service")

CHECKPOINT_PATH = os.environ.get("OILSPILL_CHECKPOINT", "models/oilspill-v1/best.pt")
_predictor: OilSpillPredictor | None = None


def get_predictor() -> OilSpillPredictor:
    global _predictor
    if _predictor is None:
        if not os.path.exists(CHECKPOINT_PATH):
            raise HTTPException(status_code=503, detail=f"checkpoint not found at {CHECKPOINT_PATH}")
        _predictor = OilSpillPredictor(CHECKPOINT_PATH)
    return _predictor


class PredictRequest(BaseModel):
    scene_id: str
    image_uri: str  # e.g. "storage://.../scene.tif" or a local/mounted path
    acquisition_time: str | None = None
    threshold: float = 0.5


class HealthResponse(BaseModel):
    status: str
    model_version: str | None = None


@app.get("/health", response_model=HealthResponse)
def health():
    try:
        predictor = get_predictor()
        return HealthResponse(status="ok", model_version="oilspill-unet-v1")
    except HTTPException:
        return HealthResponse(status="model_not_loaded")


@app.post("/predict")
def predict(req: PredictRequest):
    predictor = get_predictor()

    # In production, image_uri resolves via the configured storage layer
    # (e.g. S3/GCS/local mount); here we assume it's a locally reachable path.
    image_path = req.image_uri.replace("storage://", "/mnt/storage/")
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail=f"image not found: {image_path}")

    result = predictor.predict(
        image_path,
        scene_id=req.scene_id,
        acquisition_time=req.acquisition_time,
        threshold=req.threshold,
    )
    return result.to_dict()
