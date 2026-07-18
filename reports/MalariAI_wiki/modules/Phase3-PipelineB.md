# Phase3-PipelineB

> 疟疾血涂片细胞分割与分期分类系统的第二阶段：基于高效网络B0的细胞分类与Grad-CAM++可解释性推理

该模块实现了疟疾血涂片分析的第二阶段流程。它包含一个基于EfficientNet-B0的细胞分类器（使用Focal Loss处理类别不平衡），以及一个端到端的推理管道。推理管道首先通过分水岭算法提取细胞区域，然后对每个细胞进行分期分类（如滋养体、裂殖体等），最后利用Grad-CAM++生成热力图以可视化模型决策依据。该模块支持训练、验证和完整图像推理，输出包含分类结果、置信度、热力图及可视化图像。

## Files

### `Phase3-PipelineB/gradcam.py`

实现Grad-CAM++算法，用于生成EfficientNet-B0模型的决策热力图，增强模型可解释性。

- `GradCAMPlusPlus` (class) - Grad-CAM++的封装类，通过注册前向和后向钩子捕获目标层的激活和梯度，计算热力图。
- `_save_activation` (method) - 前向钩子函数，用于缓存目标层的特征图输出。
- `_save_gradient` (method) - 后向钩子函数，用于缓存目标层输出的梯度。
- `__call__` (method) - 执行前向传播和反向传播，计算并返回热力图、预测类别和置信度。

### `Phase3-PipelineB/stage1_watershed.py`

实现基于距离变换引导的分水岭算法，用于无监督的细胞实例分割和边界框提取。

- `watershed_cells` (function) - 核心函数，接收BGR图像，执行Otsu阈值、形态学开运算、距离变换、局部最大值检测和分水岭分割，返回细胞边界框列表。

### `Phase3-PipelineB/stage2_train.py`

训练EfficientNet-B0细胞分类器，使用Focal Loss解决类别不平衡问题。

- `compute_focal_alpha` (function) - 根据训练集中的类别频率计算Focal Loss的类别权重alpha。
- `FocalLoss` (class) - 多分类Focal Loss实现，通过调整难例权重来优化模型训练。
- `MalariaCropDataset` (class) - 自定义数据集类，从JSON标注和图像目录加载并预处理64x64的细胞裁剪图。

### `Phase3-PipelineB/stage2_inference.py`

执行端到端的推理流程：细胞分割 -> 分类 -> 热力图生成 -> 结果保存。

- `load_model` (function) - 加载预训练的EfficientNet-B0模型并替换分类头，支持从检查点恢复权重。
- `classify_crops` (function) - 对一批细胞裁剪图进行批量分类推理，返回预测类别和置信度。
- `run_inference` (function) - 主推理函数，整合分水岭分割、分类和Grad-CAM++可视化，保存结果图像和JSON。

### `Phase3-PipelineB/phase3-stage2-kaggle.ipynb`

在Kaggle环境中训练Stage 2分类器的Jupyter Notebook，包含配置、GPU检查、数据加载和训练循环。

### `Phase3-PipelineB/stage2-efficientnet-b0-completed.ipynb`

与phase3-stage2-kaggle.ipynb功能相同的Jupyter Notebook，可能为本地或不同环境的训练脚本。

### `Phase3-PipelineB/results/v1/inference/results.json`

存储推理结果的JSON文件，包含检测到的细胞数量、感染率、各类别计数及每个细胞的详细信息。

### `Phase3-PipelineB/results/v1/inference1/results.json`

另一组推理结果的JSON文件，展示不同参数或模型下的检测结果。

### `Phase3-PipelineB/results/v1/inference2/results.json`

第三组推理结果的JSON文件，用于对比分析。

### `Phase3-PipelineB/results/v1/inference2/stage2_inference.py`

与主stage2_inference.py功能相同的推理脚本，可能用于特定实验或版本控制。

## Key Concepts

- **Grad-CAM++**: 
- **Focal Loss**: 
- **分水岭分割**: 
- **EfficientNet-B0**: 
- **端到端推理**: 

## Internal Relationships

- `Phase3-PipelineB/stage2_inference.py` → `Phase3-PipelineB/stage1_watershed.py`: stage2_inference.py 导入 stage1_watershed.py 中的 watershed_cells 函数来提取细胞区域。
- `Phase3-PipelineB/stage2_inference.py` → `Phase3-PipelineB/gradcam.py`: stage2_inference.py 导入 gradcam.py 中的 GradCAMPlusPlus 类来生成热力图。
- `Phase3-PipelineB/stage2_train.py` → `Phase3-PipelineB/dataset.py`: stage2_train.py 导入 MalariaCropDataset 类来加载和预处理训练数据。
- `Phase3-PipelineB/stage2_train.py` → `shared/label_map.py`: stage2_train.py 和 stage2_inference.py 都导入 label_map.py 获取类别映射和颜色定义。
- `Phase3-PipelineB/phase3-stage2-kaggle.ipynb` → `Phase3-PipelineB/stage2_train.py`: Kaggle Notebook 实现了与 stage2_train.py 相同的训练逻辑，但采用Jupyter单元格形式。
