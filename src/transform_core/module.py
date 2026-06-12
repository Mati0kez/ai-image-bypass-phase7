"""TransformModule - 可插拔变换单元的抽象基类。"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

import numpy as np
from PIL import Image

if TYPE_CHECKING:
    from .config import TransformConfig
    from .strength import StrengthOverride


class TransformModule(ABC):
    """一个可插拔的变换单元。

    暴露 name 属性和 apply 方法，接受 Config 和 rng，
    返回处理后的图片。所有具体方法族（metadata、frequency、camera 等）
    都应继承此 ABC 并实现 apply。
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """方法族名称，用于注册表和 manifest 记录。"""
        ...

    @abstractmethod
    def apply(
        self,
        img: Image.Image,
        config: "TransformConfig",
        rng: np.random.Generator,
        strength_override: Optional["StrengthOverride"] = None,
    ) -> Image.Image:
        """执行变换。

        Args:
            img: 输入图片（RGB 模式）。
            config: 完整配置对象，包含该模块需要的参数。
            rng: 随机数生成器，保证可复现性。
            strength_override: 可选的强度覆盖对象，用于 DIL 闭环动态调整。

        Returns:
            处理后的图片（RGB 模式）。
        """
        ...


class LPIPSModule(TransformModule):
    """LPIPS 非语义攻击模块抽象基类。

    具体实现（基于 torch + lpips 的感知损失微扰）由 lpips_attack 包提供。
    此 ABC 仅声明接口，保持核心无 torch 依赖。
    """

    pass
