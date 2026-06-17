"""Gradient/Edge-aware Perturbation 方法族 Module。

在进行像素或噪声扰动时，优先在边缘和纹理区域进行，以最大化对梯度特征的破坏。
"""

import numpy as np
from PIL import Image
from typing import Optional, TYPE_CHECKING

from ..module import TransformModule
from ..registry import register_module

if TYPE_CHECKING:
    from ..config import TransformConfig
    from ..strength import StrengthOverride

try:
    from scipy import ndimage

    _SCIPY_AVAILABLE = True
except ImportError:
    _SCIPY_AVAILABLE = False


class GradientEdgeAwarePerturbationModule(TransformModule):
    """梯度/边缘感知扰动模块（Gradient Analysis 专用）。"""

    @property
    def name(self) -> str:
        return "gradient_edge_aware_perturbation"

    def apply(
        self,
        img: Image.Image,
        config: "TransformConfig",
        rng: np.random.Generator,
        strength_override: Optional["StrengthOverride"] = None,
    ) -> Image.Image:
        enabled = getattr(config, "gradient_edge_aware_perturbation_enabled", False)
        if not enabled:
            return img.convert("RGB")

        edge_weight = getattr(config, "gradient_edge_aware_perturbation_edge_weight", 2.0)
        smooth_weight = getattr(config, "gradient_edge_aware_perturbation_smooth_weight", 0.5)

        return self._apply_local(img, config, edge_weight, smooth_weight, rng)

    def _apply_local(
        self,
        img: Image.Image,
        config: "TransformConfig",
        edge_weight: float,
        smooth_weight: float,
        rng: np.random.Generator,
    ) -> Image.Image:
        """本地边缘感知扰动实现。"""
        if not _SCIPY_AVAILABLE:
            print("[GradientEdgeAwarePerturbationModule] scipy 未安装，回退 surrogate")
            return self._apply_surrogate(img, config)

        arr = np.array(img.convert("RGB")).astype(np.float32)
        result_channels = []

        for c in range(3):
            channel = arr[:, :, c]

            # 1. 边缘检测 (Sobel)
            sobel_x = ndimage.sobel(channel, axis=0)
            sobel_y = ndimage.sobel(channel, axis=1)
            edge_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)

            # 归一化边缘权重
            edge_weight_map = edge_magnitude / (np.max(edge_magnitude) + 1e-8)

            # 2. 生成扰动
            # 边缘区域施加更高强度
            noise = rng.normal(0, 1, size=channel.shape)
            perturbation = noise * (smooth_weight + edge_weight_map * (edge_weight - smooth_weight))

            # 3. 应用扰动
            cleaned_channel = channel + perturbation * getattr(config, "pixel_strength", 0.01) * 255

            result_channels.append(cleaned_channel)

        result_arr = np.stack(result_channels, axis=2)
        result_arr = np.clip(result_arr, 0, 255).astype(np.uint8)

        return Image.fromarray(result_arr, "RGB")

    def _apply_surrogate(self, img: Image.Image, config: "TransformConfig") -> Image.Image:
        """代理模式（占位）。"""
        print("[GradientEdgeAwarePerturbationModule] surrogate 模式（占位），返回原图")
        return img.convert("RGB")


# import-time 自动注册
register_module(GradientEdgeAwarePerturbationModule())
