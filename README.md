# FloodShield 🌊
### Satellite-Based Flood Detection and Road Impact Analysis

FloodShield is a Python-based geospatial application that uses Sentinel-1 Synthetic Aperture Radar (SAR) imagery to identify potential flood-affected areas and estimate their impact on nearby road networks. It compares radar observations from before and during a flood event, applies water-body filtering, and visualizes the resulting flood extent and road exposure.

The project combines satellite remote sensing, geospatial data processing, quantitative validation, and interactive mapping to explore how satellite imagery can support flood-impact assessment.

## Key Features

- **Satellite Imagery Acquisition:** Fetches Sentinel-1 SAR imagery for a selected area and date range using Google Earth Engine.
- **Before-and-After Change Detection:** Compares radar backscatter between pre-event and post-event observations to identify potential flood areas.
- **Permanent Water Masking:** Uses the JRC Global Surface Water dataset to reduce false detections from permanent water bodies.
- **Flood Patch Filtering:** Applies connected-pixel filtering to remove small candidate flood regions.
- **Road Impact Analysis:** Overlays the predicted flood extent with road-network data and estimates potentially affected road segments and road length.
- **Interactive Visualization:** Displays flood detection and road-impact results through a map-based dashboard.
- **Quantitative Validation:** Compares predicted flood masks against a reference flood mask using standard classification metrics.

## How It Works

1. **Define the study area:** Specify the area of interest (AOI) and the before/after date windows.
2. **Fetch satellite imagery:** Retrieve Sentinel-1 Ground Range Detected imagery using Google Earth Engine.
3. **Match acquisition geometry:** Select compatible pass directions and relative orbits for the two periods.
4. **Prepare radar composites:** Generate median composites and apply spatial smoothing to reduce speckle.
5. **Detect potential flooding:** Calculate the change in VH backscatter and apply a configurable threshold.
6. **Filter the flood mask:** Exclude likely permanent water bodies and remove small connected patches.
7. **Estimate road exposure:** Overlay the predicted flood mask with road-network data and calculate estimated affected road length.
8. **Visualize and evaluate:** Display the results and compare the predicted flood mask against a reference dataset.

## Flood Detection Method

FloodShield uses Sentinel-1 VH-polarized radar backscatter.

The change image is calculated as:

```text
VH Change = VH After - VH Before
```

Pixels with a sufficiently large decrease in backscatter are marked as candidate flood pixels:

```text
VH Change < -Threshold
```

The candidate mask is then refined using permanent-water masking and connected-pixel filtering.

The threshold-based method is a practical baseline. Radar backscatter changes are not unique to flooding, so the output represents **potential flood extent**, not automatically confirmed inundation.

## Technology Stack

- **Language:** Python
- **Satellite Data:** Sentinel-1 SAR
- **Remote Sensing Platform:** Google Earth Engine
- **Geospatial Processing:** Rasterio, GeoPandas and NumPy, where used in the processing pipeline
- **Permanent Water Data:** JRC Global Surface Water
- **GIS and Visual Inspection:** QGIS
- **Visualization:** Interactive map dashboard

## Quantitative Validation

FloodShield was evaluated using a June 2022 flood event in the Barpeta region of Assam, India. The predicted binary flood mask was compared with a reference mask derived from an existing flood map.

### Validation Results

| Metric | Result |
|---|---:|
| Precision | 78.18% |
| Recall | 78.45% |
| F1 Score | 78.32% |
| Intersection over Union (IoU) | 64.36% |
| Overall Accuracy | 83.38% |
| Specificity | 86.43% |
| Cohen's Kappa | 0.6484 |

### Flood Area Comparison

| Measurement | Estimated Area |
|---|---:|
| Reference flood area | 48.87 km² |
| Predicted flood area | 49.04 km² |
| Overlapping flood area | 38.34 km² |

The validation compared 1,428,453 pixels. The prediction and reference rasters had a one-column and one-row origin offset, which the validation script accounted for by aligning the prediction to the reference grid without resampling the binary classes.

### Interpreting the Results

The F1 score of 78.32% and IoU of 64.36% indicate substantial overlap between the prediction and the selected reference mask. However, false-positive and false-negative pixels remain.

These values measure agreement with a **map-derived reference mask**. They do not establish independently verified real-world flood-detection accuracy because the reference map may contain boundary, extraction or georeferencing errors.

## Road Impact Analysis

FloodShield includes a road-impact component that intersects the predicted flood extent with road-network data.

For the earlier Barpeta test, the reported estimate was:

- Road segments identified as potentially affected: 15 out of 367
- Estimated potentially affected road length: 2.53 km

These are model-derived estimates and have not been independently verified against field observations or confirmed road-closure records.

## Configuration

The study area and date windows are configured in `config.py`.

Example configuration for the Vijayawada, Andhra Pradesh flood event:

```python
AOI_CORDS = [80.55, 16.45, 80.75, 16.60]

# Before and during the September 2024 flood event
BEFORE_START, BEFORE_END = "2024-08-20", "2024-08-30"
AFTER_START, AFTER_END = "2024-09-05", "2024-09-16"
```

These are initial test settings. Before running detection, verify that suitable Sentinel-1 VH acquisitions exist in both windows and share compatible acquisition geometry. Adjust the AOI to the intended flood-affected area when necessary.

Example detection parameters:

```python
THRESHOLD_DB = 3.0
MIN_PATCH_PIXELS = 8
PERMANENT_WATER_MIN = 80
```

The parameters are configurable and may require tuning for different events, locations and land-cover conditions.


## Setup and Usage

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd FloodShield
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Ensure the dependencies in `requirements.txt` match the packages used by your implementation.

### 4. Configure Google Earth Engine

- Set up access to Google Earth Engine.
- Authenticate if required.
- Configure the Google Cloud project ID in `config.py`.
- Set the AOI and date ranges.

### 5. Fetch and prepare imagery

```bash
python src/data_fetch.py
```

Confirm that both date windows contain compatible Sentinel-1 acquisitions.

### 6. Run flood detection and the dashboard

Run the flood-detection and dashboard entry points used by your repository. Their exact commands depend on the filenames and framework in your implementation.

### 7. Run quantitative validation

With the reference and prediction rasters available:

```bash
python src/validate_geoshield.py --ref "outputs/reference_flood_mask_aligned.tif" --pred "outputs/geoshield_prediction_nodata_fixed.tif"
```

The validation script reports the confusion matrix, classification metrics and flood-area estimates, and writes a JSON results file.

## Limitations

- The reference flood mask was derived from an existing map and is not independently verified ground truth.
- The current quantitative evaluation covers one flood event and study area.
- Threshold-based radar change detection can produce false positives and false negatives.
- Permanent-water masking and connected-pixel filtering reduce some errors but cannot eliminate them.
- Raster alignment must be checked carefully because spatial offsets can affect pixel-level metrics.
- Road exposure estimates depend on the accuracy of both the predicted flood mask and the road-network dataset.
- Additional events, locations and independently verified reference data are needed to assess generalization.

## Future Improvements

- Validate predictions against independent flood-boundary datasets and field observations.
- Test multiple flood events across different Indian states.
- Evaluate alternative thresholds and detection methods.
- Add boundary-based evaluation and region-level analysis.
- Improve visualization of false positives, false negatives and overlapping flood regions.
- Assess road-impact estimates against verified inundation and road-closure information.
- Explore machine-learning-based flood classification once suitable labelled data are available.

## Project Status

FloodShield is a working flood-detection and road-impact analysis prototype with an implemented quantitative validation workflow. Its reported metrics demonstrate agreement with a map-derived reference for the tested event, while further independent validation is required before making claims about operational flood-mapping accuracy.

## Author

**Swathi Devarakonda**

FloodShield was developed as a project exploring satellite remote sensing, geospatial analysis and flood-impact assessment.
