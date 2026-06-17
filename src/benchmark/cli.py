"""Benchmark CLI 入口。

提供 `benchmark` 命令行工具，支持指定输入目录和参数。
"""

import argparse
from pathlib import Path
from .runner import BenchmarkRunner, BenchmarkConfig
from .report import generate_json_report, generate_html_report, generate_experiment_report


def main():
    parser = argparse.ArgumentParser(description="AI Image Detection Bypass Benchmark")
    parser.add_argument(
        "--input-dir",
        type=str,
        default="data/benchmark_samples",
        help="输入图像目录",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="benchmark_output",
        help="输出目录（JSON + HTML 报告）",
    )
    parser.add_argument(
        "--detector",
        type=str,
        default="local:resnet50",
        help="Detector 名称 (local:xxx 或 remote:hive)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Detector bypass 阈值",
    )
    parser.add_argument(
        "--max-images",
        type=int,
        default=20,
        help="最大评估图像数量",
    )
    parser.add_argument(
        "--profile",
        type=str,
        default="full",
        help="Transform profile",
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="benchmark",
        choices=["benchmark", "experiment"],
        help="运行模式：benchmark（快速评估）或 experiment（真实对抗验证）",
    )
    parser.add_argument(
        "--platforms",
        type=str,
        default="local:resnet50",
        help="实验模式下的平台列表（逗号分隔），例如 remote:hive,remote:mock",
    )
    parser.add_argument(
        "--samples",
        type=int,
        default=100,
        help="实验模式下的样本数量",
    )

    args = parser.parse_args()

    platforms = (
        [p.strip() for p in args.platforms.split(",")]
        if args.mode == "experiment"
        else [args.detector]
    )

    config = BenchmarkConfig(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        detector_name=platforms[0] if args.mode == "experiment" else args.detector,
        detector_threshold=args.threshold,
        max_images=args.samples if args.mode == "experiment" else args.max_images,
        profile=args.profile,
        mode=args.mode,
        platforms=platforms,
        sample_size=args.samples,
    )

    runner = BenchmarkRunner(config)
    results = runner.run()

    if args.mode == "experiment":
        report_paths = generate_experiment_report(
            results, runner.failure_cases, args.output_dir, config.platforms
        )
        print("\n✅ Experiment 完成！")
        print(f"  - JSON: {report_paths['json']}")
        print(f"  - CSV (failures): {report_paths['csv']}")
        print(f"  - MD: {report_paths['md']}")
    else:
        # 生成报告
        json_path = Path(args.output_dir) / "results.json"
        html_path = Path(args.output_dir) / "report.html"

        generate_json_report(results, str(json_path))
        generate_html_report(results, str(html_path))

        print("\n✅ Benchmark 完成！")
        print(f"  - JSON 报告: {json_path}")
        print(f"  - HTML 报告: {html_path}")


if __name__ == "__main__":
    main()
