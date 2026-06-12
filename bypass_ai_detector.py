import json
import os
import random
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

# 使 legacy 入口能找到 transform_core
sys.path.insert(0, str(Path(__file__).parent / "src"))

from transform_core.config import TransformConfig
from transform_core.pipeline import post_process_image as _new_post_process_image

try:
    import cv2
except ImportError:  # The core pipeline has Pillow fallbacks.
    cv2 = None

try:
    import piexif
except ImportError:  # Pillow EXIF support is enough for synthetic/copy-lite modes.
    piexif = None


METHOD_FAMILIES = (
    "metadata",
    "encoding",
    "noise",
    "frequency",
    "texture",
    "camera",
    "regeneration_surrogate",
)

PROFILE_METHODS = {
    "quick": ("metadata", "encoding", "noise", "frequency"),
    "full": METHOD_FAMILIES,
    "texture": ("texture",),
    "camera": ("camera",),
    "metadata": ("metadata",),
}


def _rng(seed=None):
    return np.random.default_rng(seed)


def _to_array(image):
    return np.asarray(image.convert("RGB"), dtype=np.float32)


def _from_array(values):
    return Image.fromarray(np.clip(values, 0, 255).astype(np.uint8), "RGB")


def _gray(values):
    return values[:, :, 0] * 0.299 + values[:, :, 1] * 0.587 + values[:, :, 2] * 0.114


def add_pixel_perturbation(img_np, strength=0.025, seed=None):
    """Low-amplitude pixel perturbation for detector robustness evaluation."""
    perturb = _rng(seed).normal(0, max(strength, 0.0) * 255.0, img_np.shape).astype(np.float32)
    return np.clip(img_np + perturb, 0, 255).astype(np.uint8)


def fft_perturb(image, strength=0.45, seed=None):
    """FFT frequency shaping that avoids detector-score feedback loops."""
    generator = _rng(seed)
    img_np = _to_array(image)
    result = img_np.copy()
    rows, cols = img_np.shape[:2]
    y, x = np.ogrid[:rows, :cols]
    center_y, center_x = rows // 2, cols // 2
    dist = np.sqrt((y - center_y) ** 2 + (x - center_x) ** 2)
    dist = dist / max(float(dist.max()), 1.0)
    low_freq = dist < 0.16

    for channel in range(3):
        shifted = np.fft.fftshift(np.fft.fft2(img_np[:, :, channel]))
        magnitude = np.abs(shifted)
        phase = np.angle(shifted)

        rolloff = 1.0 / np.maximum(dist, 0.04)
        rolloff = rolloff / np.mean(rolloff[~low_freq])
        rolloff = np.clip(rolloff, 0.65, 1.45)
        random_gain = 1.0 + generator.normal(0, max(strength, 0.0) * 0.08, magnitude.shape)
        phase_noise = generator.normal(0, max(strength, 0.0) * 0.045, phase.shape)

        magnitude = np.where(low_freq, magnitude, magnitude * rolloff * random_gain)
        phase = np.where(low_freq, phase, phase + phase_noise)
        rebuilt = magnitude * np.exp(1j * phase)
        result[:, :, channel] = np.real(np.fft.ifft2(np.fft.ifftshift(rebuilt)))

    return _from_array(result)


def glcm_texture_enhance(image, strength=0.6, seed=None):
    """GLCM/LBP-inspired local texture shift."""
    values = _to_array(image)
    gray = _gray(values).astype(np.uint8)

    if cv2 is not None:
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
    else:
        enhanced = np.asarray(ImageOps.autocontrast(Image.fromarray(gray)), dtype=np.uint8)

    shifted_right = np.roll(gray, 1, axis=1)
    shifted_down = np.roll(gray, 1, axis=0)
    lbp_like = ((gray > shifted_right).astype(np.float32) + (gray > shifted_down).astype(np.float32)) * 127.5
    noise = _rng(seed).normal(0, 5.0, gray.shape)
    texture = (0.65 * enhanced.astype(np.float32) + 0.35 * lbp_like + noise)[:, :, None]
    texture_rgb = np.repeat(texture, 3, axis=2)
    return _from_array(values * (1.0 - strength * 0.22) + texture_rgb * (strength * 0.22))


def add_encoding_geometric_transforms(image, quality=88):
    """JPEG, crop, resize, blur/sharpen, color and white-balance style transforms."""
    out = image.convert("RGB")
    width, height = out.size

    if random.random() > 0.5:
        out = out.rotate(random.uniform(-0.8, 0.8), expand=False, resample=Image.Resampling.BICUBIC)

    crop = 0.97
    new_w, new_h = int(width * crop), int(height * crop)
    left, top = (width - new_w) // 2, (height - new_h) // 2
    out = out.crop((left, top, left + new_w, top + new_h))
    out = out.resize((width, height), Image.Resampling.BICUBIC)
    out = out.filter(ImageFilter.GaussianBlur(radius=0.2))
    out = out.filter(ImageFilter.UnsharpMask(radius=1.0, percent=60, threshold=3))

    values = _to_array(out)
    means = values.mean(axis=(0, 1))
    global_mean = means.mean()
    values *= (1.0 + (global_mean - means).reshape(1, 1, 3) / 1800.0)
    out = _from_array(values)
    out = ImageEnhance.Contrast(out).enhance(1.06)
    out = ImageEnhance.Color(out).enhance(1.03)
    return multi_jpeg_simulation(out, rounds=1, base_quality=quality)


def add_camera_pipeline(image, seed=None):
    """Camera/screen-recapture style transform for robustness testing."""
    generator = _rng(seed)
    img_np = _to_array(image)
    height, width = img_np.shape[:2]
    y, x = np.ogrid[:height, :width]
    center = np.array([height / 2.0, width / 2.0])
    dist = np.sqrt(((y - center[0]) / max(height, 1)) ** 2 + ((x - center[1]) / max(width, 1)) ** 2)
    vignette = 1 - 0.18 * dist**2
    img_np *= vignette[..., np.newaxis]

    shift = 2
    img_np[:, :, 0] = np.roll(img_np[:, :, 0], shift, axis=1)
    img_np[:, :, 2] = np.roll(img_np[:, :, 2], -shift, axis=0)

    img_np += generator.normal(0, 3, img_np.shape)
    hot = generator.random(img_np.shape[:2]) > 0.9997
    img_np[hot] = [255, 240, 220]
    banding = np.sin(np.linspace(0, np.pi * 8, height))[:, None, None] * 1.8
    img_np += banding
    return _from_array(img_np)


def add_regeneration_surrogate(image, strength=0.25):
    """Img2img/diffusion-cleanse proxy without calling a generator."""
    if strength <= 0:
        return image.convert("RGB")
    width, height = image.size
    scale = max(0.55, 1.0 - strength)
    small = image.resize((max(1, int(width * scale)), max(1, int(height * scale))), Image.Resampling.BICUBIC)
    rebuilt = small.resize((width, height), Image.Resampling.BICUBIC)
    rebuilt = rebuilt.filter(ImageFilter.MedianFilter(size=3))
    base = _to_array(image)
    regen = _to_array(rebuilt)
    return _from_array(base * (1.0 - strength * 0.55) + regen * (strength * 0.55))


def multi_jpeg_simulation(image, rounds=2, base_quality=88):
    """Repeated JPEG compression using temporary files that are cleaned up."""
    out = image.convert("RGB")
    for _ in range(max(0, int(rounds))):
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp:
            temp_path = temp.name
        try:
            quality = int(np.clip(base_quality + random.randint(-8, 5), 35, 98))
            out.save(temp_path, "JPEG", quality=quality, optimize=True)
            out = Image.open(temp_path).convert("RGB")
        finally:
            try:
                os.remove(temp_path)
            except OSError:
                pass
    return out


def _copy_exif(real_photo_path, image):
    if not real_photo_path or str(real_photo_path).lower() == "none":
        return None
    try:
        width, height = image.size
        if piexif is not None:
            exif_dict = piexif.load(real_photo_path)
            exif_dict.setdefault("0th", {})
            exif_dict.setdefault("Exif", {})
            exif_dict["0th"][piexif.ImageIFD.ImageWidth] = width
            exif_dict["0th"][piexif.ImageIFD.ImageLength] = height
            exif_dict["Exif"][piexif.ExifIFD.PixelXDimension] = width
            exif_dict["Exif"][piexif.ExifIFD.PixelYDimension] = height
            return piexif.dump(exif_dict)

        reference = Image.open(real_photo_path)
        exif = reference.getexif()
        if not exif:
            return None
        exif[256] = width
        exif[257] = height
        exif[40962] = width
        exif[40963] = height
        return exif.tobytes()
    except Exception as exc:
        print(f"EXIF copy failed: {exc}")
        return None


def _synthetic_exif(image):
    exif = Image.Exif()
    width, height = image.size
    exif[256] = width
    exif[257] = height
    exif[271] = "InternalRobustnessRig"
    exif[272] = "DetectorEvalProfile"
    exif[305] = "metadata-robustness-suite"
    exif[40962] = width
    exif[40963] = height
    return exif.tobytes()


def _metadata_bytes(mode, real_photo_path, image):
    normalized = (mode or "copy").lower()
    if normalized == "strip":
        return None
    if normalized == "synthetic":
        return _synthetic_exif(image)
    return _copy_exif(real_photo_path, image)


def _selected_methods(profile, methods):
    if methods:
        selected = tuple(part.strip() for part in methods.split(",") if part.strip())
    else:
        selected = PROFILE_METHODS.get(profile, PROFILE_METHODS["full"])
    unknown = sorted(set(selected) - set(METHOD_FAMILIES))
    if unknown:
        raise ValueError(f"Unknown method families: {', '.join(unknown)}")
    return selected


def post_process_image(
    input_path,
    output_path,
    real_photo_path=None,
    noise_strength=0.8,
    skin_strength=0.75,
    fft_strength=0.48,
    pixel_strength=0.028,
    quality=85,
    glcm_strength=0.6,
    profile="full",
    methods=None,
    metadata_mode="copy",
    manifest_path=None,
    seed=None,
):
    """Legacy 薄适配器：保持原有 15+ 散参数签名不变。

    内部构造 TransformConfig 后调用 transform_core.pipeline 中的新实现。
    methods 参数当前忽略（未来可扩展到 TransformConfig）。
    """
    config = TransformConfig(
        input_path=input_path,
        output_path=output_path,
        manifest_path=manifest_path,
        profile=profile,
        seed=seed,
        quality=quality,
        noise_strength=noise_strength,
        fft_strength=fft_strength,
        pixel_strength=pixel_strength,
        glcm_strength=glcm_strength,
        skin_strength=skin_strength,
        metadata_mode=metadata_mode,
        real_photo_path=real_photo_path,
    )
    return _new_post_process_image(config)


def main(argv: list[str] | None = None) -> None:
    """CLI 入口，委托给可安装包 bypass_cli。"""
    from bypass_cli import main as _cli_main

    _cli_main(argv)


if __name__ == "__main__":
    main()
