"""Core watermarking implementation."""

import numpy as np
from invisible_watermark.core.transforms import dct2, idct2
from invisible_watermark.config import WATERMARK_DELTA, EMBEDDING_BANDS_QUAD

def embed_watermark_block_qim(dct_block, bands, delta):
    """Embed watermark using QIM."""
    block = dct_block.copy()
    offset = delta / 4.0
    for (r_min, r_max, c_min, c_max) in bands:
        block[r_min:r_max, c_min:c_max] = np.round(block[r_min:r_max, c_min:c_max] / delta) * delta + offset
    return block

def process_quadrant_qim(image_quad, bands, delta):
    """Process one quadrant for watermarking."""
    quad_dct = dct2(image_quad)
    watermarked_quad_dct = embed_watermark_block_qim(quad_dct, bands, delta)
    watermarked_quad = idct2(watermarked_quad_dct)
    return watermarked_quad, watermarked_quad_dct

def embed_watermark(image):
    """Embed watermark in full image."""
    q1 = image[:32, :32]
    q2 = image[:32, 32:]
    q3 = image[32:, :32]
    q4 = image[32:, 32:]
    
    q1_water, _ = process_quadrant_qim(q1, EMBEDDING_BANDS_QUAD, WATERMARK_DELTA)
    q2_water, _ = process_quadrant_qim(q2, EMBEDDING_BANDS_QUAD, WATERMARK_DELTA)
    q3_water, _ = process_quadrant_qim(q3, EMBEDDING_BANDS_QUAD, WATERMARK_DELTA)
    q4_water, _ = process_quadrant_qim(q4, EMBEDDING_BANDS_QUAD, WATERMARK_DELTA)
    
    top = np.hstack((q1_water, q2_water))
    bottom = np.hstack((q3_water, q4_water))
    return np.vstack((top, bottom))
