"""Transform Pipeline - 接受 TransformConfig 的核心处理流程。

负责 Module 调度、最终增强、EXIF 注入、保存和 manifest 生成。
"""

import json
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

from .config import TransformConfig
from .registry import METHOD_FAMILIES, TRANSFORM_MODULES, _selected_modules
from .strength import StrengthOverride  # noqa: F401

# 延迟导入 detector_loop，避免循环依赖
from detector_loop.loop import DetectorLoop, DetectorLoopConfig  # noqa: F401


def post_process_image(config: TransformConfig) -> str:
    """核心 pipeline：根据 TransformConfig 执行完整处理流程。

    Returns:
        输出文件路径。
    """
    # 优先使用用户自定义的方法族列表（用于 WebUI 逐项测试）
    if getattr(config, "methods", None):
        selected = list(config.methods)
    else:
        selected = list(_selected_modules(config.profile))

    # 动态调度：根据 config 标志启用实验性对抗模块并调整顺序
    # 基础族（已由 profile 选定）→ LPIPS → Watermark → Regeneration
    if getattr(config, "lpips_enabled", False) and "lpips" in METHOD_FAMILIES:
        if "lpips" not in selected:
            selected.append("lpips")

    if getattr(config, "watermark_remove", False) and "watermark" in METHOD_FAMILIES:
        if "watermark" not in selected:
            selected.append("watermark")

    # Regeneration 模式选择：local/remote 优先使用 regeneration，否则回退 surrogate
    regen_mode = getattr(config, "regeneration_mode", "surrogate")
    if regen_mode in ("local", "remote") and "regeneration" in METHOD_FAMILIES:
        if "regeneration" not in selected:
            selected.append("regeneration")
        # 移除 surrogate（若已存在）
        if "regeneration_surrogate" in selected:
            selected.remove("regeneration_surrogate")
    else:
        # surrogate 模式：确保 surrogate 在列表中（profile 已包含）
        if "regeneration" in selected and "regeneration_surrogate" not in selected:
            # 保留 regeneration（若用户显式要求）
            pass

    print("Starting internal detector robustness processing (TransformConfig mode)...")
    print(f"Method families: {', '.join(selected)}")

    image = Image.open(config.input_path).convert("RGB")

    # 按顺序调用已注册的 Module
    for name in selected:
        module = TRANSFORM_MODULES.get(name)
        if module is None:
            print(f"Warning: Module '{name}' not registered, skipping.")
            continue
        # 注意：rng 使用 config.seed 保证可复现
        rng = np.random.default_rng(config.seed)
        image = module.apply(image, config, rng)

    # 最终增强（与 legacy 一致）
    image = image.filter(ImageFilter.UnsharpMask(radius=1.0, percent=60, threshold=3))
    image = ImageEnhance.Contrast(image).enhance(1.04)

    # EXIF / 元数据注入（延迟导入以避免循环依赖）
    exif_bytes = None
    if "metadata" in selected:
        from bypass_ai_detector import _metadata_bytes
        exif_bytes = _metadata_bytes(
            config.metadata_mode, config.real_photo_path, image
        )

    # 保存参数
    save_params: Dict[str, Any] = {
        "quality": int(np.clip(config.quality - 3, 35, 98)),
        "optimize": True,
        "progressive": True,
    }
    if exif_bytes:
        save_params["exif"] = exif_bytes

    # Detector-in-the-Loop 真实闭环（P2）：在保存前执行迭代优化
    detector_scores: List[Dict[str, Any]] = []
    if config.detector_feedback:
        print("[Pipeline] detector_feedback=True，触发 Detector-in-the-Loop 真实闭环")
        loop_config = DetectorLoopConfig(
            detector_name=config.detector_name,
            detector_threshold=config.detector_threshold,
            max_iter=config.max_iter,
            early_stop_epsilon=config.early_stop_epsilon,
            adaptive_strength=config.detector_adaptive_strength,
            early_stop_patience=config.detector_early_stop_patience,
        )
        detector_loop = DetectorLoop(loop_config)

        # 构造 transform_fn：使用当前 selected modules + override 重新变换
        def _transform_with_override(img: Image.Image, override: StrengthOverride) -> Image.Image:
            current = img
            for name in selected:
                module = TRANSFORM_MODULES.get(name)
                if module is None:
                    continue
                rng = np.random.default_rng(config.seed)
                try:
                    current = module.apply(current, config, rng, strength_override=override)
                except TypeError:
                    # 兼容尚未更新 strength_override 的旧 Module
                    current = module.apply(current, config, rng)
            return current

        # 真实闭环执行（初始分数由 detector.score 获得）
        final_img, history = detector_loop.run(
            image,
            initial_score=None,
            transform_fn=_transform_with_override,
        )
        image = final_img  # 使用迭代优化后的图像
        detector_scores = [
            {"step": step, "detector": name, "score": round(score, 4)}
            for step, name, score in history
        ]
        print(f"[Pipeline] Detector 真实闭环历史: {detector_scores}")

    # 保存最终图像
    Path(config.output_path).parent.mkdir(parents=True, exist_ok=True)
    image.save(config.output_path, "JPEG", **save_params)
    print(f"Saved output: {config.output_path}")

    # 生成 manifest
    if config.manifest_path:
        manifest: Dict[str, Any] = {
            "purpose": "internal_detector_robustness_evaluation",
            "method_families": list(selected),
            "input_path": str(config.input_path),
            "output_path": str(config.output_path),
            "reference_photo": str(config.real_photo_path) if config.real_photo_path else None,
            "metadata_mode": config.metadata_mode,
            "detector_feedback": config.detector_feedback,
            "detector_scores": detector_scores if config.detector_feedback else None,
            "notes": [
                "detector_feedback records simulated score history; image is not re-transformed per iteration (Phase 7 P2 scope).",
                "No external platform bypass success claim is produced.",
                f"Active adversarial modules: lpips={getattr(config, 'lpips_enabled', False)}, watermark={getattr(config, 'watermark_remove', False)}, regeneration={regen_mode}.",
            ],
        }
        Path(config.manifest_path).write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"Saved manifest: {config.manifest_path}")

    return config.output_path
