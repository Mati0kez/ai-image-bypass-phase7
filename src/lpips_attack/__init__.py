"""Lpips Attack - 基于 LPIPS 的非语义攻击模块。

提供 LPIPSModule 接口和配置扩展点。
"""

from .module import LPIPSModule
from transform_core.registry import register_module

# import 时自动注册（可选方法族）
register_module(LPIPSModule())

__all__ = ["LPIPSModule"]
