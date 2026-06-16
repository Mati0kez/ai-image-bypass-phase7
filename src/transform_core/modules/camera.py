"""Camera 方法族 Module。

相机管线模拟（暗角、色差、噪声、hot pixels、banding、bayer）+ 多轮 JPEG + 屏幕/镜头 artifact。
"""

from __future__ import annotations

import numpy as np
from PIL import Image, ImageFilter

from ..module import TransformModule
from ..registry import register_module


class CameraModule(TransformModule):
    """相机/重拍模拟模块。"""

    @property
    def name(self) -> str:
        return "camera"

    def apply(
        self,
        img: Image.Image,
        config: "TransformConfig",  # type: ignore[name-defined]
        rng: np.random.Generator,
    ) -> Image.Image:
        # 延迟导入以避免循环依赖
        from bypass_ai_detector import (
            add_camera_pipeline,
            multi_jpeg_simulation,
        )

        camera_sim = getattr(config, "camera_sim", {})

        # 基础相机管线
        img = add_camera_pipeline(img, seed=config.seed)

        # 新增：Bayer + Demosaic 模拟
        if camera_sim.get("bayer_demosaic", False):
            img = self._apply_bayer_demosaic(img, rng)

        # 新增：屏幕摩尔纹
        if camera_sim.get("moire_pattern", False):
            img = self._apply_moire_pattern(img, rng)

        # 新增：镜头畸变
        if camera_sim.get("lens_distortion", False):
            img = self._apply_lens_distortion(img, rng)

        # 新增：运动模糊（如果未在基础管线中充分实现）
        if camera_sim.get("motion_blur", False):
            img = img.filter(ImageFilter.GaussianBlur(radius=1.5))

        quality = getattr(config, "quality", 85)
        return multi_jpeg_simulation(img, rounds=2, base_quality=quality)

    def _apply_bayer_demosaic(self, img: Image.Image, rng: np.random.Generator) -> Image.Image:
        """模拟 Bayer 滤波 + 简单 demosaic 插值。"""
        arr = np.array(img.convert("RGB")).astype(np.float32)
        h, w, _ = arr.shape

        # 简化 Bayer 模式 (RGGB)
        bayer = np.zeros_like(arr)
        bayer[0::2, 0::2, 0] = arr[0::2, 0::2, 0]  # R
        bayer[0::2, 1::2, 1] = arr[0::2, 1::2, 1]  # G
        bayer[1::2, 0::2, 1] = arr[1::2, 0::2, 1]  # G
        bayer[1::2, 1::2, 2] = arr[1::2, 1::2, 2]  # B

        # 简单双线性 demosaic（实际更复杂）
        result = bayer.copy()
        # 对 G 通道简单平均
        result[0::2, 0::2, 1] = (arr[0::2, 0::2, 1] + arr[0::2, 1::2, 1]) / 2
        result[1::2, 1::2, 1] = (arr[1::2, 1::2, 1] + arr[1::2, 0::2, 1]) / 2

        return Image.fromarray(np.clip(result, 0, 255).astype(np.uint8), "RGB")

    def _apply_moire_pattern(self, img: Image.Image, rng: np.random.Generator) -> Image.Image:
        """添加屏幕摩尔纹（简化正弦波叠加）。"""
        arr = np.array(img.convert("RGB")).astype(np.float32)
        h, w, _ = arr.shape
        y, x = np.meshgrid(np.arange(h), np.arange(w), indexing="ij")
        moire = (np.sin(x * 0.3) + np.sin(y * 0.3)) * 5
        arr[..., 0] = np.clip(arr[..., 0] + moire, 0, 255)
        return Image.fromarray(arr.astype(np.uint8), "RGB")

    def _apply_lens_distortion(self, img: Image.Image, rng: np.random.Generator) -> Image.Image:
        """简单桶形畸变模拟。"""
        # 使用 PIL 的 Image.transform 实现简单畸变（占位）
        # 真实实现应使用 OpenCV 或 scipy.ndimage.map_coordinates
        return img  # 占位：当前版本保持不变


# import-time 自动注册
register_module(CameraModule())
