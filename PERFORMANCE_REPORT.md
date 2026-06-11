# PERFORMANCE REPORT

This report summarizes the performance metrics collected during the video ingestion pipeline.

## Ingestion Overview

* **Video ID**: `b32c2588-49bd-4eb6-ac37-f60e3b8f4048`
* **Frames Processed**: 21
* **Video Upload Time**: 0.05 seconds
* **Total Ingestion Time**: 75.42 seconds

---

## Average Stage Timings

| Stage | Average Time (ms) | Percentage of Runtime |
| :--- | :--- | :--- |
| **Qwen VLM Inference** | 4860.94 ms | 96.39% |
| **OCR Processing** | 145.49 ms | 2.88% |
| **Frame Extraction** | 35.44 ms | 0.70% |
| **Metadata Write** | 0.49 ms | 0.01% |
| **JSON Repair & Normalization** | 0.65 ms | 0.01% |
| **Metadata Validation** | 0.02 ms | 0.00% |
| **Total Per Frame** | 5043.02 ms | 100.00% |

---

## Bottleneck Ranking

Based on total runtime spent in each stage:

1. **Qwen VLM Inference**: 102.08s total (96.39% of runtime)
2. **OCR Processing**: 3.06s total (2.88% of runtime)
3. **Frame Extraction**: 0.74s total (0.70% of runtime)
4. **JSON Repair**: 0.01s total (0.01% of runtime)
5. **Metadata Write**: 0.01s total (0.01% of runtime)
6. **Metadata Validation**: 0.00s total (0.00% of runtime)

---

## Top 10 Slowest Frames

| Rank | Frame ID | Total Frame Time (ms) | VLM Inference (ms) | OCR Time (ms) | Extract Time (ms) | Write Time (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `b32c2588-49bd-4eb6-ac37-f60e3b8f4048_f0030` | 13256.41 | 12801.15 | 418.22 | 36.22 | 0.51 |
| 2 | `b32c2588-49bd-4eb6-ac37-f60e3b8f4048_f0001` | 10975.72 | 10524.23 | 418.22 | 23.60 | 0.66 |
| 3 | `b32c2588-49bd-4eb6-ac37-f60e3b8f4048_f0051` | 5125.85 | 5007.93 | 80.95 | 36.29 | 0.59 |
| 4 | `b32c2588-49bd-4eb6-ac37-f60e3b8f4048_f0043` | 5121.29 | 5004.67 | 79.10 | 36.04 | 1.21 |
| 5 | `b32c2588-49bd-4eb6-ac37-f60e3b8f4048_f0033` | 5121.08 | 5002.56 | 81.03 | 36.24 | 0.69 |
| 6 | `b32c2588-49bd-4eb6-ac37-f60e3b8f4048_f0039` | 5088.05 | 4975.02 | 76.87 | 35.70 | 0.40 |
| 7 | `b32c2588-49bd-4eb6-ac37-f60e3b8f4048_f0031` | 5014.38 | 4560.23 | 418.22 | 35.44 | 0.41 |
| 8 | `b32c2588-49bd-4eb6-ac37-f60e3b8f4048_f0032` | 4996.83 | 4542.45 | 418.22 | 35.61 | 0.34 |
| 9 | `b32c2588-49bd-4eb6-ac37-f60e3b8f4048_f0058` | 4650.89 | 4533.29 | 80.95 | 36.07 | 0.34 |
| 10 | `b32c2588-49bd-4eb6-ac37-f60e3b8f4048_f0053` | 4646.89 | 4530.42 | 80.95 | 34.97 | 0.32 |

---

## Recommendations

1. **Optimize Qwen VLM Inference**:
   * Currently, the **Qwen VLM Inference** stage represents the largest performance bottleneck at **96.39%** of the total frame processing time.
   * If VLM is the bottleneck: Consider flash attention, quantizing the model (INT4/INT8), or enabling frame-skipping based on motion thresholding.
   * If OCR is the bottleneck: Optimize easyocr reader parameters, switch to GPU if VRAM allows, or run OCR asynchronously in parallel processes.
2. **Optimize Frame Extraction**:
   * Frame extraction takes 35.44 ms per frame on average. If this is high, utilize faster decoder libraries (like `decord`) or write frames directly to an in-memory byte stream instead of saving JPEGs to disk.
3. **Motion Detection / Pixel-Movement Filtering**:
   * Implement a frame-to-frame pixel difference threshold. For frames below a threshold (no motion), skip OCR, VLM, and JSON writing completely, and clone the previous frame's metadata to save significant compute.
