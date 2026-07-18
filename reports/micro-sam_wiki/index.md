# micro-sam

> 使用 Segment Anything 进行显微镜图像交互式与自动分割及追踪的工具。

micro-sam 提供了用于在显微镜图像中分割和追踪对象的 napari 插件和 Python 库。它支持交互式 2D 和 3D 分割，以及 2D 时间序列数据的追踪。该项目包含针对各种显微镜模态的预训练模型，以及用于在自定义数据集上微调模型的脚本。

该仓库包含用于运行标注工具、自动分割和追踪的示例脚本。此外，它还提供了详尽的文档、用于模型基准测试的评估代码以及用于研讨会的资源。核心功能基于 Segment Anything 模型构建，并针对显微镜数据进行了专门微调，具备实例分割能力。

## 技术栈

- **Python** 3.10+（编程语言）
- **PyTorch** 2.5+（框架）
- **napari** 0.7+（图形用户界面）
- **segment-anything** 最新版（库）
- **trackastra** 0.5.3+（库）

## 主要功能

- 通过 napari 插件实现交互式 2D 分割
- 针对体积数据的交互式 3D 分割
- 交互式追踪 2D 时间序列图像
- 使用微调后的解码器进行自动实例分割
- 用于自定义显微镜数据集的微调脚本
- 针对光学显微镜、电子显微镜和组织病理学的预训练模型
- 用于模型性能评估与基准测试的工具
- 用于程序化使用的 Python 库 API

## 快速开始

1. 创建 conda 环境：`conda create -c conda-forge -n micro_sam python=3.11 natsort`
2. 激活环境：`conda activate micro_sam`
3. 安装软件包：`conda install -c conda-forge "micro_sam>=1.1" "pytorch>=2.4"`
4. 使用研讨会或示例文件夹中提供的脚本下载模型和数据