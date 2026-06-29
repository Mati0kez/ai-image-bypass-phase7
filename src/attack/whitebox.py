"""White-box attack entry point."""

from __future__ import annotations

from typing import Any, Dict, Optional

from PIL import Image

from .hf_loader import HFDetector
from .pgd import pgd_attack


def whitebox_attack(
    img: Image.Image,
    target_detector_repo: str,
    epsilon: float = 0.03,
    steps: int = 20,
    lpips_weight: float = 0.5,
    lpips_model: Optional[Any] = None,
    target_class: Optional[int] = None,
) -> Dict[str, Any]:
    """Run white-box PGD against a HF image classification model.

    Returns dict with adversarial image and metadata.
    If target_class is None, attack the current predicted class (untargeted).
    If target_class is specified, attack towards that class (targeted).
    """
    detector = HFDetector(target_detector_repo)
    # 注意：pgd_attack 内部的 targeted 逻辑与 whitebox_attack 相反
    # 这里显式传递正确的 targeted 标志
    adv_img = pgd_attack(
        img,
        detector,
        lpips_model=lpips_model,
        epsilon=epsilon,
        steps=steps,
        lpips_weight=lpips_weight,
        targeted=(target_class is not None),
        target_class=target_class,
    )

    orig_label, orig_score = detector(img)
    adv_label, adv_score = detector(adv_img)

    return {
        "adversarial_image": adv_img,
        "original_label": orig_label,
        "original_score": orig_score,
        "adversarial_label": adv_label,
        "adversarial_score": adv_score,
        "success": adv_score < 0.5,
    }