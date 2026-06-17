# CLI 测试工作区

用于快速测试 P9/P10 新方法族（以及其他任意方法族组合）。

## 目录结构

```
cli_test/
├── images/          # 把需要测试的原始图片放在这里
├── outputs/         # 处理后的图片和 manifest 自动输出到这里
├── run.py           # 测试脚本
└── README.md
```

## 使用方法

### 1. 准备测试图片
把图片复制到 `images/` 文件夹，例如：
```
images/
  1.jpg
  2.png
  test_photo.jpg
```

### 2. 运行测试

```bash
cd cli_test

# 示例 1：只测试频谱峰值清洗 + PRNU
python run.py --methods frequency_peaks_cleansing,prnu_simulation

# 示例 2：测试全部四个新模块
python run.py --methods frequency_peaks_cleansing,prnu_simulation,gradient_edge_aware_perturbation,transfer_blackbox_attack

# 示例 3：使用 adversarial profile（包含 lpips 等老模块）
python run.py --profile adversarial --methods prnu_simulation,transfer_blackbox_attack

# 示例 4：指定质量和 seed
python run.py --methods frequency_peaks_cleansing --quality 90 --seed 42
```

### 3. 输出命名规则

- 输入：`1.jpg`
- 输出：`1-frequency_peaks_cleansing_prnu_simulation.jpg`
- 同时生成：`1-frequency_peaks_cleansing_prnu_simulation.manifest.json`

所有文件都在 `outputs/` 目录下，方便你批量拿去外部检测器验证效果。

## 支持的参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--methods` | 逗号分隔的方法族列表 | 无（必须指定或用 profile） |
| `--profile` | 使用预定义 profile (quick/full/adversarial 等) | full |
| `--quality` | 输出 JPEG 质量 | 90 |
| `--seed` | 随机种子 | 1234 |

## 注意事项

- 四个 P9/P10 模块默认不包含在任何 profile 中，必须通过 `--methods` 显式指定。
- 如果模块需要额外参数（如 PRNU 的 reference image），目前使用模块默认值或自生成指纹。
- 处理完成后直接去 `outputs/` 文件夹取结果图即可。