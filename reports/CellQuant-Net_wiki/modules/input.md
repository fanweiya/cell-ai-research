# input

> 负责从指定目录读取全切片图像（WSI）并加载为可处理的数据结构

该模块提供WSI文件的读取和预处理功能。它扫描指定目录，按顺序加载名为WSI1、WSI2等的图像文件，将其转换为适合下游核检测、分类和质量评估流程的张量或图像对象。模块包含文件路径解析、图像格式验证和基础加载逻辑。

## Files

### `read_wsi.py`

实现WSI文件读取和加载的核心逻辑

- `load_wsi_from_folder` (function) - 扫描输入文件夹，按命名顺序读取所有WSI文件并返回图像列表
- `validate_wsi_format` (function) - 验证图像文件是否为有效的WSI格式（如SVS、NDPI等）
- `parse_wsi_name` (function) - 从文件名中提取序列号，确保按正确顺序处理图像

### `config.py`

定义输入模块的配置参数

- `INPUT_DIR` (constant) - 存放WSI图像的目录路径
- `SUPPORTED_FORMATS` (constant) - 支持的WSI文件格式列表

## Key Concepts

- **WSI顺序加载**: 通过解析文件名中的数字序列（WSI1, WSI2...）确保图像按预期顺序处理，避免随机读取导致的流程错误
- **格式验证**: 在加载前检查文件是否为有效的全切片图像格式，防止无效文件中断后续处理流程

## Internal Relationships

- `read_wsi.py` → `config.py`: read_wsi.py导入config.py以获取输入目录路径和格式配置
