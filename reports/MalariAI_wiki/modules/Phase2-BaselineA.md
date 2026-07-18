# Phase2-BaselineA

> 实现基于Faster R-CNN的疟疾血涂片细胞分割与分期分类基线模型训练与评估

该模块旨在通过Faster R-CNN (ResNet-50 FPN backbone) 对疟疾血涂片图像进行目标检测，识别红细胞、疟原虫不同发育阶段（滋养体、环状体、裂殖体、配子体）及白细胞。支持Kaggle Notebook交互式训练与命令行脚本训练两种模式，采用两阶段训练策略（共80个epoch），并输出mAP等评估指标。

## Files

### `Phase2-BaselineA/Phase2_FasterRCNN_Kaggle.ipynb`

Kaggle Notebook主脚本，提供交互式训练环境，包含数据路径确认、依赖检查、模型构建、训练循环及可视化功能。

- `DATASET_ROOT` (variable) - 定义数据集根目录路径，需根据Kaggle输入调整
- `LABEL_TO_INT` (dictionary) - 标签字符串到整数索引的映射，包含背景及6种细胞类型
- `build_model` (function) - 构建Faster R-CNN模型，加载COCO预训练权重并调整分类头以适配7类目标
- `train_one_epoch` (function) - 执行单个epoch的训练循环，计算并打印损失
- `compute_map` (function) - 使用torchmetrics计算验证集的平均精度均值(mAP)

### `Phase2-BaselineA/train_frcnn.py`

命令行训练脚本，封装Notebook中的核心逻辑，便于在Kaggle或云GPU上无头运行。

- `build_model` (function) - 与Notebook中功能一致，构建并返回Faster R-CNN模型实例
- `train_one_epoch` (function) - 训练单轮 epoch，包含梯度裁剪和损失汇总
- `validate_loss` (function) - 在验证集上计算模型损失
- `compute_map` (function) - 计算mAP指标，过滤低置信度预测
- `main` (function) - 解析命令行参数，初始化数据集、模型、优化器，并启动训练循环

### `Phase2-BaselineA/checkpoints-kaggle-80epoch/metrics.json`

存储Kaggle 80轮完整训练后的最终评估指标。

- `map_50` (metric) - IoU阈值为0.5时的平均精度均值，值为0.5899
- `per_class_ap` (dictionary) - 各类别的平均精度(AP)，显示红细胞(RBC)和滋养体(Troph)表现较好，裂殖体(Schiz)较差

### `Phase2-BaselineA/checkpoints-local-20epoch/metrics.json`

存储本地20轮训练后的中间评估指标。

- `map_50` (metric) - 20轮训练后的mAP@0.5，值为0.5846
- `per_class_ap` (dictionary) - 20轮训练后各类别的AP值

## Key Concepts

- **Faster R-CNN ResNet-50 FPN**: 
- **两阶段训练策略**: 
- **torchmetrics MeanAveragePrecision**: 
- **数据增强与预处理**: 

## Internal Relationships

- `Phase2-BaselineA/Phase2_FasterRCNN_Kaggle.ipynb` → `Phase2-BaselineA/train_frcnn.py`: Notebook中的核心训练逻辑被重构并提取到train_frcnn.py中，两者共享相同的模型构建和训练函数实现
- `Phase2-BaselineA/train_frcnn.py` → `Phase1-EDA/dataset.py`: train_frcnn.py导入Phase1-EDA中的MalariaDataset和detection_collate函数，复用数据加载逻辑
- `Phase2-BaselineA/train_frcnn.py` → `Phase1-EDA/shared/label_map.py`: 导入共享的标签映射配置(NUM_CLASSES, INT_TO_LABEL等)，确保类别定义一致
- `Phase2-BaselineA/train_frcnn.py` → `Phase2-BaselineA/checkpoints-kaggle-80epoch/metrics.json`: 训练脚本运行结束后，将评估结果（如mAP）保存为JSON文件
