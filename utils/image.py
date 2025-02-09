"""Image processing utilities."""

import io
import numpy as np
from PIL import Image, ImageFile
from invisible_watermark.config import JPEG_QUALITY

def load_and_preprocess(image_path, size=(64, 64)):
    """Load and preprocess image."""
    try:
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        with open(image_path, 'rb') as f:
            img = Image.open(f)
            img = img.convert('RGB').convert('L')
            img = img.resize(size, Image.Resampling.BICUBIC)
            return np.array(img, dtype=np.float32) / 255.0
    except Exception as e:
        print(f"Error loading image: {e}")
        raise

def simulate_jpeg_compression(image_array, quality=JPEG_QUALITY):
    """Simulate JPEG compression."""
    image_uint8 = (image_array * 255).clip(0, 255).astype(np.uint8)
    pil_img = Image.fromarray(image_uint8)
    buffer = io.BytesIO()
    pil_img.save(buffer, format="JPEG", quality=quality)
    buffer.seek(0)
    compressed_img = Image.open(buffer).convert('L')
    compressed_img = compressed_img.resize(image_array.shape[::-1], Image.Resampling.BICUBIC)
    return np.array(compressed_img, dtype=np.float32) / 255.0

def save_image(array, path):
    """Save image array to file."""
    uint8_array = (array * 255).clip(0, 255).astype(np.uint8)
    Image.fromarray(uint8_array).save(path)
