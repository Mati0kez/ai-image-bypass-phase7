#!/usr/bin/env python3
"""
CLI 测试脚本 - 快速验证任意方法族组合

用法示例：
    python run.py --methods frequency_peaks_cleansing,prnu_simulation
    python run.py --methods frequency_peaks_cleansing,prnu_simulation,gradient_edge_aware_perturbation,transfer_blackbox_attack
"""

import argparse
import sys
from pathlib import Path
from typing import List

# 确保能导入 src 下的 transform_core
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from transform_core.config import TransformConfig
from transform_core.pipeline import post_process_image


def get_output_stem(input_stem: str, methods: List[str]) -> str:
    """生成输出文件名（不含扩展名）"""
    if methods:
        methods_str = "_".join(methods)
        return f"{input_stem}-{methods_str}"
    return input_stem


def process_folder(
    input_dir: Path,
    output_dir: Path,
    methods: List[str],
    profile: str,
    quality: int,
    seed: int,
):
    """批量处理 images/ 目录下的所有图片"""
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 支持的图片格式
    exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    image_files = [f for f in input_dir.iterdir() if f.suffix.lower() in exts]

    if not image_files:
        print(f"[WARN] {input_dir} 目录下没有找到图片文件")
        return

    print(f"找到 {len(image_files)} 张图片，开始处理...")
    print(f"启用方法族: {methods if methods else f'profile={profile}'}")

    for img_file in sorted(image_files):
        stem = img_file.stem
        suffix = img_file.suffix

        output_stem = get_output_stem(stem, methods)
        output_path = output_dir / f"{output_stem}{suffix}"
        manifest_path = output_dir / f"{output_stem}.manifest.json"

        print(f"\n处理: {img_file.name} -> {output_path.name}")

        config = TransformConfig(
            input_path=str(img_file),
            output_path=str(output_path),
            manifest_path=str(manifest_path),
            profile=profile,
            seed=seed,
            quality=quality,
            methods=methods if methods else None,
        )

        try:
            result_path = post_process_image(config)
            print(f"  ✓ 完成 -> {Path(result_path).name}")
        except Exception as e:
            print(f"  ✗ 失败: {e}")


def main():
    parser = argparse.ArgumentParser(description="CLI 方法族快速测试工具")
    parser.add_argument(
        "--methods",
        type=str,
        default="",
        help="逗号分隔的方法族列表，例如：frequency_peaks_cleansing,prnu_simulation",
    )
    parser.add_argument(
        "--profile",
        type=str,
        default="full",
        help="预定义 profile (quick/full/adversarial 等)",
    )
    parser.add_argument("--quality", type=int, default=90, help="输出 JPEG 质量")
    parser.add_argument("--seed", type=int, default=1234, help="随机种子")

    args = parser.parse_args()

    methods_list = [m.strip() for m in args.methods.split(",") if m.strip()] if args.methods else []

    input_dir = Path(__file__).parent / "images"
    output_dir = Path(__file__).parent / "outputs"

    process_folder(
        input_dir=input_dir,
        output_dir=output_dir,
        methods=methods_list,
        profile=args.profile,
        quality=args.quality,
        seed=args.seed,
    )

    print("\n全部处理完成！结果保存在 outputs/ 目录")


if __name__ == "__main__":
    main()