"""Regeneration 方法族 Module。

支持真实 img2img 重生成（本地 diffusers / 远程 API）和代理模式。
"""

import numpy as np
from PIL import Image
from typing import TYPE_CHECKING

from ..module import TransformModule
from ..registry import register_module

if TYPE_CHECKING:
    from ..config import TransformConfig


class RegenerationModule(TransformModule):
    """再生模块（真实 img2img / 远程 API / 代理）。"""

    @property
    def name(self) -> str:
        return "regeneration"

    def apply(
        self,
        img: Image.Image,
        config: "TransformConfig",
        rng: np.random.Generator,
    ) -> Image.Image:
        mode = getattr(config, "regeneration_mode", "surrogate")

        if mode == "local":
            return self._apply_local(img, config)
        elif mode == "remote":
            return self._apply_remote(img, config)
        else:
            # 向后兼容：代理模式
            return self._apply_surrogate(img, config)

    def _apply_local(self, img: Image.Image, config: "TransformConfig") -> Image.Image:
        """本地 diffusers 模式。"""
        try:
            import torch
            from diffusers import StableDiffusionImg2ImgPipeline
        except ImportError:
            print("[RegenerationModule] torch/diffusers 未安装，回退到 surrogate 模式")
            return self._apply_surrogate(img, config)

        model_path = getattr(config, "regeneration_model_path", None)
        if not model_path:
            print("[RegenerationModule] 未指定 regeneration_model_path，回退到 surrogate")
            return self._apply_surrogate(img, config)

        device = "cuda" if torch.cuda.is_available() else "cpu"
        try:
            pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
                model_path, torch_dtype=torch.float16 if device == "cuda" else torch.float32
            ).to(device)
        except Exception as e:
            print(f"[RegenerationModule] 模型加载失败: {e}，回退到 surrogate")
            return self._apply_surrogate(img, config)

        # 推理参数
        prompt = getattr(config, "regeneration_prompt", "high quality, detailed")
        strength = getattr(config, "regeneration_denoise_strength", 0.35)

        result = pipe(
            prompt=prompt,
            image=img.convert("RGB"),
            strength=strength,
            guidance_scale=7.5,
            num_inference_steps=20,
        ).images[0]

        return result

    def _apply_remote(self, img: Image.Image, config: "TransformConfig") -> Image.Image:
        """远程 API 模式（占位）。"""
        # TODO: 实现 Replicate / HF Endpoint 调用
        print("[RegenerationModule] 远程模式未完全实现，回退到 surrogate")
        return self._apply_surrogate(img, config)

    def _apply_surrogate(self, img: Image.Image, config: "TransformConfig") -> Image.Image:
        """代理模式（原有逻辑）。"""
        try:
            from bypass_ai_detector import add_regeneration_surrogate
            return add_regeneration_surrogate(img, strength=0.25)
        except Exception:
            return img.convert("RGB")


# import-time 自动注册
register_module(RegenerationModule())