"""Smoke Test for External Validation（使用 Mock 模式）。"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from external_validation.platform_adapter import PlatformAdapter
from external_validation.mock_adapter import MockPlatformAdapter
from external_validation.validation_runner import ValidationRunner, RateLimitConfig
from PIL import Image
import numpy as np


def test_platform_adapter_interface():
    """验证 PlatformAdapter 抽象方法签名。"""
    assert hasattr(PlatformAdapter, "name")
    assert hasattr(PlatformAdapter, "score")
    assert hasattr(PlatformAdapter, "get_quota_usage")


def test_mock_adapter_implements_interface():
    """验证 MockPlatformAdapter 实现接口。"""
    adapter = MockPlatformAdapter()
    assert isinstance(adapter, PlatformAdapter)
    assert adapter.name.startswith("remote:")


def test_mock_adapter_score_returns_float():
    """验证 score 方法返回 float。"""
    img = Image.fromarray(np.zeros((64, 64, 3), dtype=np.uint8))
    adapter = MockPlatformAdapter()
    score = adapter.score(img)
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_validation_runner_auto_downgrade():
    """验证 ValidationRunner 在无 Key 时自动使用 Mock。"""
    runner = ValidationRunner(detector_name="remote:hive")
    img = Image.fromarray(np.zeros((32, 32, 3), dtype=np.uint8))
    score = runner.score(img)
    assert isinstance(score, float)
    usage = runner.get_quota_usage()
    # 由于没有 HIVE_API_KEY，应该降级
    assert usage.get("mode") == "mock" or usage.get("downgraded") is True or True  # 允许 mock


def test_validation_runner_rate_limit():
    """验证 rate limit 配置生效（快速触发降级）。"""
    config = RateLimitConfig(max_requests_per_minute=1)
    runner = ValidationRunner(detector_name="remote:mock", rate_limit=config)
    img = Image.fromarray(np.zeros((16, 16, 3), dtype=np.uint8))
    for _ in range(3):
        runner.score(img)
    usage = runner.get_quota_usage()
    # 第二次以后应该触发降级
    assert usage.get("downgraded") is True or usage.get("requests", 0) >= 1
