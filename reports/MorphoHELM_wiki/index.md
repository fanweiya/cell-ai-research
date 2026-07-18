# MorphoHELM Cell Painting benchmark pipeline

> 细胞形态学基准测试与特征提取流水线

该项目实现了从原始图像下载到生成标准化嵌入的完整流水线。流程包括数据下载、光照校正、转换为HuggingFace格式、模型推理、特征聚合、标准化、质量控制及基准测试。

## Tech Stack

- **Python** 3.10+ (language)
- **PyTorch** N/A (framework)
- **HuggingFace Datasets** 2.14+ (library)
- **OpenCV** N/A (library)

## Key Features

- 支持CPG0016和BBBC036数据集的光照校正与下载
- 集成多种预训练模型（DINOv2, ResNet, OpenPhenom等）进行特征提取
- 自动化生成标准化嵌入与基准测试报告
- 包含完整的质量控制与重复性分析模块

## Getting Started

1. 安装依赖：pip install -r requirements.txt
2. 运行数据下载：python data_installation/download_illum_corrected.py --dataset cpg0016 --cpg-output-root <路径>
3. 执行推理：python feature-extraction/src/run_inference.py --config configs/inference_config.yaml
