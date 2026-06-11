# ADAPTIVE SAMPLING REPORT

This report summarizes the performance metrics and compute savings achieved by enabling Adaptive Frame Sampling.

## Ingestion Overview

* **Video ID**: `b32c2588-49bd-4eb6-ac37-f60e3b8f4048`
* **Original Frame Count (Extracted)**: 63
* **Filtered Frame Count (Sent to Qwen)**: 21
* **Frames Skipped**: 42
* **Frame Reduction Ratio**: 66.67%

---

## Runtime & Savings Analysis

* **Average Processing Time Per Sent Frame**: 5.04 seconds
* **Actual Pipeline Run Duration (with sampling)**: 75.36 seconds
* **Projected Run Duration Without Sampling**: 287.17 seconds
* **Estimated Runtime Savings**: 211.81 seconds (3.53 minutes)
* **Actual Runtime Savings**: 211.81 seconds (3.53 minutes)

---

## Threshold Configurations

* **ENABLE_ADAPTIVE_SAMPLING**: `True`
* **SSIM_THRESHOLD**: `0.92`
* **HISTOGRAM_THRESHOLD**: `0.25`
* **MOTION_THRESHOLD**: `0.15`
