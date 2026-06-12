"""DetectorInterface 抽象基类。

定义 detector 评分的统一接口，支持本地模型和远程 API 适配器。
"""

from abc import ABC, abstractmethod
from PIL import Image


class DetectorInterface(ABC):
    """Detector 评分接口。

    所有具体 detector 实现（本地模型、远程 API）都必须继承此抽象基类，
    并实现 score 方法。
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """返回 detector 的唯一标识名称，例如 'local:resnet50' 或 'remote:hive'。"""
        ...

    @abstractmethod
    def score(self, img: Image.Image) -> float:
        """对输入图像进行检测评分。

        Args:
            img: PIL Image 对象（RGB 模式）。

        Returns:
            float: 检测分数，范围通常为 [0, 1]，值越高表示越可能是 AI 生成图像。
        """
        ...