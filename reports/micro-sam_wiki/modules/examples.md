# examples

> 提供 micro_sam 库的交互式标注、自动分割、跟踪及模型微调的示例脚本。

该模块包含一系列 Python 脚本和文档，用于演示如何使用 micro_sam 进行显微镜图像的交互式标注（2D、3D、跟踪、图像序列）、自动分割与跟踪、模型微调以及将 micro_sam 作为库集成到自定义流程中。所有脚本均利用预下载的示例数据，并支持使用微调后的 SAM 模型。

## Files

### `examples/README.md`

概述 examples 模块的结构和主要功能。

### `examples/finetuning/README.md`

介绍模型微调文件夹中的脚本用途。

### `examples/annotator_2d.py`

运行交互式 2D 标注工具，支持 LIVEcell、HeLa 2D 和全切片图像。

- `livecell_annotator` (function) - 为 LIVEcell 数据集示例图像运行 2D 标注器。
- `hela_2d_annotator` (function) - 为 Cell Tracking Challenge HeLa 2D 数据集示例图像运行 2D 标注器。
- `wholeslide_annotator` (function) - 为全切片图像运行带分块（tiling）的 2D 标注器。

### `examples/annotator_3d.py`

运行交互式 3D 标注工具，用于电子显微镜体积数据。

- `em_3d_annotator` (function) - 为示例 EM 体积运行 3D 标注器。

### `examples/annotator_tracking.py`

运行交互式跟踪标注工具，用于时间序列图像。

- `track_ctc_data` (function) - 为细胞跟踪挑战（CTC）数据运行交互式跟踪。

### `examples/automatic_segmentation.py`

运行 2D 图像的自动分割，支持 AMG、AIS 和 APG 模式。

- `livecell_automatic_segmentation` (function) - 对 LIVEcell 示例图像运行自动分割。
- `hela_automatic_segmentation` (function) - 对 HeLa 2D 示例图像运行自动分割。
- `wholeslide_automatic_segmentation` (function) - 对全切片图像运行带分块的自动分割。

### `examples/automatic_tracking.py`

运行 2D 时间序列图像的自动跟踪。

- `example_automatic_tracking` (function) - 对 CTC 数据运行自动跟踪。

### `examples/bioimageio/export_model_for_bioengine.py`

将模型导出为 Bioengine 格式。

- `export_bioengine_model` (function) - 导出模型供 Bioengine 使用。

### `examples/bioimageio/export_model_for_bioimageio.py`

将模型导出为 bioimage.io 格式。

- `export_sam_model` (function) - 导出 SAM 模型供 bioimage.io 使用。

### `examples/finetuning/annotator_with_finetuned_model.py`

在 2D 标注器中使用微调后的模型。

- `run_annotator_with_finetuned_model` (function) - 使用微调后的模型运行 2D 标注器。

### `examples/finetuning/finetune_hela.py`

在自定义数据上微调 SAM 模型，包括交互式分割和实例分割解码器。

- `get_dataloader` (function) - 为微调 SAM 返回训练或验证数据加载器。
- `run_training` (function) - 运行实际的模型训练。
- `export_model` (function) - 导出训练好的模型。

### `examples/finetuning/finetune_hela_instance_segmentation.py`

仅训练实例分割解码器（UNETR），不更新交互式分割组件。

- `get_dataloader` (function) - 为训练实例分割解码器返回数据加载器。
- `run_training` (function) - 运行 UNETR 实例分割解码器的训练。
- `export_model` (function) - 导出训练好的实例分割模型。

### `examples/image_series_annotator.py`

运行图像序列的标注工具。

- `series_annotation` (function) - 标注一系列图像。

### `examples/object_classifier.py`

演示对象分类器功能，用于对分割结果进行分类。

- `livecell_annotator` (function) - 对 LIVEcell 数据运行对象分类。
- `wholeslide_annotator` (function) - 对全切片数据运行对象分类。
- `lucchi_annotator` (function) - 对 3D EM 数据运行对象分类。

### `examples/quick_start.py`

快速开始示例，演示如何使用 micro_sam 的自动实例分割功能。

- `main` (function) - 加载示例图像，运行自动实例分割并可视化。

### `examples/use_as_library/instance_segmentation.py`

展示如何将 micro_sam 作为库集成到自定义脚本中，进行实例分割。

- `cell_segmentation` (function) - 对 HeLa 细胞运行实例分割。
- `cell_segmentation_with_tiling` (function) - 对大图像运行带分块的实例分割。

## Key Concepts

- **交互式标注 (Interactive Annotation)**: 通过点击或拖动提示（points, boxes, masks）来指导 SAM 模型生成分割掩码，支持 2D、3D 和时序数据。
- **自动分割 (Automatic Segmentation)**: 无需用户交互，模型自动预测实例分割。支持三种模式：AMG（自动掩码生成）、AIS（自动实例分割，micro_sam 特有）、APG（自动提示生成）。
- **模型微调 (Model Finetuning)**: 在自定义显微镜图像数据集上微调 SAM 模型，包括整体微调（更新图像编码器、提示编码器、掩码解码器）和仅微调实例分割解码器（UNETR）。
- **嵌入缓存 (Embedding Cache)**: 为加速交互式标注和自动分割，图像特征嵌入被预计算并缓存为 .zarr 文件，避免重复推理。
- **分块处理 (Tiling)**: 处理大图像（如全切片）时，将图像分割成小块进行预测，再拼接结果，以节省内存并避免显存溢出。

## Internal Relationships

- `examples/annotator_2d.py` → `micro_sam.sam_annotator.annotator_2d`: 导入 annotator_2d 函数以启动交互式 2D 标注界面。
- `examples/automatic_segmentation.py` → `micro_sam.automatic_segmentation.get_predictor_and_segmenter`: 导入函数以获取预测器和分割器，用于自动分割。
- `examples/finetuning/finetune_hela.py` → `micro_sam.training.train_sam`: 调用训练函数以微调 SAM 模型。
- `examples/finetuning/finetune_hela_instance_segmentation.py` → `micro_sam.training.train_instance_segmentation`: 调用函数以仅训练实例分割解码器。
- `examples/quick_start.py` → `examples/automatic_segmentation.py`: 两者都使用 get_predictor_and_segmenter 和 automatic_instance_segmentation，但 quick_start 更简化。
- `examples/use_as_library/instance_segmentation.py` → `examples/automatic_segmentation.py`: 展示了如何在自定义脚本中复用自动分割的核心逻辑。
