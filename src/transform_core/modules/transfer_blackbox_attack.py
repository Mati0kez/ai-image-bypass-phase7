"""Transfer-based Black-box Attack Framework 方法族 Module。

利用代理模型生成迁移性对抗样本。
"""

import numpy as np
from PIL import Image
from typing import Optional, TYPE_CHECKING

from ..module import TransformModule
from ..registry import register_module

if TYPE_CHECKING:
    from ..config import TransformConfig
    from ..strength import StrengthOverride

try:
    import torch
    import torch.nn.functional as F
    import torchvision.models as models

    _TORCH_AVAILABLE = True
except ImportError:
    _TORCH_AVAILABLE = False
    torch = None
    models = None
    F = None


class TransferBlackboxAttackModule(TransformModule):
    """迁移性黑盒攻击模块。"""

    @property
    def name(self) -> str:
        return "transfer_blackbox_attack"

    def apply(
        self,
        img: Image.Image,
        config: "TransformConfig",
        rng: np.random.Generator,
        strength_override: Optional["StrengthOverride"] = None,
    ) -> Image.Image:
        enabled = getattr(config, "transfer_blackbox_attack_enabled", False)
        if not enabled:
            return img.convert("RGB")

        if not _TORCH_AVAILABLE:
            print("[TransferBlackboxAttackModule] torch 未安装，回退 surrogate")
            return self._apply_surrogate(img, config)

        target_repo = getattr(config, "target_detector_repo", None)
        if target_repo:
            # white-box path against HF detector
            try:
                from attack.whitebox import whitebox_attack
                result = whitebox_attack(
                    img,
                    target_repo,
                    epsilon=getattr(config, "transfer_blackbox_attack_epsilon", 0.03),
                    steps=10,
                )
                return result["adversarial_image"]
            except Exception as e:
                print(f"[TransferBlackboxAttackModule] whitebox 攻击失败: {e}，回退 surrogate")

        model_name = getattr(config, "transfer_blackbox_attack_surrogate_model", "resnet50")
        algorithm = getattr(config, "transfer_blackbox_attack_algorithm", "fgsm")
        epsilon = getattr(config, "transfer_blackbox_attack_epsilon", 0.03)

        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            if model_name == "resnet50":
                model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT).to(device).eval()
            else:
                model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT).to(device).eval()

            mean = torch.tensor([0.485, 0.456, 0.406], device=device).view(1, 3, 1, 1)
            std = torch.tensor([0.229, 0.224, 0.225], device=device).view(1, 3, 1, 1)

            orig = torch.from_numpy(np.array(img.convert("RGB"))).float() / 255.0
            orig = orig.permute(2, 0, 1).unsqueeze(0).to(device)
            x = orig.clone().detach()

            with torch.no_grad():
                resized0 = F.interpolate(orig, size=(224, 224), mode="bilinear", align_corners=False)
                orig_class = model((resized0 - mean) / std).argmax(dim=1)

            steps = 5 if algorithm == "pgd" else 1
            step_size = epsilon / steps

            for _ in range(steps):
                x = x.detach().requires_grad_(True)
                resized = F.interpolate(x, size=(224, 224), mode="bilinear", align_corners=False)
                logits = model((resized - mean) / std)
                loss = F.cross_entropy(logits, orig_class)
                loss.backward()
                with torch.no_grad():
                    step = step_size * x.grad.sign()
                    x = x + step
                    x = torch.max(torch.min(x, orig + epsilon), orig - epsilon)
                    x = torch.clamp(x, 0.0, 1.0)

            out = (x.squeeze(0).permute(1, 2, 0).cpu().numpy() * 255).astype(np.uint8)
            return Image.fromarray(out, "RGB")

        except Exception as e:
            print(f"[TransferBlackboxAttackModule] 攻击失败: {e}，回退 surrogate")
            return self._apply_surrogate(img, config)

    def _apply_surrogate(self, img: Image.Image, config: "TransformConfig") -> Image.Image:
        """代理模式（占位）。"""
        print("[TransferBlackboxAttackModule] surrogate 模式（占位），返回原图")
        return img.convert("RGB")


# import-time 自动注册
register_module(TransferBlackboxAttackModule())
