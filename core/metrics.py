"""Quality metrics for watermark evaluation."""

import numpy as np
from skimage.metrics import peak_signal_noise_ratio as psnr
from skimage.metrics import structural_similarity as ssim

from invisible_watermark.core.transforms import dct2
from invisible_watermark.config import WATERMARK_DELTA

def extract_watermark_block_qim(water_dct, bands, delta):
    """Extract watermark by computing median residuals."""
    medians = []
    for (r_min, r_max, c_min, c_max) in bands:
        coeffs = water_dct[r_min:r_max, c_min:c_max]
        quantized = np.round(coeffs / delta) * delta
        residuals = coeffs - quantized
        medians.append(np.median(residuals))
    return medians

def robust_quad_extraction_qim(water_quad, bands, delta):
    """Compute robust extraction accuracy for one quadrant."""
    water_dct = dct2(water_quad)
    medians = extract_watermark_block_qim(water_dct, bands, delta)
    expected = delta / 4.0
    accuracies = [max(0, 1 - abs(m - expected) / expected) * 100 for m in medians]
    return np.mean(accuracies)

def calculate_quadrant_robust_metrics_qim(original, watermarked, bands, delta):
    """Calculate comprehensive quality metrics."""
    orig_uint8 = (original * 255).clip(0,255).astype(np.uint8)
    water_uint8 = (watermarked * 255).clip(0,255).astype(np.uint8)
    
    metrics = {
        "psnr": psnr(orig_uint8, water_uint8),
        "ssim": ssim(orig_uint8, water_uint8),
    }
    
    # Calculate watermark accuracy for each quadrant
    q1 = watermarked[:32, :32]
    q2 = watermarked[:32, 32:]
    q3 = watermarked[32:, :32]
    q4 = watermarked[32:, 32:]
    
    acc1 = robust_quad_extraction_qim(q1, bands, delta)
    acc2 = robust_quad_extraction_qim(q2, bands, delta)
    acc3 = robust_quad_extraction_qim(q3, bands, delta)
    acc4 = robust_quad_extraction_qim(q4, bands, delta)
    
    metrics["watermark_accuracy"] = (acc1 + acc2 + acc3 + acc4) / 4.0
    return metrics
