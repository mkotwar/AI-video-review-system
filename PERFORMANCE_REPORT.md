# PERFORMANCE REPORT

This report summarizes the performance metrics collected during the video ingestion pipeline.

## Ingestion Overview

* **Video ID**: `a48b4d08-7e3c-4aa3-a801-0756875508b8`
* **Frames Processed**: 78
* **Video Upload Time**: 0.06 seconds
* **Total Ingestion Time**: 1456.66 seconds

---

## Average Stage Timings

| Stage | Average Time (ms) | Percentage of Runtime |
| :--- | :--- | :--- |
| **Qwen VLM Inference** | 4315.21 ms | 21.96% |
| **OCR Processing** | 15039.84 ms | 76.53% |
| **Frame Extraction** | 297.00 ms | 1.51% |
| **Metadata Write** | 0.41 ms | 0.00% |
| **JSON Repair & Normalization** | 0.20 ms | 0.00% |
| **Metadata Validation** | 0.02 ms | 0.00% |
| **Total Per Frame** | 19652.68 ms | 100.00% |

---

## Bottleneck Ranking

Based on total runtime spent in each stage:

1. **OCR Processing**: 1173.11s total (76.53% of runtime)
2. **Qwen VLM Inference**: 336.59s total (21.96% of runtime)
3. **Frame Extraction**: 23.17s total (1.51% of runtime)
4. **Metadata Write**: 0.03s total (0.00% of runtime)
5. **JSON Repair**: 0.02s total (0.00% of runtime)
6. **Metadata Validation**: 0.00s total (0.00% of runtime)

---

## Top 10 Slowest Frames

| Rank | Frame ID | Total Frame Time (ms) | VLM Inference (ms) | OCR Time (ms) | Extract Time (ms) | Write Time (ms) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `a48b4d08-7e3c-4aa3-a801-0756875508b8_f0019` | 25923.18 | 9940.12 | 15689.48 | 291.98 | 1.20 |
| 2 | `a48b4d08-7e3c-4aa3-a801-0756875508b8_f0004` | 25553.30 | 6972.87 | 18277.68 | 301.58 | 0.66 |
| 3 | `a48b4d08-7e3c-4aa3-a801-0756875508b8_f0053` | 24000.01 | 4828.59 | 18845.84 | 325.00 | 0.50 |
| 4 | `a48b4d08-7e3c-4aa3-a801-0756875508b8_f0059` | 23646.09 | 4494.78 | 18845.84 | 304.92 | 0.36 |
| 5 | `a48b4d08-7e3c-4aa3-a801-0756875508b8_f0021` | 23529.27 | 7527.92 | 15689.48 | 310.79 | 0.58 |
| 6 | `a48b4d08-7e3c-4aa3-a801-0756875508b8_f0058` | 23401.55 | 4248.67 | 18845.84 | 306.57 | 0.29 |
| 7 | `a48b4d08-7e3c-4aa3-a801-0756875508b8_f0006` | 23283.16 | 4679.67 | 18277.68 | 325.31 | 0.32 |
| 8 | `a48b4d08-7e3c-4aa3-a801-0756875508b8_f0013` | 23274.59 | 4664.71 | 18277.68 | 331.68 | 0.35 |
| 9 | `a48b4d08-7e3c-4aa3-a801-0756875508b8_f0001` | 23081.78 | 4701.38 | 18277.68 | 99.68 | 0.75 |
| 10 | `a48b4d08-7e3c-4aa3-a801-0756875508b8_f0070` | 22727.09 | 4917.31 | 17503.91 | 305.34 | 0.47 |

---

## Recommendations

1. **Optimize OCR Processing**:
   * Currently, the **OCR Processing** stage represents the largest performance bottleneck at **76.53%** of the total frame processing time.
   * If VLM is the bottleneck: Consider flash attention, quantizing the model (INT4/INT8), or enabling frame-skipping based on motion thresholding.
   * If OCR is the bottleneck: Optimize easyocr reader parameters, switch to GPU if VRAM allows, or run OCR asynchronously in parallel processes.
2. **Optimize Frame Extraction**:
   * Frame extraction takes 297.00 ms per frame on average. If this is high, utilize faster decoder libraries (like `decord`) or write frames directly to an in-memory byte stream instead of saving JPEGs to disk.
3. **Motion Detection / Pixel-Movement Filtering**:
   * Implement a frame-to-frame pixel difference threshold. For frames below a threshold (no motion), skip OCR, VLM, and JSON writing completely, and clone the previous frame's metadata to save significant compute.
