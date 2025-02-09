"""Client-side implementation for watermark processing."""

import json
import numpy as np
import requests
from invisible_watermark.core.transforms import dct2
from invisible_watermark.utils.image import load_and_preprocess, save_image
from invisible_watermark.config import (
    IMAGE_SIZE,
    EMBEDDING_BANDS_QUAD,
    WATERMARK_DELTA
)
from pathlib import Path

def run_client():
    """Run the FHE client."""
    original = load_and_preprocess("sample.jpg", size=IMAGE_SIZE)
    clear_dct = dct2(original)
    scale_factor = np.percentile(np.abs(clear_dct), 99)
    normalized_dct = clear_dct / scale_factor
    inp = normalized_dct.reshape(1, -1).tolist()[0]
    
    response = requests.post(
        "http://localhost:5000/fhe_forward",
        json={"input": inp}
    )
    print("Server response:", response.json())

class WatermarkClient:
    """Client for interacting with watermark server."""
    
    def __init__(self, server):
        """Initialize client with server connection."""
        self.server = server
    
    def process_image_file(self, input_path, output_path, evaluate=True):
        """Process image file through server."""
        # Create output directory if it doesn't exist
        output_dir = Path(output_path).parent
        output_dir.mkdir(exist_ok=True)
        
        # Load and preprocess image
        image = load_and_preprocess(input_path, size=IMAGE_SIZE)
        
        # Process through server
        result = self.server.process_image(image, evaluate)
        
        # Save watermarked image
        save_image(result["watermarked"], output_path)
        
        # Save results if needed
        if evaluate:
            results = {
                "clear_domain": result["clear_metrics"],
                "jpeg_compressed": result["jpeg_metrics"],
                "embedding_band_quadrant": EMBEDDING_BANDS_QUAD,
                "watermark_delta": WATERMARK_DELTA,
                "image_size": IMAGE_SIZE
            }
            with open(output_dir / "watermarking_results.json", "w") as f:
                json.dump(results, f, indent=2)
        
        return result
    
    def print_metrics(self, metrics):
        """Print evaluation metrics."""
        print("\nQuality Metrics:")
        print("-" * 40)
        for domain, domain_metrics in metrics.items():
            print(f"\n{domain.replace('_', ' ').title()}:")
            for name, value in domain_metrics.items():
                print(f"  {name}: {value:.4f}")
