"""Black-box attack utilities (SPSA/NES) for remote detectors."""

from __future__ import annotations

from typing import Callable, Optional

from PIL import Image

from lpips_attack.blackbox import spsa_attack, _to_tensor, _to_pil


def blackbox_attack(
    img: Image.Image,
    detector: Callable[[Image.Image], float],
    lpips_model: Any,
    steps: int = 20,
    strength: float = 0.03,
    detector_weight: float = 1.0,
) -> Image.Image:
    """Run SPSA black-box attack against any score-returning detector."""
    import torch

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    x0 = _to_tensor(img, device)

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