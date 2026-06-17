"""Black-box optimization for LPIPS attack.

Provides zeroth-order methods (SPSA, simplified NES) that only require
forward passes of LPIPS model and detector.score(), suitable for
non-differentiable detector feedback scenarios.
"""

from __future__ import annotations

from typing import Any, Optional, Callable
import numpy as np
from PIL import Image

# 延迟导入 torch，避免无 torch 环境导入失败
try:
    import torch

    _TORCH_AVAILABLE = True
except ImportError:
    _TORCH_AVAILABLE = False
    torch = None  # type: ignore[assignment]


def _to_tensor(img: Image.Image, device: torch.device) -> torch.Tensor:
    arr = np.array(img.convert("RGB")).astype(np.float32) / 255.0
    t = torch.from_numpy(arr).permute(2, 0, 1).unsqueeze(0).to(device)
    return t


def _to_pil(t: torch.Tensor) -> Image.Image:
    arr = (t.detach().cpu().squeeze(0).permute(1, 2, 0).numpy() * 255).clip(0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def _clip_perturbation(
    perturbed: torch.Tensor, original: torch.Tensor, max_norm: float
) -> torch.Tensor:
    diff = perturbed - original
    norm = torch.norm(diff.view(diff.shape[0], -1), dim=1, keepdim=True) + 1e-8
    norm = norm.view(-1, 1, 1, 1)
    if norm.max() > max_norm:
        perturbed = original + diff * (max_norm / norm)
    return perturbed


def spsa_attack(
    x0: torch.Tensor,
    lpips_model: Any,
    detector: Optional[Callable[[Image.Image], float]],
    steps: int = 20,
    lr: float = 0.01,
    perturbation_scale: float = 0.05,
    detector_weight: float = 1.0,
    seed: Optional[int] = None,
) -> torch.Tensor:
    """SPSA (Simultaneous Perturbation Stochastic Approximation) black-box attack.

    Minimizes lpips(x, x0) + detector_weight * detector_score(x) using only
    function evaluations (no gradients).
    """
    rng = np.random.default_rng(seed)
    device = x0.device
    x = x0.clone().detach().requires_grad_(False)
    original = x0.clone().detach()

    for _ in range(steps):
        # Sample random perturbation direction (Rademacher)
        delta = torch.tensor(rng.choice([-1.0, 1.0], size=x.shape), device=device, dtype=x.dtype)

        # Two-point evaluation
        c = perturbation_scale
        x_plus = _clip_perturbation(x + c * delta, original, perturbation_scale * 2)
        x_minus = _clip_perturbation(x - c * delta, original, perturbation_scale * 2)

        # Evaluate objective
        with torch.no_grad():
            lpips_plus = lpips_model(original, x_plus)
            lpips_minus = lpips_model(original, x_minus)

            if detector is not None:
                pil_plus = _to_pil(x_plus)
                pil_minus = _to_pil(x_minus)
                det_plus = detector(pil_plus)
                det_minus = detector(pil_minus)
            else:
                det_plus = det_minus = 0.5

            f_plus = lpips_plus + detector_weight * det_plus
            f_minus = lpips_minus + detector_weight * det_minus

        # Gradient estimate (SPSA)
        g = (f_plus - f_minus) / (2 * c) * delta

        # Update
        x = x - lr * g
        x = _clip_perturbation(x, original, perturbation_scale * 3)

    return x


def blackbox_perturb(
    img: Image.Image,
    lpips_model: Any,
    detector: Optional[Callable[[Image.Image], float]],
    config: Any,
) -> Image.Image:
    """Unified entry point for black-box LPIPS attack.

    Selects method based on config.lpips_blackbox_method (default 'spsa').
    """
    if not _TORCH_AVAILABLE:
        print("[blackbox] torch 未安装，跳过黑盒 LPIPS 攻击")
        return img.convert("RGB")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    x0 = _to_tensor(img, device)

    method = getattr(config, "lpips_blackbox_method", "spsa")
    steps = getattr(config, "lpips_steps", 15)
    strength = getattr(config, "lpips_strength", 0.02)
    detector_weight = getattr(config, "detector_weight", 1.0)

    if method == "spsa":
        x_adv = spsa_attack(
            x0,
            lpips_model,
            detector,
            steps=steps,
            lr=strength * 0.5,
            perturbation_scale=strength,
            detector_weight=detector_weight,
            seed=getattr(config, "seed", None),
        )
    else:
        x_adv = spsa_attack(
            x0,
            lpips_model,
            detector,
            steps=steps,
            lr=strength * 0.5,
            perturbation_scale=strength,
            detector_weight=detector_weight,
        )

    return _to_pil(x_adv)
