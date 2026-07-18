# VitaminP

> 基于Vision Transformer的病理细胞分割框架

VitaminP是一个用于全切片图像(WSI)中细胞和细胞核分割的深度学习框架。它利用Vision Transformer架构，从配对的H&E和MIF训练数据中学习细胞质边界，使得仅使用常规H&E切片即可实现全细胞分割，无需在推理时使用免疫荧光数据。

## Tech Stack

- **Python** 3.8+ (language)
- **PyTorch** 2.0+ (framework)
- **OpenCV** 4.8+ (library)
- **OpenSlide** 1.2+ (library)
- **Zarr** 2.16+ (library)

## Key Features

- 支持H&E和MIF双模态输入
- 提供flex、dual、syn三种模型架构
- 支持全切片图像批量推理
- 输出QuPath兼容的GeoJSON格式
- 包含14个公开数据集的预处理脚本
- 支持GAN合成MIF图像
- 集成Weights & Biases实验追踪

## Getting Started

1. 安装依赖：pip install vitaminp 或 pip install -r requirements.txt
2. 使用Docker：docker pull ghcr.io/idso-fa1-pathology/vitaminp:latest
3. 加载预训练模型：model = vitaminp.load_model('flex', device='cuda')
