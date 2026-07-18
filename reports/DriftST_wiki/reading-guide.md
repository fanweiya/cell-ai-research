# Reading Guide

本指南旨在帮助你快速理解 DriftST 项目，该框架用于从 H&E 组织切片推断空间转录组数据。建议按照从宏观配置到核心逻辑，再到具体实现的顺序阅读，重点关注数据流向和模型训练机制。

## Step 1: 项目概览与环境配置 (~5 min)

**Files:** `README.md`, `requirements.txt`, `environment.yml`

首先了解项目的整体目标、依赖库和运行环境。README 提供项目背景和使用说明，requirements 和 environment 文件定义了运行所需的 Python 包版本，确保后续代码执行环境一致。

## Step 2: 入口脚本与工作流程 (~10 min)

**Files:** `scripts/run_spot_level_train.sh`, `scripts/run_xenium_cell_level_preprocess.sh`, `scripts/run_xenium_cell_level_train.sh`

查看这些 Shell 脚本以理解项目的完整工作流程。重点关注它们如何调用 Python 模块、传递参数以及处理数据路径，这将帮助你建立对训练和预处理流程的宏观认识。

## Step 3: 数据预处理核心流程 (~15 min)

**Files:** `process/preprocess_spot_level.py`, `process/preprocess_xenium_cell_level.py`

深入阅读这两个文件，理解原始数据如何被清洗、转换和标准化。注意数据加载方式、特征工程步骤以及如何处理 H&E 图像与空间转录组数据的对齐问题。

## Step 4: 特征选择与基因筛选 (~10 min)

**Files:** `process/select_xenium_cell_level_genes.py`, `process/select_xenium_cell_level_hvg.py`, `process/generate_xenium_cell_level_splits.py`

了解项目如何筛选高变基因（HVG）和空间变量基因。这些步骤对模型性能至关重要，注意特征选择的统计方法和数据分集策略。

## Step 5: 核心数据加载与模型架构 (~15 min)

**Files:** `src/dataset.py`, `src/model.py`

dataset.py 定义了数据加载器，model.py 实现了神经网络架构。重点关注数据如何被组织成批次、模型的结构设计以及前向传播逻辑，这是理解模型行为的基础。

## Step 6: 漂移训练机制 (~15 min)

**Files:** `src/drift_step.py`

这是项目的核心创新点。理解漂移步（drift step）如何实现从 H&E 到空间转录组的映射，注意其中的优化目标和梯度更新机制。

## Step 7: 评估与后处理 (~10 min)

**Files:** `src/evaluation.py`, `src/postprocess.py`

了解模型如何被评估以及输出结果如何被处理。关注评估指标的选择和后处理步骤，如结果可视化或格式转换。

## Tips

- 在阅读代码时，先关注函数签名和主要逻辑流程，再深入细节实现。
- 结合入口脚本和核心代码，追踪数据从输入到输出的完整路径。
- 遇到不理解的数学公式或算法时，先参考 README 中的理论说明。
- 使用调试器或添加打印语句来观察数据在模型中的流动。
