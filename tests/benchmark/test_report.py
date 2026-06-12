"""Benchmark 报告生成行为测试。"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from benchmark.report import (
    generate_experiment_report,
    generate_html_report,
    generate_json_report,
)
from benchmark.runner import BenchmarkResult


def _sample_results() -> list[BenchmarkResult]:
    return [
        BenchmarkResult(
            "img1.jpg",
            {"lpips": 0.1, "psnr": 30.0, "ssim": 0.9},
            {"bypass_rate": 1.0, "final_score": 0.2},
            [],
            1.0,
            "/tmp/img1_out.jpg",
        ),
        BenchmarkResult(
            "img2.jpg",
            {"lpips": 0.2, "psnr": 28.0, "ssim": 0.85},
            {"bypass_rate": 0.0, "final_score": 0.7},
            [],
            1.2,
            "/tmp/img2_out.jpg",
        ),
    ]


def test_generate_json_report_writes_summary():
    """JSON 报告应成功写入且 summary 包含 avg_bypass_rate。"""
    with tempfile.TemporaryDirectory() as tmp:
        out_path = Path(tmp) / "results.json"
        generate_json_report(_sample_results(), str(out_path))

        assert out_path.exists()
        report = json.loads(out_path.read_text())
        assert report["total_images"] == 2
        assert "avg_bypass_rate" in report["summary"]


def test_generate_html_report_writes_file():
    """HTML 报告应成功写入非空文件。"""
    with tempfile.TemporaryDirectory() as tmp:
        out_path = Path(tmp) / "report.html"
        generate_html_report(_sample_results(), str(out_path))

        assert out_path.exists()
        assert len(out_path.read_text()) > 0


def test_generate_experiment_report_writes_all_artifacts():
    """Experiment 报告应生成 JSON、CSV、MD 三种产物。"""
    with tempfile.TemporaryDirectory() as tmp:
        failures = [
            {
                "image_name": "img2.jpg",
                "final_detector_score": 0.7,
                "perceptual_lpips": 0.2,
            }
        ]
        paths = generate_experiment_report(
            _sample_results(), failures, tmp, ["remote:mock"]
        )

        assert Path(paths["json"]).exists()
        assert Path(paths["csv"]).exists()
        assert Path(paths["md"]).exists()

        data = json.loads(Path(paths["json"]).read_text())
        assert "wilson_ci_95" in data
        assert data["failure_count"] == 1
