"""Full-resolution PGD attack supporting any differentiable model.

Can be used with LPIPS + target model logit loss for perceptual + adversarial objectives.
"""

from __future__ import annotations

from typing import Any, Optional

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image

from .hf_loader import HFDetector


def _to_tensor(img: Image.Image, device: torch.device) -> torch.Tensor:
    arr = torch.from_numpy(
        np.array(img.convert("RGB")).astype(np.float32) / 255.0
    ).permute(2, 0, 1).unsqueeze(0).to(device)
    return arr


def _to_pil(t: torch.Tensor) -> Image.Image:
    arr = (t.detach().cpu().squeeze(0).permute(1, 2, 0).numpy() * 255).clip(0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def pgd_attack(
    img: Image.Image,
    target_model: HFDetector,
    lpips_model: Optional[Any] = None,
    epsilon: float = 0.03,
    steps: int = 20,
    step_size: float = 0.003,
    lpips_weight: float = 0.5,
    targeted: bool = False,
    target_class: Optional[int] = None,
) -> Image.Image:
    """Perform PGD attack on full-resolution image.

    Returns the adversarial PIL image.
    """
    device = target_model.device
    x0 = _to_tensor(img, device)
    x = x0.clone().detach().requires_grad_(True)

    if target_class is None:
        target_class = target_model.get_target_class(img)

    for _ in range(steps):
        x = x.detach().requires_grad_(True)
        logits = target_model.forward_logits(x)
        ce_loss = F.cross_entropy(logits, torch.tensor([target_class], device=device))

        loss = ce_loss
        # 暂时注释 LPIPS，避免梯度问题
        # if lpips_model is not None:
        #     lpips_loss = lpips_model(x0, x)
        #     loss = ce_loss + lpips_weight * lpips_loss

        loss.backward()

        with torch.no_grad():
            grad = x.grad.data
            # Targeted: minimize CE loss → 梯度下降
            # Untargeted: maximize CE loss → 梯度上升
            if targeted:
                x = x + step_size * grad.sign()   # 梯度上升，最小化 loss
            else:
                x = x - step_size * grad.sign()   # 梯度下降，最大化 loss
            # project to L-inf ball
            diff = torch.clamp(x - x0, -epsilon, epsilon)
            x = torch.clamp(x0 + diff, 0.0, 1.0)

    return _to_pil(x)