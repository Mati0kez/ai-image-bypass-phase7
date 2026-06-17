"""Contract Test：验证 DetectorInterface 签名和 Adapter 一致性。"""

import sys
from pathlib import Path

# 确保 src 可被导入
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from detector_loop.detector_interface import DetectorInterface
from detector_loop.adapters.local_adapter import LocalDetectorAdapter
from detector_loop.adapters.remote_adapter import HiveAPIDetectorAdapter
from PIL import Image
import numpy as np


def test_detector_interface_signature():
    """验证 DetectorInterface 抽象方法签名。"""
    assert hasattr(DetectorInterface, "name")
    assert hasattr(DetectorInterface, "score")


def test_local_adapter_implements_interface():
    """验证 LocalDetectorAdapter 实现接口。"""
    adapter = LocalDetectorAdapter(model_name="resnet50")
    assert isinstance(adapter, DetectorInterface)
    assert adapter.name.startswith("local:")


def test_remote_adapter_implements_interface():
    """验证 HiveAPIDetectorAdapter 实现接口。"""
    adapter = HiveAPIDetectorAdapter()
    assert isinstance(adapter, DetectorInterface)
    assert adapter.name == "remote:hive"


def test_adapter_score_returns_float():
    """验证 score 方法返回 float。"""
    img = Image.fromarray(np.zeros((64, 64, 3), dtype=np.uint8))
    adapter = LocalDetectorAdapter()
    score = adapter.score(img)
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0
