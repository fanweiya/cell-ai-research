# Reading Guide

本代码库是一个名为UCell的通用细胞分割模型项目，包含训练、推理、评估及死神经元分析等完整流程。建议按‘配置 -> 核心模型 -> 训练/推理流程 -> 分析工具 -> 测试’的顺序阅读，以建立对系统架构和关键逻辑的整体认知。

## Step 1: 了解项目概览与基础配置 (~10 min)

**Files:** `README.md`, `config.py`, `pyproject.toml`

首先通过README.md了解项目背景、依赖和快速开始指南；接着阅读config.py理解全局配置参数（如路径、超参数）；最后查看pyproject.toml确认项目依赖和构建配置。这有助于建立对项目的整体认知。

## Step 2: 掌握核心模型架构 (~25 min)

**Files:** `ucell/layers.py`, `ucell/frm.py`, `ucell/dynamics.py`

阅读ucell/layers.py了解基础层实现；然后深入ucell/frm.py理解FRM模型的核心结构；最后通过ucell/dynamics.py掌握细胞动力学的数学建模部分。这是理解模型如何工作的关键。

## Step 3: 理解训练与推理流程 (~20 min)

**Files:** `train.py`, `predict.py`, `eval.py`

train.py展示完整的训练循环和数据处理；predict.py演示推理流程；eval.py提供评估指标计算。这三个文件串联起模型从训练到应用的全生命周期。

## Step 4: 探索少样本适配机制 (~15 min)

**Files:** `few_shot_adapt.py`, `ucell/lora.py`

few_shot_adapt.py实现少样本学习策略，ucell/lora.py提供LoRA微调的具体实现。了解这些内容有助于理解模型如何高效适应新任务。

## Step 5: 学习死神经元分析工具 (~20 min)

**Files:** `dead_neuron_analysis/detect_dead_neurons.py`, `dead_neuron_analysis/analyze_neurons_advanced.py`

detect_dead_neurons.py实现神经元活性检测算法；analyze_neurons_advanced.py提供深入分析功能。这些工具对于理解模型内部状态和优化至关重要。

## Step 6: 检查数据加载与处理 (~10 min)

**Files:** `data.py`

data.py包含数据加载、预处理和增强逻辑。理解数据流对于调试和自定义数据集非常重要。

## Step 7: 验证模型加载与权重一致性 (~10 min)

**Files:** `tests/test_checkpoint_loading.py`

通过测试文件了解不同检查点格式的加载机制和权重验证方法，确保模型在不同场景下的稳定性。

## Tips

- 在阅读核心模型文件时，建议配合绘制简单的架构图来理解数据流向
- 遇到不理解的数学公式或算法时，先查看相关文档注释，再深入代码实现
- 重点关注config.py中的参数如何影响各个模块的行为
- 死神经元分析部分与模型性能密切相关，建议结合训练日志一起理解
