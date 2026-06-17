"""TransformRegistry - 方法族到 Module 实例的映射表。"""

from typing import Dict, Tuple

from .module import TransformModule

# 方法族名称常量（核心 + 实验性对抗方法族）
METHOD_FAMILIES: Tuple[str, ...] = (
    "metadata",
    "encoding",
    "noise",
    "frequency",
    "texture",
    "camera",
    "regeneration_surrogate",
    "lpips",
    "watermark",
    "regeneration",
)

# Profile 到方法族的默认映射
PROFILE_METHODS: Dict[str, Tuple[str, ...]] = {
    "quick": ("metadata", "encoding", "noise", "frequency"),
    "full": METHOD_FAMILIES,
    "texture": ("texture",),
    "camera": ("camera",),
    "metadata": ("metadata",),
    "adversarial": ("metadata", "encoding", "noise", "frequency", "texture", "camera", "lpips", "watermark", "regeneration"),
}

# 全局注册表：方法族名称 -> Module 实例
TRANSFORM_MODULES: Dict[str, TransformModule] = {}


def register_module(module: TransformModule) -> None:
    """注册一个 TransformModule 实例到全局表。

    同一 name 的重复注册会覆盖前一个实例。
    """
    TRANSFORM_MODULES[module.name] = module


# 导入 modules 包以触发各 Module 的 import-time 自动注册
# 必须在 register_module 定义之后导入
from . import modules  # noqa: F401, E402


def _selected_modules(profile: str, methods: str | None = None) -> Tuple[str, ...]:
    """根据 profile 和可选的 methods 参数解析启用的方法族列表。

    Args:
        profile: 预定义 profile 名称（quick/full/texture/camera/metadata/adversarial）。
        methods: 逗号分隔的自定义方法族列表，优先级高于 profile。

    Returns:
        启用的方法族名称元组。

    Raises:
        ValueError: 如果指定了未知的方法族名称。
    """
    if methods:
        selected = tuple(part.strip() for part in methods.split(",") if part.strip())
    else:
        selected = PROFILE_METHODS.get(profile, PROFILE_METHODS["full"])

    unknown = sorted(set(selected) - set(METHOD_FAMILIES))
    if unknown:
        raise ValueError(f"Unknown method families: {', '.join(unknown)}")

    return selected
