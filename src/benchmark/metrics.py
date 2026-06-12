"""指标计算模块。

提供 perceptual 指标（SSIM、PSNR、LPIPS）和 detection 指标计算。
"""

from typing import Dict, List, Tuple
import numpy as np
from PIL import Image


def _to_array(img: Image.Image) -> np.ndarray:
    return np.array(img).astype(np.float32) / 255.0


def compute_psnr(img1: Image.Image, img2: Image.Image) -> float:
    """计算 PSNR (Peak Signal-to-Noise Ratio)。"""
    a = _to_array(img1)
    b = _to_array(img2)
    mse = np.mean((a - b) ** 2)
    if mse == 0:
        return 100.0
    return float(20 * np.log10(1.0 / np.sqrt(mse)))


def compute_ssim(img1: Image.Image, img2: Image.Image) -> float:
    """计算 SSIM (Structural Similarity Index)，简化实现。"""
    a = _to_array(img1)
    b = _to_array(img2)
    # 简化的 SSIM：使用均值和方差
    mu1, mu2 = a.mean(), b.mean()
    sigma1, sigma2 = a.var(), b.var()
    sigma12 = np.mean((a - mu1) * (b - mu2))
    c1, c2 = 0.01**2, 0.03**2
    ssim = ((2 * mu1 * mu2 + c1) * (2 * sigma12 + c2)) / \
           ((mu1**2 + mu2**2 + c1) * (sigma1 + sigma2 + c2))
    return float(np.clip(ssim, 0.0, 1.0))


def compute_lpips(img1: Image.Image, img2: Image.Image) -> float:
    """计算 LPIPS（占位实现）。真实实现需 torch + lpips 库。"""
    # TODO: 集成 src/lpips_attack 中的 LPIPS 计算
    # 当前返回基于像素差异的近似值
    a = _to_array(img1)
    b = _to_array(img2)
    return float(np.mean(np.abs(a - b)))


def compute_perceptual_metrics(
    original: Image.Image, transformed: Image.Image
) -> Dict[str, float]:
    """计算 perceptual 指标。"""
    return {
        "psnr": compute_psnr(original, transformed),
        "ssim": compute_ssim(original, transformed),
        "lpips": compute_lpips(original, transformed),
    }


def compute_detection_metrics(
    scores: List[float], threshold: float = 0.5
) -> Dict[str, float]:
    """计算 detection 相关指标。"""
    if not scores:
        return {"bypass_rate": 0.0, "mean_score": 0.0, "min_score": 0.0}

    final_scores = scores[-1:] if isinstance(scores[-1], (int, float)) else [s[2] for s in scores if isinstance(s, (list, tuple))]
    # 兼容 history 格式 [(step, detector, score), ...]
    if isinstance(scores[0], (list, tuple)) and len(scores[0]) == 3:
        final_scores = [s[2] for s in scores]
    # 兼容外部验证 dict 格式 [{"step":, "detector":, "score":}, ...]
    elif isinstance(scores[0], dict) and "score" in scores[0]:
        final_scores = [s["score"] for s in scores]
    else:
        final_scores = scores

    bypass_count = sum(1 for s in final_scores if s < threshold)
    return {
        "bypass_rate": bypass_count / len(final_scores) if final_scores else 0.0,
        "mean_score": float(np.mean(final_scores)),
        "min_score": float(np.min(final_scores)),
        "final_score": float(final_scores[-1]),
    }


def wilson_score_interval(successes: int, n: int, confidence: float = 0.95) -> Tuple[float, float]:
    """计算 Wilson score 置信区间（用于 bypass rate 的统计显著性）。

    Args:
        successes: 成功 bypass 的数量。
        n: 总样本数。
        confidence: 置信水平（默认 0.95）。

    Returns:
        (lower_bound, upper_bound)
    """
    if n == 0:
        return (0.0, 0.0)
    z = 1.96 if abs(confidence - 0.95) < 0.01 else 2.576  # 近似 z 值
    p = successes / n
    denominator = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denominator
    half_width = z * np.sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denominator
    lower = max(0.0, center - half_width)
    upper = min(1.0, center + half_width)
    return (float(lower), float(upper))