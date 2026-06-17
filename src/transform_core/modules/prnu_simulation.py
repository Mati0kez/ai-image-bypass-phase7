"""PRNU Simulation / Removal 方法族 Module。

实现 PRNU 指纹模拟（叠加）与移除功能。
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
    from scipy.ndimage import gaussian_filter

    _SCIPY_AVAILABLE = True
except ImportError:
    _SCIPY_AVAILABLE = False


class PRNUSimulationModule(TransformModule):
    """PRNU 传感器指纹模拟/移除模块。"""

    @property
    def name(self) -> str:
        return "prnu_simulation"

    def apply(
        self,
        img: Image.Image,
        config: "TransformConfig",
        rng: np.random.Generator,
        strength_override: Optional["StrengthOverride"] = None,
    ) -> Image.Image:
        enabled = getattr(config, "prnu_simulation_enabled", False)
        if not enabled:
            return img.convert("RGB")

        mode = getattr(config, "prnu_simulation_mode", "extract_add")
        if mode == "extract_add":
            return self._apply_extract_add(img, config)
        else:
            return self._apply_remove(img, config)

    def _apply_extract_add(self, img: Image.Image, config: "TransformConfig") -> Image.Image:
        """从参考图像提取 PRNU 指纹并叠加。"""
        if not _SCIPY_AVAILABLE:
            print("[PRNUSimulationModule] scipy 未安装，回退 surrogate")
            return self._apply_surrogate(img, config)

        ref_path = getattr(config, "prnu_simulation_reference_path", None)
        strength = getattr(config, "prnu_simulation_strength", 0.5)

        if not ref_path:
            print("[PRNUSimulationModule] 未指定 reference_path，回退 surrogate")
            return self._apply_surrogate(img, config)

        try:
            ref_img = Image.open(ref_path).convert("RGB")
        except Exception as e:
            print(f"[PRNUSimulationModule] 参考图像加载失败: {e}")
            return self._apply_surrogate(img, config)

        # 简化的 PRNU 提取：使用高斯滤波残差作为指纹估计
        # 实际 PRNU 提取通常使用小波去噪
        target_arr = np.array(img).astype(np.float32)
        ref_arr = np.array(ref_img.resize(img.size)).astype(np.float32)

        # 提取指纹 (简化为残差)
        # 注意：真实 PRNU 需要多张图像平均
        fingerprint = ref_arr - gaussian_filter(ref_arr, sigma=5)

        # 叠加指纹
        result_arr = target_arr + fingerprint * strength
        result_arr = np.clip(result_arr, 0, 255).astype(np.uint8)

        return Image.fromarray(result_arr, "RGB")

    def _apply_remove(self, img: Image.Image, config: "TransformConfig") -> Image.Image:
        """移除或混淆 PRNU 指纹。"""
        if not _SCIPY_AVAILABLE:
            print("[PRNUSimulationModule] scipy 未安装，回退 surrogate")
            return self._apply_surrogate(img, config)

        # 简化的移除：对图像进行轻微模糊以破坏指纹
        arr = np.array(img).astype(np.float32)
        result_arr = gaussian_filter(arr, sigma=1.0)
        result_arr = np.clip(result_arr, 0, 255).astype(np.uint8)

        return Image.fromarray(result_arr, "RGB")

    def _apply_surrogate(self, img: Image.Image, config: "TransformConfig") -> Image.Image:
        """自生成指纹代理模式（无 reference image 时使用）。"""
        if not _SCIPY_AVAILABLE:
            print("[PRNUSimulationModule] scipy 未安装，回退原图")
            return img.convert("RGB")

        print("[PRNUSimulationModule] surrogate 模式：使用输入图像自身生成模拟 PRNU 指纹")
        strength = getattr(config, "prnu_simulation_strength", 0.5)

        arr = np.array(img).astype(np.float32)
        # 使用高斯高通残差作为模拟指纹
        low_pass = gaussian_filter(arr, sigma=5)
        fingerprint = arr - low_pass

        result_arr = arr + fingerprint * strength
        result_arr = np.clip(result_arr, 0, 255).astype(np.uint8)
        return Image.fromarray(result_arr, "RGB")


# import-time 自动注册
register_module(PRNUSimulationModule())
