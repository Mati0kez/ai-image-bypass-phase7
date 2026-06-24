# 飞书 Wiki「4. 单项测试效果」— 方法族表格（粘贴用）

> 复制下方表格到 [AI 图像检测对抗方式总结](https://ysg0j0xvgmig.sg.larksuite.com/wiki/M22pwlY0piqik2kXuKJlgrhigGc) 第 4 节。  
> **实际效果** 列留空供手动填写；检测站点：aiimagecheck.org / aiphotocheck.com。

## 单项测试说明（可放在表格上方）

- 测试图：`cli_test/images/` 内样例图（如 `20260519-110735.jpg`）
- 命令：`cd cli_test && python run.py --methods <方法族> --seed 42 --quality 90`
- 输出：`cli_test/outputs/<图名>-<方法族>.jpg` + manifest
- 共 **15** 项单项方法族（与代码注册表一致）；`metadata` 为独立单项，其余处理时亦可能自动附带 synthetic EXIF

---

## 表格（15 行）

| 方法族 | CLI `--methods` | 难度 | 实际效果 | 画质损失 | 备注 |
|--------|-----------------|------|----------|----------|------|
| EXIF / 元数据注入 | `metadata` | 低 | | 无 | Metadata；copy/strip/synthetic |
| JPEG / resize / crop / color | `encoding` | 低 | | 低 | Encoding 基础方法族 |
| 噪声 / 像素微扰 | `noise` | 低 | | 低 | Noise 基础方法族 |
| FFT 频域整形 | `frequency` | 中 | | 中 | Frequency；频谱扰动 |
| GLCM / LBP 纹理整形 | `texture` | 中 | | 中 | Texture；与 Frequency 分开单项测 |
| 相机模拟 / 屏摄 / 重拍 | `camera` | 中 | | 中 | Camera；含多轮 JPEG |
| 代理重生成 | `regeneration_surrogate` | 中 | | 中 | 降采样/滤波代理，无生成模型 |
| 真实 img2img 重生成 | `regeneration` | 高 | | 高 | 需 diffusers 模型路径，否则回退 surrogate |
| LPIPS / 优化式 non-semantic | `lpips` | 高 | | 低~中 | ResNet50 PGD + 像素混合；需 PyTorch |
| SynthID 频谱水印去除 | `watermark` | 中 | | 中 | Watermark V3；中高频衰减 |
| Frequency Peaks Cleansing | `frequency_peaks_cleansing` | 中 | | 中 | P9/P10.1；8×8 DCT 峰值衰减 |
| PRNU Simulation / Removal | `prnu_simulation` | 高 | | 中 | P9/P10.2；无参考图时自生成指纹 |
| Gradient / Edge-aware Perturbation | `gradient_edge_aware_perturbation` | 中 | | 中 | P10.3；边缘感知扰动 |
| Transfer-based Black-box Attack | `transfer_blackbox_attack` | 高 | | 中高 | P10.4；需 PyTorch；输出曾裁为 224×224 |
| Diffusion Reconstruction | `diffusion_reconstruction` | 高 | | 高 | P9 SynthID；需 diffusers + 模型，否则 no-op |

---

## 与旧版 11 行表格的对应关系

| 旧表格合并项 | 拆分为单项测试 |
|--------------|----------------|
| FFT/GLCM/LBP 统计整形 | `frequency` + `texture`（2 项） |
| （未单独列出） | `metadata`、`regeneration_surrogate`、`regeneration`、`watermark`（4 项） |

合计：11 − 1（合并行）+ 1（拆成 2）+ 4（新增）= **15 项**

---

## 已验证参数（可选附在 Wiki 脚注）

详见仓库 `cli_test/TEST_SETTINGS.md` 与 `TransformConfig` 默认值（commit `5d4865fa` 起）。
