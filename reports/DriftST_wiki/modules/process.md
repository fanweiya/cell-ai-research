# process

> 提供从H&E组织切片推断空间转录组的一站式数据预处理、特征选择与空间变量基因计算流程

该模块负责处理两种主要数据格式：HEST风格的spot-level数据和Xenium风格的cell-level数据。核心流程包括：1) 从原始转录本parquet文件重建细胞-基因计数矩阵并提取H&E图像特征；2) 筛选有效基因（去除对照）和高度可变基因(HVGs)；3) 计算空间自相关性(Moran's I)以识别空间变量基因(SVGs)；4) 生成空间交叉验证分割方案。所有处理后的数据均标准化为DriftST框架所需的AnnData格式，包含基因表达矩阵、空间坐标和元数据。

## Files

### `process/compute_spatial_variable_genes.py`

基于Moran's I统计量对空间变量基因进行排序

- `main` (function) - 加载处理后的基因表达数据，构建空间邻域图，计算Moran's I，输出SVG排序结果
- `parse_args` (function) - 解析命令行参数，包括数据目录、slide ID和邻居数量

### `process/generate_xenium_cell_level_splits.py`

为单个Xenium slide生成空间5折交叉验证分割

- `main` (function) - 按X或Y坐标将细胞划分为水平或垂直条带，生成训练/测试集分割方案
- `parse_args` (function) - 解析数据目录、slide ID、折叠数和分割轴参数

### `process/preprocess_spot_level.py`

预处理HEST风格的spot-level数据集以适配DriftST

- `load_one_slide` (function) - 读取单个slide的h5ad文件，筛选目标基因，填充缺失基因，提取空间坐标和spot直径
- `load_gene_list` (function) - 加载目标基因列表

### `process/preprocess_xenium_cell_level.py`

预处理Xenium cell-level数据以适配DriftST

- `load_one_slide` (function) - 从转录本parquet文件重建细胞-基因计数矩阵，过滤低质量转录本，提取UNI2+CONCH H&E特征，构建空间邻域图
- `load_gene_list` (function) - 加载目标基因列表

### `process/select_xenium_cell_level_genes.py`

从Xenium转录本文件中提取有效面板基因

- `is_control` (function) - 根据正则表达式模式识别并排除对照探针
- `main` (function) - 扫描所有parquet文件，收集唯一特征名，过滤对照，输出有效基因列表

### `process/select_xenium_cell_level_hvg.py`

从单个Xenium转录本文件中选择高度可变基因

- `main` (function) - 读取转录本数据，过滤低质量转录本和细胞，构建计数矩阵，使用Seurat v3方法选择HVGs

## Key Concepts

- **空间变量基因 (SVGs)**: 通过Moran's I统计量识别在空间上具有显著自相关性的基因，这些基因的表达模式与组织空间结构相关
- **Xenium转录本重建**: 从原始转录本parquet文件中聚合细胞ID和基因表达计数，构建细胞-基因表达矩阵
- **空间交叉验证**: 按空间坐标（X或Y轴）将细胞划分为连续条带作为测试集，确保模型评估反映空间泛化能力
- **DriftST数据格式**: 标准化的AnnData格式，包含基因表达矩阵、空间坐标(obsm['spatial'])和元数据(obs)

## Internal Relationships

- `process/preprocess_xenium_cell_level.py` → `process/select_xenium_cell_level_genes.py`: preprocess_xenium_cell_level.py依赖select_xenium_cell_level_genes.py生成的基因列表作为输入
- `process/select_xenium_cell_level_hvg.py` → `process/select_xenium_cell_level_genes.py`: select_xenium_cell_level_hvg.py使用select_xenium_cell_level_genes.py输出的候选基因列表进行HVG筛选
- `process/compute_spatial_variable_genes.py` → `process/preprocess_spot_level.py`: compute_spatial_variable_genes.py处理preprocess_spot_level.py生成的标准化数据
- `process/generate_xenium_cell_level_splits.py` → `process/preprocess_xenium_cell_level.py`: generate_xenium_cell_level_splits.py利用preprocess_xenium_cell_level.py生成的元数据进行空间分割
