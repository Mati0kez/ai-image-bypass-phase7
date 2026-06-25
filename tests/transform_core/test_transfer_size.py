"""P3: 验证 transfer_blackbox_attack 输出尺寸与输入一致。"""

import numpy as np
from PIL import Image

from transform_core.config import TransformConfig
from transform_core.pipeline import post_process_image


def test_transfer_blackbox_attack_preserves_size(tmp_path):
    img = Image.fromarray(np.random.randint(0, 255, (256, 384, 3), dtype=np.uint8), "RGB")
    in_path = tmp_path / "in.jpg"
    out_path = tmp_path / "out.jpg"
    manifest_path = tmp_path / "out.manifest.json"
    img.save(in_path, "JPEG")

    cfg = TransformConfig(
        input_path=str(in_path),
        output_path=str(out_path),
        manifest_path=str(manifest_path),
        profile="metadata",
        methods=["transfer_blackbox_attack"],
        transfer_blackbox_attack_enabled=True,
        transfer_blackbox_attack_epsilon=0.01,
    )
    post_process_image(cfg)
    out_img = Image.open(out_path)
    assert out_img.size == img.size, f"尺寸不一致: {out_img.size} vs {img.size}"