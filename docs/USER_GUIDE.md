# AI 图片检测鲁棒性测试工具 - 用户使用指南

本文档面向人类和 AI Agent，提供当前项目的 WebUI 和 CLI 完整运行方法、测试流程以及新功能使用说明。

## 1. 项目概述

本项目用于生成对抗样本，测试各类 AI 图片检测器（ML Detection、PRNU Analysis、Gradient Analysis 等）的鲁棒性。

核心能力：
- 提供 14+ 种方法族（基础 + 对抗 + 重生成 + P9/P10 新模块）
- 支持 WebUI 可视化操作
- 支持 CLI 批量/单方法族快速测试
- 所有处理均生成 manifest，便于复现和分析

## 2. 环境准备

推荐使用项目自带的虚拟环境：

```bash
# 激活虚拟环境
source venv/bin/activate

# 设置 Python 路径（重要）
export PYTHONPATH=src
```

依赖已包含在 `venv` 中，无需额外安装。

## 3. 运行 WebUI（推荐日常使用）

```bash
source venv/bin/activate
PYTHONPATH=src python webui_bypass.py
```

启动后访问：http://127.0.0.1:7860

### WebUI 主要功能

- 上传图片
- 选择方法族（支持多选）
- 调整各模块参数（P9/P10 模块有独立参数面板）
- 一键生成处理后的图片 + manifest

**P9/P10 新模块**已全部集成到「对抗方法族」中，可直接勾选使用。

## 4. CLI 测试工具（推荐快速验证单一方法族）

项目根目录下新增了独立的测试工作区 `cli_test/`，专门用于单方法族快速测试。

### 目录结构

```
cli_test/
├── images/          # 把测试原图放在这里
├── outputs/         # 处理结果自动输出（含 manifest）
├── run.py           # 测试脚本
└── README.md
```

### 使用示例

```bash
cd cli_test

# 测试单个方法族（推荐）
python run.py --methods frequency_peaks_cleansing --quality 92 --seed 42

# 测试 PRNU（已支持自生成指纹，无需参考图也能看到效果）
python run.py --methods prnu_simulation

# 测试多个方法族组合
python run.py --methods frequency_peaks_cleansing,prnu_simulation,gradient_edge_aware_perturbation

# 测试全部 P9/P10 新模块
python run.py --methods frequency_peaks_cleansing,prnu_simulation,gradient_edge_aware_perturbation,transfer_blackbox_attack
```

### 输出命名规则

- 输入：`1.jpg`
- 输出：`1-frequency_peaks_cleansing.jpg`
- Manifest：`1-frequency_peaks_cleansing.manifest.json`

所有文件统一放在 `outputs/` 目录，方便批量拿去检测。

## 5. 当前支持的所有方法族（14 个）

| 方法族 | 所属阶段 | 说明 |
|--------|----------|------|
| camera | 基础 | 相机管线模拟 |
| diffusion_reconstruction | 对抗 | Diffusion 重建（SynthID 水印去除） |
| encoding | 基础 | JPEG、几何变换等 |
| frequency | 基础 | 频域扰动 |
| frequency_peaks_cleansing | **P9** | 频谱峰值清洗（对抗 GAN Fingerprint） |
| gradient_edge_aware_perturbation | **P10.3** | 边缘感知扰动（对抗 Gradient Analysis） |
| lpips | 对抗 | 感知损失攻击 |
| noise | 基础 | 噪声注入 |
| prnu_simulation | **P9** | PRNU 模拟/去除（对抗 PRNU Analysis） |
| regeneration | 重生成 | 真实 img2img 重生成 |
| regeneration_surrogate | 重生成 | 代理重生成 |
| texture | 基础 | 纹理增强 |
| transfer_blackbox_attack | **P10.4** | 迁移黑盒攻击（对抗 ML Detection） |
| watermark | 对抗 | 水印移除 |

> **注意**：P9/P10 四个新模块默认不包含在任何 profile 中，必须通过 `--methods` 或 WebUI Checkbox 显式启用。

## 6. 推荐测试流程

1. **快速验证单一效果** → 使用 `cli_test/run.py --methods xxx`
2. **组合测试** → 使用 `cli_test/run.py --methods a,b,c`
3. **可视化调试 + 参数调节** → 使用 WebUI
4. **拿结果去外部检测** → 直接从 `cli_test/outputs/` 或 WebUI 下载的 manifest 对应目录取图

## 7. 输出文件说明

每次处理都会生成：
- 处理后的图片（.jpg / .png）
- `xxx.manifest.json`：记录所用方法族、参数、profile 等完整配置

manifest 示例关键字段：
```json
{
  "methods": ["frequency_peaks_cleansing", "prnu_simulation"],
  "frequency_peaks_cleansing_enabled": true,
  "prnu_simulation_enabled": true,
  ...
}
```

## 8. 常见问题

**Q: PRNU 模块没效果？**  
A: 已修复。未提供参考图时会自动使用输入图像自身生成模拟指纹，现在有可见效果。

**Q: CLI 提示缺少 bypass_ai_detector？**  
A: 已修复 `cli_test/run.py`，会自动把项目根目录加入 `sys.path`。

**Q: 如何只跑 P9/P10 四个新模块？**  
A: `python cli_test/run.py --methods frequency_peaks_cleansing,prnu_simulation,gradient_edge_aware_perturbation,transfer_blackbox_attack`

---

文档维护者：Cursor Agent  
最后更新：2026-06-17

如需补充其他模块参数说明或生成对比报告脚本，请随时告知。