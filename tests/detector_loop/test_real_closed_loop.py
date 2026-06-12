"""真实 Detector-in-the-Loop 闭环测试（使用 Mock Detector）。"""

import sys
from pathlib import Path
from typing import Optional
from PIL import Image
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from detector_loop.detector_interface import DetectorInterface
from detector_loop.loop import DetectorLoop, DetectorLoopConfig
from transform_core.strength import StrengthOverride


class MockRealDetector(DetectorInterface):
    """确定性 mock detector：分数随调用次数递减。"""

    def __init__(self):
        self.call_count = 0
        self._scores = [0.85, 0.72, 0.61, 0.55, 0.48, 0.42]

    @property
    def name(self) -> str:
        return "mock:real"

    def score(self, img: Image.Image) -> float:
        idx = min(self.call_count, len(self._scores) - 1)
        self.call_count += 1
        return float(self._scores[idx])


def _dummy_transform(img: Image.Image, override: Optional[StrengthOverride] = None) -> Image.Image:
    """简单变换：添加轻微噪声模拟强度变化。"""
    arr = np.array(img).astype(np.float32)
    noise = np.random.randn(*arr.shape) * 0.5
    return Image.fromarray(np.clip(arr + noise, 0, 255).astype(np.uint8))


def test_real_closed_loop_updates_image_and_scores():
    """验证真实闭环：图像被迭代更新，分数来自真实 detector 调用。"""
    detector = MockRealDetector()
    loop = DetectorLoop(DetectorLoopConfig(max_iter=5, early_stop_patience=3))
    loop.detector = detector  # 注入 mock

    initial = Image.new("RGB", (32, 32), color=(128, 128, 128))
    final_img, history = loop.run(initial, transform_fn=_dummy_transform)

    assert len(history) >= 2
    # 验证分数是 detector 真实返回的（而非硬编码递减）
    scores = [h[2] for h in history]
    assert scores[0] == 0.85
    assert final_img is not initial  # 至少被变换过一次
