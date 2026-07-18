# HistoBIT3D

> 基于GAN的3D组织虚拟H&E染色框架

HistoBIT3D是一个用于从相位对比背光干涉层析成像（BIT）生成虚拟3D苏木精-伊红（H&E）染色的深度学习框架。该项目实现了双向多尺度内容一致性和跨域风格复用技术，能够在不进行破坏性切片的情况下实现组织三维形态学分析。

## Tech Stack

- **Python** 3.10+ (language)
- **PyTorch** 1.12.1 (framework)
- **UVC-GAN** 2.0 (library)
- **NumPy** latest (library)
- **Pandas** 1.3.5 (library)
- **Pillow** 9.0.1 (library)

## Key Features

- 3D虚拟H&E染色生成
- 双向多尺度内容一致性保持
- AdaIN跨域风格复用
- 支持多种GAN模型架构
- 完整的训练和评估流程
- 3D体积数据重建功能
- 零样本Cellpose验证

## Getting Started

1. 克隆项目仓库到本地
2. 创建conda环境并安装依赖：conda env create -f contrib/conda_env.yaml
3. 激活环境：conda activate uvcgan2
4. 安装项目包：pip install -e .
5. 配置数据路径和训练参数
