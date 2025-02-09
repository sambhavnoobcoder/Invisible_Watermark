"""FHE model definitions."""

import torch
import torch.nn as nn
from concrete.ml.torch.compile import compile_torch_model
from invisible_watermark.config import FHE_CONFIG

class IdentityNet(nn.Module):
    """Simple identity network as one linear layer."""
    def __init__(self, input_size):
        super(IdentityNet, self).__init__()
        self.fc = nn.Linear(input_size, input_size)
        with torch.no_grad():
            self.fc.weight.copy_(torch.eye(input_size))
            self.fc.bias.zero_()
            
    def forward(self, x):
        return self.fc(x)
