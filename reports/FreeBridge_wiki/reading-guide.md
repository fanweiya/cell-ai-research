# Reading Guide

本指南旨在帮助开发者快速理解 FreeBridge 项目。建议按照从宏观配置到微观实现的顺序阅读，先了解项目结构和数据流，再深入核心算法逻辑。

## Step 1: 项目概览与环境配置 (~15 min)

**Files:** `README.md`, `setup.py`, `configs/train.yaml`, `configs/experiment/bbbc021.yaml`

首先阅读 README.md 了解项目目标和整体架构。接着查看 setup.py 确认依赖项。然后深入 configs/train.yaml 和 bbbc021.yaml，重点关注 Hydra 配置结构、数据路径设置、模型超参数以及实验划分逻辑，这是理解项目如何运行的关键。

## Step 2: 数据预处理流程 (~20 min)

**Files:** `data_prep/build_bbbc021_endpoints.py`, `data_prep/crop_bbbc021_singlecell.py`, `data_prep/make_split.py`

关注数据如何从原始图像转化为模型输入。build_bbbc021_endpoints.py 展示端点构建逻辑，crop_bbbc021_singlecell.py 涉及图像切分细节，make_split.py 定义训练/验证/测试集划分。理解数据流向是后续理解模型的基础。

## Step 3: VAE 模型训练与潜变量提取 (~25 min)

**Files:** `data_prep/train_vae_full.py`, `data_prep/export_latents_from_vae.py`, `data_prep/export_latents_mu.py`

学习变分自编码器 (VAE) 的训练过程。train_vae_full.py 包含模型定义和训练循环，export_latents_from_vae.py 和 export_latents_mu.py 展示如何从训练好的模型中提取潜变量表示。注意模型架构和损失函数的设计。

## Step 4: 自由桥接核心逻辑 (~30 min)

**Files:** `freebridge/__init__.py`, `freebridge/models.py`, `freebridge/training.py`

深入核心模块 freebridge。查看 __init__.py 了解模块导出，models.py 研究 FreeBridge 模型架构，training.py 掌握训练循环和扰动响应建模的具体实现。这是项目最核心的部分。

## Step 5: 实验脚本与自动化 (~10 min)

**Files:** `scripts/train.sh`, `data_prep/run_week.sh`

查看训练脚本如何调用配置和模块。train.sh 是主要入口，run_week.sh 可能涉及长时间运行的批处理任务。理解脚本如何组合各个组件以完成端到端实验。

## Step 6: 辅助工具与适配器 (~15 min)

**Files:** `data_prep/cellvae_adapter.py`, `data_prep/finetune_decoder_lpips.py`, `data_prep/gen_cells.py`

了解项目中的工具函数。cellvae_adapter.py 可能处理 VAE 与其他模型的接口，finetune_decoder_lpips.py 涉及解码器微调，gen_cells.py 可能用于生成细胞图像。这些文件展示了项目的扩展性和灵活性。

## Tips

- 重点关注配置文件中的路径设置，确保理解数据如何被加载和处理。
- 在阅读核心模型代码时，尝试绘制数据流向图，帮助理解张量变换过程。
- 利用 .codegraph 目录了解代码依赖关系，辅助理解模块间交互。
- 遇到不熟悉的术语时，先查看相关文档或注释，避免陷入过深的细节。
