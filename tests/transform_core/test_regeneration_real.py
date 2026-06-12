"""Test for RegenerationModule (Module 5)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import numpy as np
from PIL import Image

from transform_core.modules.regeneration import RegenerationModule
from transform_core.config import TransformConfig


def test_regeneration_module_modes():
    """Verify the module can switch between modes and falls back gracefully."""
    module = RegenerationModule()
    img = Image.fromarray(np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8))

    # 1. Surrogate mode (default)
    config_surrogate = TransformConfig(input_path="", output_path="", regeneration_mode="surrogate")
    result = module.apply(img, config_surrogate, np.random.default_rng())
    assert isinstance(result, Image.Image)

    # 2. Local mode (should fallback if no torch)
    config_local = TransformConfig(input_path="", output_path="", regeneration_mode="local")
    result_local = module.apply(img, config_local, np.random.default_rng())
    assert isinstance(result_local, Image.Image)

    print("✅ RegenerationModule mode switching test passed.")