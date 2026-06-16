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
    import torchvision.models as models
    import torchvision.transforms as transforms
    _TORCH_AVAILABLE = True
except ImportError:
    _TORCH_AVAILABLE = False
    torch = None
    models = None
    transforms = None


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

        # P10.4-2: 代理模型加载与攻击逻辑 (简化 FGSM)
        model_name = getattr(config, "transfer_blackbox_attack_surrogate_model", "resnet50")
        epsilon = getattr(config, "transfer_blackbox_attack_epsilon", 0.03)
        algorithm = getattr(config, "transfer_blackbox_attack_algorithm", "fgsm")

        try:
            # 加载模型 (使用 pretrained=True 以获得 ImageNet 权重)
            if model_name == "resnet50":
                model = models.resnet50(pretrained=True)
            else:
                model = models.resnet18(pretrained=True) # Fallback

            model.eval()
            if torch.cuda.is_available():
                model.cuda()

            # 预处理
            preprocess = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])

            input_tensor = preprocess(img).unsqueeze(0)
            if torch.cuda.is_available():
                input_tensor = input_tensor.cuda()

            input_tensor.requires_grad = True

            # 前向传播
            output = model(input_tensor)
            # 假设目标是 "0" 类 (或随机)，这里简化处理
            target = torch.tensor([0]).cuda() if torch.cuda.is_available() else torch.tensor([0])

            # 计算损失 (简化)
            loss = torch.nn.functional.cross_entropy(output, target)
            model.zero_grad()
            loss.backward()

            # FGSM 攻击
            grad = input_tensor.grad.data
            perturbation = epsilon * grad.sign()

            # 应用扰动
            perturbed_tensor = input_tensor + perturbation
            perturbed_tensor = torch.clamp(perturbed_tensor, 0, 1)

            # 后处理
            perturbed_img = perturbed_tensor.squeeze(0).cpu().detach().numpy()
            perturbed_img = np.transpose(perturbed_img, (1, 2, 0))
            perturbed_img = (perturbed_img * 255).astype(np.uint8)

            return Image.fromarray(perturbed_img)

        except Exception as e:
            print(f"[TransferBlackboxAttackModule] 攻击失败: {e}，回退 surrogate")
            return self._apply_surrogate(img, config)

    def _apply_surrogate(self, img: Image.Image, config: "TransformConfig") -> Image.Image:
        """代理模式（占位）。"""
        print("[TransferBlackboxAttackModule] surrogate 模式（占位），返回原图")
        return img.convert("RGB")


# import-time 自动注册
register_module(TransferBlackboxAttackModule())
