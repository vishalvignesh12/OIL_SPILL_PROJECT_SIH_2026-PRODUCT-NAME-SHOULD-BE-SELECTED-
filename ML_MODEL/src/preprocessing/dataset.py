"""
torch Dataset wrapping the Sample index, doing tiling + SAR-safe augmentation.

Per PRD §12: only flips/rotations/crops/scale + intensity normalization.
No color jitter, no arbitrary photometric distortion — SAR backscatter has
physical meaning that arbitrary transforms would destroy.
"""
from __future__ import annotations

import random
from typing import List

import numpy as np
import torch
from torch.utils.data import Dataset

from src.preprocessing.loader import Sample, read_mask, read_sar_image
from src.preprocessing.normalize import normalize_sar
from src.preprocessing.tiling import make_tiles


_IMAGE_CACHE: dict[str, np.ndarray] = {}
_MASK_CACHE: dict[str, np.ndarray] = {}
_CACHE_CAP = 16


def _cached_read(img_path: str, mask_path: str) -> tuple[np.ndarray, np.ndarray]:
    if img_path not in _IMAGE_CACHE:
        if len(_IMAGE_CACHE) >= _CACHE_CAP:
            _IMAGE_CACHE.pop(next(iter(_IMAGE_CACHE)))
        _IMAGE_CACHE[img_path] = normalize_sar(read_sar_image(img_path))
    if mask_path not in _MASK_CACHE:
        if len(_MASK_CACHE) >= _CACHE_CAP:
            _MASK_CACHE.pop(next(iter(_MASK_CACHE)))
        _MASK_CACHE[mask_path] = read_mask(mask_path)
    return _IMAGE_CACHE[img_path], _MASK_CACHE[mask_path]


class OilSpillTileDataset(Dataset):
    def __init__(
        self,
        samples: List[Sample],
        tile_size: int = 512,
        overlap: int = 64,
        train: bool = True,
        tiles_per_scene_cap: int | None = 8,
    ):
        self.train = train
        self.tile_size = tile_size
        self.index: list[tuple[Sample, tuple[int, int]]] = []

        # Pre-compute tile offsets per sample (images are all 2048x2048, so
        # offsets are identical across samples — computed once for speed).
        dummy = np.zeros((2, 2048, 2048), dtype=np.float32)
        _, offsets = make_tiles(dummy, tile_size, overlap)
        if tiles_per_scene_cap and len(offsets) > tiles_per_scene_cap:
            offsets = random.sample(offsets, tiles_per_scene_cap)
        for s in samples:
            for off in offsets:
                self.index.append((s, off))

    def __len__(self):
        return len(self.index)

    def _augment(self, img: np.ndarray, mask: np.ndarray):
        if random.random() < 0.5:
            img, mask = img[:, :, ::-1].copy(), mask[:, ::-1].copy()
        if random.random() < 0.5:
            img, mask = img[:, ::-1, :].copy(), mask[::-1, :].copy()
        k = random.choice([0, 1, 2, 3])
        if k:
            img = np.rot90(img, k, axes=(1, 2)).copy()
            mask = np.rot90(mask, k, axes=(0, 1)).copy()
        return img, mask

    def __getitem__(self, idx):
        sample, (r, c) = self.index[idx]
        image, mask = _cached_read(sample.image_path, sample.mask_path)

        ts = self.tile_size
        img_tile = image[:, r:r + ts, c:c + ts]
        mask_tile = mask[r:r + ts, c:c + ts]

        if img_tile.shape[1:] != (ts, ts):
            # edge tile smaller than ts due to scene not being a clean multiple
            pad_h, pad_w = ts - img_tile.shape[1], ts - img_tile.shape[2]
            # Use constant padding to safely handle empty axes (e.g., when mock images are smaller than tile size)
            img_tile = np.pad(img_tile, ((0, 0), (0, pad_h), (0, pad_w)), mode="constant", constant_values=0)
            mask_tile = np.pad(mask_tile, ((0, pad_h), (0, pad_w)), mode="constant", constant_values=0)

        if self.train:
            img_tile, mask_tile = self._augment(img_tile, mask_tile)

        return (
            torch.from_numpy(img_tile.copy()).float(),
            torch.from_numpy(mask_tile.copy()).long(),
        )
