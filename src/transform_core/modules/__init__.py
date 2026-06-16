"""Transform Modules - 各方法族的 TransformModule 实现。

此包在 import 时自动注册所有 Module 到全局 registry。
"""

from . import (
    metadata,
    encoding,
    noise,
    frequency,
    texture,
    camera,
    regeneration_surrogate,
    regeneration,
    diffusion_reconstruction,
    frequency_peaks_cleansing,
    prnu_simulation,
    gradient_edge_aware_perturbation,
    transfer_blackbox_attack,
)

# 条件导入实验性对抗模块（torch 缺失时优雅降级）
try:
    from lpips_attack import LPIPSModule  # noqa: F401
except Exception:
    pass  # 无 torch 时跳过 lpips

try:
    from synthid_removal import v3_bypass  # noqa: F401
except Exception:
    pass  # 无 torch 或依赖缺失时跳过 watermark

__all__ = [
    "metadata",
    "encoding",
    "noise",
    "frequency",
    "texture",
    "camera",
    "regeneration_surrogate",
    "regeneration",
    "diffusion_reconstruction",
    "frequency_peaks_cleansing",
    "prnu_simulation",
    "gradient_edge_aware_perturbation",
    "transfer_blackbox_attack",
]
