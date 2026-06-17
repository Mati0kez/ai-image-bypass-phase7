"""TransformConfig 的单元测试。"""

import sys
from pathlib import Path

# 确保能导入 src/transform_core
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from transform_core.config import TransformConfig


def test_transform_config_minimal():
    """最小实例化测试。"""
    cfg = TransformConfig(input_path="in.jpg", output_path="out.jpg")
    assert cfg.input_path == "in.jpg"
    assert cfg.output_path == "out.jpg"
    assert cfg.profile == "full"
    assert cfg.metadata_mode == "synthetic"
    assert cfg.lpips_enabled is False


def test_transform_config_optional_fields_none():
    """Optional 字段支持 None。"""
    cfg = TransformConfig(
        input_path="in.jpg",
        output_path="out.jpg",
        noise_strength=None,
        fft_strength=None,
        real_photo_path=None,
    )
    assert cfg.noise_strength is None
    assert cfg.fft_strength is None
    assert cfg.real_photo_path is None


def test_transform_config_defaults():
    """默认值测试。"""
    cfg = TransformConfig(input_path="in.jpg", output_path="out.jpg")
    assert cfg.seed is None
    assert cfg.quality == 95
    assert cfg.camera_sim["jpeg_cycles"] == 2
    assert cfg.camera_sim["bayer_demosaic"] is False


def test_transform_config_types():
    """类型检查（简单验证）。"""
    cfg = TransformConfig(
        input_path="in.jpg",
        output_path="out.jpg",
        profile="quick",
        metadata_mode="copy",
    )
    assert isinstance(cfg.profile, str)
    assert isinstance(cfg.metadata_mode, str)
