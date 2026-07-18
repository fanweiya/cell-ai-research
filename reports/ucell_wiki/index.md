# UCell

> 通用细胞分割模型，支持微调与推理

UCell 是一个基于 PyTorch 的细胞分割模型，采用 FRM 架构，支持 LoRA 微调。项目包含训练、预测、评估及死神经元分析工具。

## Tech Stack

- **Python** 3.11+ (language)
- **PyTorch** 2.x (framework)
- **Lightning** 2.x (framework)
- **ml_collections** 0.1.x (library)

## Key Features

- 支持 LoRA 微调
- 死神经元检测与分析
- Docker 容器化部署
- GRPC 接口服务
- 多任务学习支持

## Getting Started

1. 克隆仓库并安装依赖：pip install -e .[train]
2. 准备数据集，将 *.tif 和 *_label.tif 放入指定目录
3. 运行训练脚本：python train.py --init ${BASE_MODEL} --config config.py:train --config.data_dir=${DATADIR}
