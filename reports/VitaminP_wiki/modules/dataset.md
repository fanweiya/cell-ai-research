# dataset

> 提供基于Zarr格式的多模态病理细胞分割数据集加载、增强及HV图生成模块

该模块封装了CRC（结直肠癌）及多种癌症类型（如Xenium, PanNuke, Lizard等）的病理图像数据。核心功能包括从Zarr文件中加载H&E和MIF双模态图像、实例分割掩码，使用PanNuke方法生成水平-垂直梯度图（HV maps），以及应用针对医学影像的几何和光度增强。模块支持内存缓存加速、多数据集混合训练及数据完整性验证。

## Files

### `dataset/config.py`

配置加载与验证器，负责读取YAML配置文件并应用类型检查和参数覆盖

- `Config` (class) - 配置管理类。通过__init__加载YAML文件，支持__overrides__动态覆盖参数（如batch_size, augment_prob），执行_required_sections__验证，确保split比例总和为1.0，并检查zarr路径有效性。

### `dataset/__init__.py`

模块入口，定义公共API并导出所有核心组件

- `__all__` (list) - 定义模块对外暴露的符号列表，包括Config, CRCZarrDataset, MedicalImageAugmentation及各类工具函数。

### `dataset/augmentation.py`

医学影像数据增强管道，确保多模态数据（H&E, MIF）及其掩码/HV图的一致性变换

- `MedicalImageAugmentation` (class) - 增强类。初始化时从配置加载几何（翻转、旋转、缩放、随机resize）、光度（亮度、对比度）、染色（H&E专用）、噪声模糊及Cutout参数。__call__方法对输入的所有张量（图像、掩码、HV图）应用统一的随机变换，保持空间对齐。

### `dataset/dataset.py`

核心数据集类，处理多模态Zarr数据的加载、索引构建及样本检索

- `CRCZarrDataset` (class) - 继承自torch.utils.data.Dataset。__init__构建patch索引，根据样本名（如CRC01, pannuke_train）映射到对应的Zarr基路径。__getitem__加载H&E（3通道）和MIF（2通道）图像、4种掩码（核/细胞）及生成的HV图，若为训练模式则应用增强。
- `_get_zarr_path` (method) - 根据样本名前缀（如'tissuenet', 'pannuke', 'crc'）动态返回对应的Zarr数据基路径，支持多数据集混合。

### `dataset/hv_generator.py`

HV图生成器，使用PanNuke算法将实例分割掩码转换为水平-垂直梯度图

- `generate_hv_map_pannuke` (function) - 核心HV图生成函数。对每个实例计算质心，在边界框内创建坐标网格，并分别对正负方向进行归一化（-1到1），生成(2, H, W)的梯度图，比简单的质心法更精确。
- `batch_generate_hv_maps` (function) - 批量生成HV图，优化多实例处理效率。

### `dataset/utils.py`

辅助工具函数，用于内存检查、Zarr结构验证、批次统计及可视化

- `validate_zarr_structure` (function) - 验证指定目录下所有样本的Zarr文件结构是否完整（包含he/mif的images, nuclei_masks, cell_masks），返回有效和无效样本列表。
- `print_batch_statistics` (function) - 打印批次张量的形状、数据类型及统计信息，用于调试。
- `check_memory_available` (function) - 检查系统可用内存是否满足指定GB数，防止加载大数据集时内存溢出。

## Key Concepts

- **Zarr多模态存储**: 数据以Zarr格式存储，分离H&E和MIF模态，每个模态包含图像和两种掩码（核、细胞），支持高效分块读取。
- **HV图 (水平-垂直梯度图)**: 一种将实例分割掩码转换为连续梯度场的表示方法，用于替代传统的距离变换，能更精确地指导分割网络定位实例边界。
- **多数据集混合索引**: 通过样本名前缀（如pannuke_train, crc01）自动映射到不同的Zarr基路径，实现多个癌症数据集的无缝混合训练。
- **一致性增强**: 对H&E图像、MIF图像、所有掩码及HV图应用相同的几何变换（旋转、翻转、缩放），确保多模态数据在空间上严格对齐。

## Internal Relationships

- `dataset/dataset.py` → `dataset/config.py`: CRCZarrDataset依赖Config对象获取数据路径、增强参数及缓存设置。
- `dataset/dataset.py` → `dataset/hv_generator.py`: 在__getitem__中调用batch_generate_hv_maps实时生成HV图，或加载预生成的HV图。
- `dataset/dataset.py` → `dataset/augmentation.py`: 当training=True且启用增强时，实例化MedicalImageAugmentation对样本进行变换。
- `dataset/__init__.py` → `dataset/dataset.py`: __init__导入并公开CRCZarrDataset及create_dataloaders等核心类。
- `dataset/utils.py` → `dataset/dataset.py`: 提供validate_zarr_structure用于在构建Dataset前验证数据完整性。
