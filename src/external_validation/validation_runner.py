"""ValidationRunner 外部验证运行器。

集成 rate limiter、cost guard 和自动降级逻辑，
统一管理外部平台 API 调用。
"""

import time
from dataclasses import dataclass
from typing import Optional
from PIL import Image

from .platform_adapter import PlatformAdapter
from .hive_adapter import HiveAPIDetectorAdapter
from .mock_adapter import MockPlatformAdapter


@dataclass
class RateLimitConfig:
    """速率限制配置。"""

    max_requests_per_minute: int = 10
    max_total_cost_usd: float = 5.0


class ValidationRunner:
    """外部平台验证运行器。

    负责：
    - 根据 detector_name 创建对应 Adapter（Hive / Mock）
    - 应用 rate limit 和 cost guard
    - 超限时自动降级为 Mock
    """

    def __init__(
        self,
        detector_name: str = "remote:hive",
        rate_limit: Optional[RateLimitConfig] = None,
    ):
        self.detector_name = detector_name
        self.rate_limit = rate_limit or RateLimitConfig()
        self.adapter = self._create_adapter(detector_name)
        self._request_timestamps: list[float] = []
        self._total_cost = 0.0
        self._downgraded = False

    def _create_adapter(self, name: str) -> PlatformAdapter:
        if name == "remote:hive":
            return HiveAPIDetectorAdapter()
        elif name.startswith("remote:mock"):
            return MockPlatformAdapter(name=name)
        else:
            # 默认使用 Mock
            return MockPlatformAdapter(name=name)

    def _check_rate_limit(self) -> bool:
        """检查是否超过速率限制。"""
        now = time.time()
        # 清理 60 秒前的记录
        self._request_timestamps = [t for t in self._request_timestamps if now - t < 60]
        if len(self._request_timestamps) >= self.rate_limit.max_requests_per_minute:
            return False
        return True

    def _check_cost_guard(self, estimated_cost: float = 0.01) -> bool:
        """检查是否超过成本上限。"""
        if self._total_cost + estimated_cost > self.rate_limit.max_total_cost_usd:
            return False
        return True

    def score(self, img: Image.Image) -> float:
        """执行一次外部验证评分，自动处理限流和降级。"""
        # 检查 rate limit
        if not self._check_rate_limit():
            print("[ValidationRunner] 触发 rate limit，自动降级为 mock")
            self.adapter = MockPlatformAdapter(name="remote:mock-downgraded")
            self._downgraded = True

        # 检查 cost guard
        if not self._check_cost_guard():
            print("[ValidationRunner] 触发 cost guard，自动降级为 mock")
            self.adapter = MockPlatformAdapter(name="remote:mock-downgraded")
            self._downgraded = True

        score = self.adapter.score(img)
        self._request_timestamps.append(time.time())

        # 更新成本（仅对真实平台）
        usage = self.adapter.get_quota_usage()
        self._total_cost = usage.get("estimated_cost_usd", 0.0)

        return score

    def get_quota_usage(self) -> dict:
        usage = self.adapter.get_quota_usage()
        usage["downgraded"] = self._downgraded
        return usage
