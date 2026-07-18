# Reading Guide

本代码库是一个基于Mask2Former的白细胞图像细粒度分割项目。建议按照从宏观配置到核心逻辑，再到工具实现的顺序阅读，先理解项目结构和配置，再深入模型训练与推理流程。

## Step 1: 项目概览与快速开始 (~10 min)

**Files:** `README.md`, `GETTING_STARTED.md`, `INSTALL.md`

首先了解项目的整体目标、依赖环境和安装步骤。重点关注项目支持的功能（语义/实例/全景分割）以及快速上手的命令，建立对项目的整体认知。

## Step 2: 配置文件与数据准备 (~15 min)

**Files:** `Mask2Former/mask2former/config.py`, `Mask2Former/datasets/README.md`, `dataset_txt`

深入理解项目的配置系统，特别是如何定义模型参数、训练超参数和数据加载配置。重点关注白细胞图像的数据格式、类别属性映射以及数据加载流程，这是理解后续模型输入的关键。

## Step 3: 模型架构与核心组件 (~20 min)

**Files:** `Mask2Former/mask2former/modeling/pixel_decoder/ops/setup.py`, `Mask2Former/mask2former_video/config.py`

了解模型的核心组件，特别是像素解码器（pixel decoder）和算子实现。注意视频分割配置与图像分割配置的区别，理解模型如何适应不同输入模态。

## Step 4: 训练与评估流程 (~25 min)

**Files:** `configs`, `utils`

研究训练脚本和评估脚本，理解数据如何被处理、模型如何被训练和验证。重点关注日志记录、模型保存和结果报告机制，这是实验复现和调试的基础。

## Step 5: 推理与演示 (~15 min)

**Files:** `Mask2Former/demo/README.md`, `Mask2Former/demo_video/README.md`, `results`

学习如何使用训练好的模型进行推理和可视化。查看演示代码和结果报告，理解模型的输出格式和性能表现，特别是白细胞分割的细粒度标注效果。

## Step 6: 高级功能与扩展 (~20 min)

**Files:** `ADVANCED_USAGE.md`, `MODEL_ZOO.md`, `tools/README.md`

探索项目的进阶用法，如模型 zoo、自定义训练流程和工具脚本。了解如何扩展模型功能或集成到现有工作流中。

## Tips

- 先阅读配置文件再深入代码，理解数据流和模型结构
- 重点关注白细胞图像的特殊处理逻辑，这是项目的核心创新点
- 遇到不理解的模块时，先查看README和文档，再追溯代码实现
- 利用results目录中的实验结果反推模型性能和配置参数
- 注意区分图像分割和视频分割的配置差异
