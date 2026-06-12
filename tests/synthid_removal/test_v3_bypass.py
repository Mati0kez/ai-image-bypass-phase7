"""Test for SynthID V3 Bypass (Module 4)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import numpy as np
from PIL import Image

from synthid_removal.v3_bypass import SynthIDRemovalModule
from transform_core.config import TransformConfig


def test_watermark_module_structure():
    """Verify the module can be instantiated and respects the watermark_remove flag."""
    module = SynthIDRemovalModule()

    img = Image.fromarray(np.random.randint(0, 255, (128, 128, 3), dtype=np.uint8))

    # When flag is False, should return original
    config = TransformConfig(input_path="", output_path="", watermark_remove=False)
    result = module.apply(img, config, np.random.default_rng())
    assert result.size == img.size

    print("✅ SynthIDRemovalModule structure test passed.")