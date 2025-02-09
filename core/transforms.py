"""DCT transform utilities."""

import numpy as np
from scipy.fftpack import dct, idct

def dct2(a):
    """2D Discrete Cosine Transform with orthogonal normalization."""
    return dct(dct(a.T, norm='ortho').T, norm='ortho')

def idct2(a):
    """2D Inverse Discrete Cosine Transform with orthogonal normalization."""
    return idct(idct(a.T, norm='ortho').T, norm='ortho')

def create_full_mask(image_size, bands):
    """Create a binary mask for embedding bands."""
    H, W = image_size
    mask = np.zeros((H, W), dtype=np.float32)
    half_H, half_W = H // 2, W // 2
    quadrants = [(0, 0), (0, half_W), (half_H, 0), (half_H, half_W)]
    for (r0, c0) in quadrants:
        for (r_min, r_max, c_min, c_max) in bands:
            mask[r0 + r_min : r0 + r_max, c0 + c_min : c0 + c_max] = 1.0
    return mask
