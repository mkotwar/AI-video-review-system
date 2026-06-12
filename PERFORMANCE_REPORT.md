# PERFORMANCE REPORT

This report summarizes the performance metrics collected during the video ingestion pipeline.

## Ingestion Overview

* **Video ID**: `f7453f97-0280-479e-b295-4858c6497e9c`
* **Frames Processed**: 7
* **Video Upload Time**: 0.00 seconds
* **Total Ingestion Time**: 20.11 seconds

---

## Average Stage Timings

| Stage | Average Time (ms) | Percentage of Runtime |
| :--- | :--- | :--- |
| **Qwen VLM Inference** | 4304.93 ms | 97.03% |
| **OCR Processing** | 92.44 ms | 2.08% |
| **Frame Extraction** | 38.26 ms | 0.86% |
| **Metadata Write** | 0.79 ms | 0.02% |
| **JSON Repair & Normalization** | 0.28 ms | 0.01% |
| **Metadata Validation** | 0.02 ms | 0.00% |
| **Total Per Frame** | 4436.71 ms | 100.00% |

---

## Bottleneck Ranking

Based on total runtime spent in each stage:

1. **Qwen VLM Inference**: 30.13s total (97.03% of runtime)
2. **OCR Processing**: 0.65s total (2.08% of runtime)
3. **Frame Extraction**: 0.27s total (0.86% of runtime)
4. **Metadata Write**: 0.01s total (0.02% of runtime)
5. **JSON Repair**: 0.00s total (0.01% of runtime)
6. **Metadata Validation**: 0.00s total (0.00% of runtime)

---

## Top 10 Slowest Frames

| Rank | Frame ID | Total Frame Time (ms) | VLM Inference (ms) | OCR Time (ms) | Extract Time (ms) | Write Time (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `f7453f97-0280-479e-b295-4858c6497e9c_f0002` | 5450.56 | 5318.34 | 89.98 | 40.74 | 1.21 |
| 2 | `f7453f97-0280-479e-b295-4858c6497e9c_f0006` | 5254.99 | 5118.24 | 95.71 | 40.18 | 0.56 |
| 3 | `f7453f97-0280-479e-b295-4858c6497e9c_f0008` | 4772.01 | 4635.71 | 95.71 | 39.85 | 0.45 |
| 4 | `f7453f97-0280-479e-b295-4858c6497e9c_f0003` | 4751.58 | 4618.37 | 89.98 | 42.48 | 0.48 |
| 5 | `f7453f97-0280-479e-b295-4858c6497e9c_f0004` | 4692.63 | 4561.20 | 89.98 | 41.12 | 0.24 |
| 6 | `f7453f97-0280-479e-b295-4858c6497e9c_f0001` | 3157.77 | 3043.35 | 89.98 | 23.00 | 1.02 |
| 7 | `f7453f97-0280-479e-b295-4858c6497e9c_f0005` | 2977.41 | 2839.30 | 95.71 | 40.44 | 1.56 |

---

## Recommendations

1. **Optimize Qwen VLM Inference**:
   * Currently, the **Qwen VLM Inference** stage represents the largest performance bottleneck at **97.03%** of the total frame processing time.
   * If VLM is the bottleneck: Consider flash attention, quantizing the model (INT4/INT8), or enabling frame-skipping based on motion thresholding.
   * If OCR is the bottleneck: Optimize easyocr reader parameters, switch to GPU if VRAM allows, or run OCR asynchronously in parallel processes.
2. **Optimize Frame Extraction**:
   * Frame extraction takes 38.26 ms per frame on average. If this is high, utilize faster decoder libraries (like `decord`) or write frames directly to an in-memory byte stream instead of saving JPEGs to disk.
3. **Motion Detection / Pixel-Movement Filtering**:
   * Implement a frame-to-frame pixel difference threshold. For frames below a threshold (no motion), skip OCR, VLM, and JSON writing completely, and clone the previous frame's metadata to save significant compute.
