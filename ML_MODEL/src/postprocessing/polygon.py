"""
Converts labeled regions into polygons + centroid + area, in pixel space by
default and in geographic space when a rasterio transform is available
(PRD §45: ML output must supply centroid + polygon + timestamp to the
AIS-correlation stage).
"""
from __future__ import annotations

from typing import Optional

import numpy as np
from shapely.geometry import Polygon, mapping
from skimage import measure

try:
    import rasterio
    from rasterio.transform import Affine
    _HAS_RASTERIO = True
except ImportError:
    _HAS_RASTERIO = False


def mask_to_polygons(binary_mask: np.ndarray, transform: Optional["Affine"] = None) -> list[dict]:
    """
    Returns a list of dicts, one per connected oil region:
      {polygon_geojson, centroid_xy, area_px, area_m2 (if transform given)}
    """
    contours = measure.find_contours(binary_mask.astype(float), level=0.5)
    results = []

    for contour in contours:
        # contour is (row, col) pairs; convert to (x, y) = (col, row)
        coords = [(c, r) for r, c in contour]
        if len(coords) < 3:
            continue
        poly = Polygon(coords)
        if not poly.is_valid or poly.area == 0:
            poly = poly.buffer(0)
            if poly.is_empty:
                continue

        centroid_px = (poly.centroid.x, poly.centroid.y)
        area_px = poly.area
        entry = {
            "polygon_geojson_pixel": mapping(poly),
            "centroid_px": centroid_px,
            "area_px2": area_px,
        }

        if transform is not None and _HAS_RASTERIO:
            geo_coords = [transform * (x, y) for x, y in poly.exterior.coords]
            geo_poly = Polygon(geo_coords)
            entry["polygon_geojson_geo"] = mapping(geo_poly)
            entry["centroid_geo"] = (geo_poly.centroid.x, geo_poly.centroid.y)
            # rough planar area estimate; for precise m^2 reproject to an
            # equal-area CRS first if the scene is large or high-latitude
            entry["area_m2_approx"] = geo_poly.area

        results.append(entry)

    return results
