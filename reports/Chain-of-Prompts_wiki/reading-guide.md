# Reading Guide

本代码库是一个基于 SAM (Segment Anything Model) 的实例分割演示与评估项目。建议按以下顺序阅读：先理解项目配置与依赖，再掌握核心模型架构，最后深入具体实现逻辑。

## Step 1: 了解项目概览与依赖 (~10 min)

**Files:** `README.md`, `requirements.txt`, `DATASETS.md`

首先阅读 README.md 了解项目目标、快速开始指南及整体架构；通过 requirements.txt 掌握依赖库版本；DATASETS.md 说明数据集格式与加载方式，为后续实验做准备。

## Step 2: 理解核心入口与配置 (~15 min)

**Files:** `core/cop.py`

cop.py 是项目的核心入口文件，包含主逻辑流程。重点关注其如何初始化模型、加载数据、执行推理及保存结果，这是理解整个系统运作的关键。

## Step 3: 掌握 SAM 模型初始化 (~15 min)

**Files:** `core/sam/__init__.py`, `core/sam/build_sam.py`

在 __init__.py 中查看 SAM 模块的导出接口；build_sam.py 负责根据配置文件构建模型，注意其如何加载预训练权重及选择不同规模的模型架构。

## Step 4: 研究模型配置文件 (~10 min)

**Files:** `core/sam/configs/sam2.1_hiera_b+.yaml`, `core/sam/configs/sam2_hiera_b+.yaml`

这些 YAML 文件定义了模型的具体参数，如 backbone 类型、输入尺寸、训练/推理超参数。对比不同配置文件可理解模型变体的差异。

## Step 5: 深入自动掩码生成器 (~20 min)

**Files:** `core/sam/automatic_mask_generator.py`

该文件实现了自动掩码生成的核心算法，包括提示点处理、掩码后处理等。重点关注其如何从原始预测生成最终分割结果，这是 SAM 功能的关键实现。

## Step 6: 查看基线实现 (~10 min)

**Files:** `core/sam/build_sam_baseline.py`

基线实现通常包含更简洁的模型构建逻辑，可用于对比理解标准 SAM 与当前项目变体的区别，有助于把握核心改进点。

## Tips

- 先运行示例代码再阅读对应文件，建立直观理解
- 遇到复杂逻辑时，结合调试器逐步跟踪执行流程
- 关注配置文件与代码的对应关系，理解参数如何影响行为
