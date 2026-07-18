# development

> 存放用于开发新功能（如实例分割、跟踪、3D分割、微调）的脚本和工具。

该模块包含一系列实验性脚本，用于开发和完善micro-sam的额外功能。这些脚本通常变化较快，可能不稳定。主要涵盖3D和分块图像分割、时间序列跟踪、自动提示生成、模型微调、基准测试以及数据检查等任务。

## Files

### `development/README.md`

提供模块概述和使用说明，警告脚本处于开发阶段。

### `development/annotator_3d_tiled.py`

演示如何在3D数据上使用分块（tiling）策略进行交互式标注和实例分割，以处理大内存需求。

- `annotator_with_tiling` (function) - 加载3D数据并使用分块策略启动3D标注器。
- `segment_tiled` (function) - 使用分块预计算嵌入并执行3D实例分割。

### `development/annotator_tracking_tiled.py`

演示在时间序列数据上使用分块策略进行交互式跟踪标注。

- `annotator_with_tiling` (function) - 加载时间序列数据并使用分块策略启动跟踪标注器。

### `development/annotators_in_image_series.py`

提供处理大型3D体积的不同策略：一次性加载整个体积、逐切片加载或按批次加载切片。

- `segment_volume` (function) - 将整个3D体积加载到工具中进行分割。
- `segment_each_slice` (function) - 逐个切片加载体积并使用图像系列标注器。
- `segment_each_n_slices` (function) - 将体积按Z轴批次（n个切片）分割并逐个处理。

### `development/apg_example.py`

展示自动提示生成器（Automatic Prompt Generator）的使用，包括标准模式和分块模式，以及全切片图像（WSI）处理示例。

- `example_script` (function) - 使用AutomaticPromptGenerator进行2D自动分割的示例。
- `example_script_tiled` (function) - 使用TiledAutomaticPromptGenerator进行分块自动分割的示例。
- `example_script_wsi` (function) - 处理全切片图像（WSI）的示例，包含掩膜优化。

### `development/benchmark.py`

运行性能基准测试，评估不同模型和设备下嵌入计算、提示分割等操作的运行时间。

- `benchmark_embeddings` (function) - 测量预计算图像嵌入的时间。
- `benchmark_prompts` (function) - 测量基于点、框等提示进行分割的时间。

### `development/check_3d_model.py`

用于测试和训练3D SAM模型（SemanticSamTrainer3D）的脚本。

- `predict_3d_model` (function) - 加载3D SAM模型并进行前向预测。
- `train_3d_model` (function) - 使用虚拟数据集训练3D SAM模型。

### `development/check_data_count.py`

统计和打印常用显微图像数据集（如LIVECell, DeepBacs, TissueNet等）的图像和对象数量。

- `check_data_count` (function) - 遍历多个数据集并统计图像和实例数量。

### `development/check_omero_connection.py`

演示如何连接OMERO服务器，获取图像数据，使用micro-sam进行标注，并将结果作为多边形上传回OMERO。

- `_load_image` (function) - 从OMERO加载图像，运行2D标注器，并可选上传分割结果。

### `development/instance_segmentation.py`

演示在3D光片数据（细胞核）和时间序列数据（细胞）上进行实例分割的多种方法，包括SAM直接预测和基于嵌入的分割。

- `nucleus_segmentation` (function) - 在3D光片数据单切片上分割细胞核。
- `nucleus_segmentation_3d` (function) - 在3D光片数据上进行全3D细胞核分割。
- `cell_segmentation` (function) - 在时间序列数据上分割细胞。

### `development/instance_segmentation_3d.py`

专注于3D实例分割的脚本，处理线粒体等结构的3D分割，包含数据切块加载功能。

- `get_dataset_cutout` (function) - 从HDF5文件中加载指定形状和起始位置的切块数据。

### `development/promptable_segmentation.py`

从AGAR数据集的元数据中提取点或框提示，并自动执行分割，展示提示可分割功能。

- `get_agar_data` (function) - 下载并解压AGAR演示数据集。
- `extract_prompts_from_data` (function) - 从元数据中提取点或框坐标作为提示。

### `development/support/finetune_nucleus.py`

针对细胞核分割任务微调SAM模型的脚本，包含数据加载和训练流程。

- `get_loaders` (function) - 构建训练和验证数据加载器。
- `main` (function) - 启动微调流程。

### `development/support/train_cell_fluo_embl_alm.py`

针对特定荧光显微图像数据集（EMBL ALM）微调SAM模型并导出自定义模型的脚本。

- `train_embl_alm_data` (function) - 准备数据加载器并运行训练。

### `development/tracking.py`

演示时间序列数据的跟踪功能，包括交互式标注和基于提示的自动跟踪调试。

- `debug_tracking` (function) - 使用预计算嵌入和提示从特定位点开始跟踪。
- `load_data` (function) - 从文件路径加载时间序列数据。

## Key Concepts

- **分块处理 (Tiling)**: 将大图像或体积分割成小块（tile）进行处理，配合halo区域以减少边界效应，从而在有限内存下处理大数据集。
- **自动提示生成 (Automatic Prompt Generation)**: 算法自动为图像生成点或框提示，无需人工交互即可实现实例分割。
- **3D SAM模型**: 针对3D体积数据设计的SAM变体，支持3D图像嵌入和3D分割掩膜预测。
- **微调 (Fine-tuning)**: 在特定领域数据（如细胞核、荧光图像）上继续训练SAM模型，以优化其在特定任务上的性能。
- **跟踪 (Tracking)**: 在时间序列数据中关联不同帧中的实例，形成目标的时间轨迹。

## Internal Relationships

- `development/annotator_3d_tiled.py` → `micro_sam.sam_annotator`: 导入annotator_3d和precompute_image_embeddings用于分块3D标注。
- `development/instance_segmentation.py` → `micro_sam.segment_instances`: 导入segment_instances_from_embeddings等函数执行实例分割。
- `development/apg_example.py` → `micro_sam.instance_segmentation`: 导入TiledAutomaticPromptGenerator和AutomaticPromptGenerator。
- `development/support/finetune_nucleus.py` → `micro_sam.training`: 使用sam_training模块中的训练函数和数据加载器。
- `development/check_3d_model.py` → `micro_sam.sam_3d_wrapper`: 导入get_3d_sam_model用于加载和测试3D模型。
