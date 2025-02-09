"""Server-side implementation for watermark processing."""

import numpy as np
import torch
from flask import Flask, request, jsonify
from pathlib import Path
from concrete.ml.torch.compile import compile_torch_model
from concrete.fhe.compilation.configuration import Configuration

from invisible_watermark.fhe.model import IdentityNet
from invisible_watermark.utils.image import simulate_jpeg_compression
from invisible_watermark.core.watermark import embed_watermark
from invisible_watermark.core.metrics import calculate_quadrant_robust_metrics_qim
from invisible_watermark.config import (
    EMBEDDING_BANDS_QUAD, 
    WATERMARK_DELTA, 
    JPEG_QUALITY, 
    FHE_CONFIG
)

def run_server():
    """Run the FHE server."""
    app = Flask(__name__)
    
    # Initialize with dummy input
    dummy_input = np.zeros((1, 64*64), dtype=np.float32)
    dummy_tensor = torch.tensor(dummy_input, dtype=torch.float32)
    identity_net = IdentityNet(64*64)
    identity_net.eval()
    
    # Compile model
    global quant_module
    quant_module, _ = compile_torch_model(
        identity_net,
        dummy_tensor,
        configuration=Configuration(
            dump_artifacts_on_unexpected_failures=False,
            enable_unsafe_features=True,
            use_insecure_key_cache=True,
            insecure_key_cache_location=Path(FHE_CONFIG["model_dir"]) / "keycache"
        ),
        n_bits=FHE_CONFIG["n_bits"],
        rounding_threshold_bits=FHE_CONFIG["rounding_threshold"],
        p_error=FHE_CONFIG["p_error"],
        verbose=True
    )
    
    @app.route("/fhe_forward", methods=["POST"])
    def fhe_forward():
        data = request.json
        inp = np.array(data["input"], dtype=np.float32).reshape(1, -1)
        out = quant_module.forward(inp, fhe="execute")
        return jsonify({"output": out.tolist()})
    
    app.run(host="0.0.0.0", port=5000)

class WatermarkServer:
    """Server for watermark processing and evaluation."""
    
    def process_image(self, image, evaluate=True):
        """Process image with watermarking and evaluation."""
        # Store original for metrics
        original = image.copy()
        
        # Apply watermark
        watermarked = embed_watermark(image)
        
        result = {"watermarked": watermarked}
        
        if evaluate:
            # Clear domain metrics
            clear_metrics = calculate_quadrant_robust_metrics_qim(
                original, watermarked, EMBEDDING_BANDS_QUAD, WATERMARK_DELTA
            )
            
            # JPEG compression test
            jpeg_compressed = simulate_jpeg_compression(watermarked, JPEG_QUALITY)
            jpeg_metrics = calculate_quadrant_robust_metrics_qim(
                original, jpeg_compressed, EMBEDDING_BANDS_QUAD, WATERMARK_DELTA
            )
            
            result.update({
                "clear_metrics": clear_metrics,
                "jpeg_metrics": jpeg_metrics
            })
        
        return result
