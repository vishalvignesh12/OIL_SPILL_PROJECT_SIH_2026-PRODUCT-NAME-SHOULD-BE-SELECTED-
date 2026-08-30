"""Structured result returned by the inference service (PRD §6, §45)."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class SpillRegion:
    centroid_px: tuple[float, float]
    area_px2: float
    polygon_geojson_pixel: dict
    centroid_geo: Optional[tuple[float, float]] = None
    area_m2_approx: Optional[float] = None
    polygon_geojson_geo: Optional[dict] = None


@dataclass
class PredictionResult:
    scene_id: str
    model_version: str
    presence: bool
    max_confidence: float
    regions: list[SpillRegion] = field(default_factory=list)
    present_regions: list[SpillRegion] = field(default_factory=list)
    likely_regions: list[SpillRegion] = field(default_factory=list)
    acquisition_time: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)
