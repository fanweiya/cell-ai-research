# Architecture

**Type:** framework

HASSL is a hierarchy-aware self-supervised learning framework built on top of DINOv3 for single cell microscopy. It uses a modular architecture with separate components for training, evaluation, data handling, and model definitions, following a typical PyTorch-based deep learning framework structure.

## Component Diagram

```mermaid
graph TD
  训练核心 --> 模型架构
  训练核心 --> 数据处理
  训练核心 --> 分布式支持
  评估模块 --> 模型架构
  评估模块 --> 数据处理
  工具函数 --> 训练核心
  工具函数 --> 评估模块
  工具函数 --> 分布式支持
```

## Components

### 训练核心

负责模型训练流程、损失计算和优化器管理

Files: `dinov3/train/train.py`, `dinov3/train/ssl_meta_arch.py`, `dinov3/loss/`

### 模型架构

定义和加载各种神经网络模型

Files: `dinov3/models/`, `dinov3/layers/`

### 数据处理

处理图像数据加载、增强和批处理

Files: `dinov3/data/`, `dinov3/configs/`

### 评估模块

提供多种评估任务如KNN、线性探测、分割和检测

Files: `dinov3/eval/`

### 分布式支持

管理多GPU分布式训练

Files: `dinov3/distributed/`, `dinov3/fsdp/`

### 工具函数

提供日志、配置、检查点等通用功能

Files: `dinov3/logging/`, `dinov3/configs/config.py`, `dinov3/checkpointer/`

## Sequence Diagram

```mermaid
sequenceDiagram
  participant 用户
  participant 配置系统
  participant 训练核心
  participant 模型架构
  participant 数据处理
  participant 分布式支持
  用户->>配置系统: 加载配置文件
  配置系统->>训练核心: 传递配置
  训练核心->>数据处理: 获取训练批次
  数据处理->>训练核心: 返回数据
  训练核心->>模型架构: 前向传播
  模型架构->>训练核心: 返回特征
  训练核心->>分布式支持: 同步梯度
  分布式支持->>训练核心: 返回同步梯度
  训练核心->>训练核心: 计算损失并更新参数
```

## Data Flow

配置系统读取YAML配置文件并转换为OmegaConf对象，训练核心根据配置初始化模型和数据加载器。训练过程中，数据处理模块加载图像批次并应用增强，模型架构执行前向传播生成特征表示。分布式支持模块在多GPU环境下同步梯度和参数，最终通过检查点模块保存训练状态。
