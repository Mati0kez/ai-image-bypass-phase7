"""Smoke Test for BenchmarkRunner（使用 mock 数据验证流程）。"""

import sys
from pathlib import Path
import tempfile
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from benchmark.runner import BenchmarkRunner, BenchmarkConfig
from benchmark.report import generate_json_report, generate_html_report
from PIL import Image
import numpy as np


def test_benchmark_runner_smoke():
    """验证 BenchmarkRunner 能正常运行并生成结果（使用临时目录）。"""
    with tempfile.TemporaryDirectory() as tmp:
        input_dir = Path(tmp) / "input"
        output_dir = Path(tmp) / "output"
        input_dir.mkdir()

        # 创建 3 张测试图像
        for i in range(3):
            img = Image.fromarray(
                np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
            )
            img.save(input_dir / f"test_{i}.jpg")

        config = BenchmarkConfig(
            input_dir=str(input_dir),
            output_dir=str(output_dir),
            max_images=3,
            detector_feedback=False,
        )

        runner = BenchmarkRunner(config)
        results = runner.run()

        assert len(results) == 3
        assert all(r.perceptual for r in results)
        assert all(r.detection for r in results)

        # 生成报告
        json_path = output_dir / "results.json"
        html_path = output_dir / "report.html"
        generate_json_report(results, str(json_path))
        generate_html_report(results, str(html_path))

        assert json_path.exists()
        assert html_path.exists()

        # 验证 JSON 内容
        report = json.loads(json_path.read_text())
        assert report["total_images"] == 3
        assert "avg_bypass_rate" in report["summary"]

        print("✅ Benchmark smoke test 通过！")