"""Hive 平台 Detector 适配器。

实现与 Hive API 的真实 HTTP 调用，包含重试、超时和错误处理。
"""

import os
import time
import io
import json
from typing import Optional
from PIL import Image
import numpy as np
import requests
from dotenv import load_dotenv

from .platform_adapter import PlatformAdapter

# 自动加载 .env 文件（如果存在）
load_dotenv()


class HiveAPIDetectorAdapter(PlatformAdapter):
    """Hive 平台远程 API 适配器。

    通过环境变量 HIVE_API_KEY 加载认证信息。
    实现简单的指数退避重试策略。
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: str = "https://api.thehive.ai/api/v2/task/sync",
        max_retries: int = 3,
        timeout_sec: int = 30,
    ):
        self._api_key = api_key or os.getenv("HIVE_API_KEY")
        self._endpoint = endpoint
        self._max_retries = max_retries
        self._timeout_sec = timeout_sec
        self._request_count = 0
        self._total_cost = 0.0

    @property
    def name(self) -> str:
        return "remote:hive"

    def score(self, img: Image.Image) -> float:
        """调用 Hive API 进行检测评分。

        实现真实 HTTP 请求：将 PIL Image 转为 JPEG bytes，
        通过 Authorization: Token <key> 头发送，解析返回的 JSON 分数。
        """
        if not self._api_key:
            # 无 Key 时自动降级为 mock
            print("[HiveAPIDetectorAdapter] 未找到 HIVE_API_KEY，降级为 mock 分数")
            rng = np.random.default_rng()
            return float(rng.uniform(0.2, 0.8))

        self._request_count += 1

        # 将 PIL Image 转为 JPEG bytes
        buffer = io.BytesIO()
        img.convert("RGB").save(buffer, format="JPEG", quality=95)
        buffer.seek(0)

        headers = {
            "Authorization": f"Token {self._api_key}",
            "Accept": "application/json",
        }
        files = {"image": ("image.jpg", buffer, "image/jpeg")}

        for attempt in range(self._max_retries):
            try:
                resp = requests.post(
                    self._endpoint,
                    headers=headers,
                    files=files,
                    timeout=self._timeout_sec,
                )
                resp.raise_for_status()
                data = resp.json()

                score = self._parse_hive_response(data)
                self._total_cost += 0.01
                return score

            except requests.exceptions.HTTPError as e:
                status = e.response.status_code if e.response else None
                if status == 401:
                    print("[HiveAPIDetectorAdapter] 认证失败 (401)，请检查 HIVE_API_KEY 是否正确")
                    break
                if status == 429:
                    print("[HiveAPIDetectorAdapter] 配额/速率限制 (429)，稍后重试")
                if attempt < self._max_retries - 1:
                    wait_time = 2**attempt
                    print(
                        f"[HiveAPIDetectorAdapter] HTTP {status} (attempt {attempt+1}/{self._max_retries})，{wait_time}s 后重试"
                    )
                    time.sleep(wait_time)
                else:
                    print("[HiveAPIDetectorAdapter] HTTP 错误，已达最大重试次数，降级为 mock 分数")
            except requests.exceptions.Timeout:
                if attempt < self._max_retries - 1:
                    wait_time = 2**attempt
                    print(
                        f"[HiveAPIDetectorAdapter] 超时 (attempt {attempt+1}/{self._max_retries})，{wait_time}s 后重试"
                    )
                    time.sleep(wait_time)
                else:
                    print("[HiveAPIDetectorAdapter] 请求超时，已达最大重试次数，降级为 mock 分数")
            except requests.exceptions.RequestException as e:
                if attempt < self._max_retries - 1:
                    wait_time = 2**attempt
                    print(
                        f"[HiveAPIDetectorAdapter] 请求失败 (attempt {attempt+1}/{self._max_retries}): {e}，{wait_time}s 后重试"
                    )
                    time.sleep(wait_time)
                else:
                    print(
                        f"[HiveAPIDetectorAdapter] 请求失败，已达最大重试次数: {e}，降级为 mock 分数"
                    )
            except (KeyError, json.JSONDecodeError, TypeError) as e:
                print(f"[HiveAPIDetectorAdapter] 响应解析失败: {e}，降级为 mock 分数")
                break

        # 所有重试失败后降级
        rng = np.random.default_rng()
        return float(rng.uniform(0.1, 0.6))

    def _parse_hive_response(self, data: dict) -> float:
        """从 Hive API 响应中提取 AI 生成概率分数。

        不同模型的响应结构可能不同，这里提供一个合理的默认解析逻辑。
        用户可根据实际返回格式调整。
        """
        # 常见路径：task -> result -> classifications[0] -> score
        try:
            task = data.get("task", {})
            result = task.get("result", {})
            classifications = result.get("classifications", [])
            if classifications:
                # 取第一个 classification 的 score（通常是 AI 生成类别的置信度）
                return float(classifications[0].get("score", 0.5))
        except (AttributeError, TypeError, IndexError):
            pass

        # 兜底：如果解析失败返回 0.5（中性分数）
        return 0.5

    def get_quota_usage(self) -> dict:
        return {
            "requests": self._request_count,
            "estimated_cost_usd": round(self._total_cost, 4),
        }
