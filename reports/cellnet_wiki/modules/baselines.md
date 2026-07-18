# baselines

> 实现Cellpose-SAM基线模型，用于在相差显微镜图像中通过稀疏噪声点标注定位细胞。

该模块加载预训练的Cellpose模型，对相差显微镜图像进行细胞分割，并将分割结果转换为细胞中心点，最后与真实标注的稀疏点进行比较以评估性能。流程包括：图像读取与预处理、模型推理、可视化分割结果、将掩码转换为中心点、计算sMAPE、MAE、精确率、召回率和F1分数。

## Files

### `baselines/cpsam.py`

执行Cellpose-SAM基线流程：加载图像、运行模型推理、可视化分割掩码和预测点、计算评估指标。

- `models.CellposeModel` (class) - Cellpose预训练模型类，用于加载模型权重并执行细胞分割推理。
- `model.eval` (function) - 执行模型推理，返回预测的掩码(masks_pred)、流场(flows)和风格向量(styles)。
- `io.imread` (function) - 从文件读取图像数据。
- `plotting.image` (function) - 在matplotlib轴上显示图像。
- `plotting.points` (function) - 在轴上绘制预测的细胞中心点。
- `utils.outlines_list` (function) - 从流场数据中提取细胞轮廓的坐标列表。
- `masks2centers` (function) - 将细胞分割掩码转换为细胞中心点坐标。
- `sMAPE_MAE` (function) - 计算预测中心点与真实标注点之间的对称平均百分比误差(sMAPE)和平均绝对误差(MAE)。
- `prec_rec_f1` (function) - 基于距离阈值计算精确率(Precision)、召回率(Recall)和F1分数。

## Key Concepts

- **Cellpose-SAM基线**: 使用Cellpose模型进行细胞分割，并将分割结果转换为点标注，作为后续稀疏点定位算法的对比基线。
- **掩码转中心点**: 将细胞分割得到的像素级掩码转换为单个坐标点，以便与稀疏点标注进行直接比较。
- **点标注评估指标**: 使用sMAPE、MAE、精确率、召回率和F1分数来量化预测细胞中心点与真实标注点之间的匹配程度。

## Internal Relationships

- `baselines/cpsam.py` → `cellpose.models`: 导入Cellpose模型类以加载和运行预训练模型。
- `baselines/cpsam.py` → `cellpose.io`: 导入图像读取工具函数。
- `baselines/cpsam.py` → `cellpose.utils`: 导入提取细胞轮廓的工具函数。
- `baselines/cpsam.py` → `cellnet.plot`: 导入自定义绘图模块用于可视化分割结果和预测点。
- `baselines/cpsam.py` → `cellnet.data`: 导入masks2centers函数，将分割掩码转换为细胞中心点。
- `baselines/cpsam.py` → `cellnet.evaluate`: 导入评估函数sMAPE_MAE和prec_rec_f1，用于量化预测性能。
