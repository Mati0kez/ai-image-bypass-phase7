"""TransformConfig - 图片处理流程的不可变配置对象。

收束所有方法族参数和扩展点，提供统一的数据契约。
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Literal, Optional

TransformProfile = Literal["quick", "full", "texture", "camera", "metadata", "adversarial"]
MetadataMode = Literal["copy", "strip", "synthetic"]


@dataclass(frozen=True)
class TransformConfig:
    """描述一次完整图片处理流程的配置。

    包含输入输出路径、profile 选择、各方法族强度参数、
    元数据模式以及未来扩展点（LPIPS、水印、detector 反馈）。
    """

    # 输入输出
    input_path: str
    output_path: str
    manifest_path: Optional[str] = None

    # 全局控制
    profile: TransformProfile = "full"
    seed: Optional[int] = None
    quality: int = 95

    # 各方法族强度（None 表示该族不启用）
    noise_strength: Optional[float] = None
    fft_strength: Optional[float] = None
    pixel_strength: Optional[float] = None
    glcm_strength: Optional[float] = None
    skin_strength: Optional[float] = None

    # 元数据
    metadata_mode: MetadataMode = "synthetic"
    real_photo_path: Optional[str] = None

    # 扩展点（未来模块使用）
    lpips_enabled: bool = False
    lpips_strength: float = 0.01
    lpips_steps: int = 10
    lpips_blackbox: bool = False  # 启用黑盒优化（SPSA 等），适合 detector_feedback=True
    lpips_blackbox_method: str = "spsa"  # spsa | nes
    detector_weight: float = 1.0  # LPIPS + Detector 联合优化时的 detector 分数权重

    watermark_remove: bool = False
    detector_feedback: bool = False
    detector_name: str = "local:resnet50"
    detector_threshold: float = 0.5
    max_iter: int = 10
    early_stop_epsilon: float = 0.01
    detector_adaptive_strength: bool = True
    detector_early_stop_patience: int = 2

    # Regeneration 扩展参数
    regeneration_mode: str = "surrogate"  # surrogate | local | remote
    regeneration_model_path: Optional[str] = None
    regeneration_denoise_strength: float = 0.35
    regeneration_prompt: str = "high quality, detailed, photorealistic"
    regeneration_api_endpoint: Optional[str] = None

    # 相机模拟细粒度开关
    camera_sim: Dict[str, Any] = field(
        default_factory=lambda: {
            "jpeg_cycles": 2,
            "motion_blur": True,
            "chromatic_aberration": True,
            "hot_pixels": True,
            "bayer_demosaic": False,
        }
    )
