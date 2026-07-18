# dart_experiment

> 校准和验证微流控芯片的像素尺度，并配置不同分割器进行细胞分析实验

该模块负责将微流控芯片蓝图与显微镜图像对齐，用于实时细胞分析。核心功能包括：1) 通过检测芯片上的标记点（十字和圆圈）来验证实际像素尺度与配置值的一致性；2) 提供多种实验配置，支持不同的分割器（Omnipose、Cellpose+SAM）和芯片类型（如Mother Machines），并控制图像翻转、截断和配准等参数。

## Files

### `dart_experiment/calibration_data/calibration_config.json`

存储芯片校准的元数据，包括芯片名称、校准图像路径、物镜位置、像素尺寸、芯片配置路径和模型路径。

### `dart_experiment/check_pixel_scale.py`

脚本用于检查所有腔室类型的像素尺度因子。它加载芯片配置和标记检测模型，遍历指定文件夹，检测图像中的标记点，计算物理距离与检测距离的比值，从而验证像素尺寸是否准确。

- `chip_lib` (variable) - 从sak.json加载的芯片结构库实例
- `mdm` (variable) - 标记检测模型实例，用于预测图像中的标记点
- `folders` (variable) - 文件夹名称到腔室类型的映射字典
- `config_pixel_size` (variable) - 当前配置的像素尺寸值，用于计算预期距离
- `main loop` (function) - 遍历每个文件夹，加载图像，检测标记，计算物理距离与检测距离的误差，并输出统计结果

### `dart_experiment/folder_config.json`

定义使用Omnipose分割器的实验配置，包含输入输出目录、像素尺寸、芯片配置、模型路径、图像翻转、截断、配准设置以及要处理的文件夹映射。

### `dart_experiment/folder_config_cellpose_sam.json`

定义使用Cellpose+SAM分割器的实验配置，与folder_config.json类似，但禁用了配准功能。

### `dart_experiment/folder_config_mm.json`

专门针对Mother Machines芯片类型的实验配置，仅处理Mothermachine-2x-inner文件夹。

### `dart_experiment/folder_config_reproduce.json`

用于复现实验的配置，使用Cellpose+SAM分割器且禁用配准，处理所有文件夹类型。

## Key Concepts

- **像素尺度校准**: 通过检测芯片上已知物理距离的标记点（十字和圆圈），计算图像中检测到的像素距离，从而反推实际像素尺寸，验证配置值的准确性。
- **芯片配置**: artifacts/chips/sak.json 定义了不同腔室类型中标记点的物理坐标，是计算物理距离的基础。
- **分割器选择**: 支持Omnipose和Cellpose+SAM两种分割器，通过不同的配置文件切换，以适应不同的细胞分割需求。
- **图像预处理**: 包括Y轴翻转、归一化到uint8、转换为3通道等步骤，确保图像符合模型输入要求。
- **配准**: 使用归一化互相关（NCC）方法将图像与芯片蓝图对齐，确保分析区域准确对应。

## Internal Relationships

- `dart_experiment/check_pixel_scale.py` → `dart_experiment/calibration_data/calibration_config.json`: check_pixel_scale.py 读取 calibration_config.json 中的像素尺寸和模型路径，但主要依赖 artifacts/chips/sak.json 和 artifacts/models/v26_detect_s_imgsz1280.pt
- `dart_experiment/check_pixel_scale.py` → `dart_experiment/folder_config.json`: 两者共享相同的文件夹映射和芯片配置，但 check_pixel_scale.py 是独立脚本，不直接导入这些JSON
- `dart_experiment/folder_config.json` → `dart_experiment/folder_config_cellpose_sam.json`: 两者结构相似，但分割器和配准设置不同，用于对比实验
