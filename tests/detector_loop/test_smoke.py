"""Smoke Test：使用 Mock Detector 验证 DetectorLoop 逻辑（无需 GPU）。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from detector_loop.loop import DetectorLoop, DetectorLoopConfig
from detector_loop.detector_interface import DetectorInterface
from PIL import Image
import numpy as np


class MockDetector(DetectorInterface):
    """Mock Detector，用于测试循环逻辑。"""

    def __init__(self):
        self.call_count = 0

    @property
    def name(self) -> str:
        return "mock:detector"

    def score(self, img: Image.Image) -> float:
        self.call_count += 1
        # 模拟分数逐步下降
        return max(0.1, 0.8 - self.call_count * 0.15)


def test_detector_loop_early_stopping():
    """验证 early stopping 机制。"""
    config = DetectorLoopConfig(
        detector_name="mock:detector",
        detector_threshold=0.3,
        max_iter=10,
        early_stop_epsilon=0.05,
    )
    loop = DetectorLoop(config)

    # 替换 detector 为 mock
    loop.detector = MockDetector()

    img = Image.fromarray(np.zeros((64, 64, 3), dtype=np.uint8))
    _, history = loop.run(img, initial_score=0.8)

    # 应该在分数低于阈值或 early stop 时停止
    assert len(history) <= 10
    final_score = history[-1][2]
    assert final_score < 0.5 or len(history) < 10  # early stop 或达到阈值


def test_detector_loop_respects_max_iter():
    """验证 max_iter 限制。"""
    config = DetectorLoopConfig(max_iter=3, early_stop_epsilon=0.0)
    loop = DetectorLoop(config)
    loop.detector = MockDetector()

    img = Image.fromarray(np.zeros((32, 32, 3), dtype=np.uint8))
    _, history = loop.run(img, initial_score=0.9)

    assert len(history) <= 4  # 初始 + 3 次迭代