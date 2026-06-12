import tempfile
import uuid
from pathlib import Path

import gradio as gr
from PIL import Image

from bypass_ai_detector import post_process_image


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

            post_process_image(
                str(input_path),
                str(output_path),
                str(real_photo) if real_photo else None,
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

            with Image.open(output_path) as img:
                result_image = img.copy()

            if manifest_path.exists():
                stable_manifest = Path(tempfile.gettempdir()) / f"processed_final_{uuid.uuid4().hex}.manifest.json"
                stable_manifest.write_bytes(manifest_path.read_bytes())
                manifest_output = str(stable_manifest)
            else:
                manifest_output = None

            return result_image, manifest_output, "处理完成。manifest 已生成。"

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

            noise = gr.Slider(0.0, 1.3, 0.78, label="噪声强度")
            skin = gr.Slider(0.0, 1.0, 0.72, label="局部纹理强度")
            fft = gr.Slider(0.0, 0.8, 0.45, label="FFT 频域强度")
            pixel = gr.Slider(0.0, 0.06, 0.025, label="像素微扰强度")
            glcm = gr.Slider(0.0, 1.0, 0.6, label="GLCM/LBP 纹理强度")
            quality = gr.Slider(75, 95, 86, step=1, label="JPEG 质量")

            profile = gr.Dropdown(
                ["quick", "full", "texture", "camera", "metadata"],
                value="full",
                label="方法族 profile",
            )

            metadata_mode = gr.Dropdown(
                ["copy", "strip", "synthetic"],
                value="copy",
                label="EXIF/元数据模式",
            )

            seed = gr.Number(value=1234, precision=0, label="随机种子")

            btn = gr.Button("生成内部评估变体", variant="primary")

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
        ],
        outputs=[output_image, manifest_file, status],
    )


if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860)
