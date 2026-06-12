"""BenchmarkRunner 核心模块。

负责批量加载图像、调用 pipeline、收集 perceptual 和 detection 指标。
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from typing import Literal
import time
from PIL import Image
import numpy as np

from transform_core.config import TransformConfig
from transform_core.pipeline import post_process_image
from .metrics import compute_perceptual_metrics, compute_detection_metrics

# 延迟导入 external_validation，避免循环依赖
from external_validation.validation_runner import ValidationRunner  # noqa: F401


@dataclass
class BenchmarkResult:
    """单张图像的基准评估结果。"""

    image_name: str
    perceptual: Dict[str, float]
    detection: Dict[str, float]
    detector_history: List[Dict[str, Any]]
    runtime_sec: float
    output_path: str


@dataclass
class BenchmarkConfig:
    """基准评估配置。"""

    input_dir: str
    output_dir: str
    detector_name: str = "local:resnet50"
    detector_threshold: float = 0.5
    max_images: int = 20
    profile: str = "full"
    detector_feedback: bool = True
    mode: Literal["benchmark", "experiment"] = "benchmark"
    platforms: list[str] = field(default_factory=lambda: ["local:resnet50"])
    sample_size: int = 100


class BenchmarkRunner:
    """基准评估运行器。"""

    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.results: List[BenchmarkResult] = []
        self.failure_cases: List[Dict[str, Any]] = []

    def run(self) -> List[BenchmarkResult]:
        """执行基准评估。"""
        input_path = Path(self.config.input_dir)
        output_path = Path(self.config.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        image_files = list(input_path.glob("*.jpg")) + list(input_path.glob("*.png"))
        image_files = image_files[: self.config.max_images]

        print(f"[BenchmarkRunner] 找到 {len(image_files)} 张图像，开始评估...")

        for img_file in image_files:
            start_time = time.time()
            result = self._evaluate_single_image(img_file, output_path)
            result.runtime_sec = time.time() - start_time
            self.results.append(result)
            print(f"  - {img_file.name}: bypass_rate={result.detection.get('bypass_rate', 0):.2f}, runtime={result.runtime_sec:.2f}s")

        return self.results

    def _evaluate_single_image(
        self, img_path: Path, output_dir: Path
    ) -> BenchmarkResult:
        """评估单张图像。"""
        original = Image.open(img_path).convert("RGB")

        # 构造 TransformConfig
        out_path = output_dir / f"{img_path.stem}_transformed.jpg"
        manifest_path = output_dir / f"{img_path.stem}_manifest.json"

        is_external = self.config.detector_name.startswith("remote:")

        config = TransformConfig(
            input_path=str(img_path),
            output_path=str(out_path),
            manifest_path=str(manifest_path),
            profile=self.config.profile,
            detector_feedback=False if is_external else self.config.detector_feedback,
            detector_name=self.config.detector_name,
            detector_threshold=self.config.detector_threshold,
            max_iter=5,
        )

        # 调用 pipeline（外部验证时禁用内部 detector loop）
        post_process_image(config)

        # 读取 manifest 获取 detector 分数历史
        import json
        detector_history = []
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text())
            detector_history = manifest.get("detector_scores", [])

        # 外部验证路由：使用 ValidationRunner 获取真实平台分数
        if is_external:
            vr = ValidationRunner(detector_name=self.config.detector_name)
            transformed = Image.open(out_path).convert("RGB")
            # 模拟多次评分以生成历史（实际可只评一次）
            ext_scores = []
            for step in range(3):
                s = vr.score(transformed)
                ext_scores.append({"step": step, "detector": self.config.detector_name, "score": round(s, 4)})
            detector_history = ext_scores

        # 计算 perceptual 指标
        transformed = Image.open(out_path).convert("RGB")
        perceptual = compute_perceptual_metrics(original, transformed)

        # 计算 detection 指标
        detection = compute_detection_metrics(
            detector_history, threshold=self.config.detector_threshold
        )

        # 失败案例收集（experiment 模式或 final_score >= threshold）
        final_score = detection.get("final_score", 1.0)
        if final_score >= self.config.detector_threshold:
            self.failure_cases.append({
                "image_name": img_path.name,
                "original_path": str(img_path),
                "transformed_path": str(out_path),
                "final_detector_score": round(final_score, 4),
                "perceptual_lpips": perceptual.get("lpips", 0.0),
                "platform": self.config.detector_name,
            })

        return BenchmarkResult(
            image_name=img_path.name,
            perceptual=perceptual,
            detection=detection,
            detector_history=detector_history,
            runtime_sec=0.0,
            output_path=str(out_path),
        )