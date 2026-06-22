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

    # 各方法族强度（None 时各 Module 使用下方 verified 默认值）
    noise_strength: Optional[float] = None
    fft_strength: Optional[float] = None
    pixel_strength: Optional[float] = 0.028
    glcm_strength: Optional[float] = None
    skin_strength: Optional[float] = None

    # 元数据
    metadata_mode: MetadataMode = "synthetic"
    real_photo_path: Optional[str] = None

    # 扩展点（未来模块使用）
    lpips_enabled: bool = False
    lpips_strength: float = 0.06
    lpips_steps: int = 25
    lpips_blackbox: bool = False  # 启用黑盒优化（SPSA 等），适合 detector_feedback=True
    lpips_blackbox_method: str = "spsa"  # spsa | nes
    detector_weight: float = 1.0  # LPIPS + Detector 联合优化时的 detector 分数权重

    # 自定义方法族列表（用于 WebUI 逐项测试，优先级高于 profile）
    methods: Optional[list[str]] = None

    watermark_remove: bool = False
    watermark_spectral_mid_high_factor: float = 0.55
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

    # Diffusion Reconstruction（SynthID 水印去除）扩展参数
    diffusion_reconstruction_enabled: bool = False
    diffusion_reconstruction_mode: str = "local"  # local | surrogate
    diffusion_reconstruction_model_path: Optional[str] = None
    diffusion_reconstruction_denoise_strength: float = 0.25
    diffusion_reconstruction_guidance_scale: float = 7.5
    diffusion_reconstruction_num_passes: int = 2
    diffusion_reconstruction_prompt: str = "high quality, detailed, clean"

    # Frequency Peaks Cleansing (频谱峰值清洗) 扩展参数
    frequency_peaks_cleansing_enabled: bool = False
    frequency_peaks_cleansing_domain: str = "dct"  # dct | fft
    frequency_peaks_cleansing_threshold: float = 2.0
    frequency_peaks_cleansing_replacement_strategy: str = "attenuate"  # attenuate | zeroing | noise_injection
    frequency_peaks_cleansing_attenuation: float = 0.35

    # PRNU Simulation / Removal (传感器指纹模拟/去除) 扩展参数
    prnu_simulation_enabled: bool = False
    prnu_simulation_mode: str = "extract_add"  # extract_add | remove
    prnu_simulation_reference_path: Optional[str] = None
    prnu_simulation_strength: float = 0.75

    # Gradient/Edge-aware Perturbation (梯度/边缘感知扰动) 扩展参数
    gradient_edge_aware_perturbation_enabled: bool = False
    gradient_edge_aware_perturbation_edge_weight: float = 2.0
    gradient_edge_aware_perturbation_smooth_weight: float = 0.5

    # Transfer-based Black-box Attack Framework 扩展参数
    transfer_blackbox_attack_enabled: bool = False
    transfer_blackbox_attack_surrogate_model: str = "resnet50"
    transfer_blackbox_attack_algorithm: str = "fgsm"  # fgsm | pgd
    transfer_blackbox_attack_epsilon: float = 0.03

    # LPIPS 无 detector 闭环时的混合扰动系数（ResNet PGD 之后叠加 pixel perturbation）
    lpips_pixel_hybrid_factor: float = 0.45

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
