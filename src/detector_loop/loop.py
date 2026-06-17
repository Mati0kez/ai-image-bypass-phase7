"""DetectorLoop 迭代优化框架。

实现 detector-in-the-loop 反馈循环，支持 early stopping 和参数自适应。
真实闭环：每轮调用 detector.score()，根据真实分数动态调整 strength。
"""

from typing import List, Tuple, Callable, Optional
from dataclasses import dataclass
from PIL import Image

from .detector_interface import DetectorInterface
from . import LocalDetectorAdapter, HiveAPIDetectorAdapter

# 延迟导入以避免循环依赖
from transform_core.strength import StrengthOverride  # noqa: F401


@dataclass
class DetectorLoopConfig:
    """Detector 反馈循环配置。"""

    detector_name: str = "local:resnet50"
    detector_threshold: float = 0.5
    max_iter: int = 10
    early_stop_epsilon: float = 0.01
    adaptive_strength: bool = True
    early_stop_patience: int = 2


class DetectorLoop:
    """Detector-in-the-Loop 迭代优化器。

    根据外部 detector 的分数，迭代调整图像变换强度，直到满足阈值或达到最大迭代次数。
    """

    def __init__(self, config: DetectorLoopConfig):
        self.config = config
        self.detector = self._create_detector(config.detector_name)
        self.history: List[Tuple[int, str, float]] = []  # (step, detector_name, score)
        self._no_improve_count = 0

    def _create_detector(self, name: str) -> DetectorInterface:
        """根据名称创建对应的 Detector 适配器。"""
        if name.startswith("local:"):
            model_name = name.split(":", 1)[1]
            return LocalDetectorAdapter(model_name=model_name)
        elif name.startswith("remote:hive"):
            return HiveAPIDetectorAdapter()
        else:
            # 默认使用本地模型
            return LocalDetectorAdapter(model_name="resnet50")

    def run(
        self,
        img: Image.Image,
        initial_score: Optional[float] = None,
        transform_fn: Optional[Callable[[Image.Image, StrengthOverride], Image.Image]] = None,
    ) -> Tuple[Image.Image, List[Tuple[int, str, float]]]:
        """执行真实反馈闭环。

        Args:
            img: 输入图像。
            initial_score: 初始 detector 分数（若为 None，则由 detector.score(img) 获得）。
            transform_fn: 可选的变换函数，签名 (img, strength_override) -> new_img。
                          若提供，则每轮使用 override 重新变换图像。

        Returns:
            (优化后的图像, 迭代历史列表)
        """
        current_img = img.copy()

        # 真实初始分数：优先使用 detector.score
        if initial_score is None:
            current_score = self.detector.score(current_img)
        else:
            current_score = initial_score

        self.history = [(0, self.detector.name, current_score)]
        current_override = StrengthOverride()

        for step in range(1, self.config.max_iter + 1):
            # 1. 若提供 transform_fn，则使用当前 override 重新变换图像
            if transform_fn is not None:
                current_img = transform_fn(current_img, current_override)

            # 2. 真实 detector 评分
            current_score = self.detector.score(current_img)

            self.history.append((step, self.detector.name, current_score))

            # 3. Early stopping with patience
            if len(self.history) >= 2:
                prev_score = self.history[-2][2]
                if abs(current_score - prev_score) < self.config.early_stop_epsilon:
                    self._no_improve_count += 1
                    if self._no_improve_count >= self.config.early_stop_patience:
                        print(f"[DetectorLoop] Early stopping at step {step} (patience reached)")
                        break
                else:
                    self._no_improve_count = 0

            if current_score < self.config.detector_threshold:
                print(
                    f"[DetectorLoop] Score {current_score:.3f} < threshold {self.config.detector_threshold:.3f}, stopping."
                )
                break

            # 4. 自适应强度：根据真实 gap 更新 override
            if self.config.adaptive_strength:
                gap = max(0.0, current_score - self.config.detector_threshold)
                # 简单线性映射示例（可扩展更复杂策略）
                noise_adj = min(2.0, 1.0 + gap * 1.5)
                fft_adj = min(2.0, 1.0 + gap * 1.2)
                pixel_adj = min(2.0, 1.0 + gap * 0.8)
                current_override = StrengthOverride(
                    noise_scale=noise_adj,
                    fft_scale=fft_adj,
                    pixel_scale=pixel_adj,
                )
                print(
                    f"[DetectorLoop] Step {step} real adaptive: noise*{noise_adj:.2f}, fft*{fft_adj:.2f}, pixel*{pixel_adj:.2f}"
                )

        return current_img, self.history
