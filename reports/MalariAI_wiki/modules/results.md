# results

> 存储和记录疟疾血涂片细胞分割与分期分类系统的评估指标和性能统计。

该模块包含JSON格式的结果文件，用于量化评估不同实验配置下模型在BBBC041数据集上的表现。主要指标包括各类别平均精度(AP)、mAP@0.5、二分类寄生AP、分割阶段(stage1)的TP/FP/FN、召回率、精确率和F1分数，以及运行时间统计。文件按实验版本组织，便于对比不同迭代版本的性能差异。

## Files

### `results/v2/e2e_bbbc041/metrics.json`

记录v2端到端模型在BBBC041数据集上的完整评估指标，包括分割和分类性能。

### `results/v2/e2e_bbbc041/stage1_stats.json`

单独存储v2模型分割阶段(stage1)的详细统计信息，作为metrics.json的子集。

### `results/v2/e2e_bbbc041_v2/metrics.json`

记录v2改进版本端到端模型在BBBC041数据集上的评估指标，用于与前一版本对比。

## Key Concepts

- **iou_threshold**: 交并比阈值，用于判定预测框与真实框是否匹配的标准，此处固定为0.5。
- **AP (Average Precision)**: 平均精度，衡量分类器在不同召回率水平下的精确度，值越高表示分类性能越好。
- **mAP_at_iou50**: 在IoU阈值为0.5时的平均精度均值，综合评估模型在所有类别上的检测性能。
- **stage1**: 分割阶段，负责将图像中的细胞实例分割为独立区域，其性能直接影响后续分类准确性。
- **TP/FP/FN**: 真阳性、假阳性和假阴性，用于计算召回率、精确率和F1分数的基础统计量。

## Internal Relationships

- `results/v2/e2e_bbbc041/stage1_stats.json` → `results/v2/e2e_bbbc041/metrics.json`: stage1_stats.json是metrics.json中stage1部分的独立副本，便于单独分析分割阶段性能。
