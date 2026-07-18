# feature-extraction

> Cell Painting 图像特征提取流水线，支持多模型推理与结果聚合

该模块实现了从原始显微图像到特征向量的完整处理流程。核心功能包括：通过 YAML 配置动态加载模型和预处理流程、支持单通道与多通道模型的推理、处理不同数据集（CPG0016, BBBC036）的切片、将推理结果聚合为 Parquet 文件。系统支持本地和云环境（AMLT）部署，包含诊断工具和单元测试。

## Files

### `feature-extraction/src/config.py`

中央配置模块，负责加载 YAML 配置文件并动态构建模型包装器、数据加载器和图像变换流程。

- `load_config` (function) - 加载 YAML 配置文件并设为活动配置
- `get_transform` (function) - 根据模型名称返回对应的图像预处理变换
- `get_model_wrapper` (function) - 根据模型名称返回对应的模型包装器类
- `MODEL_WRAPPERS` (dictionary) - 模型包装器类注册表，映射模型名到类
- `_build_classic_transform` (function) - 构建适用于 ImageNet 预训练模型的标准化变换流程

### `feature-extraction/src/models/base_model_wrapper.py`

定义所有模型包装器的抽象基类，提供推理循环、补丁处理（patching）和通用工具方法。

- `ModelWrapper` (class) - 抽象基类，定义 _load_model, infer, postprocess 接口
- `_patch_batch` (method) - 将图像批次分割为不重叠的补丁，支持对齐约束
- `_average_patch_outputs` (method) - 对补丁输出进行平均，支持张量和字典类型

### `feature-extraction/src/custom_datasets/direct_dataset.py`

直接从磁盘加载 PNG 图像的 PyTorch Dataset，绕过 HuggingFace 数据集开销，支持单通道和多通道模式。

- `DirectImageDataset` (class) - 直接图像加载数据集类
- `_get_stacked_item` (method) - 加载并堆叠 5 个通道用于多通道模型
- `_get_single_channel_item` (method) - 加载单个通道用于单通道模型

### `feature-extraction/src/aggregate_features.py`

将每个 GPU 的推理结果（pkl）聚合成按孔板（well）级别的特征 Parquet 文件。

- `run_aggregation_for_config` (function) - 根据配置运行聚合流程
- `get_model_category` (function) - 判断模型类别（单通道、多通道等）以确定聚合策略
- `parse_single_channel_filename` (function) - 解析单通道文件名提取孔板、井号和通道信息

### `feature-extraction/src/run_inference.py`

主推理脚本，支持多 GPU 并行推理，处理 HuggingFace 数据集格式。

- `inference` (function) - 在单个 GPU 上运行模型推理
- `run_model` (function) - 为单个模型启动多 GPU 推理进程
- `run_inference_for_config` (function) - 根据配置运行所有启用的模型

### `feature-extraction/src/run_inference_direct.py`

直接推理脚本，直接从磁盘加载 PNG 并预过滤 MOA 化合物，比 HF 路径快约 4 倍。

- `load_and_filter_metadata` (function) - 加载并过滤元数据，仅保留 MOA 化合物和对照
- `inference_direct` (function) - 直接模式下的单 GPU 推理

### `feature-extraction/src/models/resnet101_wrapper.py`

ResNet-101 包装器，加载 ImageNet 预训练权重，输出 2048 维特征向量。

- `ResNetWrapper` (class) - ResNet-101 包装器类

### `feature-extraction/src/models/resnet101_untrained_wrapper.py`

随机初始化 ResNet-101 包装器，作为基线对比。

- `ResNetUntrainedWrapper` (class) - 未训练 ResNet-101 包装器类

### `feature-extraction/src/models/dinov2_wrapper.py`

DINOv2 包装器，支持标准 224x224 和高分辨率 448x448 输入，输出 cls_token 和 patch_token 特征。

- `DINOv2Wrapper` (class) - 标准 DINOv2 包装器
- `DINOv2HighRes448Wrapper` (class) - 448x448 输入 DINOv2 包装器

### `feature-extraction/src/models/vgg19_wrapper.py`

VGG19 包装器，加载 ImageNet 预训练权重，输出 4096 维特征向量。

- `VGG19Wrapper` (class) - VGG19 包装器类

### `feature-extraction/src/models/OpenPhenom_wrapper.py`

OpenPhenom MAE 模型包装器，从 HuggingFace 自动下载权重，输出 384 维特征向量。

- `OpenPhenomWrapper` (class) - OpenPhenom 包装器类

### `feature-extraction/src/models/cloome_wrapper.py`

CLOOME 模型包装器，使用修改版 ResNet-50 处理 5 通道图像，输出 512 维 L2 归一化嵌入。

- `CloomeWrapper` (class) - CLOOME 包装器类

### `feature-extraction/src/models/subcell_wrapper.py`

SubCell 模型包装器，基于 ViT 和门控注意力池化，对 ER-DNA-Protein 变体进行 3 次推理并拼接特征。

- `SubCellWrapper` (class) - SubCell 包装器类
- `GatedAttentionPooler` (class) - 门控注意力池化模块

### `feature-extraction/src/models/openphenom/huggingface_mae.py`

OpenPhenom MAE 模型实现，包含编码器、解码器和损失函数。

- `MAEModel` (class) - MAE 模型主类
- `MAEConfig` (class) - MAE 配置类

### `feature-extraction/src/models/cloome/model.py`

CLOOME 模型核心实现，包含 ResNet 骨干网络和 CLIP 通用架构。

- `ResNet` (class) - CLOOME 使用的 ResNet 实现
- `Bottleneck` (class) - ResNet 瓶颈块

### `feature-extraction/src/run_inference_splits.py`

支持对多个数据集切片（splits）进行批量推理的脚本。

- `build_split_config` (function) - 为指定切片构建专用配置
- `parse_splits` (function) - 解析命令行提供的切片列表

### `feature-extraction/src/aggregate_splits.py`

对多个切片的推理结果进行聚合，支持并行模型聚合。

- `main` (function) - 聚合脚本入口点

### `feature-extraction/src/diagnose_nan.py`

诊断工具，检查聚合后的 Parquet 文件和原始 pkl 文件中是否存在 NaN 或 Inf 值。

- `check_parquets` (function) - 检查 Parquet 文件中的 NaN/Inf
- `check_pkls` (function) - 检查 pkl 文件中的 NaN/Inf

### `feature-extraction/src/tests/test_patching.py`

单元测试，验证补丁处理逻辑的几何正确性和输出一致性。

- `TestPatchGeometry` (class) - 补丁几何测试类

### `feature-extraction/src/utils/util.py`

通用工具函数，包括图像归一化、位深转换、板分块等。

- `illumination_threshold_tensor` (function) - 16 位图像转 8 位的光照阈值化
- `get_plate_chunks` (function) - 将孔板分配给多个 GPU
- `repeat` (function) - 单通道重复为 3 通道

### `feature-extraction/src/utils/huggingface_loader.py`

HuggingFace 数据集包装器，统一接口并应用变换。

- `DatasetWrapper` (class) - 数据集包装类

### `feature-extraction/configs/inference_config.yaml`

标准推理配置文件，定义模型、数据集和推理参数。

### `feature-extraction/configs/inference_splits.yaml`

多切片推理配置文件，支持对多个数据集切片进行批量处理。

### `feature-extraction/configs/direct_moa_config.yaml`

直接推理配置，专门用于 MOA 化合物分析，预过滤数据以提高效率。

## Key Concepts

- **模型包装器模式**: 所有模型通过统一的 ModelWrapper 接口封装，隐藏具体实现细节，支持热插拔和并行推理。
- **补丁处理（Patching）**: 对于大图像，可将其分割为多个不重叠补丁分别推理，然后平均结果，以适配显存限制或提高分辨率。
- **单通道 vs 多通道**: 单通道模型（如 ResNet）每次处理一个通道并重复为 3 通道；多通道模型（如 CLOOME）直接处理 5 通道堆叠图像。
- **直接数据集加载**: 绕过 HuggingFace 数据集层，直接从 PNG 文件读取，配合元数据过滤，显著提升 MOA 分析效率。
- **多 GPU 并行推理**: 通过 torch.multiprocessing 将不同孔板分配给不同 GPU，每个进程独立运行模型并保存中间 pkl 文件。
- **结果聚合策略**: 根据模型类型采用不同聚合方式：单通道模型按孔板和通道平均后拼接；多通道模型直接按孔板平均。

## Internal Relationships

- `run_inference.py` → `config.py`: 导入 config 模块以加载配置和获取模型包装器
- `run_inference.py` → `models/base_model_wrapper.py`: 使用 ModelWrapper 基类实例化具体模型
- `run_inference_direct.py` → `custom_datasets/direct_dataset.py`: 使用 DirectImageDataset 直接从磁盘加载图像
- `aggregate_features.py` → `run_inference.py`: 依赖 run_inference 生成的 pkl 文件进行聚合
- `models/OpenPhenom_wrapper.py` → `models/openphenom/huggingface_mae.py`: OpenPhenomWrapper 调用 MAEModel 进行推理
- `models/cloome_wrapper.py` → `models/cloome/model.py`: CloomeWrapper 加载 CLIPGeneral 模型
- `config.py` → `models/__init__.py`: 从 models 包导入所有包装器类到注册表
- `run_inference_splits.py` → `aggregate_splits.py`: split 推理后可直接调用 aggregate_splits 进行结果聚合
