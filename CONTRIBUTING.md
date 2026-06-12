# Contributing to AI Image Bypass Framework

感谢您的贡献！本项目欢迎任何形式的改进，包括新变换模块、detector 适配器、文档完善和 bug 修复。

## 开发环境

```bash
git clone <repo>
cd ai图片添加元数据
make install-dev
```

## 添加新 TransformModule

1. 在 `src/transform_core/modules/` 下创建 `your_module.py`
2. 继承 `TransformModule`：

```python
from transform_core.module import TransformModule
from transform_core.registry import register_module

class YourModule(TransformModule):
    @property
    def name(self) -> str:
        return "your_method"

    def apply(self, img, config, rng):
        # 实现变换逻辑
        return img

register_module(YourModule())
```

3. 更新 `PROFILE_METHODS`（如需要新 profile）
4. 添加对应测试到 `tests/transform_core/`

## 添加新 DetectorAdapter

在 `src/external_validation/` 或 `src/detector_loop/adapters/` 下创建新适配器，继承 `PlatformAdapter` 或 `DetectorInterface`，实现 `score` 和 `get_quota_usage`（或 `name`）。

## 提交 PR

- 确保 `make lint` 和 `make test` 通过
- 新功能需附带测试
- 更新 README / CONTEXT.md（如涉及新术语）
- PR 标题使用简洁英文，描述清晰

## 代码规范

- 遵循 Black + Ruff
- 公共函数添加简短 docstring
- 避免在核心模块中引入 torch（使用可选依赖）
