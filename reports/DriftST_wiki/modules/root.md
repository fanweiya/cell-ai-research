# root

> DriftST 项目的根模块，提供从 H&E 组织切片推断空间转录组的一站式生成框架，包含训练、测试、数据预处理及实验脚本。

该模块实现了 DriftST 框架，通过提取病理基础模型特征、使用 STransformer 模块预测空间基因表达，并采用漂移目标（drifting objective）训练预测器。支持细胞级 Xenium 数据和斑点级 Visium 数据集。核心流程包括：预处理原始数据生成统一格式、训练模型（结合 ZINB 重建损失与一步漂移损失）、评估模型性能并导出预测结果。

## Files

### `train.py`

训练入口点，执行 DriftST 模型的训练流程。

- `capture_stochastic` (function) - 收集每个空间点的 K 个随机 Dropout 预测样本，用于分布可视化。
- `warmup_bank` (function) - 使用 K 次 Dropout 前向传播填充预测银行（PredictionBank），为漂移步骤准备负样本。
- `sample_k_predictions` (function) - 返回 K 个随机预测，仅保留第一个的梯度，用于高效训练。
- `main` (function) - 解析参数，构建数据集，初始化模型和漂移银行，执行训练循环并记录指标。

### `test.py`

在验证/测试集上评估训练好的 DriftST 检查点，并可选导出 h5ad 文件。

- `main` (function) - 加载模型和测试数据，执行评估指标计算（PCC, SVG-PCC, MSE, MAE），支持方差后处理校准。

### `src/model.py`

定义 DriftST 核心模型架构（GenePredictor/STransformer）及损失函数。

- `GenePredictor` (class) - 主模型类，包含图像特征编码器、STransformer 模块、基因残差门控机制，输出基因表达分布。
- `zinb_loss` (function) - 零膨胀负二项分布（ZINB）重建损失函数，用于原始计数数据的拟合。

### `src/dataset.py`

数据加载器，将原始计数转换为 log1p(count) 目标并准备图像特征及邻居图。

- `build_datasets` (function) - 构建训练集、验证集和测试集，处理空间坐标、邻居映射及基因表达数据。

### `src/drift_step.py`

实现一步漂移目标（one-step drifting target）和预测银行（PredictionBank）。

- `PredictionBank` (class) - 环形缓冲区，存储模型生成的随机预测样本作为漂移损失的负样本。
- `multi_scale_drift_step` (function) - 执行多尺度漂移步骤，对齐随机预测分布与匹配的真实转录组谱。
- `drift_loss_fn` (function) - 计算漂移损失函数，结合正样本（真实表达）和负样本（银行中的预测）。

### `src/evaluation.py`

计算模型评估指标，包括 PCC、SVG-PCC、MSE、MAE。

- `evaluate` (function) - 综合计算各项指标，返回评估结果字典。
- `metrics_from_arrays` (function) - 基于预测数组和真实数组计算具体指标值。

### `src/postprocess.py`

对导出预测进行基因级方差校准（per-gene variance calibration）。

- `gene_stats` (function) - 计算基因统计信息，用于方差校准参考。
- `variance_postprocess` (function) - 执行仿射方差校准，调整预测方差以匹配训练集的参考方差。

### `process/preprocess_xenium_cell_level.py`

Xenium 细胞级数据预处理，从转录表重建细胞-基因矩阵并提取细胞中心 H&E 特征。

- `main` (function) - 执行完整的 Xenium 细胞级预处理流程。

### `process/select_xenium_cell_level_genes.py`

选择 Xenium 面板基因。

- `main` (function) - 根据面板信息筛选基因。

### `process/select_xenium_cell_level_hvg.py`

可选的 Xenium 高变基因（HVG）选择。

- `main` (function) - 识别并选择高变基因。

### `process/generate_xenium_cell_level_splits.py`

生成细胞级空间交叉验证分割（spatial CV splits）。

- `main` (function) - 为单个切片生成 5 折空间交叉验证分割。

### `process/preprocess_spot_level.py`

HEST 风格斑点级数据预处理（如 Visium）。

- `main` (function) - 处理斑点级数据，生成统一格式。

### `process/compute_spatial_variable_genes.py`

计算空间可变基因（SVG）排名，用于评估。

- `main` (function) - 计算并保存 SVG 排名。

### `scripts/run_xenium_cell_level_preprocess.sh`

执行默认的 Xenium 细胞级预处理脚本。

### `scripts/run_xenium_cell_level_train.sh`

在 Xenium 乳腺癌细胞级数据上训练 DriftST。

### `scripts/run_xenium_coad_cell_level_train.sh`

在 Xenium COAD 细胞级数据上训练 DriftST。

### `scripts/run_spot_level_train.sh`

在 HER2ST/PRAD/Kidney 等斑点级数据上训练 DriftST。

## Key Concepts

- **漂移目标（Drifting Objective）**: 一种训练策略，将模型生成的随机 Dropout 预测（负样本）与匹配的真实转录组谱（正样本）进行对齐，通过漂移损失函数优化模型分布。
- **预测银行（Prediction Bank）**: 一个环形缓冲区，存储模型在训练过程中生成的随机预测样本，作为漂移损失的负样本池。
- **STransformer 模块**: 基于 Transformer 的空间转录组预测核心，利用病理基础模型（UNI2/CONCH）提取的图像特征，结合共表达注意力偏置和渐进基因残差门控机制。
- **ZINB 重建**: 零膨胀负二项分布重建损失，用于直接拟合原始基因计数数据，处理空间转录组数据中的零膨胀特性。
- **方差后处理校准**: 对导出预测进行基因级仿射方差校准，使预测方差与训练集参考方差匹配，提高预测质量。

## Internal Relationships

- `train.py` → `src/dataset.py`: train.py 导入 build_datasets 以加载训练和验证数据。
- `train.py` → `src/model.py`: train.py 导入 GenePredictor 和 zinb_loss 以构建模型和计算损失。
- `train.py` → `src/drift_step.py`: train.py 导入 PredictionBank、multi_scale_drift_step 和 drift_loss_fn 以执行漂移训练。
- `train.py` → `src/evaluation.py`: train.py 导入 evaluate 以在训练过程中监控性能。
- `test.py` → `src/dataset.py`: test.py 导入 build_datasets 以加载测试数据。
- `test.py` → `src/model.py`: test.py 导入 GenePredictor 以加载预训练模型。
- `test.py` → `src/evaluation.py`: test.py 导入 evaluate 和 metrics_from_arrays 以计算评估指标。
- `test.py` → `src/postprocess.py`: test.py 导入 gene_stats 和 variance_postprocess 以进行方差校准。
- `process/preprocess_xenium_cell_level.py` → `src/dataset.py`: 预处理脚本生成符合 src.dataset 要求的 processed_data 格式。
