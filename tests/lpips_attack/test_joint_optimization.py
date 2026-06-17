"""Test for LPIPS + Detector joint optimization (Module 3)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import numpy as np
from PIL import Image

from lpips_attack.module import LPIPSModule
from transform_core.config import TransformConfig


class MockDetectorForLPIPS:
    """Mock detector that returns decreasing scores to simulate real feedback."""

    def __init__(self):
        self.call_count = 0

    def score(self, img: Image.Image) -> float:
        self.call_count += 1
        # Simulate that more perturbation lowers the AI score
        return max(0.1, 0.8 - self.call_count * 0.05)


def test_lpips_joint_optimization_structure():
    """Verify that LPIPSModule accepts a detector and runs without error."""
    # This test only checks the interface and graceful degradation when torch is missing.
    # Full gradient test requires torch + lpips installed.

    module = LPIPSModule(detector=MockDetectorForLPIPS())

    img = Image.fromarray(np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8))

    config = TransformConfig(
        input_path="",
        output_path="",
        lpips_enabled=True,
        detector_feedback=True,
        detector_weight=1.0,
        lpips_strength=0.01,
        lpips_steps=3,
    )

    # If torch is not installed, it should return the original image (graceful degradation)
    result = module.apply(img, config, np.random.default_rng())

    assert isinstance(result, Image.Image)
    print("✅ LPIPSModule joint optimization interface test passed (structure OK)")
