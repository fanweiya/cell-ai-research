# metrics

> 提供病理细胞分割任务的二值分割和实例分割评估指标计算及工具函数

该模块专注于评估基于Vision Transformer的病理细胞分割框架的性能。它包含两类核心指标：针对像素级二值掩码的分割指标（如Dice、IoU）和针对实例级分割的指标（如PQ、AJI）。模块通过优化算法（如匈牙利算法）高效计算实例匹配，并提供批量处理、结果聚合和打印等实用工具，支持HE和MIF两种染色图像中细胞核与细胞的全方位评估。

## Files

### `metrics/__init__.py`

模块入口，导出所有公共接口，包括二值分割指标、实例分割指标和工具函数

- `dice_coefficient` (function) - 计算二值分割的Dice系数
- `panoptic_quality` (function) - 计算实例分割的Panoptic Quality (PQ)
- `compute_all_metrics` (function) - 计算单个样本的所有指标并返回字典

### `metrics/segmentation.py`

实现像素级二值分割评估指标，用于评估细胞核或细胞的二值掩码预测

- `dice_coefficient` (function) - 计算预测与真实掩码的Dice相似系数
- `iou_score` (function) - 计算预测与真实掩码的交并比(IoU)
- `precision_score` (function) - 计算精确率
- `recall_score` (function) - 计算召回率
- `f1_score` (function) - 计算F1分数
- `pixel_accuracy` (function) - 计算像素准确率
- `batch_dice_coefficient` (function) - 对批次中的每个样本单独计算Dice系数

### `metrics/instance.py`

实现实例分割评估指标，核心是计算PQ、AJI等指标，处理实例ID匹配问题

- `remap_label` (function) - 将实例ID重映射为连续整数，优化后续计算性能
- `get_fast_pq` (function) - 快速计算Panoptic Quality (PQ)、Detection Quality (DQ)和Segmentation Quality (SQ)
- `panoptic_quality` (function) - 计算完整的PQ指标
- `aggregated_jaccard_index` (function) - 计算聚合Jaccard指数(AJI)
- `aggregated_jaccard_index_plus` (function) - 计算改进的聚合Jaccard指数(AJI+)
- `get_fast_aji` (function) - 快速计算AJI

### `metrics/utils.py`

提供指标计算的辅助函数，包括批量处理、多任务指标聚合和结果格式化输出

- `compute_all_metrics` (function) - 对单个样本计算所有二值和实例指标
- `compute_batch_metrics` (function) - 遍历批次中的每个样本，计算四个任务（HE/MIF的核/细胞）的指标并求平均
- `aggregate_metrics` (function) - 聚合多个样本的指标统计信息
- `print_metrics` (function) - 格式化打印指标结果
- `compute_overall_metrics` (function) - 计算整体平均指标

## Key Concepts

- **Panoptic Quality (PQ)**: 实例分割的核心指标，结合了检测质量(DQ)和分割质量(SQ)，公式为PQ = TP * SQ / (TP + 0.5*FP + 0.5*FN)
- **实例ID重映射**: 通过remap_label函数将非连续的实例ID转换为连续整数，提高匈牙利算法匹配的效率
- **匈牙利算法匹配**: 使用scipy.optimize.linear_sum_assignment基于IoU矩阵进行最优实例匹配，确定真阳性(TP)
- **批量指标计算**: 支持对包含多个样本的批次进行循环计算，并自动对HE和MIF两种染色下的细胞核和细胞四个任务分别统计

## Internal Relationships

- `metrics/__init__.py` → `metrics/segmentation.py`: __init__.py从segmentation.py导入二值分割指标函数
- `metrics/__init__.py` → `metrics/instance.py`: __init__.py从instance.py导入实例分割指标函数
- `metrics/__init__.py` → `metrics/utils.py`: __init__.py从utils.py导入工具函数
- `metrics/utils.py` → `metrics/segmentation.py`: utils.py在compute_all_metrics和compute_batch_metrics中调用segmentation.py的指标函数
- `metrics/utils.py` → `metrics/instance.py`: utils.py在compute_all_metrics和compute_batch_metrics中调用instance.py的指标函数
