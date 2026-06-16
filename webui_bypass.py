import tempfile
import uuid
import shutil
from pathlib import Path

import gradio as gr
from PIL import Image

# 仅使用 legacy 接口（已验证能正常注入 metadata 且保持对抗效果）
from bypass_ai_detector import post_process_image as legacy_post_process_image


def process_image(
    input_image,
    real_photo,
    noise,
    skin,
    fft,
    pixel,
    glcm,
    quality,
    profile,
    metadata_mode,
    seed,
    detector_feedback,
    lpips_enabled,
    lpips_blackbox,
    max_iter,
    lpips_strength,
    lpips_steps,
    quality_priority,
    method_base,
    method_adversarial,
    method_regen,
):
    if input_image is None:
        return None, None, "请上传图片"

    try:
        seed_value = None if seed is None else int(seed)
        quality_value = int(quality)

        if metadata_mode == "copy" and not real_photo:
            metadata_mode = "synthetic"

        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            input_path = tmpdir / "input.jpg"
            output_path = tmpdir / "processed_final.jpg"
            manifest_path = tmpdir / "processed_final.manifest.json"

            input_image = input_image.convert("RGB")
            input_image.save(input_path, quality=95)

            # 画质优先模式：强制使用低强度参数
            if quality_priority:
                noise = 0.30
                skin = 0.30
                fft = 0.20
                pixel = 0.010
                glcm = 0.25
                quality = 93
                max_iter = 2
                lpips_strength = 0.005
                lpips_steps = 8
                status_note = "（画质优先模式已启用，强度已自动降低）"
            else:
                status_note = ""

            # 修复 real_photo 的传递（关键修复）
            real_photo_path = None
            if real_photo and str(real_photo).lower() != "none":
                real_photo_path = str(real_photo)

            # 调用 legacy 接口（不传递 methods 参数，让 legacy 内部根据 profile 选择）
            # 同时确保 metadata_mode 和 real_photo_path 正确传递
            legacy_post_process_image(
                str(input_path),
                str(output_path),
                real_photo_path,
                noise_strength=float(noise),
                skin_strength=float(skin),
                fft_strength=float(fft),
                pixel_strength=float(pixel),
                quality=quality_value,
                glcm_strength=float(glcm),
                profile=profile,
                metadata_mode=metadata_mode,
                manifest_path=str(manifest_path),
                seed=seed_value,
            )

            if manifest_path.exists():
                stable_manifest = Path(tempfile.gettempdir()) / f"processed_final_{uuid.uuid4().hex}.manifest.json"
                stable_manifest.write_bytes(manifest_path.read_bytes())
                manifest_output = str(stable_manifest)
            else:
                manifest_output = None

            # 使用 shutil.copy 复制到持久的临时位置，确保文件在函数返回后仍然存在
            stable_output = Path(tempfile.gettempdir()) / f"processed_final_{uuid.uuid4().hex}.jpg"
            shutil.copy(str(output_path), str(stable_output))

            # 返回持久的文件路径给 gr.File，确保 EXIF 不丢失
            return str(stable_output), manifest_output, f"处理完成。manifest 已生成。{status_note}"

    except Exception as exc:
        return None, None, f"错误: {type(exc).__name__}: {exc}"


with gr.Blocks(title="AI 图片检测鲁棒性评估工具", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        "# AI 图片检测鲁棒性评估工具\n"
        "用于内部 detector 变换测试与鲁棒性评估。"
    )

    with gr.Row():
        with gr.Column():
            input_image = gr.Image(type="pil", label="输入图片")

            real_photo = gr.File(
                label="参考真实照片 EXIF（可选）",
                file_types=[".jpg", ".jpeg"],
                type="filepath",
            )

            noise = gr.Slider(0.0, 1.3, 0.78, label="噪声强度（推荐 0.2~0.4）")
            skin = gr.Slider(0.0, 1.0, 0.72, label="局部纹理强度（推荐 0.2~0.4）")
            fft = gr.Slider(0.0, 0.8, 0.45, label="FFT 频域强度（推荐 0.1~0.3）")
            pixel = gr.Slider(0.0, 0.06, 0.025, label="像素微扰强度（推荐 0.005~0.015）")
            glcm = gr.Slider(0.0, 1.0, 0.6, label="GLCM/LBP 纹理强度（推荐 0.2~0.4）")
            quality = gr.Slider(75, 95, 86, step=1, label="JPEG 质量（推荐 88~95）")

            # 画质优先模式的推荐值
            QUALITY_PRIORITY_VALUES = {
                "noise": 0.30,
                "skin": 0.30,
                "fft": 0.20,
                "pixel": 0.010,
                "glcm": 0.25,
                "quality": 93,
            }

            # 方法族 → 相关参数的映射（用于智能联动）
            METHOD_PARAM_MAP = {
                "noise": ["noise", "pixel"],
                "frequency": ["fft"],
                "texture": ["skin", "glcm"],
                "encoding": ["quality"],
                # 其他方法族（metadata, camera, lpips, watermark, regeneration*）暂不锁定特定滑块
            }

            profile = gr.Dropdown(
                choices=[
                    ("quick（快速）", "quick"),
                    ("full（完整）", "full"),
                    ("texture（纹理）", "texture"),
                    ("camera（相机）", "camera"),
                    ("metadata（元数据）", "metadata"),
                    ("adversarial（对抗）", "adversarial"),
                ],
                value="full",
                label="方法族 profile",
            )

            metadata_mode = gr.Dropdown(
                choices=[
                    ("copy（复制）", "copy"),
                    ("strip（剥离）", "strip"),
                    ("synthetic（合成）", "synthetic"),
                ],
                value="copy",
                label="EXIF/元数据模式",
            )

            seed = gr.Number(value=1234, precision=0, label="随机种子")

            # P2/P3 新能力控件
                with gr.Accordion("高级对抗选项（P2/P3/P10.4）", open=False):
                quality_priority = gr.Checkbox(
                    label="画质优先模式（推荐，自动降低强度以保持画质）",
                    value=True
                )

                # === 方法族分组显示 ===
                with gr.Accordion("基础方法族", open=True):
                    method_base = gr.CheckboxGroup(
                        choices=[
                            ("metadata（元数据）", "metadata"),
                            ("encoding（编码）", "encoding"),
                            ("noise（噪声）", "noise"),
                            ("frequency（频域）", "frequency"),
                            ("texture（纹理）", "texture"),
                            ("camera（相机）", "camera"),
                        ],
                        label="基础方法族",
                        value=[],
                    )

                with gr.Accordion("对抗方法族", open=True):
                    method_adversarial = gr.CheckboxGroup(
                        choices=[
                            ("lpips（感知攻击）", "lpips"),
                            ("watermark（水印移除）", "watermark"),
                            ("transfer_blackbox_attack（迁移黑盒攻击 P10.4）", "transfer_blackbox_attack"),
                        ],
                        label="对抗方法族",
                        value=[],
                    )

                with gr.Accordion("重生成方法族", open=True):
                    method_regen = gr.CheckboxGroup(
                        choices=[
                            ("regeneration_surrogate（代理重生成）", "regeneration_surrogate"),
                            ("regeneration（真实重生成）", "regeneration"),
                        ],
                        label="重生成方法族",
                        value=[],
                    )

                detector_feedback = gr.Checkbox(label="启用 Detector-in-the-Loop（真实闭环）", value=False)
                lpips_enabled = gr.Checkbox(label="启用 LPIPS 非语义攻击", value=False)
                lpips_blackbox = gr.Checkbox(label="使用黑盒优化（detector_feedback 时推荐）", value=True)
                max_iter = gr.Slider(1, 15, 3, step=1, label="最大迭代次数")
                lpips_strength = gr.Slider(0.001, 0.1, 0.005, label="LPIPS 扰动强度")
                lpips_steps = gr.Slider(5, 30, 10, step=1, label="LPIPS 迭代步数")

            btn = gr.Button("生成内部评估变体", variant="primary")

            # === 方法族智能联动 + 画质优先模式 ===
            def update_slider_states(method_base, method_adversarial, method_regen, is_quality_priority):
                """
                根据当前选中的方法族和画质优先模式，动态控制滑块的可编辑状态。
                """
                selected_methods = (method_base or []) + (method_adversarial or []) + (method_regen or [])

                # 如果开启画质优先模式，优先使用低值 + 锁定
                if is_quality_priority:
                    return (
                        gr.Slider(value=QUALITY_PRIORITY_VALUES["noise"], interactive=False),
                        gr.Slider(value=QUALITY_PRIORITY_VALUES["skin"], interactive=False),
                        gr.Slider(value=QUALITY_PRIORITY_VALUES["fft"], interactive=False),
                        gr.Slider(value=QUALITY_PRIORITY_VALUES["pixel"], interactive=False),
                        gr.Slider(value=QUALITY_PRIORITY_VALUES["glcm"], interactive=False),
                        gr.Slider(value=QUALITY_PRIORITY_VALUES["quality"], interactive=False),
                    )

                # 没有选择任何方法族 → 全部可编辑
                if not selected_methods:
                    return (
                        gr.Slider(interactive=True),
                        gr.Slider(interactive=True),
                        gr.Slider(interactive=True),
                        gr.Slider(interactive=True),
                        gr.Slider(interactive=True),
                        gr.Slider(interactive=True),
                    )

                # 根据选中的方法族，决定哪些参数应该启用
                active_params = set()
                for m in selected_methods:
                    if m in METHOD_PARAM_MAP:
                        active_params.update(METHOD_PARAM_MAP[m])

                return (
                    gr.Slider(interactive="noise" in active_params),
                    gr.Slider(interactive="skin" in active_params),
                    gr.Slider(interactive="fft" in active_params),
                    gr.Slider(interactive="pixel" in active_params),
                    gr.Slider(interactive="glcm" in active_params),
                    gr.Slider(interactive="quality" in active_params),
                )

            # 监听方法族变化和画质优先模式变化
            for component in [method_base, method_adversarial, method_regen, quality_priority]:
                component.change(
                    fn=update_slider_states,
                    inputs=[method_base, method_adversarial, method_regen, quality_priority],
                    outputs=[noise, skin, fft, pixel, glcm, quality],
                )

        with gr.Column():
            output_image = gr.Image(label="处理后图片")
            manifest_file = gr.File(label="运行 manifest")
            status = gr.Textbox(label="状态")

    btn.click(
        process_image,
        inputs=[
            input_image,
            real_photo,
            noise,
            skin,
            fft,
            pixel,
            glcm,
            quality,
            profile,
            metadata_mode,
            seed,
            detector_feedback,
            lpips_enabled,
            lpips_blackbox,
            max_iter,
            lpips_strength,
            lpips_steps,
            quality_priority,
            method_base,
            method_adversarial,
            method_regen,
        ],
        outputs=[output_image, manifest_file, status],
    )


if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)
