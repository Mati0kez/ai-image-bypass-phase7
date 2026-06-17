"""LPIPSModule 实现。

基于多步迭代的 LPIPS 非语义攻击。
支持与 Detector 的联合优化（当 detector_feedback=True 时）：
loss = lpips_loss + detector_weight * detector_score

注意：本模块依赖 torch + lpips（可选依赖）。无 torch 时 apply 将直接返回原图。
"""

from __future__ import annotations

import numpy as np
from PIL import Image
from typing import TYPE_CHECKING, Any, Optional

from transform_core.module import LPIPSModule as BaseLPIPSModule
from transform_core.config import TransformConfig

if TYPE_CHECKING:
    from transform_core.strength import StrengthOverride

# 延迟导入 torch/lpips，避免核心包依赖 torch
try:
    import torch
    import lpips

    _TORCH_AVAILABLE = True
except ImportError:
    _TORCH_AVAILABLE = False
    torch = None  # type: ignore[assignment]
    lpips = None  # type: ignore[assignment]


class LPIPSModule(BaseLPIPSModule):
    """LPIPS 非语义攻击模块。

    使用多步迭代（PGD-style）最小化 LPIPS 感知损失，
    在视觉几乎无损的情况下产生微扰。
    """

    def __init__(self, detector=None):
        super().__init__()
        self._lpips_model = None
        self._device = None
        self.detector = detector  # 可选：传入 DetectorInterface 实例以实现真实联合优化

    @property
    def name(self) -> str:
        return "lpips"

    def _get_device(self, config: TransformConfig) -> Any:
        """自动设备检测，优先 cuda，否则 cpu。"""
        if hasattr(config, "device") and config.device:
            return torch.device(config.device)
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def _get_lpips_model(self, device: Any):
        """延迟加载 LPIPS 模型（alex backbone）。"""
        if self._lpips_model is None or self._device != device:
            self._lpips_model = lpips.LPIPS(net="alex").to(device).eval()
            self._device = device
        return self._lpips_model

    def apply(
        self,
        img: Image.Image,
        config: TransformConfig,
        rng: np.random.Generator,
        strength_override: Optional["StrengthOverride"] = None,  # type: ignore[name-defined]
    ) -> Image.Image:
        if not getattr(config, "lpips_enabled", False):
            return img.convert("RGB")

        if not _TORCH_AVAILABLE:
            print("[LPIPSModule] torch/lpips 未安装，跳过 LPIPS 攻击（优雅降级）")
            return img.convert("RGB")

        # P3: 黑盒路径选择
        use_blackbox = getattr(config, "lpips_blackbox", False) or getattr(
            config, "detector_feedback", False
        )
        if use_blackbox:
            try:
                from .blackbox import blackbox_perturb

                # 构造 detector callable（如果 self.detector 存在）
                det_callable = self.detector.score if self.detector is not None else None
                return blackbox_perturb(
                    img, self._get_lpips_model(self._get_device(config)), det_callable, config
                )
            except Exception as e:
                print(f"[LPIPSModule] blackbox 路径失败，回退梯度路径: {e}")

        # 原有梯度路径（纯 LPIPS 或 detector_feedback=False）
        device = self._get_device(config)
        lpips_model = self._get_lpips_model(device)

        img_tensor = torch.from_numpy(np.array(img.convert("RGB"))).float() / 255.0
        img_tensor = img_tensor.permute(2, 0, 1).unsqueeze(0).to(device)
        perturbed = img_tensor.clone().detach().requires_grad_(True)

        strength = getattr(config, "lpips_strength", 0.01)
        steps = getattr(config, "lpips_steps", 10)
        lr = strength / max(steps, 1)

        optimizer = torch.optim.Adam([perturbed], lr=lr)

        detector_weight = getattr(config, "detector_weight", 1.0)
        use_detector = getattr(config, "detector_feedback", False)

        for _ in range(steps):
            optimizer.zero_grad()
            lpips_loss = lpips_model(img_tensor, perturbed)

            if use_detector:
                if self.detector is not None:
                    perturbed_pil = Image.fromarray(
                        (perturbed.detach().cpu().squeeze(0).permute(1, 2, 0).numpy() * 255).astype(
                            np.uint8
                        ),
                        "RGB",
                    )
                    detector_score = self.detector.score(perturbed_pil)
                else:
                    detector_score = 0.5

                loss = lpips_loss + detector_weight * detector_score
            else:
                loss = lpips_loss

            loss.backward()
            optimizer.step()

            with torch.no_grad():
                diff = perturbed - img_tensor
                norm = torch.norm(diff.reshape(diff.shape[0], -1), dim=1, keepdim=True)
                norm = norm.view(-1, 1, 1, 1) + 1e-8
                max_norm = strength * 0.1
                if norm.max() > max_norm:
                    perturbed.data = img_tensor + diff * (max_norm / norm)

        out = perturbed.detach().cpu().squeeze(0).permute(1, 2, 0).numpy()
        out = np.clip(out * 255, 0, 255).astype(np.uint8)
        return Image.fromarray(out, "RGB")
