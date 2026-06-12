"""TransformModule ABC 的单元测试。"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from transform_core.module import TransformModule
from transform_core.config import TransformConfig


def test_transform_module_abc_can_be_inherited():
    """验证 ABC 可被继承。"""

    class DummyModule(TransformModule):
        @property
        def name(self) -> str:
            return "dummy"

        def apply(self, img, config, rng):
            return img

    m = DummyModule()
    assert m.name == "dummy"
    assert isinstance(m, TransformModule)


def test_transform_module_apply_signature():
    """验证 apply 签名接受 (img, config, rng) 并返回 Image。"""
    cfg = TransformConfig(input_path="in.jpg", output_path="out.jpg")
    rng = np.random.default_rng(42)
    img = Image.new("RGB", (10, 10), color="red")

    class DummyModule(TransformModule):
        @property
        def name(self) -> str:
            return "dummy"

        def apply(self, img, config, rng):
            return img.convert("RGB")

    m = DummyModule()
    result = m.apply(img, cfg, rng)
    assert isinstance(result, Image.Image)
    assert result.mode == "RGB"
