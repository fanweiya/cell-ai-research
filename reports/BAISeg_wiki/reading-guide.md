# Reading Guide

本指南旨在帮助你快速理解基于符号距离函数（SDF）和边界感知损失的显微镜细胞实例分割框架。建议按从配置到核心逻辑再到工具函数的顺序阅读，重点关注数据流、模型架构和训练循环。

## Step 1: 理解项目概览与依赖 (~5 min)

**Files:** `README.md`, `requirements.txt`

首先阅读README.md了解项目目标、核心功能（SDF预测、边界感知损失）和运行方式。接着查看requirements.txt确认Python版本和关键依赖库（如PyTorch、OpenCV等），确保环境理解。

## Step 2: 掌握数据加载与预处理 (~15 min)

**Files:** `dataset.py`

重点查看数据集类如何加载显微镜图像、生成符号距离函数（SDF）标签以及应用数据增强。理解输入输出格式对后续模型设计至关重要。

## Step 3: 学习模型基础组件 (~10 min)

**Files:** `models/base_model.py`, `models/blocks.py`

base_model.py定义模型基类，了解通用接口；blocks.py包含构建网络的基本模块（如卷积块、上采样块）。关注这些组件如何组合成完整网络。

## Step 4: 深入UNet架构实现 (~20 min)

**Files:** `models/unet.py`

这是核心模型文件。重点查看UNet的编码器-解码器结构、跳跃连接、SDF预测头以及边界感知损失的具体实现。注意其与普通UNet的区别。

## Step 5: 理解训练流程与配置 (~15 min)

**Files:** `train_unet.py`, `unet2d.yml`

train_unet.py是训练入口，查看数据加载、模型初始化、损失计算、优化器设置和训练循环。unet2d.yml提供超参数配置，理解各参数对训练的影响。

## Step 6: 掌握工具函数与辅助功能 (~10 min)

**Files:** `utils.py`

utils.py包含数据后处理、可视化、指标计算等实用函数。特别关注如何将SDF预测转换为最终分割掩码，以及边界检测的实现。

## Step 7: 探索代码图管理（可选） (~3 min)

**Files:** `.codegraph/.gitignore`

了解.codegraph目录用于管理代码图数据，虽然.gitignore内容较少，但需知晓其存在及用途，避免误操作缓存文件。

## Tips

- 阅读时先关注数据流向：图像输入 -> SDF生成 -> 模型预测 -> 后处理输出分割结果
- 对比标准UNet实现，重点关注本代码中针对SDF预测和边界感知的特殊修改
- 遇到复杂函数时，先查看调用位置再深入函数内部，建立上下文联系
