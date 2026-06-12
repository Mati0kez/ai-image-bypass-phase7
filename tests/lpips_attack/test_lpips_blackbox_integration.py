"""P3-3 端到端集成测试：adversarial profile + lpips_blackbox + detector_feedback。

验证 LPIPS 黑盒路径在真实 DIL 场景下被正确调用。
"""

import sys
from pathlib import Path
import tempfile

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from transform_core.config import TransformConfig
from transform_core.pipeline import post_process_image
from PIL import Image
import numpy as np


def test_adversarial_with_lpips_blackbox_and_detector_feedback():
    """profile=adversarial + lpips_blackbox + detector_feedback 应正常运行。"""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        input_path = tmp_path / "in.jpg"
        output_path = tmp_path / "out.jpg"
        manifest_path = tmp_path / "manifest.json"

        img = Image.fromarray(np.zeros((48, 48, 3), dtype=np.uint8))
        img.save(input_path)

        config = TransformConfig(
            input_path=str(input_path),
            output_path=str(output_path),
            manifest_path=str(manifest_path),
            profile="adversarial",
            lpips_enabled=True,
            lpips_blackbox=True,
            detector_feedback=True,
            lpips_strength=0.005,
            lpips_steps=2,
            max_iter=2,
        )

        result = post_process_image(config)

        assert Path(result).exists()
        # manifest 应存在且包含 lpips
        import json
        manifest = json.loads(manifest_path.read_text())
        assert "lpips" in manifest.get("method_families", [])
        print("✅ LPIPS blackbox + DIL 集成测试通过")