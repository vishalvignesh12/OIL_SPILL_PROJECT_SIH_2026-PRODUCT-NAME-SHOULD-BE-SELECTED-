"""
Phase 1 (PRD §8): document dataset stats before writing any model code.
Run this first, right after downloading the Zenodo parts, to confirm image
dimensions, channel count, class balance, and to sanity-check CLIP_DB in
normalize.py against the actual data.

Usage:
    python notebooks/dataset_analysis.py --data-root data/raw --n-samples 30
"""
import argparse
import os
import random
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import matplotlib.pyplot as plt
import numpy as np

from src.preprocessing.loader import build_dataset_index, read_mask, read_sar_image
from src.preprocessing.normalize import compute_channel_stats


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data-root", default="data/raw")
    p.add_argument("--n-samples", type=int, default=30, help="how many images to sample for stats/preview")
    p.add_argument("--out-dir", default="reports/dataset_analysis")
    args = p.parse_args()

    import os
    os.makedirs(args.out_dir, exist_ok=True)

    samples = build_dataset_index(args.data_root)
    if not samples:
        raise SystemExit("No samples found — check data-root and that Zenodo parts were unzipped correctly.")

    by_cat = {}
    for s in samples:
        by_cat.setdefault(s.category, []).append(s)
    print("\n=== Class distribution ===")
    for cat, items in by_cat.items():
        print(f"  {cat}: {len(items)}")

    subset = random.sample(samples, min(args.n_samples, len(samples)))
    imgs, shapes, mask_fg_fractions = [], [], []
    for s in subset:
        img = read_sar_image(s.image_path)
        mask = read_mask(s.mask_path)
        imgs.append(img)
        shapes.append(img.shape)
        mask_fg_fractions.append(mask.mean())

    print("\n=== Image shapes (sampled) ===")
    print(set(shapes))

    print("\n=== Channel stats (sampled, dB) ===")
    stats = compute_channel_stats(imgs)
    print(stats)
    print("Compare these percentiles against CLIP_DB in src/preprocessing/normalize.py "
          "and widen/tighten the clip range if p1/p99 fall outside it.")

    print("\n=== Foreground (oil) pixel fraction, sampled ===")
    print(f"mean={np.mean(mask_fg_fractions):.4f}, "
          f"max={np.max(mask_fg_fractions):.4f}, "
          f"frac_of_tiles_with_any_oil={np.mean([f > 0 for f in mask_fg_fractions]):.2f}")
    print("A low mean fraction confirms class imbalance -> BCEDiceLoss + pos_weight "
          "in src/training/losses.py is warranted.")

    # Visual sample grid: one oil, one no_oil, one lookalike if available
    fig, axes = plt.subplots(1, min(3, len(by_cat)), figsize=(5 * len(by_cat), 5))
    if len(by_cat) == 1:
        axes = [axes]
    for ax, (cat, items) in zip(axes, by_cat.items()):
        s = random.choice(items)
        img = read_sar_image(s.image_path)
        mask = read_mask(s.mask_path)
        ax.imshow(img[0], cmap="gray")
        ax.imshow(mask, cmap="Reds", alpha=0.4)
        ax.set_title(f"{cat} (VV + mask overlay)")
        ax.axis("off")
    plt.tight_layout()
    out_path = f"{args.out_dir}/sample_grid.png"
    plt.savefig(out_path, dpi=150)
    print(f"\nSample grid saved to {out_path}")


if __name__ == "__main__":
    main()
