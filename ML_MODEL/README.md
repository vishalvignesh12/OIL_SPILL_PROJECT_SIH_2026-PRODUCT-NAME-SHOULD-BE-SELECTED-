# Oil Spill Segmentation — SIH PS 26143 (ML Module)

Implements Phases 1–6 of `AI_ML_Oil_Spill_Detection_PRD.md`: dataset loading,
preprocessing, U-Net baseline segmentation, evaluation, and geospatial
post-processing (polygon/centroid/area) for the AIS-correlation stage to
consume.

## Dataset — Sentinel-1 SAR Oil Spill Dataset (Trujillo-Acatitla et al.)

Download manually from Zenodo (no API key needed, but files are large):

| Part | DOI / URL | Contents |
|---|---|---|
| I | https://zenodo.org/records/8346860 | 1,200 oil-spill images + masks (train/val) |
| II | https://zenodo.org/records/8253899 | 685 no-oil + 685 look-alike images + masks (train/val) |
| III | https://zenodo.org/records/13761290 | 150 oil + 150 no-oil + 150 look-alike images + masks (test) |

Specs common to all parts:
- Images: Sentinel-1 SAR **Sigma0, in decibels (dB)**, **2 channels (VV, VH)**, `2048x2048x2`, TIFF
- Masks: `2048x2048` single-channel, binary — `1` = oil-spill foreground, `0` = background
  (no-oil and look-alike scenes have all-zero masks — they are hard negatives)
- Only Part I / III "Oil" images are georeferenced; masks are not georeferenced

Unzip everything under `data/raw/` so it looks like:

```
data/raw/
├── part1/
│   ├── 01_Train_Val_Oil_Spill_images/*.tif
│   └── 01_Train_Val_Oil_Spill_mask/*.tif
├── part2/
│   ├── 01_Train_Val_No_Oil_Images/*.tif
│   ├── 01_Train_Val_No_Oil_mask/*.tif
│   ├── 01_Train_Val_Lookalike_images/*.tif
│   └── 01_Train_Val_Lookalike_mask/*.tif
└── part3/
    ├── Oil/{images,mask}/*.tif
    ├── No_oil/{images,mask}/*.tif
    └── Lookalike/{images,mask}/*.tif
```
(Zenodo's exact inner folder names can vary slightly release-to-release —
`src/preprocessing/loader.py` glob-matches on keywords `oil`, `no_oil`,
`lookalike`, `mask`/`images` so small naming differences won't break it, but
verify with `notebooks/dataset_analysis.py` after downloading.)

## Why this design

- **Binary segmentation, not multiclass.** Your PRD's mandatory objective is
  oil vs. background. We keep look-alikes and no-oil scenes as hard-negative
  training examples (their mask is all zero) rather than trying to also
  classify *what kind* of look-alike it is — that's not in the PRD's scope.
- **U-Net baseline first, DeepLabv3+ comparison second** — per PRD §13–14,
  we don't jump to the fancier model without a measured baseline.
- **Tiling is mandatory, not optional**, because 2048×2048×2 float tiles
  don't comfortably fit consumer GPU memory at a usable batch size, and your
  PRD explicitly requires tiled inference with overlap-merge reconstruction.
- **PyTorch**, matching the PRD's `models/oilspill-v1/best.pt` checkpoint
  convention and giving direct ONNX export for the deployment step.

## Quickstart

```bash
pip install -r requirements.txt

# Phase 1 — dataset stats, class balance, sample visualization
python notebooks/dataset_analysis.py --data-root data/raw

# Phase 3 — train the U-Net baseline (checks CLIP_DB in normalize.py against
# the Phase 1 output before running this for real)
python -m src.training.train --data-root data/raw --epochs 40 --batch-size 8

# Phase 4/5 — evaluate on the held-out Part III test set: IoU/Dice/Precision/
# Recall, scene-level confusion matrix + AUC-ROC, interpretation heatmap
python -m src.training.evaluate --checkpoint models/oilspill-v1/best.pt --data-root data/raw

# Phase 6 — export for deployment (ONNX + TorchScript)
python -m src.inference.export --checkpoint models/oilspill-v1/best.pt --out-dir models/oilspill-v1

# Phase 7 — single-scene inference
python -m src.inference.predictor --checkpoint models/oilspill-v1/best.pt --image path/to/scene.tif

# Phase 7 — inference API
uvicorn src.api.routes:app --host 0.0.0.0 --port 8080

# Tests (no data download required — synthetic arrays only)
pytest tests/
```

## Known limitation of this build

This code was written and syntax-checked in a sandbox with **no network
access and no copy of the ~40GB dataset**, so it has not been executed
end-to-end against real Zenodo data yet. Run `notebooks/dataset_analysis.py`
first after downloading — it will surface any small folder-naming or
channel-order mismatch against what `src/preprocessing/loader.py` expects,
and update `CLIP_DB` in `normalize.py` from the printed percentiles before
trusting training results.
