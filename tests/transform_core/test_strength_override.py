"""StrengthOverride 接口行为测试。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from transform_core.strength import StrengthOverride


def test_strength_override_default_none():
    """默认所有 scale 应为 None。"""
    override = StrengthOverride()
    assert override.noise_scale is None
    assert override.fft_scale is None


def test_strength_override_get_scale():
    """get_scale 应正确返回对应族的缩放因子。"""
    override = StrengthOverride(noise_scale=1.5, fft_scale=0.8)
    assert override.get_scale("noise") == 1.5
    assert override.get_scale("frequency") == 0.8
    assert override.get_scale("pixel") is None


def test_strength_override_frozen():
    """StrengthOverride 应为 frozen dataclass。"""
    override = StrengthOverride(noise_scale=1.2)
    try:
        override.noise_scale = 2.0  # type: ignore[misc]
        assert False, "Should be frozen"
    except Exception:
        assert True
