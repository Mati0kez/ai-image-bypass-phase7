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
from typing import List, Optional

# 确保能导入 src 下的 transform_core 和根目录的 legacy bypass_ai_detector
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from transform_core.config import TransformConfig
from transform_core.pipeline import post_process_image


def method_enabled_flags(methods: List[str]) -> dict:
    """显式选中某方法族时，同步设置对应的 enabled 标志（与 WebUI 一致）。"""
    selected = set(methods)
    flags = {
        "frequency_peaks_cleansing_enabled": "frequency_peaks_cleansing" in selected,
        "prnu_simulation_enabled": "prnu_simulation" in selected,
        "gradient_edge_aware_perturbation_enabled": "gradient_edge_aware_perturbation" in selected,
        "transfer_blackbox_attack_enabled": "transfer_blackbox_attack" in selected,
        "lpips_enabled": "lpips" in selected,
        "watermark_remove": "watermark" in selected,
        "diffusion_reconstruction_enabled": "diffusion_reconstruction" in selected,
    }
    return flags




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
    prnu_ref: Optional[str] = None,
    regeneration_model: Optional[str] = None,
    diffusion_model: Optional[str] = None,
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

        config_kwargs = {
            "input_path": str(img_file),
            "output_path": str(output_path),
            "manifest_path": str(manifest_path),
            "profile": profile,
            "seed": seed,
            "quality": quality,
            "methods": methods if methods else None,
        }
        if methods:
            config_kwargs.update(method_enabled_flags(methods))
        if prnu_ref and "prnu_simulation" in methods:
            config_kwargs["prnu_simulation_reference_path"] = prnu_ref
        if regeneration_model:
            config_kwargs["regeneration_mode"] = "local"
            config_kwargs["regeneration_model_path"] = regeneration_model
        if diffusion_model and "diffusion_reconstruction" in methods:
            config_kwargs["diffusion_reconstruction_enabled"] = True
            config_kwargs["diffusion_reconstruction_mode"] = "local"
            config_kwargs["diffusion_reconstruction_model_path"] = diffusion_model
        if (regeneration_model is None or regeneration_model == "") and "regeneration" in methods:
            print("[WARN] regeneration 方法族未指定 --regeneration-model，将回退 surrogate")
        if (diffusion_model is None or diffusion_model == "") and "diffusion_reconstruction" in methods:
            print("[WARN] diffusion_reconstruction 方法族未指定 --diffusion-model，将回退 surrogate")

        config = TransformConfig(**config_kwargs)

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
    parser.add_argument(
        "--prnu-ref",
        type=str,
        default="",
        help="PRNU 参考图像路径（可选；未指定时使用自生成指纹）",
    )
    parser.add_argument(
        "--regeneration-model",
        type=str,
        default="",
        help="Stable Diffusion 模型路径（用于 regeneration / diffusion_reconstruction 真实 img2img）",
    )
    parser.add_argument(
        "--diffusion-model",
        type=str,
        default="",
        help="Stable Diffusion 模型路径（用于 diffusion_reconstruction）",
    )

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
        prnu_ref=args.prnu_ref.strip() or None,
        regeneration_model=args.regeneration_model.strip() or None,
        diffusion_model=args.diffusion_model.strip() or None,
    )

    print("\n全部处理完成！结果保存在 outputs/ 目录")


if __name__ == "__main__":
    main()