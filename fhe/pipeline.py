"""FHE processing pipeline."""

import os
import time
from pathlib import Path
import torch
import numpy as np
from concrete.fhe.compilation.configuration import Configuration
from concrete.ml.torch.compile import compile_torch_model
from ..core.transforms import dct2, idct2
from ..config import FHE_CONFIG

def measure_execution_time(func):
    """Measure execution time of a function."""
    start = time.time()
    result = func()
    end = time.time()
    return result, end - start

def process_image_fhe(flat_input, output_shape, model, model_dir=None):
    """Process image through FHE pipeline."""
    model_dir = model_dir or FHE_CONFIG["model_dir"]
    os.makedirs(model_dir, exist_ok=True)
    
    print("Compiling the FHE model with enhanced precision...")
    config = Configuration(
        dump_artifacts_on_unexpected_failures=False,
        enable_unsafe_features=True,
        use_insecure_key_cache=True,
        insecure_key_cache_location=Path(model_dir) / "keycache"
    )
    
    # Compile model
    quant_module, comp_time = measure_execution_time(
        lambda: compile_torch_model(
            model, 
            flat_input,
            configuration=config,
            n_bits=FHE_CONFIG["n_bits"],
            rounding_threshold_bits=FHE_CONFIG["rounding_threshold"],
            p_error=FHE_CONFIG["p_error"],
            verbose=True
        )
    )
    print(f"FHE model compilation took {comp_time:.2f} seconds")
    
    # Generate keys
    _, keygen_time = measure_execution_time(
        lambda: quant_module.fhe_circuit.keygen(force=True)
    )
    print(f"Key generation took {keygen_time:.2f} seconds")
    
    # Forward pass
    output, forward_time = measure_execution_time(
        lambda: quant_module.forward(flat_input.numpy(), fhe="execute")
    )
    print(f"FHE forward call took {forward_time:.4f} seconds")
    
    # Reshape and denormalize
    output = output.reshape(output_shape)
    return idct2(output)  # Return the inverse DCT of the output
