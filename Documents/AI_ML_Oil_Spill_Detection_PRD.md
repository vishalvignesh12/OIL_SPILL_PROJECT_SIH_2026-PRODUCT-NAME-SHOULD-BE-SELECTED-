# AI/ML Oil Spill Detection & Analysis — Product Requirements Document

**Project:** AI-Based Oil Spill Detection, Drift Hindcasting/Forecasting & Vessel Correlation Platform  
**Module:** AI/ML Layer — Satellite Image Analysis  
**Version:** 1.0  
**Status:** Implementation Specification  
**Primary Input:** Sentinel-1 SAR satellite imagery  
**Primary Output:** Oil-spill segmentation + confidence + geospatial spill attributes

---

# 1. Executive Summary

The AI/ML layer is responsible for analysing incoming Sentinel-1 Synthetic Aperture Radar (SAR) satellite scenes and determining whether an oil spill is present.

When a valid satellite scene enters the backend ingestion pipeline, the ML system must:

1. Load the satellite image.
2. Validate and preprocess the SAR data.
3. Run an oil-spill segmentation model.
4. Determine whether an oil slick is present.
5. Produce a pixel-level oil-spill mask.
6. Calculate a confidence score.
7. Convert the detected region into geospatial information.
8. Return a structured result to the backend.
9. Make the result available to downstream drift and AIS-correlation modules.

The model is **not responsible for identifying the culprit vessel directly**.

The intended system architecture is:

```text
Satellite Scene
      │
      ▼
ML Preprocessing
      │
      ▼
Oil Spill Segmentation Model
      │
      ▼
Oil Spill Mask
      │
      ├── Presence / Absence
      ├── Confidence
      ├── Area
      ├── Centroid
      └── Polygon / Geometry
      │
      ▼
Backend
      │
      ├───────────────┐
      ▼               ▼
Drift Engine      AIS Correlation
      │               │
      └───────┬───────┘
              ▼
       Vessel Ranking
```

---

# 2. Problem Definition

Given a Sentinel-1 SAR scene covering a marine region:

> Determine whether one or more regions in the scene exhibit characteristics consistent with an oil slick, and generate a spatially explicit detection that can be consumed by downstream geospatial analysis.

The model should perform **semantic segmentation**, rather than simply classifying the entire image.

### Why segmentation?

A binary classifier can answer:

```text
Oil spill: YES
```

but cannot answer:

```text
Where is the oil spill?
What shape does it have?
How large is it?
What coordinates does it occupy?
```

Those attributes are necessary for:

- mapping the spill
- estimating affected area
- drift modelling
- temporal comparison
- AIS correlation
- vessel attribution

Therefore, **pixel-level segmentation is the primary ML task**.

---

# 3. ML Objectives

## 3.1 Mandatory Objectives

The model must:

- detect oil slicks in Sentinel-1 SAR imagery
- generate pixel-level segmentation masks
- distinguish oil-slick regions from non-oil regions
- provide a confidence score
- support inference on unseen satellite scenes
- preserve the geographic relationship between pixels and the source scene
- return machine-readable results
- provide inference metadata required by the backend

## 3.2 Recommended Objectives

The system should additionally:

- identify multiple oil-slick regions in one scene
- remove very small noisy detections
- provide connected components / individual slick regions
- calculate approximate spill area
- calculate centroid
- produce polygons
- support configurable confidence thresholds
- expose model version information

## 3.3 Future Objectives

These are outside the first ML model:

- direct vessel identification
- AIS correlation
- drift prediction
- ocean-current modelling
- weather/wind modelling
- autonomous incident classification

---

# 4. Non-Goals

The oil-spill segmentation model must NOT:

- determine legal responsibility
- declare a vessel guilty
- independently identify vessels
- replace AIS analysis
- predict drift trajectories
- perform final attribution
- make regulatory decisions
- claim that every dark SAR region is oil

This distinction is critical.

A dark region in SAR imagery may have multiple causes, including:

- oil
- low wind
- natural slicks
- look-alike phenomena
- sea-state effects
- acquisition artefacts

Therefore:

```text
ML Detection ≠ Vessel Guilt
```

The ML output is evidence for downstream correlation.

---

# 5. Input Requirements

## 5.1 Primary Input

The primary input is:

```text
Sentinel-1 SAR imagery
```

The model pipeline should support the project's selected Sentinel-1 product format.

The exact product format must be confirmed against the available dataset.

Possible inputs may include:

```text
VV
VH
VV + VH
derived channels
```

The ML engineer must determine which representation is actually available in the dataset before finalising the model input layer.

---

# 6. Input Contract

The inference service should receive a scene reference rather than requiring the backend to transmit a massive image through JSON.

Example:

```json
{
  "scene_id": "S1A_20250615_001",
  "image_uri": "storage://satellite-scenes/S1A_20250615_001.tif",
  "acquisition_time": "2025-06-15T05:12:00Z",
  "bbox": {
    "min_lat": 12.0,
    "min_lon": 68.0,
    "max_lat": 12.5,
    "max_lon": 68.5
  }
}
```

The inference worker retrieves the image from the configured storage layer.

---

# 7. Data Requirements

The ML engineer must establish:

```text
Dataset
    │
    ├── Satellite images
    ├── Ground-truth masks
    ├── Metadata
    └── Geographic information
```

The project has access to the:

```text
Zenodo — Sentinel-1 SAR Oil Spill Dataset
```

The complete dataset is approximately 40 GB.

The full dataset is **not required for local development at the beginning**.

Development should support:

```text
small dataset subset
       ↓
pipeline validation
       ↓
model experimentation
       ↓
larger training subset
```

---

# 8. Dataset Preparation

Before training, the ML engineer must document:

- number of images
- image dimensions
- available channels
- label format
- number of oil-spill examples
- number of non-oil examples
- geographic distribution
- temporal distribution
- class imbalance
- missing/corrupt samples

The dataset must not be blindly split into train/test sets.

---

# 9. Train / Validation / Test Split

Recommended:

```text
Train       70%
Validation  15%
Test        15%
```

However, the exact split should be selected based on dataset structure.

### Important

Avoid leakage.

If highly related scenes from the same geographic region or acquisition sequence appear in both train and test sets, the reported performance can be misleading.

Where possible, split by:

```text
scene / region / acquisition group
```

rather than randomly splitting individual image patches.

---

# 10. Preprocessing Pipeline

The preprocessing pipeline should be deterministic.

```text
Raw Sentinel-1
       │
       ▼
Read Raster
       │
       ▼
Validate Channels
       │
       ▼
Radiometric / Dataset-Specific Preprocessing
       │
       ▼
Normalization
       │
       ▼
Resize / Tile
       │
       ▼
Model Input
```

The exact SAR preprocessing must be determined from the dataset's documented product format.

The engineer must document every transformation.

---

# 11. Tiling

Large satellite scenes may not fit into GPU memory.

The inference pipeline should therefore support tiling:

```text
Full Scene
┌─────────────────────────┐
│ ┌────┬────┬────┐        │
│ │ T1 │ T2 │ T3 │        │
│ ├────┼────┼────┤        │
│ │ T4 │ T5 │ T6 │        │
│ └────┴────┴────┘        │
└─────────────────────────┘
```

The system must then reconstruct the full-scene prediction.

If overlapping tiles are used:

```text
Tile overlap
     ↓
Prediction
     ↓
Merge / averaging
     ↓
Final mask
```

The tiling configuration must be recorded.

---

# 12. Data Augmentation

Recommended training augmentations:

- horizontal flip
- vertical flip
- rotation
- random crop
- scale variation where appropriate
- intensity normalization

Augmentations must preserve the semantic meaning of the SAR data.

Do not apply arbitrary image transformations that distort SAR characteristics.

---

# 13. Candidate Model Architecture

The first model should be a semantic segmentation network.

Candidates:

### Option A — U-Net

```text
Input
  │
Encoder
  │
Bottleneck
  │
Decoder
  │
Skip Connections
  │
Segmentation Mask
```

### Option B — DeepLabv3 / DeepLabv3+

```text
Input
  │
Backbone
  │
ASPP
  │
Decoder
  │
Segmentation Mask
```

The team has previously considered U-Net and DeepLabv3.

The final architecture must be selected based on:

- validation IoU
- Dice score
- precision/recall
- false-positive rate
- inference speed
- model size
- available hardware
- training stability

Do not select a model solely because it is more complex.

---

# 14. Recommended Initial Baseline

The ML engineer should first implement a baseline:

```text
U-Net
+
appropriate encoder
+
binary segmentation
```

Then establish measurable performance.

After the baseline works, compare against:

```text
DeepLabv3+
```

This provides a defensible engineering comparison.

---

# 15. Output Classes

Initial model:

```text
0 = Background / Non-Oil
1 = Oil Spill
```

Output:

```text
H × W × 2
```

or equivalent binary-logit representation.

The exact implementation is up to the ML engineer.

---

# 16. Loss Function

Because oil-spill pixels may occupy a relatively small portion of the image, class imbalance must be considered.

Candidate losses:

```text
Binary Cross Entropy
Dice Loss
BCE + Dice
Focal Loss
```

Recommended initial experiment:

```text
Combined BCE + Dice Loss
```

The final loss must be selected using validation performance.

The ML engineer should record the reasoning and experimental results.

---

# 17. Model Output

For every inference, produce:

```json
{
  "scene_id": "S1A_20250615_001",
  "oil_spill_detected": true,
  "confidence": 0.91,
  "model_version": "oilspill-v1",
  "spill_regions": []
}
```

Each region should contain information similar to:

```json
{
  "region_id": "spill_001",
  "confidence": 0.91,
  "area_pixels": 18240,
  "centroid": {
    "lat": 12.231,
    "lon": 68.231
  },
  "polygon": []
}
```

---

# 18. Confidence Score

The system must expose a confidence value.

Example:

```text
0.00 → very low confidence
1.00 → very high confidence
```

Do not present the score as a probability unless calibration has been established.

The UI may later translate the value into:

```text
Low
Medium
High
```

but the backend should preserve the numeric score.

---

# 19. Thresholding

The raw model output should be converted into a binary mask using a configurable threshold.

Example:

```text
threshold = 0.5
```

Do not hard-code the threshold permanently.

Configuration should support:

```env
OIL_SPILL_CONFIDENCE_THRESHOLD=0.50
```

The optimal threshold should be selected from validation data.

---

# 20. Post-Processing

After model inference:

```text
Probability Map
      │
      ▼
Threshold
      │
      ▼
Binary Mask
      │
      ▼
Noise Removal
      │
      ▼
Connected Components
      │
      ▼
Regions
```

Possible operations:

- remove tiny isolated components
- morphological opening/closing
- connected-component analysis
- contour extraction

Post-processing must be validated because excessive filtering can remove genuine small spills.

---

# 21. Geospatial Extraction

The segmentation mask must be transformed from pixel coordinates into geographic coordinates.

Pipeline:

```text
Pixel Mask
    │
    ▼
Raster Transform
    │
    ▼
Geographic Coordinates
    │
    ▼
Polygon
```

Output should include:

```text
centroid
polygon
bounding box
area
```

The exact calculation depends on the source raster's CRS/geotransform.

Do not assume a geographic projection if the raster metadata says otherwise.

---

# 22. Spill Area

The system should estimate the detected spill area.

Possible calculation:

```text
number of spill pixels
        ×
area represented by each pixel
        =
estimated spill area
```

Preferred units:

```text
m²
km²
```

The calculation must account for the image's geographic projection/resolution.

Do not report square kilometres by simply multiplying pixel count by a constant unless the raster resolution supports that assumption.

---

# 23. Multiple Spill Regions

A single scene may contain multiple detected regions.

Therefore the output should support:

```text
spill_regions[]
```

Example:

```json
{
  "oil_spill_detected": true,
  "spill_regions": [
    {
      "region_id": "spill_001",
      "confidence": 0.92
    },
    {
      "region_id": "spill_002",
      "confidence": 0.76
    }
  ]
}
```

---

# 24. Model Evaluation

The model must not be evaluated using accuracy alone.

Required metrics:

| Metric | Required | Purpose |
|---|---:|---|
| IoU / Jaccard | YES | Segmentation overlap |
| Dice / F1 | YES | Region overlap |
| Precision | YES | False-positive control |
| Recall | YES | Missed-spill control |
| Confusion Matrix | YES | Error analysis |
| Inference latency | YES | Deployment feasibility |
| Model size | Recommended | Deployment planning |

---

# 25. Primary Success Metrics

The primary metrics should be:

```text
IoU
Dice
Precision
Recall
```

The team should establish target values after creating a baseline because the achievable performance depends on the exact dataset and label quality.

Do **not** claim an arbitrary accuracy target before measuring the baseline.

---

# 26. Error Analysis

Every training experiment should examine:

### False Positives

Examples:

```text
Low-wind regions
Natural ocean phenomena
Look-alikes
SAR artefacts
```

### False Negatives

Examples:

```text
Small spills
Low-contrast spills
Fragmented slicks
Noisy scenes
```

The engineer should maintain an error-analysis set.

---

# 27. Training Experiment Tracking

Every experiment should record:

```text
experiment_id
model architecture
encoder
input channels
image size
loss
optimizer
learning rate
batch size
epochs
augmentation
threshold
IoU
Dice
precision
recall
inference latency
checkpoint
```

Recommended tools:

```text
MLflow
Weights & Biases
```

For a hackathon, lightweight experiment logging is sufficient.

---

# 28. Checkpointing

The training process must save:

```text
best validation model
latest model
training configuration
```

Example:

```text
models/
└── oilspill/
    ├── v1/
    │   ├── best.pt
    │   ├── config.json
    │   └── metrics.json
```

---

# 29. Model Versioning

Every deployed model must have a version.

Example:

```text
oilspill-v1
oilspill-v2
oilspill-v3
```

The inference result must return:

```json
{
  "model_version": "oilspill-v1"
}
```

This is essential for reproducibility.

---

# 30. Inference Service

The trained model should be exposed through a service.

Recommended:

```text
FastAPI
```

Example:

```http
POST /predict
```

Request:

```json
{
  "scene_id": "S1A_20250615_001",
  "image_uri": "storage://satellite-scenes/S1A_20250615_001.tif"
}
```

Response:

```json
{
  "scene_id": "S1A_20250615_001",
  "oil_spill_detected": true,
  "confidence": 0.91,
  "model_version": "oilspill-v1",
  "spill_regions": []
}
```

---

# 31. Backend Integration

The intended interaction is:

```text
Backend
   │
   │ Analysis Job
   ▼
ML Service
   │
   │ prediction
   ▼
Backend
   │
   ▼
Database
   │
   ▼
Frontend
```

The backend should not need to understand the internal PyTorch/TensorFlow implementation.

---

# 32. Asynchronous Processing

Inference should not block satellite ingestion.

Recommended:

```text
Satellite Ingestion
       │
       ▼
Analysis Job
       │
       ▼
Queue
       │
       ▼
ML Worker
       │
       ▼
Prediction
       │
       ▼
Backend
```

The ML worker can process jobs independently.

---

# 33. Failure Handling

If inference fails:

```json
{
  "scene_id": "S1A_20250615_001",
  "status": "FAILED",
  "error_code": "MODEL_INFERENCE_FAILED"
}
```

The system should support retries for transient failures.

Do not endlessly retry invalid inputs.

---

# 34. Hardware Requirements

Training:

```text
GPU strongly recommended
```

Inference:

```text
GPU preferred
CPU fallback recommended
```

The ML engineer must benchmark:

```text
CPU inference
GPU inference
```

using the same sample scene.

The deployment target should be selected based on actual latency rather than assumptions.

---

# 35. Docker Requirements

The ML service should be containerized.

Conceptual structure:

```text
ml/
├── app/
│   ├── api/
│   ├── inference/
│   ├── preprocessing/
│   ├── postprocessing/
│   └── schemas/
├── models/
├── tests/
├── Dockerfile
├── requirements.txt
└── README.md
```

If GPU inference is required, provide a compatible GPU container configuration.

---

# 36. Suggested ML Stack

## Mandatory

```text
Python
PyTorch
TorchVision / relevant segmentation libraries
NumPy
Rasterio
GeoPandas / Shapely where needed
OpenCV where needed
FastAPI
Pydantic
```

## Recommended

```text
Albumentations
MLflow
scikit-learn
Matplotlib
Weights & Biases
```

Use only libraries that are justified by the implementation.

---

# 37. Testing Requirements

## Unit Tests

Test:

```text
preprocessing
normalization
tiling
mask reconstruction
thresholding
post-processing
area calculation
polygon generation
confidence calculation
```

## Integration Tests

Test:

```text
API
    ↓
image loading
    ↓
model
    ↓
post-processing
    ↓
response
```

## Regression Tests

Maintain a small fixed set of scenes:

```text
ML Regression Dataset
├── clear ocean
├── obvious oil
├── small spill
├── noisy scene
└── difficult look-alike
```

A model update must be evaluated against this set.

---

# 38. Performance Requirements

The team should measure:

```text
image loading time
preprocessing time
model inference time
post-processing time
total latency
memory usage
GPU memory usage
```

Target latency must be determined from the actual deployment hardware.

For the hackathon, prioritize:

```text
correctness
reproducibility
stable inference
```

over extreme optimization.

---

# 39. Observability

Each inference should log:

```text
scene_id
model_version
processing_start
processing_end
latency
prediction_status
confidence
number_of_regions
```

Example:

```json
{
  "event": "oil_spill_inference_completed",
  "scene_id": "S1A_20250615_001",
  "model_version": "oilspill-v1",
  "latency_ms": 842,
  "oil_spill_detected": true,
  "confidence": 0.91
}
```

---

# 40. Model Monitoring

After deployment, monitor:

```text
inference failures
latency
confidence distribution
input failures
model version
prediction distribution
```

If ground truth later becomes available, monitor:

```text
IoU
Dice
precision
recall
```

---

# 41. Explainability / Visualization

For the demonstration, the ML service should make it possible to visualize:

```text
Original SAR
      +
Predicted Mask
      +
Overlay
```

Example:

```text
SAR Image
   +
Oil Mask
   ↓
Detection Overlay
```

This is important for judge-facing demonstration because it provides visual evidence that the model is detecting a spatial region rather than producing an unexplained classification.

---

# 42. Required Output Artifacts

For a successful prediction, the system should be capable of producing:

```text
1. Detection status
2. Confidence
3. Segmentation mask
4. Spill polygon
5. Bounding box
6. Centroid
7. Estimated area
8. Model version
9. Processing time
```

Not every artifact must be returned directly in the JSON response. Large masks should be stored in object storage and referenced by URI.

---

# 43. Example Complete Response

```json
{
  "scene_id": "S1A_20250615_001",
  "status": "COMPLETED",
  "oil_spill_detected": true,
  "confidence": 0.91,
  "model_version": "oilspill-v1",
  "processing_time_ms": 842,
  "spill_regions": [
    {
      "region_id": "spill_001",
      "confidence": 0.91,
      "area_m2": 1824000,
      "centroid": {
        "lat": 12.231,
        "lon": 68.231
      },
      "bbox": {
        "min_lat": 12.20,
        "min_lon": 68.20,
        "max_lat": 12.27,
        "max_lon": 68.27
      },
      "polygon_uri": "storage://predictions/spill_001.geojson",
      "mask_uri": "storage://predictions/spill_001.png"
    }
  ]
}
```

---

# 44. Interface With Drift Engine

The ML model supplies the initial observed spill geometry.

```text
Satellite Scene
      │
      ▼
Oil Spill Mask
      │
      ▼
Spill Polygon
      │
      ▼
Observed Spill Location
      │
      ▼
Drift Engine
```

The drift engine then determines:

```text
Where could the spill
have originated?
```

and potentially:

```text
Where could it move?
```

The ML model does not perform this task.

---

# 45. Interface With AIS Correlation

The ML output supplies:

```text
spill centroid
spill polygon
spill timestamp
```

The AIS system then searches for vessels in a relevant:

```text
spatial window
+
temporal window
```

Example conceptual flow:

```text
Detected Spill
      │
      ├── Location
      └── Acquisition Time
             │
             ▼
        AIS Query
             │
             ▼
       Candidate Vessels
             │
             ▼
       Ranking Engine
```

The ML model must not declare the responsible vessel.

---

# 46. Critical Scientific Constraint

The system must distinguish between:

```text
Detection
```

and:

```text
Attribution
```

The model can produce:

> "This region is consistent with an oil slick with model confidence X."

It should not produce:

> "Vessel X caused the spill."

The second conclusion requires additional spatio-temporal evidence.

---

# 47. Development Roadmap

## Phase 1 — Dataset Understanding

Deliverables:

- dataset downloaded/subset selected
- dataset structure documented
- image format confirmed
- label format confirmed
- channel configuration confirmed
- sample visualizations created

### Exit Criteria

The engineer can load:

```text
image → label mask
```

from code.

---

## Phase 2 — Preprocessing Pipeline

Deliverables:

- raster loader
- normalization
- resizing/tiling
- augmentation
- visualization

### Exit Criteria

```text
raw image
   ↓
model-ready tensor
```

works reproducibly.

---

## Phase 3 — Baseline Model

Implement:

```text
U-Net
```

Train on a manageable subset.

Deliverables:

- training script
- validation loop
- checkpoints
- metrics
- loss curves

### Exit Criteria

A trained model produces a segmentation mask on an unseen test image.

---

## Phase 4 — Model Evaluation

Evaluate:

```text
IoU
Dice
Precision
Recall
```

Perform false-positive and false-negative analysis.

---

## Phase 5 — Architecture Comparison

Compare:

```text
U-Net
vs
DeepLabv3+
```

Use the same test methodology.

Select the model based on measured results.

---

## Phase 6 — Geospatial Post-Processing

Implement:

```text
mask
 ↓
connected regions
 ↓
polygon
 ↓
centroid
 ↓
area
```

Validate against known raster geometry.

---

## Phase 7 — Inference Service

Implement:

```http
POST /predict
```

Containerize the service.

---

## Phase 8 — Backend Integration

Connect:

```text
Satellite Ingestion
       ↓
Analysis Job
       ↓
ML Worker
       ↓
Prediction
       ↓
Backend Database
```

---

## Phase 9 — Replay Demonstration

Run:

```text
Historical Sentinel-1 scenes
          ↓
Replay Script
          ↓
Backend
          ↓
ML
          ↓
Oil Detection
          ↓
Frontend
```

The system should appear to process satellite acquisitions sequentially.

---

# 48. Definition of Done

The ML module is considered complete when:

```text
✓ Sentinel-1 scene can be loaded
✓ preprocessing works
✓ trained segmentation model exists
✓ model predicts on unseen imagery
✓ oil mask is generated
✓ confidence is returned
✓ spill regions are extracted
✓ geospatial polygon is generated
✓ spill area can be estimated
✓ model version is tracked
✓ inference API works
✓ Docker deployment works
✓ backend can invoke the model
✓ prediction is persisted
✓ tests pass
✓ replay pipeline works
```

---

# 49. Mandatory vs Recommended

| Requirement | Priority |
|---|---|
| Sentinel-1 loading | MANDATORY |
| Dataset/label validation | MANDATORY |
| SAR preprocessing | MANDATORY |
| Binary segmentation | MANDATORY |
| U-Net baseline | MANDATORY |
| IoU/Dice/Precision/Recall | MANDATORY |
| Confidence output | MANDATORY |
| Geospatial mask/polygon | MANDATORY |
| Backend inference API | MANDATORY |
| Model versioning | MANDATORY |
| Docker inference | MANDATORY |
| Unit/integration tests | MANDATORY |
| Replay integration | MANDATORY |
| DeepLabv3+ comparison | RECOMMENDED |
| MLflow/W&B | RECOMMENDED |
| Advanced ensemble models | OPTIONAL |
| Transformer segmentation | OPTIONAL |
| Automated retraining | FUTURE |
| Direct vessel attribution | OUT OF SCOPE |
| Live satellite API | FUTURE |

---

# 50. Recommended Repository Structure

```text
ai/
├── README.md
├── requirements.txt
├── Dockerfile
├── .env.example
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── samples/
│
├── notebooks/
│   ├── dataset_analysis.ipynb
│   └── model_evaluation.ipynb
│
├── src/
│   ├── api/
│   │   └── routes.py
│   │
│   ├── preprocessing/
│   │   ├── loader.py
│   │   ├── normalize.py
│   │   └── tiling.py
│   │
│   ├── models/
│   │   ├── unet.py
│   │   └── deeplab.py
│   │
│   ├── training/
│   │   ├── train.py
│   │   ├── losses.py
│   │   └── metrics.py
│   │
│   ├── inference/
│   │   └── predictor.py
│   │
│   ├── postprocessing/
│   │   ├── mask.py
│   │   ├── polygon.py
│   │   └── geospatial.py
│   │
│   └── schemas/
│       └── prediction.py
│
├── models/
│   └── oilspill-v1/
│       ├── best.pt
│       ├── config.json
│       └── metrics.json
│
└── tests/
    ├── test_preprocessing.py
    ├── test_inference.py
    ├── test_postprocessing.py
    └── test_api.py
```

---

# 51. Final ML Architecture

```text
                  SENTINEL-1 SAR
                       │
                       ▼
               ┌───────────────┐
               │ Preprocessing │
               └───────┬───────┘
                       │
                       ▼
               ┌───────────────┐
               │ Segmentation  │
               │    Model      │
               │ U-Net / DLv3+ │
               └───────┬───────┘
                       │
                       ▼
                Probability Map
                       │
                       ▼
                   Threshold
                       │
                       ▼
                 Binary Mask
                       │
                       ▼
              Post-Processing
                       │
            ┌──────────┼──────────┐
            ▼          ▼          ▼
         Polygon    Centroid     Area
            │          │          │
            └──────────┼──────────┘
                       ▼
                ML Prediction
                       │
                       ▼
                   BACKEND
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
        Drift Engine        AIS Engine
             │                   │
             └─────────┬─────────┘
                       ▼
                Vessel Ranking
```

---

# 52. Core Principle for the ML Engineer

The first objective is **not to build the most complicated model**.

The first objective is to build a scientifically defensible pipeline:

```text
DATA
  ↓
PREPROCESSING
  ↓
SEGMENTATION
  ↓
VALIDATION
  ↓
GEOSPATIAL OUTPUT
  ↓
API
  ↓
BACKEND
```

The team should establish a strong baseline first, measure it objectively, and then improve it.

The final system must make a clear distinction between:

```text
"What does the satellite image show?"
```

and:

```text
"Which vessel caused it?"
```

The ML model answers the first question. Drift and AIS correlation provide evidence for the second.
