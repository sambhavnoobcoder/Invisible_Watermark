"""Configuration parameters for watermarking."""

# Global Parameters
WATERMARK_DELTA = 0.10        # Quantization step for QIM embedding
WATERMARK_OFFSET = WATERMARK_DELTA / 4.0
BETA = 0.35                   # (Not used for QIM embedding, but reserved if needed)
# Use a single low-frequency band per quadrant (for QIM embedding)
EMBEDDING_BANDS_QUAD = [(1, 8, 1, 8)]
JPEG_QUALITY = 50
IMAGE_SIZE = (64, 64)

# FHE Configuration
FHE_CONFIG = {
    "n_bits": 16,
    "rounding_threshold": 8,
    "p_error": 0.001,
    "model_dir": "./fhe_model"
}
