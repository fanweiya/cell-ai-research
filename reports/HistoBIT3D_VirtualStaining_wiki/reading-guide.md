# Reading Guide

本指南旨在帮助你系统性地理解 HistoBIT3D 项目，这是一个基于 GAN 的 3D 组织虚拟 H&E 染色框架。建议从配置和入口点开始，逐步深入到核心逻辑和工具函数，以建立对整体架构的清晰认知。

## Step 1: 理解项目概览与环境依赖 (~10 min)

**Files:** `README.md`, `HistoBIT3D_Code/requirements.txt`, `HistoBIT3D_Code/setup.py`

首先通过 README.md 了解项目的整体目标、功能特性和使用方法。接着查看 requirements.txt 和 setup.py，明确项目依赖的第三方库、Python 版本要求以及安装方式，为后续代码阅读奠定环境基础。

## Step 2: 掌握核心配置结构 (~15 min)

**Files:** `HistoBIT3D_Code/uvcgan2/config/config.py`

阅读 config.py 以理解项目的配置管理方式。重点关注数据路径、模型超参数（如学习率、batch size）、训练策略和实验设置。这是理解模型行为的关键，因为大部分逻辑都围绕这些配置展开。

## Step 3: 探索数据预处理与重建流程 (~20 min)

**Files:** `HistoBIT3D_Code/scripts/reconstruct_bit_vhe_from_metadata.py`, `HistoBIT3D_Code/scripts/downsize_right.py`

了解数据如何被加载、预处理和重建。reconstruct_bit_vhe_from_metadata.py 展示了从元数据重建 3D 体积数据的核心逻辑，而 downsize_right.py 则涉及图像尺寸调整。理解数据流是掌握模型输入输出的前提。

## Step 4: 分析训练与微调脚本 (~25 min)

**Files:** `HistoBIT3D_Code/scripts/pretrain_BIT2HE.py`, `HistoBIT3D_Code/scripts/resume_training_from_config_3D.py`, `HistoBIT3D_Code/scripts/finetune_from_checkpoint_3D.py`

研究训练脚本以理解模型训练流程。pretrain_BIT2HE.py 展示预训练过程，resume_training_from_config_3D.py 涉及断点续训，finetune_from_checkpoint_3D.py 则关注微调策略。重点关注模型初始化、损失函数定义和优化器设置。

## Step 5: 深入评估与指标计算 (~20 min)

**Files:** `HistoBIT3D_Code/scripts/eval_all_epochs_A2B_metrics.py`, `HistoBIT3D_Code/scripts/eval_fid.py`, `HistoBIT3D_Code/scripts/eval_il2_scores.py`

学习如何评估模型性能。eval_all_epochs_A2B_metrics.py 包含全面的指标计算，eval_fid.py 专注于 FID 分数，eval_il2_scores.py 则计算 IL2 评分。理解这些评估方法有助于判断模型质量和改进方向。

## Step 6: 查看推理与辅助工具 (~10 min)

**Files:** `HistoBIT3D_Code/scripts/run_inference_A2B.sh`, `HistoBIT3D_Code/scripts/print_model.py`, `HistoBIT3D_Code/scripts/fix_double_tif_suffix.py`

了解模型推理流程和辅助工具。run_inference_A2B.sh 是推理脚本的入口，print_model.py 用于打印模型结构，fix_double_tif_suffix.py 处理文件名问题。这些工具在实际应用中非常实用。

## Step 7: 理解脚本封装与自动化 (~15 min)

**Files:** `HistoBIT3D_Code/scripts/run_eval_all_epochs_A2B_metrics.sh`, `HistoBIT3D_Code/scripts/run_eval_all_epochs_A2B_metrics_style_TM.sh`, `HistoBIT3D_Code/scripts/run_eval_all_epochs_A2B_metrics_style_WSL.sh`, `HistoBIT3D_Code/scripts/run_finetune_from_checkpoint_3D_WSL.sh`

分析 Shell 脚本如何封装和自动化执行流程。这些脚本通常调用 Python 脚本并设置环境变量，理解它们有助于掌握项目的实验工作流和不同场景下的配置差异。

## Tips

- 在阅读代码时，优先关注函数签名和文档字符串，快速把握功能意图。
- 结合配置文件和实际脚本，追踪数据从输入到输出的完整路径。
- 遇到不理解的模块时，先查看其调用关系，再深入具体实现。
- 利用 print_model.py 和配置信息，建立对模型架构的直观认识。
