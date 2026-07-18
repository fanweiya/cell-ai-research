# notebooks

> 提供四个示例Jupyter笔记本，展示如何使用micro_sam库进行交互式分割、自动分割、推理评估及SAM微调。

该模块包含四个独立的Jupyter笔记本，分别演示micro_sam库的核心功能：快速入门、高级自动分割、批量推理与评估、以及针对自定义数据的模型微调。这些笔记本是用户快速上手和深入理解库功能的主要入口，依赖micro_sam库本身，并可在本地或Kaggle环境中直接运行。

## Files

### `quick_start.ipynb`

展示如何以最小配置实现自动实例分割。

- `quick_start` (notebook) - 演示使用默认参数快速运行SAM进行分割的完整流程。

### `automatic_segmentation.ipynb`

展示如何配置更多选项以实现自动实例分割。

- `automatic_segmentation` (notebook) - 演示如何调整分割器参数、提示点生成策略等高级选项。

### `inference_and_evaluation.ipynb`

展示如何对大量图像应用SAM并评估分割质量。

- `inference_and_evaluation` (notebook) - 演示批量推理脚本及与真值（ground-truth）对比的评估指标计算。

### `sam_finetuning.ipynb`

展示如何在自定义数据上微调SAM模型。

- `sam_finetuning` (notebook) - 演示数据准备、训练循环及模型保存的完整微调流程。

## Key Concepts

- **Segment Anything Model (SAM)**: 由Meta AI开发的基础视觉模型，能够根据提示（如点、框）生成高质量分割掩码。
- **micro_sam**: 封装SAM的Python库，提供针对显微镜图像优化的分割和跟踪工具。
- **实例分割**: 将图像中的每个目标实例分割成独立的掩码，区分不同物体。
- **微调**: 在特定领域数据上继续训练预训练模型，以提高其在特定任务上的性能。

## Internal Relationships

- `quick_start.ipynb` → `automatic_segmentation.ipynb`: quick_start是automatic_segmentation的简化版本，后者包含前者未涉及的高级配置。
- `inference_and_evaluation.ipynb` → `automatic_segmentation.ipynb`: inference_and_evaluation基于automatic_segmentation中的分割逻辑，增加了批量处理和评估功能。
- `sam_finetuning.ipynb` → `micro_sam`: sam_finetuning调用micro_sam库中的训练和微调API来优化模型。
