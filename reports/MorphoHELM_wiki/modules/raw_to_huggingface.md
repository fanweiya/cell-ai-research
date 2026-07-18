# raw_to_huggingface

> 将原始细胞形态学图像板文件夹转换为每块板的 HuggingFace 数据集。

该模块负责将原始的 Cell Painting 图像数据（按板文件夹组织）转换为 HuggingFace DatasetDict 格式。每个板文件夹对应一个独立的数据集，包含训练集分割。数据集中的每一行记录包含图像本身（以字节形式存储）、文件名、板名、孔位、视野（FOV）、通道元数据，以及从同板级别的 pickle 文件中查找到的边界框。它支持 CPG 和 BBBC036 两种数据集格式，通过正则表达式解析文件名，并处理图像数据的标准化和编码。

## Files

### `raw_to_huggingface/transform_dataset.py`

实现从原始图像板文件夹到 HuggingFace 数据集的转换逻辑，包括目录发现、图像加载、元数据提取、边界框关联和数据序列化。

- `ImageRecord` (dataclass) - 定义单条图像记录的数据结构，包含图像字典、文件名、板名、孔位、FOV、通道和边界框列表。
- `discover_plates` (function) - 扫描原始根目录，返回所有符合板目录命名规则（排除包含 bf、metadata、brightfield 的目录）的板名列表。
- `_normalise_boxes` (function) - 标准化边界框数据，将 numpy 数组转换为列表，处理 None 情况。
- `_to_uint8` (function) - 将任意 numpy 图像数组转换为 0-255 范围的 uint8 数组，处理不同数据类型的归一化。
- `_uint8_png_payload` (function) - 读取图像文件，转换为 uint8 PNG 格式，并返回包含字节内容和文件名的字典。
- `_load_cpg_boxes` (function) - 从 pickle 文件中加载 CPG 格式的边界框数据，按板名解析并返回键值对映射。
- `_load_bbbc036_boxes` (function) - 从 pickle 文件中加载 BBBC036 格式的边界框数据，解析文件名中的孔位和 FOV 信息。
- `process_plate` (function) - 处理单个板文件夹，遍历其中的图像文件，提取元数据，加载边界框，构建 ImageRecord 列表并保存为 HuggingFace 数据集。
- `main` (function) - 命令行入口函数，解析参数，调用 process_plate 处理指定的板或所有板。

## Key Concepts

- **HuggingFace DatasetDict**: 
- **板级边界框查找**: 
- **图像标准化**: 
- **多数据集支持**: 
