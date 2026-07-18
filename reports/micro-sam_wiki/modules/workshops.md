# workshops

> 提供用于micro-sam工作坊的教程文档、数据下载脚本和模型下载脚本

该模块包含针对EPFL 2026、I2K 2024和TIM 2025三个工作坊的完整准备材料。每个工作坊子目录包含README教程文档、用于下载示例数据集和预计算嵌入的脚本、以及用于微调SAM模型的脚本。这些文件共同确保参与者能够在工作坊前安装软件、下载必要的数据和模型，并快速开始交互式分割和自动分割的练习。

## Files

### `workshops/epfl_2026/README.md`

EPFL 2026工作坊的教程文档，包含安装指南、模型下载步骤和四个示例应用说明

### `workshops/i2k_2024/README.md`

I2K 2024工作坊的教程文档，涵盖线下和线上工作坊的准备步骤

### `workshops/tim_2025/README.md`

TIM 2025工作坊的教程文档，包含详细的安装说明和三个小时的议程

### `workshops/epfl_2026/download_datasets.py`

下载工作坊所需示例数据集的脚本，支持细胞、3D细胞核、体积EM和HPA数据集

- `_download_sample_data` (function) - 从URL下载并解压数据集
- `_get_cells_sample_data_paths` (function) - 获取2D细胞分割数据集路径
- `_get_nuclei_3d_data_paths` (function) - 获取3D细胞核分割数据集路径
- `_get_volume_em_data_paths` (function) - 获取体积EM分割数据集路径
- `_get_hpa_data_paths` (function) - 获取HPA数据集路径
- `_get_dataset_paths` (function) - 根据数据集名称返回路径并可选下载

### `workshops/i2k_2024/download_datasets.py`

I2K 2024版本的数据下载脚本，支持owncloud和Google Drive两种下载源

- `_download_sample_data` (function) - 支持owncloud和drive的下载解压
- `_get_cells_sample_data_paths` (function) - 获取细胞数据集路径
- `_get_hpa_data_paths` (function) - 获取HPA数据集路径
- `_get_nuclei_3d_data_paths` (function) - 获取3D细胞核数据集路径
- `_get_volume_em_data_paths` (function) - 获取体积EM数据集路径
- `_get_dataset_paths` (function) - 根据数据集名称和下载器返回路径

### `workshops/tim_2025/download_datasets.py`

TIM 2025版本的数据下载脚本，与I2K版本类似但针对TIM工作坊优化

- `_download_sample_data` (function) - 下载并解压样本数据
- `_get_cells_sample_data_paths` (function) - 获取细胞数据集路径
- `_get_hpa_data_paths` (function) - 获取HPA数据集路径
- `_get_nuclei_3d_data_paths` (function) - 获取3D细胞核数据集路径
- `_get_volume_em_data_paths` (function) - 获取体积EM数据集路径
- `_get_dataset_paths` (function) - 返回数据集路径

### `workshops/epfl_2026/download_embeddings.py`

下载预计算图像嵌入的脚本，用于3D交互式分割

- `_download_embeddings` (function) - 下载并解压指定数据集的嵌入文件
- `main` (function) - 解析命令行参数并调用下载函数

### `workshops/i2k_2024/download_embeddings.py`

I2K 2024版本的嵌入下载脚本，支持owncloud和Google Drive

- `_download_embeddings` (function) - 根据下载器选择下载嵌入
- `main` (function) - 解析参数并执行下载

### `workshops/tim_2025/download_embeddings.py`

TIM 2025版本的嵌入下载脚本，与I2K版本结构相同

- `_download_embeddings` (function) - 下载嵌入文件
- `main` (function) - 命令行入口

### `workshops/epfl_2026/download_models.py`

下载micro-sam工作模型（vit_b_lm和vit_b_em_organelles）的脚本

- `main` (function) - 调用get_sam_model下载两个模型

### `workshops/i2k_2024/download_models.py`

I2K 2024版本的模型下载脚本，下载三个模型

- `main` (function) - 下载vit_b、vit_b_lm和vit_b_em_organelles模型

### `workshops/tim_2025/download_models.py`

TIM 2025版本的模型下载脚本，下载三个模型

- `main` (function) - 下载三个SAM模型

### `workshops/epfl_2026/finetune_sam.py`

使用HPA数据集微调SAM模型的示例脚本

- `load_images_and_labels` (function) - 加载图像和标签并预处理
- `get_dataloaders` (function) - 创建训练和验证数据加载器

### `workshops/i2k_2024/finetune_sam.py`

I2K 2024版本的微调脚本，包含数据下载、验证和预处理功能

- `download_dataset` (function) - 下载HPA数据集
- `verify_inputs` (function) - 验证输入数据格式
- `preprocess_inputs` (function) - 预处理图像数据
- `visualize_inputs` (function) - 可视化图像和标签

### `workshops/tim_2025/finetune_sam.py`

TIM 2025版本的微调脚本，与I2K版本功能相同

- `download_dataset` (function) - 下载数据集
- `verify_inputs` (function) - 验证输入
- `preprocess_inputs` (function) - 预处理输入
- `visualize_inputs` (function) - 可视化输入

### `workshops/tim_2025/check_omero_mask.py`

从OMERO服务器加载分割掩码并在napari中可视化的脚本

- `load_masks` (function) - 从OMERO加载ROI并转换为分割掩码
- `main` (function) - 连接OMERO并可视化结果

### `workshops/tim_2025/omero_utils.py`

OMERO连接和上传工具的实用函数库

- `connect_to_omero` (function) - 连接到OMERO服务器
- `upload_lucchi` (function) - 上传Lucchi数据集到OMERO
- `upload_livecell` (function) - 上传LiveCell数据到OMERO
- `omero_credential_parser` (function) - 解析OMERO凭据参数
- `create_dataset` (function) - 在OMERO中创建新数据集

### `workshops/tim_2025/upload_segmentation_to_omero.py`

将分割结果上传到OMERO服务器的脚本，支持多边形和掩码格式

- `upload_as_polygon` (function) - 将分割作为多边形上传
- `upload_as_mask` (function) - 将分割作为二值掩码上传
- `upload_segmentation` (function) - 上传整个分割结果

## Key Concepts

- **预计算嵌入**: 为3D交互式分割预先计算的图像特征嵌入，避免在CPU上实时计算的高耗时
- **SAM模型类型**: workshops中使用的三种SAM变体：vit_b（通用）、vit_b_lm（光显微镜）、vit_b_em_organelles（电子显微镜细胞器）
- **数据下载器**: 支持从owncloud或Google Drive下载数据，适应不同网络环境
- **OMERO集成**: TIM 2025工作坊特有的功能，用于在OMERO服务器上传和加载分割结果
- **微调流程**: 使用HPA数据集展示如何微调SAM模型以适应特定显微镜图像分割任务

## Internal Relationships

- `workshops/epfl_2026/download_models.py` → `micro_sam.util`: 调用get_sam_model下载模型
- `workshops/epfl_2026/download_embeddings.py` → `torch_em.data.datasets.util`: 使用下载和解压工具
- `workshops/epfl_2026/finetune_sam.py` → `micro_sam.training`: 使用训练模块创建数据加载器
- `workshops/i2k_2024/download_datasets.py` → `workshops/i2k_2024/download_embeddings.py`: 两者配合使用，先下载数据再下载嵌入
- `workshops/tim_2025/check_omero_mask.py` → `workshops/tim_2025/omero_utils.py`: 使用omero_utils中的连接函数
- `workshops/tim_2025/upload_segmentation_to_omero.py` → `workshops/tim_2025/omero_utils.py`: 使用omero_utils中的连接和凭证解析函数
