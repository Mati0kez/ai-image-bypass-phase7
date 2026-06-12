"""Benchmark 基准评估框架。

提供 BenchmarkRunner、指标计算和报告生成功能，
用于系统性地评估变换 pipeline 对 detector 的鲁棒性。
"""

from .runner import BenchmarkRunner
from .metrics import compute_perceptual_metrics, compute_detection_metrics
from .report import generate_json_report, generate_html_report

__all__ = [
    "BenchmarkRunner",
    "compute_perceptual_metrics",
    "compute_detection_metrics",
    "generate_json_report",
    "generate_html_report",
]
