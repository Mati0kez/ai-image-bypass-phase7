"""SpectralCodebook - 多分辨率 SynthID 水印指纹集合。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Tuple

import numpy as np


class SpectralCodebook:
    """按分辨率存储 SynthID 水印载波指纹的集合。

    支持自动匹配和已知信号减法。
    """

    def __init__(self, profiles: Dict[Tuple[int, int], Dict[str, Any]] | None = None):
        self.profiles = profiles or {}

    @classmethod
    def load(cls, path: str | Path) -> SpectralCodebook:
        """从 .npz 或 .json 文件加载 codebook。"""
        path = Path(path)
        if path.suffix == ".npz":
            data = np.load(path, allow_pickle=True)
            profiles = {tuple(k): v.item() for k, v in data.items()}
            return cls(profiles)
        elif path.suffix == ".json":
            with open(path, "r", encoding="utf-8") as f:
                profiles = json.load(f)
            # JSON 键是字符串，需要转回 tuple
            profiles = {tuple(map(int, k.split(","))): v for k, v in profiles.items()}
            return cls(profiles)
        else:
            raise ValueError(f"Unsupported file format: {path}")

    def save(self, path: str | Path) -> None:
        """保存为 .npz 格式。"""
        path = Path(path)
        if path.suffix != ".npz":
            path = path.with_suffix(".npz")
        np.savez(path, **{f"{k[0]},{k[1]}": v for k, v in self.profiles.items()})

    def get_profile(self, resolution: Tuple[int, int]) -> Dict[str, Any] | None:
        """获取指定分辨率的 profile。"""
        return self.profiles.get(resolution)

    def auto_match(self, image_shape: Tuple[int, int]) -> Tuple[int, int] | None:
        """自动选择最接近的 profile 分辨率。

        Profile 结构示例：
        {
            (1024, 1024): {
                "carriers": [(x1,y1), (x2,y2), ...],
                "magnitudes": [m1, m2, ...],
                "phases": [p1, p2, ...]
            },
            ...
        }
        """
        if not self.profiles:
            return None
        h, w = image_shape
        # 简单启发式：找面积最接近的
        best = min(
            self.profiles.keys(),
            key=lambda res: abs(res[0] * res[1] - h * w),
        )
        return best
