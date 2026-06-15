# ADAPTIVE SAMPLING REPORT

This report summarizes the performance metrics and compute savings achieved by enabling Adaptive Frame Sampling.

## Ingestion Overview

* **Video ID**: `fef5394a-b684-4862-963a-d4ef12682f43`
* **Original Frame Count (Extracted)**: 826
* **Filtered Frame Count (Sent to Qwen)**: 411
* **Frames Skipped**: 415
* **Frame Reduction Ratio**: 50.24%

---

## Runtime & Savings Analysis

* **Average Processing Time Per Sent Frame**: 4.30 seconds
* **Actual Pipeline Run Duration (with sampling)**: 1112.99 seconds
* **Projected Run Duration Without Sampling**: 2897.87 seconds
* **Estimated Runtime Savings**: 1784.87 seconds (29.75 minutes)
* **Actual Runtime Savings**: 1784.87 seconds (29.75 minutes)

---

## Threshold Configurations

* **ENABLE_ADAPTIVE_SAMPLING**: `True`
* **SSIM_THRESHOLD**: `0.92`
* **HISTOGRAM_THRESHOLD**: `0.25`
* **MOTION_THRESHOLD**: `0.15`
