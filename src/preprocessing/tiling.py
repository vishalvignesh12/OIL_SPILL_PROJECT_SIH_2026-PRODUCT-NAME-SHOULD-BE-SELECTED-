"""
Tiling for 2048x2048 scenes -> model-sized patches, and stitching predictions
back together with overlap-averaging (PRD §11).
"""
from __future__ import annotations

from typing import List, Tuple

import numpy as np


def make_tiles(
    arr: np.ndarray, tile_size: int = 512, overlap: int = 64
) -> Tuple[List[np.ndarray], List[Tuple[int, int]]]:
    """
    arr: (C, H, W) or (H, W).
    Returns list of tiles and their (row_start, col_start) offsets.
    Pads the scene so tiles evenly cover it.
    """
    is_2d = arr.ndim == 2
    if is_2d:
        arr = arr[None, ...]
    c, h, w = arr.shape
    stride = tile_size - overlap

    pad_h = (-(h - tile_size) % stride) if h > tile_size else max(0, tile_size - h)
    pad_w = (-(w - tile_size) % stride) if w > tile_size else max(0, tile_size - w)
    padded = np.pad(arr, ((0, 0), (0, pad_h), (0, pad_w)), mode="reflect")

    tiles, offsets = [], []
    for r in range(0, padded.shape[1] - tile_size + 1, stride):
        for cix in range(0, padded.shape[2] - tile_size + 1, stride):
            tile = padded[:, r:r + tile_size, cix:cix + tile_size]
            tiles.append(tile[0] if is_2d else tile)
            offsets.append((r, cix))
    return tiles, offsets


def stitch_predictions(
    predictions: List[np.ndarray],
    offsets: List[Tuple[int, int]],
    full_shape: Tuple[int, int],
    tile_size: int = 512,
) -> np.ndarray:
    """
    predictions: list of (tile_size, tile_size) probability maps (float32).
    Reconstructs full-scene probability map by averaging overlapping regions.
    """
    max_r = max(o[0] for o in offsets) + tile_size
    max_c = max(o[1] for o in offsets) + tile_size
    accum = np.zeros((max_r, max_c), dtype=np.float32)
    counts = np.zeros((max_r, max_c), dtype=np.float32)

    for pred, (r, c) in zip(predictions, offsets):
        accum[r:r + tile_size, c:c + tile_size] += pred
        counts[r:r + tile_size, c:c + tile_size] += 1.0

    counts[counts == 0] = 1.0
    full = accum / counts
    return full[: full_shape[0], : full_shape[1]]
