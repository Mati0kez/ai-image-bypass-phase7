"""Diffusion Reconstruction 方法族 Module。

实现基于扩散模型的 SynthID 水印去除功能。
采用低去噪强度 + 结构引导 + 多轮重建的策略。
"""

import numpy as np
from PIL import Image
from typing import Optional, TYPE_CHECKING

from ..module import TransformModule
from ..registry import register_module

if TYPE_CHECKING:
    from ..config import TransformConfig
    from ..strength import StrengthOverride


class DiffusionReconstructionModule(TransformModule):
    """扩散重建模块（SynthID 水印去除专用）。"""

    @property
    def name(self) -> str:
        return "diffusion_reconstruction"

    def apply(
        self,
        img: Image.Image,
        config: "TransformConfig",
        rng: np.random.Generator,
        strength_override: Optional["StrengthOverride"] = None,
    ) -> Image.Image:
        enabled = getattr(config, "diffusion_reconstruction_enabled", False)
        if not enabled:
            return img.convert("RGB")

        mode = getattr(config, "diffusion_reconstruction_mode", "local")
        if mode == "local":
            return self._apply_local(img, config)
        else:
            return self._apply_surrogate(img, config)

    def _apply_local(self, img: Image.Image, config: "TransformConfig") -> Image.Image:
        """本地 diffusers 低去噪重建（SynthID 去除专用）。"""
        try:
            import torch
            from diffusers import StableDiffusionImg2ImgPipeline
        except ImportError:
            print("[DiffusionReconstructionModule] torch/diffusers 未安装，回退 surrogate")
            return self._apply_surrogate(img, config)

        model_path = getattr(config, "diffusion_reconstruction_model_path", None)
        if not model_path:
            print("[DiffusionReconstructionModule] 未指定模型路径，回退 surrogate")
            return self._apply_surrogate(img, config)

        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if device == "cuda" else torch.float32

        try:
            pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
                model_path, torch_dtype=dtype
            ).to(device)
        except Exception as e:
            print(f"[DiffusionReconstructionModule] 模型加载失败: {e}")
            return self._apply_surrogate(img, config)

        prompt = getattr(config, "diffusion_reconstruction_prompt", "high quality, detailed, clean")
        strength = getattr(config, "diffusion_reconstruction_denoise_strength", 0.25)
        guidance = getattr(config, "diffusion_reconstruction_guidance_scale", 7.5)
        num_passes = getattr(config, "diffusion_reconstruction_num_passes", 2)

        # 简单 Canny 结构引导（使用 PIL FIND_EDGES 作为占位）
        try:
            from PIL import ImageFilter
            _ = img.convert("L").filter(ImageFilter.FIND_EDGES)
            # 这里仅做演示，实际可传入 ControlNet
        except Exception:
            pass

        result = img.convert("RGB")
        for i in range(num_passes):
            result = pipe(
                prompt=prompt,
                image=result,
                strength=strength,
                guidance_scale=guidance,
                num_inference_steps=20,
            ).images[0]

        return result

    def _apply_surrogate(self, img: Image.Image, config: "TransformConfig") -> Image.Image:
        """代理模式（占位）。"""
        print("[DiffusionReconstructionModule] surrogate 模式，返回原图")
        return img.convert("RGB")


# import-time 自动注册
register_module(DiffusionReconstructionModule())