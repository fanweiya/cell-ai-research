# Foundation Models & Representation Learning

## 2026-07-11 | HASSL: Hierarchy-Aware Self-Supervised Learning Framework for Single Cell Microscopy | arXiv:2607.04353 | 核心方法：层级感知对比学习 + 重建损失 + 层级约束，利用图神经网络编码细胞亚结构关系 | 复现级别：B (需要数据) | priority: 9+5=14

**论文概述**：针对单细胞显微图像中细胞形态多变、尺度差异大及标注稀缺的问题，HASSL 提出层级感知自监督学习框架。相比传统监督方法依赖大量标注数据，该框架利用无标签数据学习细胞层级结构特征，提升模型在少样本场景下的泛化能力。

**算法要点**：
- 损失函数：`L_total = λ1 * L контраст и ve + λ2 * L_reconstruction + λ3 * L_hierarchy`
- 对比学习拉近同类细胞特征距离、推开异类距离
- 重建损失保证特征可逆性
- 层级约束损失显式建模细胞亚结构（核、质）的层级关系，通过图神经网络编码层级拓扑

**代码分析**：
- 框架：PyTorch
- 项目结构：配置文件、文档、测试数据、核心逻辑
- 问题：目录列表缺少核心源代码文件，无法进行详细的模块级代码分析

**复现评估**：
- GPU 要求：24GB VRAM, 1x A100/RTX4090
- 数据公开：是 (manifest_train_fixed.csv.gz, manifest_test_fixed.csv.gz)
- 依赖：PyTorch, CUDA 11.8
- 步骤：1. 配置环境 2. 下载数据 3. 运行 src/train.py

---

## 2026-07-11 | SpaCellAgent: A Self-Evolving LLM-Based Multi-Agent Framework for Trajectory Analysis | arXiv:2607.07467 | 核心方法：多智能体强化学习 + 轨迹优化 + 自我进化机制 | 复现级别：B (需要数据) | priority: 9+5=14

**论文概述**：针对传统轨迹推断方法在空间转录组数据中难以捕捉复杂细胞状态演化路径的问题，SpaCellAgent 采用自进化大语言模型多智能体框架，通过多智能体协作与自我进化机制，动态调整分析策略，适应不同数据集的异质性。

**算法要点**：
- 损失函数：`L_total = λ1 * L_trajectory + λ2 * L_agent_collaboration + λ3 * L_evolution`
- 核心数学原理基于多智能体强化学习与轨迹优化
- 多目标加权求和优化

**代码分析**：
- 框架：PyTorch, Python API
- 项目结构：api.py, main.py, Docker 配置
- 架构：input→api_handler→feature_extractor→model_inference→output_formatter→response

**复现评估**：
- GPU 要求：24GB VRAM, 1x A100/RTX4090
- 数据公开：需要公开数据集
- 依赖：PyTorch, CUDA 11.8
- 性能：轨迹准确率 0.92, 比 Monocle3 快 3.5 倍

---
## 2026-07-12 | ZipDepth: Bringing Lightweight Zero-Shot Monocular Depth Anywhere, on Any Device | arXiv:2607.08771 | 核心方法：多任务学习（深度+边缘）+ 轻量级架构 | 复现级别：B (需要数据) | priority: 16

**论文概述**：ZipDepth 是一个轻量级的零样本单目深度估计模型，可以在任何设备上运行。它无需在目标域上训练即可实现跨场景的零样本泛化。

**算法要点**：
- 损失函数：`L = λ1*L_depth + λ2*L_edge + λ3*L_{...}`
- 多任务学习联合优化深度和边缘
- 采用轻量级网络设计，适合边缘设备部署

**代码分析**：
- 框架：PyTorch
- GitHub repo: fabiotosi92/ZipDepth (64 stars)
- 架构紧凑，易于集成

**复现评估**：
- GPU 要求：1x GPU (8GB VRAM)
- 数据公开：需要申请或自有数据集
- 依赖：PyTorch, CUDA
- 步骤：1. git clone 2. 安装依赖 3. 运行 inference

---
