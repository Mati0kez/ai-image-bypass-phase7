# Domain Glossary

本文件记录 AI 图片检测对抗框架的领域术语定义。
所有术语均与代码中的概念严格对应，不包含实现细节。

## TransformConfig

描述一次完整图片处理流程的不可变配置对象。
包含输入输出路径、profile 选择、各方法族强度参数、
元数据模式以及未来扩展点（LPIPS、水印、detector 反馈）。

## TransformModule

一个可插拔的变换单元。
暴露 name 属性和 apply 方法，接受 Config 和 rng，
返回处理后的图片。
所有具体方法族（metadata、frequency、camera 等）
都继承此抽象基类。

## Registry

方法族名称到 TransformModule 实例的映射表。
支持按 profile 动态选择启用的方法族集合，
并提供 register_module 函数进行模块注册。

## BenchmarkRunner

基准评估运行器。
负责批量加载图像、调用 Transform Pipeline、
收集 perceptual 指标和 detection 指标，
并生成结构化报告。

## Bypass Rate

在给定 detector 阈值下，成功将图像分数降低到阈值以下的比例。
是衡量“对抗有效性”的核心指标。

## Perceptual Budget

感知代价预算。
指在保持图像视觉质量的前提下，允许的 perceptual 距离上限。
常用指标包括 LPIPS、SSIM、PSNR。

## Detection Score Curve

检测分数变化曲线。
记录 detector-in-the-loop 迭代过程中，
detector 分数随迭代步数的变化序列。

## PlatformAdapter

外部平台 Detector 适配器抽象基类。
定义统一接口（score、get_quota_usage），
支持 Hive、Illuminarty 等真实平台和 Mock 实现。

## External Validation

真实外部平台验证。
通过 PlatformAdapter 调用第三方 detector API，
记录 bypass rate、perceptual 指标和配额消耗，
与内部 benchmark 统一输出格式。

## Quota Guard

配额保护机制。
在 ValidationRunner 中实现 rate limit（每分钟请求上限）
和 cost guard（总花费上限），超限时自动降级为 MockAdapter。

## Experiment Mode

实验模式。
BenchmarkRunner 的特殊运行模式（mode='experiment'），
用于大规模真实平台验证，输出 bypass rate（含 Wilson CI）、
失败案例 CSV 和人类可读的 summary。

## Wilson Score Confidence Interval

Wilson score 置信区间。
用于估计 bypass rate 的统计显著性范围，
提供 lower/upper bound（默认 95% 置信水平）。

## Failure Case Analysis

失败案例分析。
记录未能 bypass 的图像（final_score >= threshold），
包括原始/变换路径、perceptual 距离和 detector 分数，
便于后续根因分析和迭代优化。

## Closed-Loop Optimization

闭环优化（P2 已实现结构）。
以 detector.score 返回的真实分数为反馈信号，迭代调整 StrengthOverride
并重新变换图像，直至分数低于阈值或触发 early stopping。
当前实现支持 mock detector 与真实接口调用路径。

## Targeted Watermark Removal

针对性水印移除（目标能力）。
在频域对已知水印载波位置进行定向处理，
而非全局频谱衰减。属于研究领域概念。

## Semantic Regeneration

语义级重生成（目标能力）。
通过 img2img 或扩散模型生成语义相近的新图像，
以降低 detector 分数。属于研究领域概念。

## Capability Maturity

能力成熟度。
README 中用于标注各功能实现状态的三档分类：
可用、实验性、占位。
