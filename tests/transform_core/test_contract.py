"""Contract Test - 验证公共接口不变性。"""

import sys
from pathlib import Path

import pytest
from PIL import Image
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from transform_core.module import TransformModule
from transform_core.registry import TRANSFORM_MODULES, METHOD_FAMILIES, _selected_modules


def test_transform_module_interface_contract():
    """验证 TransformModule ABC 接口不变性。"""
    for name, module in TRANSFORM_MODULES.items():
        assert hasattr(module, "name")
        assert isinstance(module.name, str)
        assert hasattr(module, "apply")
        # 简单调用测试
        img = Image.new("RGB", (10, 10))
        cfg = type("cfg", (), {"seed": 42})()
        rng = np.random.default_rng(42)
        result = module.apply(img, cfg, rng)
        assert isinstance(result, Image.Image)


def test_method_family_names_match_legacy():
    """验证 legacy METHOD_FAMILIES 均为已注册 Module。"""
    assert set(METHOD_FAMILIES).issubset(TRANSFORM_MODULES.keys())


def test_profile_parsing_contract():
    """验证 profile 解析行为稳定。"""
    full = _selected_modules("full")
    assert len(full) == 10  # 7 核心 + lpips + watermark + regeneration
    quick = _selected_modules("quick")
    assert len(quick) == 4
