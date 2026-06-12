"""Tests for HiveAPIDetectorAdapter (real HTTP + retry + fallback)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import responses
from PIL import Image
import numpy as np

from external_validation.hive_adapter import HiveAPIDetectorAdapter


def test_hive_adapter_no_key_falls_back_to_mock():
    """当没有 API Key 时应自动降级为 mock 分数。"""
    adapter = HiveAPIDetectorAdapter(api_key=None)
    img = Image.fromarray(np.zeros((32, 32, 3), dtype=np.uint8))
    score = adapter.score(img)
    assert 0.0 <= score <= 1.0


@responses.activate
def test_hive_adapter_successful_response():
    """模拟 Hive API 返回成功响应时能正确解析分数。"""
    adapter = HiveAPIDetectorAdapter(api_key="fake-key")
    img = Image.fromarray(np.zeros((32, 32, 3), dtype=np.uint8))

    # 模拟 Hive 响应
    responses.add(
        responses.POST,
        "https://api.thehive.ai/api/v2/task/sync",
        json={
            "task": {
                "result": {
                    "classifications": [{"score": 0.87}]
                }
            }
        },
        status=200,
    )

    score = adapter.score(img)
    assert score == 0.87


@responses.activate
def test_hive_adapter_401_auth_failure():
    """模拟 401 错误时应优雅降级。"""
    adapter = HiveAPIDetectorAdapter(api_key="bad-key")
    img = Image.fromarray(np.zeros((32, 32, 3), dtype=np.uint8))

    responses.add(
        responses.POST,
        "https://api.thehive.ai/api/v2/task/sync",
        status=401,
    )

    score = adapter.score(img)
    assert 0.0 <= score <= 1.0  # 降级为 mock 分数


@responses.activate
def test_hive_adapter_retry_on_429():
    """模拟 429 错误时应重试后降级。"""
    adapter = HiveAPIDetectorAdapter(api_key="rate-limited", max_retries=2)
    img = Image.fromarray(np.zeros((32, 32, 3), dtype=np.uint8))

    responses.add(
        responses.POST,
        "https://api.thehive.ai/api/v2/task/sync",
        status=429,
    )
    responses.add(
        responses.POST,
        "https://api.thehive.ai/api/v2/task/sync",
        status=429,
    )

    score = adapter.score(img)
    assert 0.0 <= score <= 1.0
    assert len(responses.calls) == 2  # 验证重试次数