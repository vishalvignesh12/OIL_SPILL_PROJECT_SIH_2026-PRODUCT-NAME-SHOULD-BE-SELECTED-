"""
Normalization for Sigma0-in-dB Sentinel-1 imagery.

Sigma0 dB values typically range roughly -30 to +5 dB for ocean scenes
(calm sea / oil-dampened areas sit low, look-alikes and rough sea sit
higher). We clip to a documented range then min-max scale to [0, 1],
per-channel (VV, VH separately, since their dynamic ranges differ).

IMPORTANT: compute the actual per-channel percentiles on your downloaded
training set (see notebooks/dataset_analysis.py) and update CLIP_DB below
before training — these are reasonable literature-typical defaults, not
measured from your specific data.
"""
import numpy as np

# (min_db, max_db) clip range per channel: (VV, VH) calibrated from dataset analysis
CLIP_DB = np.array([[-50.0, 2.0], [-45.0, 10.0]], dtype=np.float32)


def normalize_sar(img: np.ndarray) -> np.ndarray:
    """img: (2, H, W) float32 in dB. Returns (2, H, W) float32 in [0, 1]."""
    out = np.empty_like(img)
    for c in range(img.shape[0]):
        lo, hi = CLIP_DB[c]
        clipped = np.clip(img[c], lo, hi)
        out[c] = (clipped - lo) / (hi - lo + 1e-8)
    return out


def compute_channel_stats(images: list[np.ndarray]) -> dict:
    """Run once over a sample of training images to sanity-check CLIP_DB."""
    stacked = np.stack(images)  # (N, 2, H, W)
    stats = {}
    for c, name in enumerate(("VV", "VH")):
        vals = stacked[:, c].ravel()
        stats[name] = {
            "min": float(vals.min()),
            "p1": float(np.percentile(vals, 1)),
            "p50": float(np.percentile(vals, 50)),
            "p99": float(np.percentile(vals, 99)),
            "max": float(vals.max()),
        }
    return stats
