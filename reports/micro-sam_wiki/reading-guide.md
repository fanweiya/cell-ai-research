# Reading Guide

本指南旨在帮助开发者快速理解 micro-sam 代码库的架构与核心功能。建议从项目配置和文档入手，建立宏观认知，随后深入核心模块 micro_sam 和 finetuning，最后通过示例和测试验证理解。

## Step 1: 理解项目概览与安装配置 (~15 min)

**Files:** `README.md`, `pyproject.toml`, `setup.cfg`, `development/README.md`

首先阅读 README.md 了解项目目标、核心功能及快速开始指南。接着查看 pyproject.toml 和 setup.cfg 理解依赖管理、项目结构和构建配置。development/README.md 将揭示开发环境设置和贡献指南。

## Step 2: 掌握核心库架构 (micro_sam) (~30 min)

**Files:** `micro_sam/__init__.py`, `micro_sam/util.py`, `micro_sam/segment.py`, `micro_sam/models.py`

进入核心模块，查看 __init__.py 了解库的导出接口。重点阅读 util.py 理解通用工具函数，segment.py 掌握分割逻辑，models.py 了解模型加载与集成方式。这是理解 SAM 如何被适配到显微图像的关键。

## Step 3: 探索微调与评估流程 (finetuning) (~25 min)

**Files:** `finetuning/README.md`, `finetuning/generalists/training/`, `finetuning/evaluation/`

阅读 finetuning/README.md 了解微调的整体工作流。然后深入 generalists/training 目录查看训练脚本，理解如何自定义训练参数和数据加载。最后查看 evaluation 目录，了解模型性能评估指标和脚本。

## Step 4: 学习示例与交互式应用 (~20 min)

**Files:** `examples/README.md`, `examples/interactive_segmentation.py`, `notebooks/`

通过 examples/README.md 了解可用的示例类型。运行或阅读 interactive_segmentation.py 等脚本，学习如何在实际场景中调用库进行交互式标注和自动分割。notebooks 提供了更详细的交互式教程，适合快速上手。

## Step 5: 理解测试与质量保证 (~15 min)

**Files:** `test/test_micro_sam.py`, `test/test_finetuning.py`

查看测试文件以反向理解核心功能的使用方式。test_micro_sam.py 展示了库 API 的正确用法，test_finetuning.py 则验证了微调流程的完整性。这有助于发现潜在的使用陷阱和边界条件。

## Tips

- 先运行示例脚本再阅读代码，建立直观感受
- 遇到不理解的函数时，查看其调用链和测试用例
- 关注 micro_sam 和 finetuning 两个核心目录的依赖关系
- 利用 notebooks 进行交互式学习，边运行边理解
