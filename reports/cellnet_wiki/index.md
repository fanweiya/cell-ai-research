# CellNet

> 使用稀疏噪声点标注定位相差显微镜图像中的细胞

CellNet 是一个用于在相差显微镜图像中定位细胞的深度学习项目。它基于稀疏且带有噪声的中心点标注进行训练，旨在解决标注数据稀缺和噪声问题。项目由 Wellcome Sanger Institute、哥廷根大学计算细胞分析组和塔图大学生物医学计算机视觉实验室合作开发。

## Tech Stack

- **Python** 3.12.0 (language)
- **PyTorch** 2.6.0 (framework)
- **segmentation-models-pytorch** 0.5.0+ (library)
- **NumPy** <2.0 (library)
- **Pillow** 12.2.0+ (library)
- **Matplotlib** 3.10.8+ (library)

## Key Features

- 支持命令行和 Python 模块两种使用方式
- 自动下载和缓存最新模型版本
- 提供训练、评估和发布工作流
- 支持远程集群作业提交（Slurm/LSF）
- 兼容 Label Studio 标注格式
- 包含基线模型 cpsam.py

## Getting Started

1. 克隆仓库并切换到 draft 分支（可选）
2. 使用 micromamba 或 conda 创建环境：micromamba create -yf cellnet.yml
3. 激活环境并运行 bin/install 进行可编辑安装
4. 将图像放入 data/images，标注放入 data/annotations
5. 运行 bin/normalize_paths 规范化路径，然后运行 preprocess_annotations.py 转换标注格式
