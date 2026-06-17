"""Noise 方法族 Module。

包含高斯噪声注入和低幅度像素扰动。
"""

from __future__ import annotations

import numpy as np
from PIL import Image
from typing import TYPE_CHECKING

from ..module import TransformModule
from ..registry import register_module

if TYPE_CHECKING:
    from ..config import TransformConfig


class NoiseModule(TransformModule):
    """噪声与像素扰动模块。"""

    @property
    def name(self) -> str:
        return "noise"

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
            add_pixel_perturbation,
        )

        img_np = _to_array(img)

        # pixel perturbation
        pixel_strength = getattr(config, "pixel_strength", None)
        if pixel_strength is None:
            pixel_strength = 0.028
        img_np = add_pixel_perturbation(img_np, pixel_strength, seed=config.seed)

        # 高斯噪声
        img_np = img_np.astype(np.float32) / 255.0
        noise_strength = getattr(config, "noise_strength", None)
        if noise_strength is None:
            noise_strength = 0.8
        noise = rng.normal(0, noise_strength * 0.0095, img_np.shape)
        return _from_array((img_np + noise) * 255)


# import-time 自动注册
register_module(NoiseModule())
