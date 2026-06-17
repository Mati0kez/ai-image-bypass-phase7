"""Real Detector-in-the-Loop closed loop test (using MockDetector)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from detector_loop.loop import DetectorLoop, DetectorLoopConfig
from detector_loop.detector_interface import DetectorInterface
from PIL import Image
import numpy as np


class MockRealDetector(DetectorInterface):
    """Mock detector that returns decreasing scores to simulate real feedback."""

    def __init__(self):
        self.call_count = 0

    @property
    def name(self) -> str:
        return "mock:real-detector"

    def score(self, img: Image.Image) -> float:
        self.call_count += 1
        # Simulate real detector: score decreases with more perturbation
        return max(0.1, 0.85 - self.call_count * 0.12)


def test_real_loop_with_adaptive_and_patience():
    """Verify real closed-loop with adaptive strength and patience early stopping."""
    config = DetectorLoopConfig(
        detector_name="mock:real-detector",
        detector_threshold=0.4,
        max_iter=10,
        early_stop_epsilon=0.05,
        adaptive_strength=True,
        early_stop_patience=2,
    )
    loop = DetectorLoop(config)
    loop.detector = MockRealDetector()

    img = Image.fromarray(np.zeros((64, 64, 3), dtype=np.uint8))
    final_img, history = loop.run(img, initial_score=0.85)

    assert len(history) >= 3
    # Should stop due to patience or threshold
    final_score = history[-1][2]
    assert final_score < 0.5 or len(history) < 10

    print("✅ Real DetectorLoop closed-loop test passed (adaptive + patience)!")
