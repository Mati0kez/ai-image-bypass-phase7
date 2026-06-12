"""本地模型 Detector 适配器。

支持 torch / onnx 格式的本地模型，自动检测 CPU / GPU 设备。
"""

from typing import Any, Optional
from PIL import Image
import numpy as np

from ..detector_interface import DetectorInterface


class LocalDetectorAdapter(DetectorInterface):
    """本地模型 Detector 适配器。

    目前为骨架实现，实际模型加载和推理逻辑留待后续扩展。
    """

    def __init__(self, model_name: str = "resnet50", model_path: Optional[str] = None):
        self._model_name = model_name
        self._model_path = model_path
        self._model: Any = None  # 延迟加载

    @property
    def name(self) -> str:
        return f"local:{self._model_name}"

    def _load_model(self) -> None:
        """延迟加载本地模型（torch / onnx）。"""
        if self._model is not None:
            return
        # TODO: 实现 torch / onnx 模型加载逻辑
        # 示例：使用 torch.hub 或 torch.load
        print(f"[LocalDetectorAdapter] 模型 {self._model_name} 加载占位（未实现真实推理）")

    def score(self, img: Image.Image) -> float:
        """对图像进行本地模型评分。

        当前返回随机分数作为占位，真实实现需替换为模型推理。
        """
        self._load_model()
        # 占位：返回 0.3~0.7 之间的随机分数
        rng = np.random.default_rng()
        return float(rng.uniform(0.3, 0.7))