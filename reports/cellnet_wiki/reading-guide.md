# Reading Guide

本指南旨在帮助你快速理解CellNet项目，通过从入口点和配置开始，逐步深入到核心逻辑和工具函数。建议按顺序阅读，每一步都关注关键设计模式和数据流。

## Step 1: 理解项目概览与配置 (~10 min)

**Files:** `README.md`, `pyproject.toml`, `cellnet.yml`

首先阅读README.md了解项目目标、依赖和快速开始指南；查看pyproject.toml确认项目结构、依赖包和构建配置；cellnet.yml提供实验配置示例，帮助理解参数设置。

## Step 2: 探索入口脚本与工作流程 (~15 min)

**Files:** `bin/submit-job`, `bin/data-sync`, `bin/install`

查看bin目录下的脚本，了解项目如何启动、数据如何同步以及环境如何安装。重点关注submit-job脚本，它可能包含作业提交的核心逻辑。

## Step 3: 分析核心模块初始化 (~20 min)

**Files:** `cellnet/__init__.py`, `cellnet/data.py`

阅读__init__.py了解模块导出和初始化逻辑；data.py包含数据加载和处理的核心函数，是理解细胞定位流程的关键。注意数据结构和预处理步骤。

## Step 4: 研究基线模型实现 (~25 min)

**Files:** `baselines/cpsam.py`

查看基线模型cpsam.py，了解Cellpose-SAM如何整合用于稀疏噪声点标注。关注模型架构、训练流程和推理方法。

## Step 5: 理解调试与辅助工具 (~10 min)

**Files:** `cellnet/debug.py`, `bin/code-tunnel`

debug.py提供调试功能，code-tunnel脚本用于代码调试连接。了解这些工具如何帮助开发和问题排查。

## Tips

- 重点关注数据流：从数据加载到模型推理的完整路径
- 注意配置参数如何影响模型行为和输出结果
- 结合README和实际代码理解项目架构
- 遇到不理解的函数时，先查看调用上下文
