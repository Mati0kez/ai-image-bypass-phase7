"""Foolbox-based white-box attacks (PGD with restarts, CW, etc.).

Since Foolbox 3.x does not ship AutoAttack by default, we provide
a strong LinfPGD with random restarts (option 2) and a Carlini-Wagner
L2 attack (option 3).
"""

from __future__ import annotations

from typing import Dict, Any

import torch
from PIL import Image

from .hf_loader import HFDetector


def foolbox_pgd_with_restarts(
    img: Image.Image,
    target_detector_repo: str,
    epsilon: float = 0.03,
    restarts: int = 5,
    steps: int = 40,
    verbose: bool = False,
) -> Dict[str, Any]:
    """Linf PGD with multiple random restarts (stronger than single-run PGD).

    This is the "选项2: 优化 PGD 添加 Random Restarts" implementation.
    """
    import foolbox as fb
    import numpy as np

    detector = HFDetector(target_detector_repo)
    device = detector.device

    x = torch.from_numpy(np.array(img.convert("RGB")).astype(np.float32) / 255.0)
    x = x.permute(2, 0, 1).unsqueeze(0).to(device)

    # Custom Foolbox model wrapper that returns only logits
    class HFModelWrapper(torch.nn.Module):
        def __init__(self, model):
            super().__init__()
            self.model = model
        def forward(self, x):
            out = self.model(x)
            if hasattr(out, "logits"):
                return out.logits
            return out

    wrapped_model = HFModelWrapper(detector.model)
    fmodel = fb.PyTorchModel(wrapped_model, bounds=(0, 1))
    attack = fb.attacks.LinfPGD(steps=steps)

    target_class = detector.get_target_class(img)
    target = torch.tensor([target_class], device=device)

    best_adv = None
    best_score = 1.0

    for r in range(restarts):
        # Random start inside the epsilon ball
        delta = torch.empty_like(x).uniform_(-epsilon, epsilon)
        x_start = torch.clamp(x + delta, 0, 1)

        adv_x, success = attack(fmodel, x_start, target, epsilons=epsilon)

        with torch.no_grad():
            adv_logits = detector.forward_logits(adv_x)
            adv_score = torch.softmax(adv_logits, dim=-1).max().item()

        if adv_score < best_score:
            best_score = adv_score
            best_adv = adv_x

        if verbose:
            print(f"Restart {r+1}/{restarts}: score={adv_score:.4f}")

    adv_img = Image.fromarray(
        (best_adv.squeeze(0).permute(1, 2, 0).cpu().numpy() * 255).astype(np.uint8)
    )

    with torch.no_grad():
        orig_logits = detector.forward_logits(x)
        adv_logits = detector.forward_logits(best_adv)

    orig_score = torch.softmax(orig_logits, dim=-1).max().item()
    adv_score = torch.softmax(adv_logits, dim=-1).max().item()

    orig_label = detector.model.config.id2label[orig_logits.argmax().item()]
    adv_label = detector.model.config.id2label[adv_logits.argmax().item()]

    return {
        "adversarial_image": adv_img,
        "original_label": orig_label,
        "original_score": orig_score,
        "adversarial_label": adv_label,
        "adversarial_score": adv_score,
        "success": adv_score < 0.5 or adv_label != orig_label,
    }