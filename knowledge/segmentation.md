# Cell Segmentation

## 2026-07-12 | An Edge-aware Prompt-enhanced SAM for Ultrasound Image Segmentation | arXiv:2607.07240 | 核心方法：边缘感知提示增强SAM | 复现级别：D (无代码) | priority: 15

**论文概述**：针对超声图像噪声大、边界模糊的特点，在SAM（Segment Anything Model）基础上引入边缘感知模块和提示增强机制，通过显式边缘特征引导分割，显著提卟边界定位精度。

**算法要点**：
- 损失函数：`L = λ1*L_dice + λ2*L_edge + λ3*L_prompt`
- 边缘编码器提取边界特征
- SAM Prompt Encoder 集成可学习提示向量
- 多任务协同优化

**代码分析**：
- 基于SAM架构修改
- 无公开代码仓库

**复现评估**：
- 需要超声图像数据集
- 依赖SAM预训练权重

---

## 2026-07-12 | Revisiting foundation models for cell instance segmentation | arXiv:2607.17845 | 核心方法：重新审视基础模型在细胞实例分割中的应用 | 复现级别：? | priority: ?

**论文概述**：评估SAM等视觉基础模型在细胞实例分割任务上的性能，分析其优势和局限性。

**算法要点**：
- SAM在显微图像上的适应性
- 实例分割后处理优化

**代码分析**：
- 待查

**复现评估**：
- 待评估

---