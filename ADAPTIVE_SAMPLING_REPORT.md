# ADAPTIVE SAMPLING REPORT

This report summarizes the performance metrics and compute savings achieved by enabling Adaptive Frame Sampling.

## Ingestion Overview

* **Video ID**: `a48b4d08-7e3c-4aa3-a801-0756875508b8`
* **Original Frame Count (Extracted)**: 119
* **Filtered Frame Count (Sent to Qwen)**: 78
* **Frames Skipped**: 41
* **Frame Reduction Ratio**: 34.45%

---

## Runtime & Savings Analysis

* **Average Processing Time Per Sent Frame**: 19.65 seconds
* **Actual Pipeline Run Duration (with sampling)**: 1456.61 seconds
* **Projected Run Duration Without Sampling**: 2262.37 seconds
* **Estimated Runtime Savings**: 805.76 seconds (13.43 minutes)
* **Actual Runtime Savings**: 805.76 seconds (13.43 minutes)

---

## Threshold Configurations

* **ENABLE_ADAPTIVE_SAMPLING**: `True`
* **SSIM_THRESHOLD**: `0.92`
* **HISTOGRAM_THRESHOLD**: `0.25`
* **MOTION_THRESHOLD**: `0.15`
