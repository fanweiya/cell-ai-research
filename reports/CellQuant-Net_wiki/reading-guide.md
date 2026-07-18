# Reading Guide

本指南旨在帮助你系统性地理解 CellQuant-Net 项目。建议从配置和入口点入手，建立对整体架构的宏观认识，随后深入核心模型与数据处理逻辑，最后关注后处理与工具函数。通过由浅入深的阅读，逐步掌握代码结构与设计意图。

## Step 1: 项目概览与依赖配置 (~10 分钟)

**Files:** `README.md`, `requirements.txt`, `WSI_QA/config.py`

首先阅读 README.md 了解项目背景、功能概述及运行流程；接着查看 requirements.txt 确认依赖包版本；最后深入 WSI_QA/config.py 理解全局配置项，如路径设置、模型参数等，这是理解项目运行环境的基础。

## Step 2: 核心模型架构解析 (~20 分钟)

**Files:** `CP-Net/model/model.py`, `CP-Net/model/unirepLKnet.py`

进入 CP-Net 模块，先阅读 model.py 了解整体模型结构定义，再深入 unirepLKnet.py 掌握具体的网络层实现与特征提取机制，这是理解细胞核检测与分类算法的核心部分。

## Step 3: 数据加载与预处理流程 (~15 分钟)

**Files:** `CP-Net/dataset.py`, `CP-Net/spli_H.py`

查看 dataset.py 了解 WSI 图像如何被切片、增强并转换为模型输入；同时阅读 spli_H.py 理解图像分块策略，确保理解数据如何从原始文件转化为可训练/推理的张量。

## Step 4: 推理流水线与后处理 (~15 分钟)

**Files:** `CP-Net/post_process.py`, `CP-Net/test_cp_net.py`

阅读 post_process.py 掌握模型输出如何被转换为最终的细胞核坐标、类别及质量评分；通过 test_cp_net.py 了解端到端推理的调用流程，包括输入路径、模型加载及结果保存逻辑。

## Step 5: 辅助工具与输出格式 (~10 分钟)

**Files:** `CP-Net/qupath_jsn.py`, `CP-Net/configs/configs_test.yaml`

查看 qupath_jsn.py 了解结果如何与 QuPath 格式兼容，便于后续分析；同时阅读 configs_test.yaml 了解测试配置的具体参数，有助于复现实验或调整推理设置。

## Step 6: WSI_QA 模块与质量评估 (~15 分钟)

**Files:** `WSI_QA/datasets/dataset.py`, `WSI_QA/network/ConvNeXt/ConvNeXtUnet.py`

深入 WSI_QA 模块，理解其独立的数据集加载逻辑及基于 ConvNeXt 的质量评估网络结构，这是实现细胞核质量评分的关键组件。

## Tips

- 在阅读模型文件时，优先关注类定义和核心方法，忽略过于细节的数学公式推导。
- 结合 README 中的流程图或架构图（如有）对照代码，能更快建立整体认知。
- 遇到不理解的函数调用时，使用 IDE 的跳转功能追踪调用链，避免孤立阅读。
- 配置文件中常包含路径和超参数，修改前务必确认其影响范围。
