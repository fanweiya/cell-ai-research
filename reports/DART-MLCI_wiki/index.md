# DART-MLCI

> 将微流控芯片蓝图与显微镜图像对齐，实现实时细胞分析。

DART-MLCI 处理来自微流控芯片的显微图像帧，自动检测对齐标记、校正旋转、裁剪感兴趣区域并分割细胞。该系统处理两种对齐任务：用于掩膜单个腔室的精细对齐，以及用于将整个芯片蓝图映射到物理台坐标的粗对齐。

该系统使用 YOLO 模型检测芯片上的十字和圆形标记，然后将其与 JSON 配置中的预期位置进行匹配。它旋转图像以对齐芯片，应用多边形掩膜以隔离腔室，并可选择使用 Cellpose-SAM 或 Omnipose 进行细胞分割。所有芯片设计均由单个 JSON 配置文件描述。

该系统可作为 Python 库、FastAPI 服务运行，或通过命令行脚本进行延时实验的批量处理。该流程支持 GPU 加速，并包含用于校准、基准测试和生成可视化报告的工具。

## 技术栈

- **Python** 3.10+（编程语言）
- **PyTorch** 2.5.1+cu121（深度学习）
- **Ultralytics YOLO** 最新版（目标检测）
- **FastAPI** 0.109.0+（API）
- **OpenCV** 最新版（图像处理）
- **Cellpose-SAM** 最新版（分割）

## 核心功能

- 芯片对齐的标记检测与匹配
- 自动图像旋转和 ROI 裁剪
- 特定腔室的多边形掩膜
- 使用 Cellpose-SAM 或 Omnipose 进行细胞分割
- 蓝图到台坐标的校准
- 用于实时处理的 FastAPI 服务
- 用于延时序列的批量处理脚本
- 支持 GPU 自动检测的 Docker 容器

## 快速开始

1. 克隆仓库并安装依赖：`pip install '.[dev,api,segmentation}'`
2. 通过 Docker 运行应用：`docker-compose up --build`
3. 或从 PyPI 安装：`pip install dart-mlci`