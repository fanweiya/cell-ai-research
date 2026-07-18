# data_installation

> 提供公共Cell Painting数据集的下载、去光照校正及元数据管理功能

该模块负责从S3、HTTP等来源下载Cell Painting原始图像数据，应用特定的光照校正算法将其转换为uint8格式的PNG图像，并管理相关元数据。它支持BBBC036和CPG0016两个主要数据集，处理多通道图像，并包含重试机制和原子写入操作以确保下载可靠性。

## Files

### `data_installation/cellpainting_io.py`

提供通用的IO辅助函数，用于处理S3对象存储、URL下载、压缩包提取及字节流操作

- `unsigned_s3_client` (function) - 创建一个无需签名的S3客户端，用于访问公开S3桶
- `parse_s3_uri` (function) - 解析s3:// URI字符串，返回桶名和键名
- `retry` (function) - 带指数退避的重试装饰器，用于处理网络波动导致的操作失败
- `read_s3_bytes` (function) - 从S3 URI读取二进制数据，自动处理重试
- `download_url` (function) - 通过原子临时文件方式下载URL内容，防止损坏
- `extract_tar_members` (function) - 解压tar文件，支持按名称过滤成员
- `read_zip_member` (function) - 读取zip文件中的指定成员内容
- `list_zip_files` (function) - 列出zip文件中符合后缀要求的文件列表

### `data_installation/illumination.py`

提供图像去光照校正的核心算法和工具函数

- `image_bytes_to_array` (function) - 将图像字节流解码为NumPy数组
- `to_uint8` (function) - 将任意数值类型的图像数组转换为uint8格式，处理归一化和截断
- `_divide_by_illumination` (function) - 执行基础的光照校正除法操作，避免除零
- `correct_cpg0016_to_uint8` (function) - 应用CPG0016数据集特定的光照校正和对比度拉伸
- `correct_bbbc036_to_uint8` (function) - 应用BBBC036数据集特定的光照校正和对比度拉伸
- `save_uint8_png` (function) - 将uint8数组保存为PNG图像文件

### `data_installation/manifests.py`

定义数据集的源配置、通道映射和URL模板

- `CPG_METADATA_REPO_URL` (constant) - CPG0016元数据仓库的Git URL
- `CPG_LOAD_DATA_TEMPLATE` (constant) - CPG0016数据集加载数据的S3路径模板
- `CpgChannel` (class) - 数据类，定义CPG0016通道名称、输出索引及原始/光照URL列名
- `CPG_CHANNELS` (constant) - CPG0016的5个通道配置元组
- `Bbbc036Channel` (class) - 数据类，定义BBBC036通道名称及对应的光照图像名称
- `BBBC036_CHANNELS` (constant) - BBBC036的5个通道配置元组
- `BBBC036_IMAGE_URL_TEMPLATE` (constant) - BBBC036图像ZIP文件的HTTP URL模板
- `BBBC036_ILLUM_URL_TEMPLATE` (constant) - BBBC036光照校正tar.gz文件的URL模板
- `BBBC036_PLATES` (constant) - BBBC036数据集所有板卡编号列表

### `data_installation/download_illum_corrected.py`

主脚本，协调下载流程，处理元数据并生成去光照校正后的PNG图像

- `_ensure_cpg_metadata_repo` (function) - 确保CPG元数据仓库已克隆到本地缓存
- `_cache_cpg_benchmark_metadata` (function) - 将公共JUMP元数据文件复制到本地安装缓存
- `_select_cpg_plates` (function) - 根据命令行参数或文件选择要处理的板卡列表
- `_load_cpg_plate_table` (function) - 加载特定板卡的元数据表格，包含光照校正数据路径

## Key Concepts

- **原子下载**: 使用临时文件下载，完成后再重命名，避免部分下载导致文件损坏
- **光照校正**: 将原始图像除以光照图以消除照明不均匀，不同数据集采用不同的后处理策略
- **元数据缓存**: 将远程元数据克隆并缓存到本地，减少重复下载和网络依赖
- **重试机制**: 对网络操作实施指数退避重试，提高在弱网环境下的成功率

## Internal Relationships

- `download_illum_corrected.py` → `cellpainting_io.py`: 导入下载、解压和S3读取等IO工具函数
- `download_illum_corrected.py` → `illumination.py`: 导入光照校正算法和图像保存函数
- `download_illum_corrected.py` → `manifests.py`: 导入数据集配置、URL模板和通道定义
- `cellpainting_io.py` → `illumination.py`: 无直接导入，但通过字节流处理间接协作
