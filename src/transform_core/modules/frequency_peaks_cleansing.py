"""Frequency Peaks Cleansing 方法族 Module。

在频域 (DCT/FFT) 中识别并抑制代表上采样伪影的特定频率峰值。
"""

from __future__ import annotations

import numpy as np
from PIL import Image
from typing import Optional, TYPE_CHECKING

from ..module import TransformModule
from ..registry import register_module

if TYPE_CHECKING:
    from ..config import TransformConfig
    from ..strength import StrengthOverride


class FrequencyPeaksCleansingModule(TransformModule):
    """频谱峰值清洗模块（GAN Fingerprint / Frequency Analysis 专用）。"""

    @property
    def name(self) -> str:
        return "frequency_peaks_cleansing"

    def apply(
        self,
        img: Image.Image,
        config: "TransformConfig",
        rng: np.random.Generator,
        strength_override: Optional["StrengthOverride"] = None,
    ) -> Image.Image:
        enabled = getattr(config, "frequency_peaks_cleansing_enabled", False)
        if not enabled:
            return img.convert("RGB")

        domain = getattr(config, "frequency_peaks_cleansing_domain", "dct")
        threshold = getattr(config, "frequency_peaks_cleansing_threshold", 0.5)
        strategy = getattr(config, "frequency_peaks_cleansing_replacement_strategy", "zeroing")

        return self._apply_local(img, config, domain, threshold, strategy)

    def _apply_local(self, img: Image.Image, config: "TransformConfig", domain: str, threshold: float, strategy: str) -> Image.Image:
        """本地频域峰值清洗实现。"""
        try:
            from scipy.fftpack import dct, idct
        except ImportError:
            print("[FrequencyPeaksCleansingModule] scipy 未安装，回退 surrogate")
            return self._apply_surrogate(img, config)

        arr = np.array(img.convert("RGB")).astype(np.float32)
        result_channels = []

        for c in range(3):
            channel = arr[:, :, c]
            
            # 1. 转换到频域
            if domain == "dct":
                # DCT 通常在 8x8 块上计算，但为简化，我们计算全局 DCT
                # 注意：实际 GAN 指纹通常在块级 DCT 中
                freq = dct(dct(channel, axis=0, norm='ortho'), axis=1, norm='ortho')
            else: # fft
                freq = np.fft.fft2(channel)
                freq = np.fft.fftshift(freq)

            # 2. 对数缩放与峰值识别
            log_spectrum = np.log(np.abs(freq) + 1e-8)
            mean_spectrum = np.mean(log_spectrum)
            
            # 识别峰值：高于均值 + 阈值
            # 这里简化处理，实际可能需要更复杂的峰值检测算法
            mask = log_spectrum > (mean_spectrum + threshold)

            # 3. 峰值抑制
            if strategy == "zeroing":
                freq[mask] = 0
            else: # noise_injection
                # 注入小幅噪声
                noise = rng.normal(0, 1, size=freq.shape) * np.abs(freq[mask]) * 0.1  # noqa: F821
                freq[mask] = freq[mask] + noise

            # 4. 转换回空间域
            if domain == "dct":
                cleaned_channel = idct(idct(freq, axis=0, norm='ortho'), axis=1, norm='ortho')
            else:
                cleaned_channel = np.fft.ifftshift(freq)
                cleaned_channel = np.fft.ifft2(cleaned_channel)
                cleaned_channel = np.real(cleaned_channel)

            result_channels.append(cleaned_channel)

        result_arr = np.stack(result_channels, axis=2)
        result_arr = np.clip(result_arr, 0, 255).astype(np.uint8)
        
        return Image.fromarray(result_arr, "RGB")

    def _apply_surrogate(self, img: Image.Image, config: "TransformConfig") -> Image.Image:
        """代理模式（占位实现）。"""
        print("[FrequencyPeaksCleansingModule] surrogate 模式（占位），返回原图")
        return img.convert("RGB")


# import-time 自动注册
register_module(FrequencyPeaksCleansingModule())