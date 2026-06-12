"""Transform Core - AI 图片检测对抗框架核心模块。

提供 TransformConfig 数据契约和 TransformModule 抽象接口。
"""

from .config import TransformConfig
from .module import TransformModule
from .registry import (
    TRANSFORM_MODULES,
    register_module,
    _selected_modules,
)
from . import modules

__all__ = [
    "TransformConfig",
    "TransformModule",
    "TRANSFORM_MODULES",
    "register_module",
    "_selected_modules",
    "modules",
]
