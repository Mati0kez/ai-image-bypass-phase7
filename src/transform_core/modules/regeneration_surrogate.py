"""Regeneration_surrogate 方法族 Module。

降采样/重建/滤波代理（不调用生成模型）。
"""

from __future__ import annotations

import numpy as np
from PIL import Image
from typing import TYPE_CHECKING

from ..module import TransformModule
from ..registry import register_module

if TYPE_CHECKING:
    from ..config import TransformConfig


class RegenerationSurrogateModule(TransformModule):
    """再生代理模块。"""

    @property
    def name(self) -> str:
        return "regeneration_surrogate"

    def apply(
        self,
        img: Image.Image,
        config: "TransformConfig",  # type: ignore[name-defined]
        rng: np.random.Generator,
    ) -> Image.Image:
        # 延迟导入以避免循环依赖
        from bypass_ai_detector import add_regeneration_surrogate

        # regeneration_surrogate 固定 strength=0.25（与 legacy 一致）
        return add_regeneration_surrogate(img, strength=0.25)


# import-time 自动注册
register_module(RegenerationSurrogateModule())
