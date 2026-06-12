"""Detector-in-the-Loop 反馈框架。

提供 DetectorInterface 抽象和多种适配器（本地模型、远程 API），
支持在 TransformConfig.detector_feedback=True 时由 pipeline 触发迭代优化。
"""

from .detector_interface import DetectorInterface

__all__ = [
    "DetectorInterface",
    "DetectorLoop",
    "LocalDetectorAdapter",
    "HiveAPIDetectorAdapter",
]

# 延迟导入以避免循环依赖
from .adapters.local_adapter import LocalDetectorAdapter  # noqa: F401
from .adapters.remote_adapter import HiveAPIDetectorAdapter  # noqa: F401
from .loop import DetectorLoop  # noqa: F401
