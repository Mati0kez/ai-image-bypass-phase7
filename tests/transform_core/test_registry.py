"""Registry 和 Module 注册的单元测试。"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from transform_core.registry import (
    TRANSFORM_MODULES,
    _selected_modules,
    METHOD_FAMILIES,
    PROFILE_METHODS,
)


def test_core_method_families_registered():
    """验证 METHOD_FAMILIES 中的核心 + 实验性方法族均已注册。"""
    # 7 核心 + lpips/watermark/regeneration
    assert len(METHOD_FAMILIES) >= 7
    assert set(METHOD_FAMILIES).issubset(TRANSFORM_MODULES.keys())


def test_selected_modules_full():
    """验证 profile='full' 返回全部方法族。"""
    selected = _selected_modules("full")
    assert selected == METHOD_FAMILIES


def test_selected_modules_quick():
    """验证 quick profile。"""
    selected = _selected_modules("quick")
    assert selected == PROFILE_METHODS["quick"]


def test_selected_modules_custom():
    """验证自定义 methods 参数。"""
    selected = _selected_modules("full", methods="noise,frequency")
    assert selected == ("noise", "frequency")


def test_unknown_method_raises():
    """验证未知方法族抛出 ValueError。"""
    with pytest.raises(ValueError):
        _selected_modules("full", methods="unknown")


def test_adversarial_profile():
    """验证 adversarial profile 包含 lpips/watermark/regeneration。"""
    selected = _selected_modules("adversarial")
    assert "lpips" in selected
    assert "watermark" in selected
    assert "regeneration" in selected
    assert len(selected) == 9
