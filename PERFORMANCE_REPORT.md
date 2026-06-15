# PERFORMANCE REPORT

This report summarizes the performance metrics collected during the video ingestion pipeline.

## Ingestion Overview

* **Video ID**: `fef5394a-b684-4862-963a-d4ef12682f43`
* **Frames Processed**: 411
* **Video Upload Time**: 0.04 seconds
* **Total Ingestion Time**: 1113.03 seconds

---

## Average Stage Timings

| Stage | Average Time (ms) | Percentage of Runtime |
| :--- | :--- | :--- |
| **Qwen VLM Inference** | 4197.71 ms | 97.60% |
| **OCR Processing** | 74.85 ms | 1.74% |
| **Frame Extraction** | 27.51 ms | 0.64% |
| **Metadata Write** | 0.60 ms | 0.01% |
| **JSON Repair & Normalization** | 0.22 ms | 0.01% |
| **Metadata Validation** | 0.02 ms | 0.00% |
| **Total Per Frame** | 4300.90 ms | 100.00% |

---

## Bottleneck Ranking

Based on total runtime spent in each stage:

1. **Qwen VLM Inference**: 1725.26s total (97.60% of runtime)
2. **OCR Processing**: 30.77s total (1.74% of runtime)
3. **Frame Extraction**: 11.30s total (0.64% of runtime)
4. **Metadata Write**: 0.25s total (0.01% of runtime)
5. **JSON Repair**: 0.09s total (0.01% of runtime)
6. **Metadata Validation**: 0.01s total (0.00% of runtime)

---

## Top 10 Slowest Frames

| Rank | Frame ID | Total Frame Time (ms) | VLM Inference (ms) | OCR Time (ms) | Extract Time (ms) | Write Time (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `fef5394a-b684-4862-963a-d4ef12682f43_f0002` | 8877.12 | 8501.53 | 343.40 | 31.57 | 0.39 |
| 2 | `fef5394a-b684-4862-963a-d4ef12682f43_f0001` | 6587.57 | 6219.26 | 343.40 | 13.72 | 1.37 |
| 3 | `fef5394a-b684-4862-963a-d4ef12682f43_f0182` | 5259.91 | 5178.58 | 53.95 | 26.85 | 0.34 |
| 4 | `fef5394a-b684-4862-963a-d4ef12682f43_f0255` | 5254.84 | 5145.83 | 79.26 | 28.80 | 0.65 |
| 5 | `fef5394a-b684-4862-963a-d4ef12682f43_f0260` | 5238.92 | 5124.75 | 85.90 | 27.53 | 0.44 |
| 6 | `fef5394a-b684-4862-963a-d4ef12682f43_f0231` | 5237.17 | 5154.36 | 55.05 | 27.21 | 0.35 |
| 7 | `fef5394a-b684-4862-963a-d4ef12682f43_f0778` | 5229.14 | 5140.67 | 59.28 | 28.16 | 0.75 |
| 8 | `fef5394a-b684-4862-963a-d4ef12682f43_f0158` | 5214.75 | 5073.68 | 113.81 | 26.60 | 0.43 |
| 9 | `fef5394a-b684-4862-963a-d4ef12682f43_f0267` | 5209.44 | 5107.22 | 71.35 | 29.85 | 0.69 |
| 10 | `fef5394a-b684-4862-963a-d4ef12682f43_f0805` | 5206.75 | 5130.56 | 48.48 | 27.19 | 0.32 |

---

## Recommendations

1. **Optimize Qwen VLM Inference**:
   * Currently, the **Qwen VLM Inference** stage represents the largest performance bottleneck at **97.60%** of the total frame processing time.
   * If VLM is the bottleneck: Consider flash attention, quantizing the model (INT4/INT8), or enabling frame-skipping based on motion thresholding.
   * If OCR is the bottleneck: Optimize easyocr reader parameters, switch to GPU if VRAM allows, or run OCR asynchronously in parallel processes.
2. **Optimize Frame Extraction**:
   * Frame extraction takes 27.51 ms per frame on average. If this is high, utilize faster decoder libraries (like `decord`) or write frames directly to an in-memory byte stream instead of saving JPEGs to disk.
3. **Motion Detection / Pixel-Movement Filtering**:
   * Implement a frame-to-frame pixel difference threshold. For frames below a threshold (no motion), skip OCR, VLM, and JSON writing completely, and clone the previous frame's metadata to save significant compute.
