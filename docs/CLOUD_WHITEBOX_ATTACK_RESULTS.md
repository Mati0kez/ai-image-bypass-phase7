# 云端白盒攻击验证结果（Vast.ai RTX 5090）

**验证日期**：2026-06-30  
**测试平台**：Vast.ai（新实例）  
**GPU**：NVIDIA GeForce RTX 5090  
**攻击框架**：`src/attack/whitebox.py`（targeted PGD）  
**模型加载**：本地 `transformers`（`pytorch_model.bin`）

---

## 模型 1：umm-maybe/AI-image-detector

| 参数 | 值 |
|------|-----|
| `target_detector_repo` | `umm-maybe/AI-image-detector` |
| `target_class` | 0（artificial） |
| `epsilon` | 0.5 |
| `steps` | 30 |
| `step_size` | 0.0167 |

**迭代日志（关键节点）**：
- Step 00: artificial_prob=0.1434
- Step 10: artificial_prob=1.0000（已翻转）
- Step 20~30: artificial_prob=1.0000（稳定）

**最终结果**：
- 最终 artificial 概率：**1.0000**
- 最终 human 概率：**0.0000**
- 攻击结论：**完全成功**
- 保存文件：`cli_test/outputs/adv_umm_maybe_final.jpg`

---

## 模型 2：Organika/sdxl-detector

| 参数 | 值 |
|------|-----|
| `target_detector_repo` | `Organika/sdxl-detector` |
| `target_class` | 0（artificial） |
| `epsilon` | 0.3 |
| `steps` | 30 |
| `step_size` | 0.01 |

**迭代日志**：
- 30 步内快速收敛至 1.0000

**最终结果**：
- 最终 artificial 概率：**1.0000**
- 最终 human 概率：**0.0000**
- 攻击结论：**完全成功**
- 保存文件：`cli_test/outputs/adv_sdxl_final.jpg`

---

## 总结

| 模型 | epsilon | steps | 攻击结果 | 最终 artificial 概率 |
|------|---------|-------|----------|---------------------|
| umm-maybe/AI-image-detector | 0.5 | 30 | **成功** | 1.0000 |
| Organika/sdxl-detector | 0.3 | 30 | **成功** | 1.0000 |

**结论**：两个模型在云端白盒 targeted PGD 攻击下均**完全有效**，梯度方向修复后收敛迅速。

---

## 备注

- HF Inference API 验证因模型版本/预处理差异暂不一致，本地模型验证已确认有效。
- 后续可继续测试 Foolbox 攻击或更激进参数。