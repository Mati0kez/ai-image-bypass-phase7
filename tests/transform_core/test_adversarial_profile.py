"""Adversarial profile smoke test（验证动态调度与模块启用）。"""

import sys
from pathlib import Path
import tempfile

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from transform_core.config import TransformConfig
from transform_core.pipeline import post_process_image
from PIL import Image
import numpy as np


def test_adversarial_profile_with_flags():
    """profile=adversarial + lpips_enabled + watermark_remove 应生成 manifest。"""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        input_path = tmp_path / "in.jpg"
        output_path = tmp_path / "out.jpg"
        manifest_path = tmp_path / "manifest.json"

        # 创建测试图像
        img = Image.fromarray(np.zeros((64, 64, 3), dtype=np.uint8))
        img.save(input_path)

        config = TransformConfig(
            input_path=str(input_path),
            output_path=str(output_path),
            manifest_path=str(manifest_path),
            profile="adversarial",
            lpips_enabled=True,
            watermark_remove=True,
            regeneration_mode="surrogate",
        )

        result = post_process_image(config)

        assert Path(result).exists()
        assert manifest_path.exists()

        import json

        manifest = json.loads(manifest_path.read_text())
        families = manifest["method_families"]
        assert "lpips" in families
        assert "watermark" in families
        assert "regeneration" in families or "regeneration_surrogate" in families
