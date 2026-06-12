"""External Validation 真实平台验证框架。

提供 PlatformAdapter 抽象和 Hive 等外部 detector 平台的适配器，
支持 API Key 安全加载、rate limit、cost guard 和 mock 降级。
与 BenchmarkRunner 统一集成。
"""

from .platform_adapter import PlatformAdapter
from .validation_runner import ValidationRunner

__all__ = [
    "PlatformAdapter",
    "ValidationRunner",
    "HiveAPIDetectorAdapter",
    "MockPlatformAdapter",
]

# 延迟导入 adapters
from .hive_adapter import HiveAPIDetectorAdapter  # noqa: F401
from .mock_adapter import MockPlatformAdapter  # noqa: F401
