# DriftST

> 从H&E组织切片推断空间转录组的一站式生成框架

DriftST 是一个基于生成式模型的工具，它从局部H&E组织切片图像中提取特征，预测空间基因表达。该框架使用漂移目标（drifting objective）将随机预测分布与匹配的转录组图谱对齐，支持细胞级（Xenium）和斑点级（Visium）数据。

## Tech Stack

- **Python** 3.10.20 (language)
- **PyTorch** 2.5.1 (framework)
- **Scanpy** 1.11.5 (library)
- **Squidpy** 1.6.5 (library)

## Key Features

- 支持 Xenium 细胞级和 Visium 斑点级数据
- 使用 UNI2 和 CONCH 病理基础模型特征
- 采用 STransformer 模块预测空间基因表达
- 实现一步漂移目标对齐预测分布
- 支持 ZINB 重建和基因方差校准

## Getting Started

1. 创建 Conda 环境：conda env create -f environment.yml
2. 激活环境：conda activate DriftST
3. 下载 UNI2 和 CONCH 权重文件到 weights/ 目录
4. 运行预处理脚本生成 processed_data 数据
