"""Metadata 方法族 Module。

此族不修改图像像素，仅在最终保存时注入 EXIF。
apply 方法返回原图（identity transform）。
"""

from __future__ import annotations

import numpy as np
from PIL import Image
from typing import TYPE_CHECKING

from ..module import TransformModule
from ..registry import register_module

if TYPE_CHECKING:
    from ..config import TransformConfig


class MetadataModule(TransformModule):
    """元数据策略模块。

    根据 config.metadata_mode 和 real_photo_path，
    实际的 EXIF 注入逻辑由 post_process_image 的保存步骤负责。
    此 Module 仅作为占位，apply 返回原图。
    """

    @property
    def name(self) -> str:
        return "metadata"

    def apply(
        self,
        img: Image.Image,
        config: "TransformConfig",  # type: ignore[name-defined]
        rng: np.random.Generator,
    ) -> Image.Image:
        # metadata 族不修改像素，返回原图
        return img.convert("RGB")


# import-time 自动注册
register_module(MetadataModule())
