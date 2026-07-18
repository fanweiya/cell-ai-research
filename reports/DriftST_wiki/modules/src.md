# src

> 实现从H&E组织切片推断空间转录组的核心数据加载、模型架构、漂移训练机制、评估及后处理流程。

该模块包含构建DriftST框架所需的所有核心组件。dataset.py 负责处理预处理的图像和基因表达数据，支持数据增强和邻居查询；model.py 定义了基于FiLM和自注意力机制的神经网络，用于将图像嵌入映射为基因表达；drift_step.py 实现了多尺度漂移步长算法和预测银行，用于生成目标分布和负采样；evaluation.py 提供基于PCC和log2空间误差的评估指标；postprocess.py 执行基因级别的方差校准以修正预测压缩问题。

## Files

### `dataset.py`

提供空间转录组数据集的加载与采样逻辑，支持图像特征增强和邻居索引。

- `SpatialDataset` (class) - 继承自torch.utils.data.Dataset，封装基因表达矩阵、图像特征及邻居关系。支持训练时随机选择图像增强版本，推理时使用原始特征。
- `_parse_slide_ids` (function) - 静态方法，从条形码解析滑片ID，优先使用summary.json，否则按分隔符分割。

### `drift_step.py`

实现DriftST的核心漂移更新算法及负采样缓冲区。

- `multi_scale_drift_step` (function) - 计算漂移目标。使用分离的softmax处理正负样本，通过多半径（R_list）聚合速度向量，返回目标分布及其缩放因子。
- `drift_loss_fn` (function) - 计算漂移损失，即当前预测与目标在缩放空间下的MSE。
- `PredictionBank` (class) - 环形缓冲区，存储随机预测作为负样本池，支持动态入队以扩大负采样范围。

### `evaluation.py`

计算模型预测与真实值的评估指标，包括基因级PCC、SVG PCC及log2空间误差。

- `metrics_from_arrays` (function) - 基于numpy数组计算全套指标，包括PCC-10/50/200、SVG PCC、MSE/MAE (log2)。
- `evaluate` (function) - 在给定模型和数据加载器上运行推理，收集预测与真实值，并调用metrics_from_arrays输出结果。

### `model.py`

定义DriftST神经网络的层与模块，实现图像到基因表达的映射。

- `NeighborAggregator` (class) - 基于注意力的邻居聚合模块，将中心点与K个邻居的特征融合。
- `AdaLN` (class) - 条件自适应层归一化，根据spot级图像表示调整特征分布。
- `GeneGate` (class) - 上下文感知门控，控制每个基因token的残差更新，可初始化生物先验偏差。
- `BioGuidedAttentionBlock` (class) - 基因维度的Transformer块，利用共表达矩阵作为注意力偏置，结合门控机制。

### `postprocess.py`

对模型预测进行基因级别的仿射方差校准，以恢复预测的分布范围。

- `variance_postprocess` (function) - 应用仿射变换：pred' = ref_mean + (pred - pred_mean) * (ref_std / pred_std) * alpha。不改变单调性，保留PCC。

## Key Concepts

- **分离式漂移步长**: 
- **多尺度半径聚合**: 
- **生物引导注意力**: 
- **方差后校准**: 

## Internal Relationships

- `evaluation.py` → `dataset.py`: evaluation.py 使用 dataset.py 中定义的 DataLoader 进行推理循环。
- `model.py` → `drift_step.py`: 模型训练过程中，model.py 调用 drift_step.py 中的 multi_scale_drift_step 生成漂移目标。
- `evaluation.py` → `postprocess.py`: 评估流程中，evaluation.py 可调用 postprocess.py 对预测结果进行方差校准后再计算指标。
- `dataset.py` → `model.py`: dataset.py 加载的图像特征和基因表达数据直接作为 model.py 的输入张量。
