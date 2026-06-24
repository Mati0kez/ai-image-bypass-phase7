# 各方法族 GitHub 参考项目

> 按 15 个 CLI 方法族整理 GitHub 上语义最接近的参考项目。

同一仓库可对应多个方法族。基础方法族（encoding / noise / frequency / texture / camera / regeneration_surrogate）的直接上游为 [PurinNyova/Image-Detection-Bypass-Utility](https://github.com/PurinNyova/Image-Detection-Bypass-Utility)。

---

## 1. `metadata` — EXIF / 元数据注入

| 优先级 | 仓库 | 说明 |
|--------|------|------|
| 1 | [wiltodelta/remove-ai-watermarks](https://github.com/wiltodelta/remove-ai-watermarks) | 剥离 C2PA / Copyright 等 AI 溯源元数据 |
| 2 | [aloshdenny/reverse-SynthID](https://github.com/aloshdenny/reverse-SynthID) | SynthID / C2PA 溯源分析与对抗研究 |
| 3 | [ianare/exif-py](https://github.com/ianare/exif-py) | EXIF 解析（读侧参考） |
| 4 | [hMatoba/piexif](https://github.com/hMatoba/piexif) | EXIF 读写库（合成 EXIF 实现参考） |

---

## 2. `encoding` — JPEG / resize / crop / color

| 优先级 | 仓库 | 说明 |
|--------|------|------|
| 1 | [PurinNyova/Image-Detection-Bypass-Utility](https://github.com/PurinNyova/Image-Detection-Bypass-Utility) | 重编码、缩放、裁剪等编码链路上游 |
| 2 | [wiltodelta/remove-ai-watermarks](https://github.com/wiltodelta/remove-ai-watermarks) | JPEG 重压缩 + 尺寸变换流水线 |
| 3 | [python-pillow/Pillow](https://github.com/python-pillow/Pillow) | 编码/色彩空间通用工具库 |
| 4 | [ImageMagick/ImageMagick](https://github.com/ImageMagick/ImageMagick) | 通用图像转码（非对抗专用） |

---

## 3. `noise` — 噪声 / 像素微扰

| 优先级 | 仓库 | 说明 |
|--------|------|------|
| 1 | [PurinNyova/Image-Detection-Bypass-Utility](https://github.com/PurinNyova/Image-Detection-Bypass-Utility) | 高斯/均匀噪声注入 |
| 2 | [cleverhans-lab/cleverhans](https://github.com/cleverhans-lab/cleverhans) | 经典对抗扰动框架 |
| 3 | [bethgelab/foolbox](https://github.com/bethgelab/foolbox) | FGSM / PGD 等像素级攻击 |
| 4 | [Trusted-AI/adversarial-robustness-toolbox](https://github.com/Trusted-AI/adversarial-robustness-toolbox) | 工业级对抗攻击工具箱 |

---

## 4. `frequency` — FFT 频域整形

| 优先级 | 仓库 | 说明 |
|--------|------|------|
| 1 | [PurinNyova/Image-Detection-Bypass-Utility](https://github.com/PurinNyova/Image-Detection-Bypass-Utility) | FFT 频谱平滑/匹配 |
| 2 | [aloshdenny/reverse-SynthID](https://github.com/aloshdenny/reverse-SynthID) | SynthID 频域载体分析 |
| 3 | [andrekassis/ai-watermark](https://github.com/andrekassis/ai-watermark) | UnMarker 高频段处理 |
| 4 | [gmelodie/silentMoire](https://github.com/gmelodie/silentMoire) | FFT 域滤波（摩尔纹/频域操作参考） |

---

## 5. `texture` — GLCM / LBP 纹理整形

| 优先级 | 仓库 | 说明 |
|--------|------|------|
| 1 | [PurinNyova/Image-Detection-Bypass-Utility](https://github.com/PurinNyova/Image-Detection-Bypass-Utility) | GLCM / LBP 统计整形 |
| 2 | [ningyu1991/ArtificialGANFingerprints](https://github.com/ningyu1991/ArtificialGANFingerprints) | GAN 纹理指纹检测（逆向问题参考） |
| 3 | [ningyu1991/ScalableGANFingerprints](https://github.com/ningyu1991/ScalableGANFingerprints) | 可扩展 GAN 指纹检测 |

纹理对抗方向的公开 bypass 项目较少，相关仓库多为**检测侧**实现。

---

## 6. `camera` — 相机模拟 / 屏摄 / 重拍

| 优先级 | 仓库 | 说明 |
|--------|------|------|
| 1 | [PurinNyova/Image-Detection-Bypass-Utility](https://github.com/PurinNyova/Image-Detection-Bypass-Utility) | 多轮 JPEG + 相机链路模拟 |
| 2 | [Dantong88/Moire_Attack](https://github.com/Dantong88/Moire_Attack) | NeurIPS 2021 屏摄摩尔纹物理模拟 |
| 3 | [gmelodie/silentMoire](https://github.com/gmelodie/silentMoire) | 屏摄摩尔纹 FFT 建模 |
| 4 | [wiltodelta/remove-ai-watermarks](https://github.com/wiltodelta/remove-ai-watermarks) | 含 degradation 链路的重拍近似 |

---

## 7. `regeneration_surrogate` — 代理重生成

| 优先级 | 仓库 | 说明 |
|--------|------|------|
| 1 | [PurinNyova/Image-Detection-Bypass-Utility](https://github.com/PurinNyova/Image-Detection-Bypass-Utility) | 降采样/滤波代理，无生成模型 |
| 2 | [wiltodelta/remove-ai-watermarks](https://github.com/wiltodelta/remove-ai-watermarks) | 轻量 degradation 代理链 |
| 3 | [andrekassis/ai-watermark](https://github.com/andrekassis/ai-watermark) | UnMarker 代理重建阶段 |

---

## 8. `regeneration` — 真实 img2img 重生成

| 优先级 | 仓库 | 说明 |
|--------|------|------|
| 1 | [AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui) | img2img 常用入口 |
| 2 | [huggingface/diffusers](https://github.com/huggingface/diffusers) | 官方 img2img / pipeline |
| 3 | [00quebec/Synthid-Bypass](https://github.com/00quebec/Synthid-Bypass) | 针对 SynthID 的 SD 重生成 bypass |
| 4 | [wiltodelta/remove-ai-watermarks](https://github.com/wiltodelta/remove-ai-watermarks) | 集成 DeSynth 等重生成路径 |

---

## 9. `lpips` — LPIPS / 优化式 non-semantic

| 优先级 | 仓库 | 说明 |
|--------|------|------|
| 1 | [richzhang/PerceptualSimilarity](https://github.com/richzhang/PerceptualSimilarity) | **LPIPS 官方实现**（度量库） |
| 2 | [andrekassis/ai-watermark](https://github.com/andrekassis/ai-watermark) | UnMarker 的 DFL + LPIPS 优化攻击 |
| 3 | [mkettune/elpips](https://github.com/mkettune/elpips) | 扩展 LPIPS 变体 |
| 4 | [cassidylaidlaw/perceptual-advex](https://github.com/cassidylaidlaw/perceptual-advex) | 感知约束对抗样本 |

---

## 10. `watermark` — SynthID 频谱水印去除

| 优先级 | 仓库 | 说明 |
|--------|------|------|
| 1 | [aloshdenny/reverse-SynthID](https://github.com/aloshdenny/reverse-SynthID) | SynthID 逆向/去除研究标杆 |
| 2 | [wiltodelta/remove-ai-watermarks](https://github.com/wiltodelta/remove-ai-watermarks) | 多工具集成的一站式去除 |
| 3 | [00quebec/Synthid-Bypass](https://github.com/00quebec/Synthid-Bypass) | SynthID 专用 bypass |
| 4 | [andrekassis/ai-watermark](https://github.com/andrekassis/ai-watermark) | UnMarker（CVPR 2024）官方实现 |

---

## 11. `frequency_peaks_cleansing` — Frequency Peaks Cleansing

| 优先级 | 仓库 | 说明 |
|--------|------|------|
| 1 | [andrekassis/ai-watermark](https://github.com/andrekassis/ai-watermark) | UnMarker 高频峰值清洗思路最接近 |
| 2 | [aloshdenny/reverse-SynthID](https://github.com/aloshdenny/reverse-SynthID) | 频域载体/峰值分析 |
| 3 | [ningyu1991/ScalableGANFingerprints](https://github.com/ningyu1991/ScalableGANFingerprints) | GAN 频域峰值指纹（检测侧） |
| 4 | [nxZhai/FPBA](https://github.com/nxZhai/FPBA) | FPBA 论文官方实现（语义最贴） |

---

## 12. `prnu_simulation` — PRNU Simulation / Removal

| 优先级 | 仓库 | 说明 |
|--------|------|------|
| 1 | [polimi-ispl/prnu-python](https://github.com/polimi-ispl/prnu-python) | PRNU 提取/分析常用 Python 库 |
| 2 | [pkorus/multiscale-prnu](https://github.com/pkorus/multiscale-prnu) | 多尺度 PRNU |
| 3 | [polimi-ispl/dip_prnu_anonymizer](https://github.com/polimi-ispl/dip_prnu_anonymizer) | PRNU 匿名化/去除 |
| 4 | [sim-pez/prnu](https://github.com/sim-pez/prnu) | PRNU 指纹工具 |

PRNU 属于小众数字取证方向，公开 bypass 仓库相对有限。

---

## 13. `gradient_edge_aware_perturbation` — 边缘感知梯度扰动

| 优先级 | 仓库 | 说明 |
|--------|------|------|
| 1 | [bethgelab/foolbox](https://github.com/bethgelab/foolbox) | PGD / 梯度攻击基础框架 |
| 2 | [cleverhans-lab/cleverhans](https://github.com/cleverhans-lab/cleverhans) | 梯度扰动经典库 |
| 3 | [Trusted-AI/adversarial-robustness-toolbox](https://github.com/Trusted-AI/adversarial-robustness-toolbox) | 含边界/约束攻击 |
| 4 | [PurinNyova/Image-Detection-Bypass-Utility](https://github.com/PurinNyova/Image-Detection-Bypass-Utility) | 像素扰动上游（非 edge-aware） |

---

## 14. `transfer_blackbox_attack` — 迁移黑盒攻击

| 优先级 | 仓库 | 说明 |
|--------|------|------|
| 1 | [Trustworthy-AI-Group/TransferAttack](https://github.com/Trustworthy-AI-Group/TransferAttack) | **迁移攻击专用工具箱**（语义最贴） |
| 2 | [cleverhans-lab/cleverhans](https://github.com/cleverhans-lab/cleverhans) | 迁移/集成攻击基础 |
| 3 | [Trusted-AI/adversarial-robustness-toolbox](https://github.com/Trusted-AI/adversarial-robustness-toolbox) | 黑盒/迁移攻击模块 |
| 4 | [bethgelab/foolbox](https://github.com/bethgelab/foolbox) | 多模型迁移评估 |

---

## 15. `diffusion_reconstruction` — Diffusion 重建

| 优先级 | 仓库 | 说明 |
|--------|------|------|
| 1 | [huggingface/diffusers](https://github.com/huggingface/diffusers) | Diffusion 去噪/重建 pipeline |
| 2 | [00quebec/Synthid-Bypass](https://github.com/00quebec/Synthid-Bypass) | SD 扩散重建 bypass SynthID |
| 3 | [wiltodelta/remove-ai-watermarks](https://github.com/wiltodelta/remove-ai-watermarks) | 集成 DeSynth 扩散重建 |
| 4 | [0xROOTPLS/DeSynth](https://github.com/0xROOTPLS/DeSynth) | 扩散去噪重建 |

---

## 领域标杆速查

### AI 图像 bypass / 水印对抗

| 仓库 | 主要对应方法族 |
|------|----------------|
| [aloshdenny/reverse-SynthID](https://github.com/aloshdenny/reverse-SynthID) | watermark、frequency、metadata |
| [wiltodelta/remove-ai-watermarks](https://github.com/wiltodelta/remove-ai-watermarks) | watermark、encoding、metadata、regeneration |
| [00quebec/Synthid-Bypass](https://github.com/00quebec/Synthid-Bypass) | watermark、regeneration、diffusion_reconstruction |
| [andrekassis/ai-watermark](https://github.com/andrekassis/ai-watermark) | watermark、frequency_peaks_cleansing、lpips |
| [PurinNyova/Image-Detection-Bypass-Utility](https://github.com/PurinNyova/Image-Detection-Bypass-Utility) | encoding、noise、frequency、texture、camera 等基础族 |

### 对抗攻击通用框架

| 仓库 |
|------|
| [cleverhans-lab/cleverhans](https://github.com/cleverhans-lab/cleverhans) |
| [Trusted-AI/adversarial-robustness-toolbox](https://github.com/Trusted-AI/adversarial-robustness-toolbox) |
| [richzhang/PerceptualSimilarity](https://github.com/richzhang/PerceptualSimilarity) |
| [bethgelab/foolbox](https://github.com/bethgelab/foolbox) |
| [Trustworthy-AI-Group/TransferAttack](https://github.com/Trustworthy-AI-Group/TransferAttack) |

---

## 说明

1. **参考 ≠ 可直接复用**：Pillow、diffusers、SD WebUI 等是通用工具，不是 bypass 专用，但实现同类能力时常作参考。
2. **小众方向公开项目较少**：PRNU、FPBA、DeSynth、edge-aware 等专用 bypass 仓库相对有限，语义最近的项目未必最知名。
3. **与本项目实测一致**：camera / noise / texture 对应 PurinNyova 基础族，外部检测效果最好；watermark / lpips / prnu 等参考项目效果也多为「小幅有效」。
