#!/usr/bin/env python3
"""
Main execution script for invisible watermarking with FHE support.
Uses the same functionality as zama_bounty.py but with modular components.
"""

import sys
import json
import numpy as np
import torch
from pathlib import Path

from invisible_watermark.server.server import WatermarkServer, run_server
from invisible_watermark.server.client import WatermarkClient, run_client
from invisible_watermark.utils.image import load_and_preprocess, save_image
from invisible_watermark.core.transforms import dct2
from invisible_watermark.core.watermark import embed_watermark
from invisible_watermark.fhe.model import IdentityNet
from invisible_watermark.fhe.pipeline import process_image_fhe
from invisible_watermark.core.metrics import calculate_quadrant_robust_metrics_qim
from invisible_watermark.config import (
    IMAGE_SIZE, 
    WATERMARK_DELTA, 
    WATERMARK_OFFSET,
    EMBEDDING_BANDS_QUAD,
    FHE_CONFIG
)

def main():
    """Main execution pipeline."""
    # Get package directory for relative paths
    package_dir = Path(__file__).parent
    image_path = package_dir / "sample.jpg"
    output_dir = package_dir / "output"
    output_dir.mkdir(exist_ok=True)
    
    output_size = IMAGE_SIZE
    
    # Load and process original image
    print("Loading and processing image...")
    original = load_and_preprocess(str(image_path), size=output_size)
    
    # Create server and client
    server = WatermarkServer()
    client = WatermarkClient(server)
    
    # Process image and get results
    result = client.process_image_file(
        str(image_path),
        str(output_dir / "watermarked_sample.png"),
        evaluate=True
    )
    
    # Print clear domain metrics
    print("\nClear Domain Quality Metrics (Four-Quadrant QIM Robust Evaluation):")
    for k, v in result["clear_metrics"].items():
        print(f"  {k}: {v}")
    
    print(f"\nJPEG Compressed Quality Metrics:")
    for k, v in result["jpeg_metrics"].items():
        print(f"  {k}: {v}")
    
    # FHE pipeline processing
    print("\nProcessing through FHE pipeline...")
    watermarked = result["watermarked"]
    full_dct = dct2(watermarked)
    scale_factor = np.percentile(np.abs(full_dct), 99)
    normalized_dct = full_dct / scale_factor
    normalized_dct_tensor = torch.tensor(normalized_dct.reshape(1, -1), dtype=torch.float32)
    output_shape = full_dct.shape
    
    # Initialize and run FHE pipeline
    identity_net = IdentityNet(output_size[0] * output_size[1])
    identity_net.eval()
    
    fhe_output_flat = process_image_fhe(
        normalized_dct_tensor,
        output_shape,
        identity_net,
        model_dir=str(output_dir / "fhe_model")
    )
    
    # Scale back and inverse transform
    fhe_output = fhe_output_flat * scale_factor
    
    # Calculate FHE metrics
    fhe_metrics = calculate_quadrant_robust_metrics_qim(
        original, fhe_output, EMBEDDING_BANDS_QUAD, WATERMARK_DELTA
    )
    
    # Print FHE metrics
    print("\nFHE Pipeline Quality Metrics (Four-Quadrant QIM Robust Evaluation, Original vs FHE Processed):")
    for k, v in fhe_metrics.items():
        print(f"  {k}: {v}")
    
    # Save FHE processed result
    save_image(fhe_output, str(output_dir / "fhe_processed_sample.png"))
    print("FHE processed image saved as 'fhe_processed_sample.png'")
    
    # Save complete results
    results = {
        "clear_domain": result["clear_metrics"],
        "jpeg_compressed": result["jpeg_metrics"],
        "fhe_pipeline": fhe_metrics,
        "embedding_band_quadrant": EMBEDDING_BANDS_QUAD,
        "watermark_delta": WATERMARK_DELTA,
        "watermark_offset": WATERMARK_OFFSET,
        "image_size": output_size
    }
    
    with open(output_dir / "watermarking_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Results saved to 'watermarking_results.json'")

if __name__ == "__main__":
    if "--server" in sys.argv:
        run_server()
    elif "--client" in sys.argv:
        run_client()
    else:
        main()
