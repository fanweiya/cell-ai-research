# utils

> 提供实验工具、日志记录、模型加载及数据转换等通用功能

该模块封装了白细胞图像分割项目中所需的底层工具函数和类，包括指标追踪、高性能日志记录、实验目录管理、模型加载（DinoBloom/ViT）以及PyTorch张量与图像转换。核心目标是减少重复代码，提升实验可复现性和运行效率。

## Files

### `utils/average_value_tracker.py`

实现多指标的平均值追踪器，用于在训练或验证过程中累积并计算多个指标的均值

- `AverageValueTracker` (class) - 初始化时接收指标键名列表，支持reset重置、update更新数值（可选权重计数）及get_averages获取当前平均值

### `utils/logger.py`

实现支持多线程、内存/数量限制及强制保存的高性能日志记录器

- `Logger` (class) - 将日志条目累积在内存中，当达到内存限制或数量限制时自动写入文件；支持多线程安全操作和信号处理（SIGINT）以在程序退出时保存日志
- `log` (method) - 记录日志字典，若force=True则立即触发保存
- `_should_save_logs` (method) - 判断是否达到保存阈值（数量或内存大小）
- `_save_logs` (method) - 将累积的日志写入JSON文件并清空缓冲区

### `utils/utils.py`

提供基础工具函数，包括随机种子设置、实验目录创建、文件IO（pickle/json/yaml/gzip）及统计指标计算

- `LoopingIterator` (class) - 包装DataLoader，当迭代器耗尽时自动重置，实现无限循环遍历
- `conf95` (function) - 计算95%置信区间：1.96 * 标准差 / sqrt(样本数)
- `get_meanpm95conf_strlatex` (function) - 返回均值±95%置信区间的LaTeX格式字符串
- `setup_seed` (function) - 设置随机种子，支持从环境变量读取或自动生成
- `setup_savedir` (function) - 根据前缀、参数和时间戳创建唯一的实验保存目录，若存在则自动追加序号
- `save_pkl` (function) - 使用pickle序列化保存Python对象
- `load_pkl` (function) - 读取pickle文件并反序列化对象
- `save_args` (function) - 将命令行参数对象保存为JSON文件
- `gzip_file_and_remove_original` (function) - 压缩文件并删除原始文件
- `load_yaml` (function) - 读取YAML配置文件

### `utils/utils_dino_bloom.py`

加载和配置DinoBloom视觉模型及ViT分割网络，处理位置编码插值与图像填充

- `get_dino_bloom` (function) - 加载预训练的DinoBloom模型，支持指定模型尺寸（S/B/L/G），自动处理位置编码和状态字典加载
- `get_resized_positional_embedding` (function) - 为指定图像尺寸预计算插值后的位置编码，避免推理时重复计算
- `ZeroPadToMultiple` (class) - 将图像填充至宽高为指定倍数的模块
- `ViTSeg` (class) - 基于ViT骨干网络的分割模型，支持多尺度特征上采样和骨干网络冻结

### `utils/utils_torch.py`

提供PyTorch图像预处理、张量转换及图像编码器获取工具

- `GetTransform` (class) - 根据split（train/nocrop/val）返回不同的图像变换流水线，包含Resize、Crop、Flip、Normalize
- `denormalize` (function) - 将归一化的Tensor还原为[0,1]范围的图像张量
- `tensor_to_pil_image` (function) - 将PyTorch张量转换为Pillow图像对象
- `get_image_encoder` (function) - 根据名称加载 torchvision 或 timm 的图像编码器，移除分类头并返回模型及输出维度

## Key Concepts

- **增量日志缓冲**: Logger类将日志先存入内存列表，仅在达到内存或数量阈值时写入磁盘，减少I/O开销
- **位置编码插值优化**: get_resized_positional_embedding函数预先计算ViT模型在特定输入尺寸下的位置编码，避免每次前向传播时重复插值
- **无限数据迭代**: LoopingIterator包装DataLoader，在迭代结束时自动重启，适用于需要多轮遍历的训练循环
- **实验可复现性**: 通过setup_seed统一设置随机种子，结合setup_savedir生成带时间戳的唯一目录，确保实验可追踪

## Internal Relationships

- `utils/utils.py` → `utils/logger.py`: 实验脚本可能使用Logger记录训练日志，并通过utils.py中的setup_savedir创建日志存储路径
- `utils/utils_dino_bloom.py` → `utils/utils_torch.py`: ViTSeg模型可能使用utils_torch中的图像变换或编码器加载逻辑进行数据预处理
- `utils/average_value_tracker.py` → `utils/utils.py`: 训练循环中可能调用AverageValueTracker统计指标，并通过utils.py的统计函数生成报告
- `utils/utils_torch.py` → `utils/utils_dino_bloom.py`: DinoBloom模型加载可能需要使用utils_torch中的图像归一化或张量转换功能
