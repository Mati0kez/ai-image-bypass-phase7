"""Experiment Mode Smoke Test（使用 mock 验证统计输出和 CSV 生成）。"""

import sys
from pathlib import Path
import tempfile
import json
import csv

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from benchmark.report import generate_experiment_report
from benchmark.metrics import wilson_score_interval


def test_wilson_ci_basic():
    """验证 Wilson CI 计算正确性。"""
    lower, upper = wilson_score_interval(70, 100)
    assert 0.6 < lower < 0.8
    assert 0.6 < upper < 0.85
    assert lower < upper


def test_experiment_report_generation():
    """验证 experiment 报告生成（JSON + CSV + MD）。"""
    with tempfile.TemporaryDirectory() as tmp:
        # 模拟结果
        from benchmark.runner import BenchmarkResult
        results = [
            BenchmarkResult("img1.jpg", {"lpips": 0.1}, {"bypass_rate": 0.8, "final_score": 0.3}, [], 1.0, ""),
            BenchmarkResult("img2.jpg", {"lpips": 0.2}, {"bypass_rate": 0.4, "final_score": 0.6}, [], 1.0, ""),
        ]
        failures = [
            {"image_name": "img2.jpg", "final_detector_score": 0.6, "perceptual_lpips": 0.2}
        ]

        paths = generate_experiment_report(results, failures, tmp, ["remote:mock"])

        # 检查文件存在
        assert Path(paths["json"]).exists()
        assert Path(paths["csv"]).exists()
        assert Path(paths["md"]).exists()

        # 检查 JSON 内容
        data = json.loads(Path(paths["json"]).read_text())
        assert "wilson_ci_95" in data
        assert data["failure_count"] == 1

        # 检查 CSV
        with open(paths["csv"]) as f:
            reader = csv.reader(f)
            rows = list(reader)
            assert len(rows) == 2  # header + 1 failure

        print("✅ Experiment report generation test 通过！")