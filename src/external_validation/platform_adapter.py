"""PlatformAdapter 抽象基类。

定义外部 detector 平台验证的统一接口。
"""

from abc import ABC, abstractmethod
from PIL import Image


class PlatformAdapter(ABC):
    """外部平台 Detector 适配器抽象基类。

    所有具体平台实现（Hive、Illuminarty 等）都必须继承此抽象基类，
    并实现 score 方法和配额管理接口。
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """返回平台名称，例如 'remote:hive'。"""
        ...

    @abstractmethod
    def score(self, img: Image.Image) -> float:
        """调用外部平台 API 进行检测评分。

        Args:
            img: PIL Image 对象（RGB 模式）。

        Returns:
            float: 检测分数，范围 [0, 1]，值越高表示越可能是 AI 生成图像。
        """
        ...

    @abstractmethod
    def get_quota_usage(self) -> dict:
        """返回本次运行的配额消耗估算。

        Returns:
            dict: 例如 {"requests": 5, "estimated_cost_usd": 0.05}
        """
        ...
