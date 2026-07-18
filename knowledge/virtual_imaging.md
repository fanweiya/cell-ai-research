# Virtual Imaging and Computational Microscopy

## 2026-07-12 | ZipDepth: Bringing Lightweight Zero-Shot Monocular Depth Anywhere, on Any Device | arXiv:2607.08771 | 核心方法：轻量级零样本单目深度估计 | 复现级别：B (需要数据) | priority: 16

**论文概述**：ZipDepth 是一个轻量级的零样本单目深度估计模型，可以在任何设备上运行。无需在目标域上训练即可实现跨场景的零样本泛化，适用于计算显微镜中的虚拟成像应用。

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