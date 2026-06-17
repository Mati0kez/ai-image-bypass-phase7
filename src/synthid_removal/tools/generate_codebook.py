"""离线 SpectralCodebook 生成工具。

真实实现：对已知含 SynthID 的图像进行 FFT 分析，提取稳定载波指纹。
"""

import argparse
from pathlib import Path
from typing import List, Tuple

import numpy as np
from PIL import Image

from ..spectral_codebook import SpectralCodebook


def _extract_carriers(fft_magnitude: np.ndarray, top_k: int = 20) -> List[Tuple[int, int]]:
    """从 FFT 幅度谱中提取能量最高的 K 个频率点作为潜在载波。"""
    # 简化实现：取幅度最高的点
    flat_idx = np.argpartition(fft_magnitude.ravel(), -top_k)[-top_k:]
    coords = np.unravel_index(flat_idx, fft_magnitude.shape)
    return list(zip(coords[0], coords[1]))


def generate_codebook(
    image_paths: List[str], resolutions: List[Tuple[int, int]]
) -> SpectralCodebook:
    """从图像列表生成 SpectralCodebook。"""
    profiles = {}
    for res in resolutions:
        carriers = []
        magnitudes = []
        phases = []

        for img_path in image_paths:
            img = Image.open(img_path).convert("RGB").resize(res)
            arr = np.array(img, dtype=np.float32)
            for c in range(3):
                f = np.fft.fft2(arr[:, :, c])
                fshift = np.fft.fftshift(f)
                mag = np.abs(fshift)
                ph = np.angle(fshift)

                # 提取载波（简化）
                top_carriers = _extract_carriers(mag, top_k=10)
                carriers.extend(top_carriers)
                for y, x in top_carriers:
                    magnitudes.append(mag[y, x])
                    phases.append(ph[y, x])

        # 聚类简化：取平均值
        if carriers:
            profiles[res] = {
                "carriers": carriers[:20],  # 限制数量
                "magnitudes": np.mean(magnitudes[:20]) if magnitudes else [],
                "phases": np.mean(phases[:20]) if phases else [],
            }

    return SpectralCodebook(profiles)


def main():
    parser = argparse.ArgumentParser(
        description="Generate SpectralCodebook from known SynthID images"
    )
    parser.add_argument(
        "--images", type=str, required=True, help="Directory or list of images containing SynthID"
    )
    parser.add_argument(
        "--resolutions",
        type=str,
        required=True,
        help="Comma-separated list, e.g. 1024,1024;512,512",
    )
    parser.add_argument("--output", type=str, default="synthid_codebook.npz")
    args = parser.parse_args()

    # 解析分辨率
    res_list = [tuple(map(int, r.split(","))) for r in args.resolutions.split(";")]

    # 加载图像路径
    img_dir = Path(args.images)
    if img_dir.is_dir():
        image_paths = [str(p) for p in img_dir.glob("*.png")] + [
            str(p) for p in img_dir.glob("*.jpg")
        ]
    else:
        image_paths = [args.images]

    print(f"Processing {len(image_paths)} images for resolutions {res_list}...")

    codebook = generate_codebook(image_paths, res_list)
    codebook.save(args.output)
    print(f"Codebook saved to {args.output}")


if __name__ == "__main__":
    main()
