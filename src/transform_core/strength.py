"""StrengthOverride - 动态强度调整数据契约。

用于 Detector-in-the-Loop 闭环中，根据 detector 分数差距
动态缩放各方法族的变换强度。
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class StrengthOverride:
    """强度覆盖对象。

    各字段为可选缩放因子（1.0 表示不变，>1.0 增强，<1.0 减弱）。
    None 表示不覆盖该族强度。
    """

    noise_scale: Optional[float] = None
    fft_scale: Optional[float] = None
    pixel_scale: Optional[float] = None
    glcm_scale: Optional[float] = None
    skin_scale: Optional[float] = None
    camera_scale: Optional[float] = None
    lpips_scale: Optional[float] = None
    watermark_scale: Optional[float] = None
    regeneration_scale: Optional[float] = None

    def get_scale(self, family: str) -> Optional[float]:
        """根据方法族名称返回对应的缩放因子。"""
        mapping = {
            "noise": self.noise_scale,
            "frequency": self.fft_scale,
            "pixel": self.pixel_scale,
            "texture": self.glcm_scale,
            "skin": self.skin_scale,
            "camera": self.camera_scale,
            "lpips": self.lpips_scale,
            "watermark": self.watermark_scale,
            "regeneration": self.regeneration_scale,
        }
        return mapping.get(family)
