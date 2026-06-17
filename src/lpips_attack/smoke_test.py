"""Smoke test for LPIPSModule.

Run this after installing optional dependencies:
    pip install -r src/lpips_attack/requirements-lpips.txt
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent.parent))

from lpips_attack import LPIPSModule
from transform_core.config import TransformConfig


def main():
    print("Running LPIPSModule smoke test (CPU mode)...")

    # 创建测试图片
    img = Image.fromarray(np.random.randint(0, 255, (128, 128, 3), dtype=np.uint8), "RGB")

    # 配置
    cfg = TransformConfig(
        input_path="dummy.jpg",
        output_path="dummy_out.jpg",
        lpips_enabled=True,
        lpips_strength=0.01,
        lpips_steps=3,  # 少量步数用于 smoke test
    )

    module = LPIPSModule()
    result = module.apply(img, cfg, np.random.default_rng(42))

    assert isinstance(result, Image.Image)
    assert result.size == img.size
    assert result.mode == "RGB"

    print("Smoke test PASSED (LPIPSModule works on CPU).")


if __name__ == "__main__":
    main()
