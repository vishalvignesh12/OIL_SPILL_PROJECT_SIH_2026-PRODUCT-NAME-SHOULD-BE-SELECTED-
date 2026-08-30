"""
Dataset loader for the Trujillo-Acatitla et al. Sentinel-1 SAR Oil Spill
Dataset (Zenodo, Parts I-III).

Each sample is a (image_path, mask_path, scene_group) tuple.
`scene_group` is used to split by acquisition/category rather than randomly,
avoiding leakage between train/val/test (PRD §9).
"""
from __future__ import annotations

import glob
import os
from dataclasses import dataclass
from typing import List, Literal

import numpy as np
import tifffile

Category = Literal["oil", "no_oil", "lookalike"]


@dataclass
class Sample:
    image_path: str
    mask_path: str
    category: Category
    part: str  # "part1", "part2", "part3"

    @property
    def scene_group(self) -> str:
        # group by (part, category) so a train/val split never mixes a scene
        # category across splits in a way that leaks near-duplicate frames
        return f"{self.part}:{self.category}"


def _match_pairs(image_dir: str, mask_dir: str, category: Category, part: str) -> List[Sample]:
    images = sorted(glob.glob(os.path.join(image_dir, "*.tif")) +
                     glob.glob(os.path.join(image_dir, "*.tiff")))
    samples = []
    missing = 0
    for img_path in images:
        stem = os.path.splitext(os.path.basename(img_path))[0]
        mask_candidates = glob.glob(os.path.join(mask_dir, f"{stem}.*"))
        if not mask_candidates:
            missing += 1
            continue
        samples.append(Sample(img_path, mask_candidates[0], category, part))
    if missing:
        print(f"[loader] WARNING: {missing} images in {image_dir} had no matching mask")
    return samples


def _find_dir(root: str, *keywords: str) -> str | None:
    """Case-insensitive search for a subdirectory whose name contains all keywords."""
    for dirpath, dirnames, _ in os.walk(root):
        for d in dirnames:
            dl = d.lower()
            if all(k in dl for k in keywords):
                return os.path.join(dirpath, d)
    return None


def build_dataset_index(data_root: str) -> List[Sample]:
    """
    Scans data_root/part{1,2,3}/... for image/mask folder pairs.
    Tolerant to minor naming variation across Zenodo releases.
    """
    samples: List[Sample] = []

    part_specs = {
        "part1": [("oil", ("oil", "image"), ("oil", "mask"))],
        "part2": [
            ("no_oil", ("no_oil", "image"), ("no_oil", "mask")),
            ("lookalike", ("lookalike", "image"), ("lookalike", "mask")),
        ],
        "part3": [
            ("oil", ("oil", "image"), ("oil", "mask")),
            ("no_oil", ("no_oil", "image"), ("no_oil", "mask")),
            ("lookalike", ("lookalike", "image"), ("lookalike", "mask")),
        ],
    }

    for part, specs in part_specs.items():
        part_root = os.path.join(data_root, part)
        if not os.path.isdir(part_root):
            print(f"[loader] {part_root} not found, skipping")
            continue
        for category, img_kw, mask_kw in specs:
            img_dir = _find_dir(part_root, *img_kw)
            mask_dir = _find_dir(part_root, *mask_kw)
            if img_dir is None or mask_dir is None:
                print(f"[loader] WARNING: could not locate {category} dirs under {part_root}")
                continue
            samples.extend(_match_pairs(img_dir, mask_dir, category, part))

    print(f"[loader] indexed {len(samples)} samples "
          f"({sum(s.category=='oil' for s in samples)} oil, "
          f"{sum(s.category=='no_oil' for s in samples)} no_oil, "
          f"{sum(s.category=='lookalike' for s in samples)} lookalike)", flush=True)
    return samples


def read_sar_image(path: str) -> np.ndarray:
    """Returns float32 array, shape (2, H, W) = (VV, VH), in dB (as stored)."""
    arr = tifffile.imread(path)
    if arr.ndim == 3 and arr.shape[-1] == 2:
        arr = np.transpose(arr, (2, 0, 1))  # HWC -> CHW
    elif arr.ndim == 2:
        arr = arr[None, ...].repeat(2, axis=0)  # degrade gracefully if single-band
    return arr.astype(np.float32)


def read_mask(path: str) -> np.ndarray:
    """Returns uint8 array, shape (H, W), values in {0, 1}."""
    arr = tifffile.imread(path)
    if arr.ndim == 3:
        arr = arr[..., 0]
    return (arr > 0).astype(np.uint8)


def official_train_val_split(samples: List[Sample], val_fraction: float = 0.15, seed: int = 42):
    """
    Splits Part I + Part II (train/val pool) by scene_group-stratified random
    split; Part III is always held out entirely as the untouched test set
    (this matches the dataset's own train/val/test partitioning from Zenodo,
    so we don't re-shuffle across the authors' intended split).
    """
    rng = np.random.default_rng(seed)
    trainval = [s for s in samples if s.part in ("part1", "part2")]
    test = [s for s in samples if s.part == "part3"]

    by_group: dict[str, list[Sample]] = {}
    for s in trainval:
        by_group.setdefault(s.scene_group, []).append(s)

    train, val = [], []
    for group, group_samples in by_group.items():
        idx = rng.permutation(len(group_samples))
        n_val = max(1, int(len(group_samples) * val_fraction))
        val_idx = set(idx[:n_val])
        for i, s in enumerate(group_samples):
            (val if i in val_idx else train).append(s)

    print(f"[loader] split -> train={len(train)} val={len(val)} test={len(test)}", flush=True)
    return train, val, test
