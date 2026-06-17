"""Encoding 方法族 Module。

包含 JPEG、裁剪、resize、模糊/锐化、颜色/白平衡等几何与编码变换。
"""

from __future__ import annotations

import numpy as np
from PIL import Image
from typing import TYPE_CHECKING

from ..module import TransformModule
from ..registry import register_module

if TYPE_CHECKING:
    from ..config import TransformConfig


class EncodingModule(TransformModule):
    """编码与几何变换模块。"""

    @property
    def name(self) -> str:
        return "encoding"

    def apply(
        self,
        img: Image.Image,
        config: "TransformConfig",  # type: ignore[name-defined]
        rng: np.random.Generator,
    ) -> Image.Image:
        # 延迟导入以避免循环依赖
        from bypass_ai_detector import add_encoding_geometric_transforms

        # encoding 族使用 config.quality
        quality = getattr(config, "quality", 88)
        return add_encoding_geometric_transforms(img, quality=quality)


# import-time 自动注册
register_module(EncodingModule())
