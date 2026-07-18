# WBCAtt+ Dataset

> 白细胞图像细粒度像素级形态标注与分割

该项目提供白细胞图像数据集及标注，包含像素级分割掩码和细胞属性注释。基于Mask2Former实现语义分割模型训练，支持多种骨干网络。

## Tech Stack

- **Python** 3.9.18 (language)
- **PyTorch** 2.2.2 (framework)
- **MMSegmentation** 1.2.1 (library)
- **Detectron2** latest (library)
- **CUDA** 12.1 (platform)

## Key Features

- 白细胞细粒度像素级分割标注
- 11种细胞属性注释
- 支持Mask2Former语义分割训练
- 多种骨干网络实现
- 属性预测基线模型

## Getting Started

1. 创建conda环境：conda create --name wbcattplus python=3.9.19
2. 激活环境并安装依赖：pip install -r requirements.txt
3. 下载数据集：wget pbcseg_final_v1.tar 放入 data/PBC
4. 安装MMCV：mim install mmcv==2.1.0
5. 安装MMSegmentation：pip install mmsegmentation==1.2.2
