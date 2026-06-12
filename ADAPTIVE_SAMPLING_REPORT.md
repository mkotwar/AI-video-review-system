# ADAPTIVE SAMPLING REPORT

This report summarizes the performance metrics and compute savings achieved by enabling Adaptive Frame Sampling.

## Ingestion Overview

* **Video ID**: `2841952d-d276-4d08-824e-eb03a7492404`
* **Original Frame Count (Extracted)**: 826
* **Filtered Frame Count (Sent to Qwen)**: 411
* **Frames Skipped**: 415
* **Frame Reduction Ratio**: 50.24%

---

## Runtime & Savings Analysis

* **Average Processing Time Per Sent Frame**: 0.00 seconds
* **Actual Pipeline Run Duration (with sampling)**: 139.02 seconds
* **Projected Run Duration Without Sampling**: 139.02 seconds
* **Estimated Runtime Savings**: 0.00 seconds (0.00 minutes)
* **Actual Runtime Savings**: 0.00 seconds (0.00 minutes)

---

## Threshold Configurations

* **ENABLE_ADAPTIVE_SAMPLING**: `True`
* **SSIM_THRESHOLD**: `0.92`
* **HISTOGRAM_THRESHOLD**: `0.25`
* **MOTION_THRESHOLD**: `0.15`
