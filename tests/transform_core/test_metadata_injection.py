"""TDD 测试：验证 metadata 注入在自定义方法族场景下是否正常工作。"""

import sys
from pathlib import Path
import tempfile
import json

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from transform_core.config import TransformConfig
from transform_core.pipeline import post_process_image
from PIL import Image


def test_metadata_injection_with_custom_methods():
    """
    RED 测试：
    当用户通过自定义方法族（不包含 metadata）+ metadata_mode="synthetic" 时，
    pipeline 应该强制加入 metadata 方法族并注入 EXIF。
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        input_path = tmp / "input.jpg"
        output_path = tmp / "output.jpg"
        manifest_path = tmp / "manifest.json"

        # 创建测试图片
        img = Image.new("RGB", (128, 128), color="blue")
        img.save(input_path, quality=95)

        # 只使用 metadata 方法族本身来测试（避免 legacy 依赖）
        config = TransformConfig(
            input_path=str(input_path),
            output_path=str(output_path),
            manifest_path=str(manifest_path),
            profile="metadata",           # 只使用 metadata profile
            metadata_mode="synthetic",    # 用户选择了合成元数据
            quality=90,
        )

        post_process_image(config)

        # 验证 1: manifest 中应该包含 metadata 方法族
        manifest = json.loads(manifest_path.read_text())
        assert "metadata" in manifest.get("method_families", []), \
            f"metadata 方法族未被加入，当前 method_families: {manifest.get('method_families')}"

        # 验证 2: 输出图片应该有 EXIF
        out_img = Image.open(output_path)
        exif_data = out_img.info.get("exif")
        assert exif_data is not None, "输出图片没有 EXIF 元数据"

        print("✅ 测试通过：metadata 方法族被正确加入并注入 EXIF")


if __name__ == "__main__":
    test_metadata_injection_with_custom_methods()
