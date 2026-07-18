# huggingface_loader

> 用于创建和管理显微镜图像数据集的划分与特征提取的实用工具

该模块提供了一套完整的流水线，用于从原始元数据生成Hugging Face格式的数据集划分。核心功能包括按来源(source)、批次(batch)或板(plate)进行数据分割，使用贪婪算法确保划分比例接近目标值，支持数据集下采样，以及基于JCP元数据进行过滤。模块通过懒加载机制处理大型Parquet元数据文件，并直接构建可立即用于模型训练的数据集对象。

## Files

### `src/cellpainting_huggingface_loader/create_splits.py`

实现数据集划分、下采样和过滤的核心逻辑

- `CreateSplits` (class) - 核心类，负责管理数据集划分流程。初始化时接收元数据路径和Blob存储挂载点。
- `__init__` (method) - 初始化实例，设置元数据路径和Blob挂载点，初始化元数据DataFrame为None。
- `metadata_df` (property) - 懒加载属性，仅在需要时读取plate_metadata/metadata.parquet文件到内存。
- `generate_dataset_splits` (method) - 主方法，根据split_type（source/batch/plate）生成训练、验证和测试集。内部调用_load_source_batch_plate_info加载信息，使用_greedy_find_splits算法进行划分，最后调用_create_hf_dataset构建Hugging Face数据集。
- `_load_source_batch_plate_info` (method) - 私有方法，从Blob存储加载源、批次和板的信息数据。
- `_specify_split` (method) - 私有方法，确定包含在划分中的源列表，并计算总图像数。
- `_generate_name_count_list` (method) - 私有方法，生成包含源/批次/板名称及其图像计数的列表，用于贪婪算法。
- `_greedy_find_splits` (method) - 私有方法，使用贪婪算法将名称列表划分为训练、验证和测试集，以匹配目标比例。
- `_count_split_image_count` (method) - 私有方法，统计各划分集中的实际图像数量，并检查是否与目标比例偏差过大。
- `_create_hf_dataset` (method) - 私有方法，根据给定的划分列表创建Hugging Face DatasetDict对象。
- `create_downsampled_dataset` (method) - 方法，对现有划分进行下采样（默认0.2），并创建新的Hugging Face数据集。根据split_type不同，下采样后的划分层级会提升（如by_source下采样后变为by_batch划分）。
- `_downsample_data` (method) - 私有方法，对指定列表进行下采样处理。
- `filter_dataset` (method) - 方法，根据JCP元数据列表过滤数据集，移除不匹配的条目。
- `filter_JCP_metadata` (function) - 内部函数，用于filter_dataset，检查示例的filename是否在JCP元数据列表中。

## Key Concepts

- **懒加载元数据**: 
- **贪婪划分算法**: 
- **分层划分**: 
- **Hugging Face数据集集成**: 

## Internal Relationships

- `src/cellpainting_huggingface_loader/create_splits.py` → `src/cellpainting_huggingface_loader/__init__.py`: create_splits.py 中的类会被导入到包初始化文件中，以便外部使用。
- `src/cellpainting_huggingface_loader/create_splits.py` → `datasets`: create_splits.py 导入 datasets 库用于加载、连接和创建Hugging Face数据集对象。
- `src/cellpainting_huggingface_loader/create_splits.py` → `pandas`: create_splits.py 导入 pandas 用于处理元数据表格和进行数据过滤操作。
- `src/cellpainting_huggingface_loader/create_splits.py` → `numpy`: create_splits.py 导入 numpy 用于数值计算和数组操作。
