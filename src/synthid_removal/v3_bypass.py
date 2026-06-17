"""V3 Bypass 策略 - Multi-resolution Spectral Subtraction。"""

import numpy as np
from PIL import Image

from transform_core.module import TransformModule
from transform_core.config import TransformConfig

from .spectral_codebook import SpectralCodebook


class SynthIDRemovalModule(TransformModule):
    """SynthID 水印移除模块（V3 策略）。"""

    def __init__(self, codebook_path: str | None = None):
        self.codebook = None
        if codebook_path:
            self.codebook = SpectralCodebook.load(codebook_path)

    @property
    def name(self) -> str:
        return "watermark"

    def _fft_subtract(self, channel: np.ndarray, profile: dict) -> np.ndarray:
        """V3 Bypass：基于 codebook 的多分辨率相位相干频谱减法。

        如果 profile 包含 carriers/magnitudes/phases，则进行针对性减法；
        否则回退到全局衰减。
        """
        f = np.fft.fft2(channel)
        fshift = np.fft.fftshift(f)
        magnitude = np.abs(fshift)
        phase = np.angle(fshift)

        if profile and "carriers" in profile:
            # 真实减法逻辑（简化版）
            carriers = profile.get("carriers", [])
            phases = profile.get("phases", [])

            h, w = magnitude.shape
            for i, (x, y) in enumerate(carriers):
                if 0 <= x < w and 0 <= y < h:
                    # 计算相位相干度
                    coherence = np.cos(phase[y, x] - phases[i]) if i < len(phases) else 0.0
                    # 相位相干时减去更多能量
                    reduction = 0.8 if coherence > 0.5 else 0.3
                    magnitude[y, x] *= 1 - reduction
        else:
            # 回退：全局衰减
            magnitude *= 0.7

        f_ishift = np.fft.ifftshift(magnitude * np.exp(1j * phase))
        img_back = np.fft.ifft2(f_ishift)
        return np.real(img_back)

    def apply(
        self,
        img: Image.Image,
        config: TransformConfig,
        rng: np.random.Generator,
    ) -> Image.Image:
        if not getattr(config, "watermark_remove", False):
            return img.convert("RGB")

        arr = np.array(img.convert("RGB"), dtype=np.float32)
        result = np.zeros_like(arr)

        # 自动匹配 profile（如果 codebook 存在）
        profile = None
        if self.codebook:
            h, w = arr.shape[:2]
            res = self.codebook.auto_match((h, w))
            if res:
                profile = self.codebook.get_profile(res)

        for c in range(3):
            result[:, :, c] = self._fft_subtract(arr[:, :, c], profile or {})

        result = np.clip(result, 0, 255).astype(np.uint8)
        return Image.fromarray(result, "RGB")


# 自动注册到 transform_core
try:
    from transform_core.registry import register_module

    register_module(SynthIDRemovalModule())
except Exception:
    pass  # 允许独立导入
