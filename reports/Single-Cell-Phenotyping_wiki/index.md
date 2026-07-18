# Towards Label-Free Single-Cell Phenotyping Using Multi-Task Learning

> 无标签单细胞表型分类与蛋白表达回归

本项目是一个深度学习框架，直接从无标记微分干涉相差（DPC）显微镜图像中同时完成白细胞分类和连续蛋白表达水平回归，无需荧光染色。

## Tech Stack

- **Python** 3.10+ (language)
- **PyTorch** 2.0.0+ (framework)
- **scikit-learn** 1.3.0+ (library)

## Key Features

- 混合CNN-ViT架构融合局部纹理与全局空间依赖
- 多任务学习同时预测离散细胞类型和连续蛋白表达
- 任务自适应门控实现可控的跨任务信息交换
- LLM可解释性模块生成生物学自然语言摘要

## Getting Started

1. git clone https://github.com/saqibnaziir/Single-Cell-Phenotyping.git
2. cd Single-Cell-Phenotyping && pip install -r requirements.txt
3. 下载BSCCM数据集：pip install bsccm && python -c "from bsccm import download_dataset; download_dataset('./data', mnist=True)"
