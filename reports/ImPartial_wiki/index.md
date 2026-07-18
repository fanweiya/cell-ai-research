# ImPartial

> 基于部分标注的交互式实例分割深度学习框架

ImPartial 是一个用于病理图像细胞分割的深度学习框架，通过稀疏涂鸦和有限监督实现高精度分割。它利用自监督多通道量化插补增强分割目标，在仅需少量标注的情况下达到与全监督模型相当的性能。

## Tech Stack

- **Python** 3.8+ (language)
- **PyTorch** 1.x (framework)
- **MONAI Label** 0.8.0 (framework)
- **Java** 1.8 (language)
- **ImageJ/Fiji** 2.3.0+ (platform)

## Key Features

- 支持稀疏涂鸦标注的交互式分割
- 自监督多通道量化插补
- ImageJ/Fiji 插件界面
- MONAI Label API 集成
- 多用户会话管理
- 不确定性感知的主动学习
- 模型训练与推理一体化

## Getting Started

1. 克隆项目仓库
2. 安装依赖：pip install -r requirements.txt
3. 构建 ImageJ 插件：cd imagej-plugin && mvn clean package
4. 将生成的 jar 文件复制到 Fiji 插件目录
5. 启动 MONAI Label 服务器：monailabel start_server -a pathology -s <dataset_path>
