# 五项方法族 verified 测试参数（2026-06-22）

以下参数在 `20260519-110735.jpg` 上通过外部检测验证：**小幅有效、画质可接受**。已写入 `TransformConfig` 默认值，CLI/WebUI 不额外覆盖。

## 通用测试命令

```bash
cd cli_test
python run.py --methods <方法族名> --seed 42 --quality 90
```

| 通用项 | 值 | 说明 |
|--------|-----|------|
| `seed` | `42` | CLI 测试固定种子（可复现） |
| `quality` | `90` | 输出 JPEG 质量；保存时 pipeline 会 `quality - 3` |
| `metadata_mode` | `synthetic` | 自动附加合成 EXIF |
| 后处理 | UnsharpMask + Contrast×1.04 | 所有方法族共用 |

---

## 1. frequency_peaks_cleansing（频谱峰值清洗）

| 参数 | 值 |
|------|-----|
| `frequency_peaks_cleansing_enabled` | `true`（选中方法族时） |
| `frequency_peaks_cleansing_domain` | `dct` |
| `frequency_peaks_cleansing_threshold` | `2.0`（高频 AC 系数，标准差倍数） |
| `frequency_peaks_cleansing_replacement_strategy` | `attenuate` |
| `frequency_peaks_cleansing_attenuation` | `0.35` |

实现：8×8 块 DCT，仅处理 `u+v≥4` 的高频 AC 峰值；**不再使用全局 DCT 清零**（曾导致纯黑图）。

---

## 2. prnu_simulation（PRNU 模拟）

| 参数 | 值 |
|------|-----|
| `prnu_simulation_enabled` | `true` |
| `prnu_simulation_mode` | `extract_add` |
| `prnu_simulation_strength` | `0.75` |
| `prnu_simulation_reference_path` | `null`（自生成指纹 surrogate） |

---

## 3. watermark（SynthID 频谱去除）

| 参数 | 值 |
|------|-----|
| `watermark_remove` | `true` |
| `watermark_spectral_mid_high_factor` | `0.55` |

实现：无 codebook 时，仅对 FFT 中频/高频（归一化半径 0.12~0.85）乘以 `0.55`，低频保留。

---

## 4. gradient_edge_aware_perturbation（边缘感知扰动）

| 参数 | 值 |
|------|-----|
| `gradient_edge_aware_perturbation_enabled` | `true` |
| `gradient_edge_aware_perturbation_edge_weight` | `2.0` |
| `gradient_edge_aware_perturbation_smooth_weight` | `0.5` |
| `pixel_strength` | `0.028` |

---

## 5. lpips（LPIPS / 代理对抗）

| 参数 | 值 |
|------|-----|
| `lpips_enabled` | `true` |
| `lpips_strength` | `0.06` |
| `lpips_steps` | `25` |
| `lpips_pixel_hybrid_factor` | `0.45` |
| `detector_feedback` | `false` |

实现（无 detector 闭环时）：

1. ResNet50 PGD，`epsilon = max(lpips_strength, 0.03)`
2. 叠加 `add_pixel_perturbation(strength × lpips_pixel_hybrid_factor)`

---

## 检测效果备注（同图、单项）

| 方法族 | aiimagecheck.org | aiphotocheck.com |
|--------|------------------|------------------|
| frequency_peaks_cleansing | 修复后可视正常 | 待复测 |
| prnu / watermark / gradient | 效果甚微 | 约 3–8% 降幅 |
| lpips | 无显著变化 | 无显著变化 |

**结论**：上述参数作为**轻度单项默认**；若需更大降幅，建议与 `camera` / `noise` / `texture` 组合使用。

---

## 参数定义位置

- 默认值：`src/transform_core/config.py` → `TransformConfig`
- CLI enabled 同步：`cli_test/run.py` → `method_enabled_flags()`
- WebUI 控件默认：`webui_bypass.py`
- manifest 记录：`src/transform_core/pipeline.py` → `module_parameters`
