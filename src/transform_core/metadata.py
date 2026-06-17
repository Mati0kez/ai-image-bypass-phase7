"""Metadata 注入逻辑。

包含 synthetic / copy EXIF 的生成函数，
供 pipeline 调用以注入元数据。
"""

from typing import Optional
from PIL import Image

try:
    import piexif
except ImportError:
    piexif = None


def _copy_exif(real_photo_path: Optional[str], image: Image.Image) -> Optional[bytes]:
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
        return exif.tobytes()
    except Exception:
        return None


def _synthetic_exif(image: Image.Image) -> bytes:
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


def _metadata_bytes(
    mode: str, real_photo_path: Optional[str], image: Image.Image
) -> Optional[bytes]:
    normalized = (mode or "copy").lower()
    if normalized == "strip":
        return None
    if normalized == "synthetic":
        return _synthetic_exif(image)
    return _copy_exif(real_photo_path, image)
