# Count Anything

> 文本引导跨域目标计数模型

Count Anything 是一个通用模型，通过文本提示在跨域场景中执行目标计数。它接收图像和自然语言查询，返回实例化的点集，点的数量即为计数结果。该模型统一了类别条件计数与可解释的空间定位。

## Tech Stack

- **Python** 3.10+ (language)
- **PyTorch** 2.0+ (framework)
- **Transformers** timm>=1.0.17 (library)

## Key Features

- 跨域文本引导计数
- 双粒度实例枚举（RSC + PDC）
- 点中心监督与互补融合
- 支持六种视觉领域
- CLOC 数据集（220K 图像，619 类别）

## Getting Started

1. 克隆仓库并进入项目目录
2. 安装依赖：pip install -r requirements.txt
3. 下载 CLOC 数据集：cloc_annotations.zip 和 cloc_augmented.zip 放入 data/ 目录
4. 解压数据集：unzip -q cloc_annotations_v1.1.zip 和 unzip -q cloc_augmented.zip
5. 运行训练脚本：bash train.sh
6. 运行验证脚本：bash val.sh
7. 运行推理脚本：bash test.sh
