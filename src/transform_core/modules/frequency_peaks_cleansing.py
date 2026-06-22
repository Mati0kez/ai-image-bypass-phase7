"""Frequency Peaks Cleansing 方法族 Module。

在 8x8 DCT 块或 FFT 高频区域中识别并抑制 GAN 上采样伪影峰值。
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

_BLOCK = 8


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
        threshold = getattr(config, "frequency_peaks_cleansing_threshold", 2.0)
        strategy = getattr(config, "frequency_peaks_cleansing_replacement_strategy", "attenuate")
        attenuation = getattr(config, "frequency_peaks_cleansing_attenuation", 0.35)

        try:
            if domain == "dct":
                return self._apply_block_dct(img, threshold, strategy, attenuation, rng)
            return self._apply_fft_peaks(img, threshold, attenuation, rng)
        except ImportError:
            print("[FrequencyPeaksCleansingModule] scipy 未安装，回退 surrogate")
            return self._apply_surrogate(img, config)

    def _apply_block_dct(
        self,
        img: Image.Image,
        threshold: float,
        strategy: str,
        attenuation: float,
        rng: np.random.Generator,
    ) -> Image.Image:
        """8x8 块 DCT 峰值清洗（JPEG 风格，保护 DC 与低频）。"""
        from scipy.fftpack import dct, idct

        arr = np.array(img.convert("RGB")).astype(np.float32)
        h, w, _ = arr.shape
        pad_h = ( _BLOCK - h % _BLOCK) % _BLOCK
        pad_w = (_BLOCK - w % _BLOCK) % _BLOCK
        if pad_h or pad_w:
            arr = np.pad(arr, ((0, pad_h), (0, pad_w), (0, 0)), mode="reflect")

        out = np.zeros_like(arr)
        ph, pw, _ = arr.shape

        u_idx, v_idx = np.meshgrid(np.arange(_BLOCK), np.arange(_BLOCK), indexing="ij")
        hf_mask_8 = (u_idx + v_idx) >= 4

        for c in range(3):
            channel_out = np.zeros((ph, pw), dtype=np.float32)
            channel = arr[:, :, c]
            for y in range(0, ph, _BLOCK):
                for x in range(0, pw, _BLOCK):
                    block = channel[y : y + _BLOCK, x : x + _BLOCK]
                    dct_block = dct(dct(block, axis=0, norm="ortho"), axis=1, norm="ortho")

                    ac_mag = np.abs(dct_block)
                    ac_hf = ac_mag[hf_mask_8]
                    if ac_hf.size == 0:
                        cleaned = block
                    else:
                        mean_hf = float(np.mean(ac_hf))
                        std_hf = float(np.std(ac_hf)) + 1e-8
                        peak_mask = np.zeros((_BLOCK, _BLOCK), dtype=bool)
                        peak_mask[hf_mask_8] = ac_mag[hf_mask_8] > (mean_hf + threshold * std_hf)

                        if strategy == "zeroing":
                            dct_block[peak_mask] *= 0.15
                        elif strategy == "noise_injection":
                            noise = rng.normal(0, 1, size=dct_block.shape)
                            dct_block[peak_mask] += noise[peak_mask] * ac_mag[peak_mask] * attenuation * 0.05
                        else:  # attenuate
                            dct_block[peak_mask] *= max(0.0, 1.0 - attenuation)

                        cleaned = idct(idct(dct_block, axis=0, norm="ortho"), axis=1, norm="ortho")

                    channel_out[y : y + _BLOCK, x : x + _BLOCK] = cleaned
            out[:, :, c] = channel_out

        out = out[:h, :w, :]
        out = np.clip(out, 0, 255).astype(np.uint8)
        return Image.fromarray(out, "RGB")

    def _apply_fft_peaks(
        self,
        img: Image.Image,
        threshold: float,
        attenuation: float,
        rng: np.random.Generator,
    ) -> Image.Image:
        """FFT 高频峰值衰减（仅处理中高频，保护低频内容）。"""
        arr = np.array(img.convert("RGB")).astype(np.float32)
        rows, cols = arr.shape[:2]
        y_grid, x_grid = np.ogrid[:rows, :cols]
        cy, cx = rows // 2, cols // 2
        dist = np.sqrt((y_grid - cy) ** 2 + (x_grid - cx) ** 2)
        dist_norm = dist / max(float(dist.max()), 1.0)
        low_freq = dist_norm < 0.12
        mid_high = (~low_freq) & (dist_norm < 0.85)

        result = arr.copy()
        for c in range(3):
            channel = arr[:, :, c]
            shifted = np.fft.fftshift(np.fft.fft2(channel))
            magnitude = np.abs(shifted)
            phase = np.angle(shifted)
            log_mag = np.log(magnitude + 1e-8)
            region = log_mag[mid_high]
            if region.size == 0:
                continue
            peak_mask = np.zeros_like(magnitude, dtype=bool)
            peak_mask[mid_high] = log_mag[mid_high] > (
                float(np.mean(region)) + threshold * float(np.std(region))
            )
            magnitude[peak_mask] *= max(0.0, 1.0 - attenuation)
            rebuilt = magnitude * np.exp(1j * phase)
            result[:, :, c] = np.real(np.fft.ifft2(np.fft.ifftshift(rebuilt)))

        result = np.clip(result, 0, 255).astype(np.uint8)
        return Image.fromarray(result, "RGB")

    def _apply_surrogate(self, img: Image.Image, config: "TransformConfig") -> Image.Image:
        """代理模式：轻量 FFT 高频整形。"""
        rng = np.random.default_rng(getattr(config, "seed", None))
        return self._apply_fft_peaks(img, threshold=2.0, attenuation=0.25, rng=rng)


register_module(FrequencyPeaksCleansingModule())
