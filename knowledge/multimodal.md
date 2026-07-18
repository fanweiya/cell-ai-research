# Multimodal Learning and Representation

## 2026-07-12 | Diarization-Guided Qwen-ASR Adaptation for Multilingual Two-Speaker Conversational Speech | arXiv:2607.08208 | 核心方法：对话分离引导的自监督ASR适配 | 复现级别：D (无代码) | priority: 17

**论文概述**：使用对话分离（speaker diarization）结果引导Qwen-ASR模型在多语言双声道对话场景下的自适应。通过分离说话人声道信号，提升ASR模型对不同语言混合对话的识别性能。

**算法要点**：
- 对话分离模型提取说话人时间边界
- 基于分离信号的ASR适配器训练
- 多语言混合对话鲁棒性提升

**代码分析**：
- 无公开代码仓库
- 实现依赖Qwen-ASR框架

**复现评估**：
- 需要原始数据和分离模型
- 无法直接进入代码复现

---

## 2026-07-12 | CT-CLIP Representations for Multimodal Lung Cancer Survival Prediction | arXiv:2607.08503 | 核心方法：CT-文本对比学习 | 复现级别：D (无代码) | priority: 16

**论文概述**：结合CT影像和临床文本的CLIP表示，用于肺癌生存预测。通过跨模态对齐学习，提取多模态特征进行预后建模。

**算法要点**：
- CT影像编码器与文本编码器的对比学习
- 生存分析头（Cox loss 或类似）

**代码分析**：
- 无公开代码

**复现评估**：
- 需要医学影像和文本配对数据

---