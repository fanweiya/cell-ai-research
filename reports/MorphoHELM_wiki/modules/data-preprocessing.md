# data-preprocessing

> 对细胞形态学基准测试的聚合特征数据进行标准化、降维和稳健化处理

该模块负责将原始细胞形态学特征（parquet格式）按照特定配置进行预处理流水线操作。核心流程包括：按板（plate）或批次（batch）进行中心化和缩放（CenterScale）、主成分分析（PCA）、基于中位数绝对偏差（MAD）的稳健化，以及可选的球形化（Spherize）。配置通过YAML文件定义，支持多种处理配置文件（profiles）以适应不同实验设计（如是否使用对照、PCA降维维度等）。代码针对性能进行了优化，使用NumPy直接替代了部分pycytominer功能以提升速度。

## Files

### `data-preprocessing/configs/normalize_splits.yaml`

定义预处理流水线的配置文件，包括路径设置、处理配置文件（profiles）和数据分割（splits）信息

- `profiles` (configuration) - 包含多种预设处理流程，如CSAll_Plate__PCA64__MADCtrl_Plate__NoSph，每个流程定义了中心缩放、PCA、MAD和球形化的具体参数
- `splits` (configuration) - 定义不同数据集分割（如cpg-crispr, bbbc036）的元数据路径和对照列标识
- `execution` (configuration) - 指定执行模式（local或amlt）

### `data-preprocessing/src/normalize_splits.py`

主入口脚本，解析配置并协调对多个数据集分割执行标准化流程

- `resolve_profile` (function) - 从配置和默认配置中合并并解析指定的处理配置文件，进行有效性验证
- `_root` (function) - 根据执行模式（local/amlt）解析配置中的根路径
- `parse_list` (function) - 解析命令行参数中的列表值

### `data-preprocessing/src/normalize_utils.py`

提供核心标准化算法的底层实现，包含PCA、中心缩放、MAD稳健化和球形化

- `embed_by_pca` (function) - 对特征矩阵执行主成分分析，返回降维后的float32数组
- `centerscale_by_plate` (function) - 按板对特征进行中心化和缩放，支持基于所有样本或仅基于对照组计算均值和标准差
- `_mad_robustize_plate` (function) - 对单个板执行MAD稳健化，将特征值转换为相对于对照组中位数的偏差
- `_build_plate_indices` (function) - 预构建每块板的行索引和对照组索引，避免重复的布尔掩码操作以提升性能

## Key Concepts

- **处理配置文件 (Profiles)**: 预定义的标准化参数组合，控制是否启用中心缩放、PCA降维维度、MAD作用范围以及是否进行球形化，以适应不同的实验设计需求
- **中心缩放 (CenterScale)**: 将特征转换为均值为0、标准差为1的分布。可选择基于所有样本（去除板效应）或仅基于对照组（计算相对于未处理基线的偏差）
- **MAD稳健化**: 使用中位数绝对偏差（Median Absolute Deviation）替代标准差进行缩放，对异常值更不敏感，通常基于对照组计算
- **球形化 (Spherize)**: 一种数据变换技术，旨在使特征分布更接近球形，通常用于改善后续机器学习模型的性能

## Internal Relationships

- `normalize_splits.py` → `normalize_utils.py`: normalize_splits.py 导入 normalize_utils.py 中的函数来执行具体的标准化计算
- `normalize_splits.py` → `configs/normalize_splits.yaml`: normalize_splits.py 读取并解析 normalize_splits.yaml 配置来确定处理流程和路径
