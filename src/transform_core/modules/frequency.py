"""Frequency 方法族 Module。

FFT 频域扰动与相位噪声注入。
"""

from __future__ import annotations

import numpy as np
from PIL import Image
from typing import TYPE_CHECKING

from ..module import TransformModule
from ..registry import register_module

if TYPE_CHECKING:
    from ..config import TransformConfig


class FrequencyModule(TransformModule):
    """FFT 频域变换模块。"""

    @property
    def name(self) -> str:
        return "frequency"

    def apply(
        self,
        img: Image.Image,
        config: "TransformConfig",  # type: ignore[name-defined]
        rng: np.random.Generator,
    ) -> Image.Image:
        # 延迟导入以避免循环依赖
        from bypass_ai_detector import fft_perturb

        fft_strength = getattr(config, "fft_strength", None)
        if fft_strength is None:
            fft_strength = 0.48
        return fft_perturb(img, strength=fft_strength, seed=config.seed)


# import-time 自动注册
register_module(FrequencyModule())
