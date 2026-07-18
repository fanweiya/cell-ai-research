# Reading Guide

本指南旨在帮助你快速理解基于Vision Transformer的病理细胞分割框架VitaminP。请按照从宏观配置到核心逻辑的顺序阅读，重点关注数据流和模型架构。

## Step 1: 理解项目概览与部署环境 (~10 min)

**Files:** `README.md`, `Dockerfile`, `requirements.txt`

首先通过README.md了解项目的核心功能（病理细胞分割与合成）、依赖环境及基本用法。接着查看Dockerfile和requirements.txt，确认项目运行所需的Python版本、关键库（如PyTorch, Vision Transformer相关库）以及Docker构建指令，为后续代码阅读建立环境上下文。

## Step 2: 掌握核心配置结构 (~15 min)

**Files:** `dataset/config.py`, `configs/inference/inference.yaml`, `configs/jobs/job.yaml`

dataset/config.py定义了数据集加载、增强及HV图生成的全局配置，是理解数据流向的关键。configs目录下的yaml文件则分别管理推理（inference）和作业（jobs）的具体参数，重点关注模型输入输出路径、超参数设置及不同模态（如Xenium, H&E）的配置差异。

## Step 3: 梳理训练与推理入口流程 (~20 min)

**Files:** `scripts/train.py`, `scripts/run_wsi_inference.py`

train.py是模型训练的主入口，需关注其如何解析配置、初始化数据集、构建Vision Transformer模型以及训练循环逻辑。run_wsi_inference.py则是全切片图像（WSI）推理的入口，重点看它如何加载预训练模型、处理大规模图像切片以及调用后处理模块生成最终分割结果。

## Step 4: 深入核心数据模块 (~25 min)

**Files:** `dataset/__init__.py`, `dataset/dataset.py`, `dataset/utils.py`

进入dataset模块内部，查看数据加载器如何从Zarr格式读取多模态病理数据，数据增强策略如何应用，以及HV图（Heatmap Vector）是如何生成的。这是理解模型输入数据形态和预处理逻辑的核心。

## Step 5: 解析模型架构与后处理 (~20 min)

**Files:** `vitaminp/models/vit.py`, `postprocessing/hv_to_instances.py`

vitaminp/models/vit.py包含Vision Transformer的具体实现，需关注其编码器结构、注意力机制及分割头的输出形式。postprocessing模块负责将模型输出的HV图转换为实例分割掩码，这是从预测结果到可用分割结果的关键步骤，需理解其算法逻辑。

## Step 6: 了解评估与指标计算 (~10 min)

**Files:** `metrics/segmentation_metrics.py`, `metrics/instance_metrics.py`

查看metrics模块如何计算二值分割和实例分割的评估指标（如Dice系数、IoU等）。了解这些指标如何定义，以及它们如何被集成到训练或评估脚本中，这对于理解项目如何量化模型性能至关重要。

## Tips

- 在阅读代码时，优先关注函数签名和文档字符串，快速把握模块功能。
- 结合配置文件和脚本入口，尝试在脑海中绘制数据从读取到输出的完整流程图。
- 遇到不理解的依赖库时，先查阅requirements.txt确认版本，再查看官方文档。
- 利用IDE的跳转功能，从入口脚本追踪到具体的模型类定义，理清调用链。
