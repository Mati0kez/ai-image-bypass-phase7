"""Mock Platform Adapter。

用于无 API Key 环境、CI 测试和快速验证。
"""

from PIL import Image
import numpy as np

from .platform_adapter import PlatformAdapter


class MockPlatformAdapter(PlatformAdapter):
    """Mock 外部平台适配器。

    模拟真实 API 行为，但不产生实际网络请求和费用。
    可配置返回分数的分布和延迟。
    """

    def __init__(
        self,
        name: str = "remote:mock",
        mock_score_range: tuple = (0.1, 0.7),
        simulated_latency_ms: int = 50,
    ):
        self._name = name
        self._score_range = mock_score_range
        self._latency_ms = simulated_latency_ms
        self._request_count = 0

    @property
    def name(self) -> str:
        return self._name

    def score(self, img: Image.Image) -> float:
        """返回模拟分数，并模拟网络延迟。"""
        self._request_count += 1
        if self._latency_ms > 0:
            time.sleep(self._latency_ms / 1000.0)
        rng = np.random.default_rng()
        return float(rng.uniform(*self._score_range))

    def get_quota_usage(self) -> dict:
        return {
            "requests": self._request_count,
            "estimated_cost_usd": 0.0,
            "mode": "mock",
        }


import time  # noqa: E402
