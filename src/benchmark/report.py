"""报告生成模块。

支持 JSON（结构化数据）和 HTML（可视化报告）两种格式。
"""

import json
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime

import numpy as np

from .runner import BenchmarkResult


def generate_json_report(results: List[BenchmarkResult], output_path: str) -> str:
    """生成 JSON 格式的结构化报告。"""
    report = {
        "generated_at": datetime.now().isoformat(),
        "total_images": len(results),
        "summary": _compute_summary(results),
        "results": [
            {
                "image_name": r.image_name,
                "perceptual": r.perceptual,
                "detection": r.detection,
                "detector_history": r.detector_history,
                "runtime_sec": round(r.runtime_sec, 3),
                "output_path": r.output_path,
            }
            for r in results
        ],
    }

    Path(output_path).write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return output_path


def generate_html_report(results: List[BenchmarkResult], output_path: str) -> str:
    """生成 HTML 可视化报告（简化版，包含表格和基本统计）。"""
    summary = _compute_summary(results)

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Benchmark Report - AI Image Detection Bypass</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
        th {{ background-color: #f2f2f2; }}
        .summary {{ background-color: #e8f4fd; padding: 15px; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>AI Image Detection Bypass Benchmark Report</h1>
    <p>Generated at: {datetime.now().isoformat()}</p>
    
    <div class="summary">
        <h2>Summary</h2>
        <p>Total Images: {summary['total_images']}</p>
        <p>Average Bypass Rate: {summary['avg_bypass_rate']:.2%}</p>
        <p>Average PSNR: {summary['avg_psnr']:.2f} dB</p>
        <p>Average SSIM: {summary['avg_ssim']:.3f}</p>
        <p>Average LPIPS: {summary['avg_lpips']:.4f}</p>
    </div>
    
    <h2>Detailed Results</h2>
    <table>
        <tr>
            <th>Image</th>
            <th>Bypass Rate</th>
            <th>Final Score</th>
            <th>PSNR</th>
            <th>SSIM</th>
            <th>LPIPS</th>
            <th>Runtime (s)</th>
        </tr>
"""
    for r in results:
        html += f"""        <tr>
            <td>{r.image_name}</td>
            <td>{r.detection.get('bypass_rate', 0):.2%}</td>
            <td>{r.detection.get('final_score', 0):.3f}</td>
            <td>{r.perceptual.get('psnr', 0):.2f}</td>
            <td>{r.perceptual.get('ssim', 0):.3f}</td>
            <td>{r.perceptual.get('lpips', 0):.4f}</td>
            <td>{r.runtime_sec:.2f}</td>
        </tr>
"""

    html += """    </table>
</body>
</html>"""

    Path(output_path).write_text(html, encoding="utf-8")
    return output_path


def _compute_summary(results: List[BenchmarkResult]) -> Dict[str, Any]:
    """计算汇总统计。"""
    if not results:
        return {}

    bypass_rates = [r.detection.get("bypass_rate", 0) for r in results]
    psnrs = [r.perceptual.get("psnr", 0) for r in results]
    ssims = [r.perceptual.get("ssim", 0) for r in results]
    lpipses = [r.perceptual.get("lpips", 0) for r in results]

    return {
        "total_images": len(results),
        "avg_bypass_rate": float(np.mean(bypass_rates)),
        "avg_psnr": float(np.mean(psnrs)),
        "avg_ssim": float(np.mean(ssims)),
        "avg_lpips": float(np.mean(lpipses)),
    }


def generate_experiment_report(
    results: List[BenchmarkResult],
    failure_cases: List[Dict[str, Any]],
    output_dir: str,
    platforms: List[str],
) -> Dict[str, str]:
    """生成 experiment 模式的报告：JSON + CSV + MD。"""
    from .metrics import wilson_score_interval
    import csv

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 1. experiment_results.json
    bypass_rates = [r.detection.get("bypass_rate", 0) for r in results]
    total_bypass = sum(1 for br in bypass_rates if br > 0)
    n = len(results)
    lower, upper = wilson_score_interval(total_bypass, n)

    json_report = {
        "generated_at": datetime.now().isoformat(),
        "platforms": platforms,
        "total_samples": n,
        "bypass_rate": float(np.mean(bypass_rates)),
        "wilson_ci_95": {"lower": lower, "upper": upper},
        "avg_perceptual": _compute_summary(results),
        "failure_count": len(failure_cases),
    }
    json_path = output_path / "experiment_results.json"
    json_path.write_text(json.dumps(json_report, ensure_ascii=False, indent=2), encoding="utf-8")

    # 2. failure_cases.csv
    csv_path = output_path / "failure_cases.csv"
    if failure_cases:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=failure_cases[0].keys())
            writer.writeheader()
            writer.writerows(failure_cases)

    # 3. summary.md
    md_path = output_path / "summary.md"
    md_content = f"""# Experiment Summary

- Platforms: {', '.join(platforms)}
- Total Samples: {n}
- Bypass Rate: {json_report['bypass_rate']:.2%}
- 95% Wilson CI: [{lower:.2%}, {upper:.2%}]
- Failures: {len(failure_cases)}

See experiment_results.json for full data.
"""
    md_path.write_text(md_content, encoding="utf-8")

    return {
        "json": str(json_path),
        "csv": str(csv_path),
        "md": str(md_path),
    }