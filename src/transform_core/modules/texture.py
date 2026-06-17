"""Texture 方法族 Module。

包含皮肤区域噪声注入和 GLCM/LBP 纹理增强。
"""

from __future__ import annotations

import numpy as np
from PIL import Image
from typing import TYPE_CHECKING

from ..module import TransformModule
from ..registry import register_module

if TYPE_CHECKING:
    from ..config import TransformConfig


class TextureModule(TransformModule):
    """纹理与局部统计整形模块。"""

    @property
    def name(self) -> str:
        return "texture"

    def apply(
        self,
        img: Image.Image,
        config: "TransformConfig",  # type: ignore[name-defined]
        rng: np.random.Generator,
    ) -> Image.Image:
        # 延迟导入以避免循环依赖
        from bypass_ai_detector import (
            _to_array,
            _from_array,
            glcm_texture_enhance,
        )

        img_np = _to_array(img)

        # skin_noise（对应 skin_strength）
        skin_strength = getattr(config, "skin_strength", None)
        if skin_strength is None:
            skin_strength = 0.75
        skin_noise = rng.normal(0, 20, img_np.shape[:2]).astype(np.float32)
        skin_noise = np.repeat(skin_noise[:, :, None], 3, axis=2)
        img = _from_array(img_np + skin_noise * max(skin_strength, 0.0) * 0.25)

        # glcm_texture_enhance
        glcm_strength = getattr(config, "glcm_strength", None)
        if glcm_strength is None:
            glcm_strength = 0.6
        return glcm_texture_enhance(img, glcm_strength, seed=config.seed)


# import-time 自动注册
register_module(TextureModule())
