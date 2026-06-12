"""远程 API Detector 适配器。

支持 Hive、Illuminarty 等外部检测平台的 HTTP API 调用，带重试和超时机制。
"""

from typing import Optional
from PIL import Image
import numpy as np

from ..detector_interface import DetectorInterface


class HiveAPIDetectorAdapter(DetectorInterface):
    """Hive 平台远程 API 适配器。

    当前为骨架实现，实际 HTTP 请求逻辑留待后续扩展。
    """

    def __init__(self, api_key: Optional[str] = None, endpoint: str = "https://api.hive.com/detect"):
        self._api_key = api_key
        self._endpoint = endpoint

    @property
    def name(self) -> str:
        return "remote:hive"

    def score(self, img: Image.Image) -> float:
        """调用远程 API 进行检测评分。

        当前返回随机分数作为占位，真实实现需替换为 HTTP 请求 + 重试逻辑。
        """
        # TODO: 实现 requests.post + 重试 + 超时 + 错误处理
        print(f"[HiveAPIDetectorAdapter] 调用 {self._endpoint} 占位（未实现真实 API）")
        rng = np.random.default_rng()
        return float(rng.uniform(0.2, 0.8))