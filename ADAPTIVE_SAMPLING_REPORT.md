# ADAPTIVE SAMPLING REPORT

This report summarizes the performance metrics and compute savings achieved by enabling Adaptive Frame Sampling.

## Ingestion Overview

* **Video ID**: `f7453f97-0280-479e-b295-4858c6497e9c`
* **Original Frame Count (Extracted)**: 8
* **Filtered Frame Count (Sent to Qwen)**: 7
* **Frames Skipped**: 1
* **Frame Reduction Ratio**: 12.50%

---

## Runtime & Savings Analysis

* **Average Processing Time Per Sent Frame**: 4.44 seconds
* **Actual Pipeline Run Duration (with sampling)**: 20.11 seconds
* **Projected Run Duration Without Sampling**: 24.55 seconds
* **Estimated Runtime Savings**: 4.44 seconds (0.07 minutes)
* **Actual Runtime Savings**: 4.44 seconds (0.07 minutes)

---

## Threshold Configurations

* **ENABLE_ADAPTIVE_SAMPLING**: `True`
* **SSIM_THRESHOLD**: `0.92`
* **HISTOGRAM_THRESHOLD**: `0.25`
* **MOTION_THRESHOLD**: `0.15`
