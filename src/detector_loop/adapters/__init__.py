"""Detector 适配器集合。"""

from .local_adapter import LocalDetectorAdapter
from .remote_adapter import HiveAPIDetectorAdapter

__all__ = ["LocalDetectorAdapter", "HiveAPIDetectorAdapter"]
