# Reading Guide

本代码库是一个基于 Cell Painting 技术的细胞形态学基准测试与特征提取系统。建议按‘配置先行、核心逻辑跟进、工具链收尾’的顺序阅读，以快速建立全局认知并深入关键模块。

## Step 1: 项目概览与依赖配置 (~5 min)

**Files:** `README.md`, `requirements.txt`, `huggingface_loader/pyproject.toml`

首先了解项目目标、架构概览及核心依赖。README.md 提供整体功能描述；requirements.txt 和 pyproject.toml 揭示技术栈（如 PyTorch、HuggingFace 库），帮助理解环境要求。

## Step 2: 核心配置参数解析 (~10 min)

**Files:** `feature-extraction/src/config.py`, `benchmarks/config.py`, `benchmarks/configs/benchmarks.yaml`

这些文件定义了数据路径、模型选择、批处理大小等关键参数。重点关注 config.py 中的类结构，理解配置如何驱动特征提取与基准测试流程。

## Step 3: 数据安装与预处理流程 (~15 min)

**Files:** `data_installation/README.md`, `data-preprocessing/normalize.py`, `data-preprocessing/dimensionality_reduction.py`

了解原始数据如何下载、去光照校正，以及后续如何标准化和降维。注意数据流向和中间产物格式，这是特征提取的基础。

## Step 4: 特征提取核心流水线 (~20 min)

**Files:** `feature-extraction/src/pipeline.py`, `feature-extraction/src/model_inference.py`

阅读特征提取的主流程：图像加载、模型推理、结果聚合。重点关注多模型支持机制和并行处理策略，这是系统的核心计算部分。

## Step 5: HuggingFace 数据集集成 (~10 min)

**Files:** `huggingface_loader/dataset_builder.py`, `raw_to_huggingface/convert.py`

理解如何将本地图像数据转换为 HuggingFace 数据集格式。注意数据划分逻辑和元数据管理，这对后续模型训练至关重要。

## Step 6: 基准测试执行与评估 (~15 min)

**Files:** `benchmarks/enrichment/cpg_moa/run_cpg_moa_enrichment.py`, `benchmarks/enrichment/cpg_moa/plot_moa_results.py`

分析基准测试的具体实现：富集分析、结果可视化。关注统计方法和评估指标，理解如何验证特征提取的有效性。

## Step 7: 辅助工具与实用函数 (~10 min)

**Files:** `data/utils.py`, `benchmarks/utils/plotting.py`

浏览通用工具函数，如数据加载器、绘图辅助。这些模块虽非核心，但能提升代码复用性和可维护性。

## Tips

- 先通读 README.md 建立整体框架，再深入具体模块
- 重点关注 config.py 文件，配置参数往往决定系统行为
- 遇到复杂逻辑时，结合调试日志或测试用例理解数据流
- 利用 .codegraph 目录了解代码依赖关系图
