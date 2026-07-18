# notebooks

> 提供基于Vision Transformer的病理细胞分割框架的数据预处理、推理、基准测试和评估的交互式实验环境。

该模块包含一系列Jupyter Notebook，用于支持Vitamin-P框架的完整工作流程。主要功能包括：Xenium和CRC数据集的预处理与Zarr格式转换、模型推理（含合成MIF生成）、与Cellpose-SAM和CellSAM等基准方法的对比评估、实例分割指标计算、以及性能基准测试。Notebooks通过配置YAML文件管理数据加载，利用DINOv2作为骨干网络，并支持在GPU上运行大规模WSI推理。

## Files

### `notebooks/Xenium/Untitled.ipynb`

处理Xenium细胞分割结果，将大型GeoJSON文件分割为多个部分以便后续处理。

- `split_geojson` (function) - 读取GeoJSON文件并将其特征分割为5个部分，保存为独立的GeoJSON文件。

### `notebooks/Xenium/inference.ipynb`

配置环境并初始化VitaminPFlex模型，用于Xenium数据的推理。

- `VitaminPFlex` (class) - 初始化具有共享编码器和4个独立解码器的Flex架构模型。
- `DINOv2Backbone` (class) - 使用DINOv2 Vision Transformer作为骨干网络提取特征。

### `notebooks/benchmarks/CellSAM/cellsam_zeroshot.ipynb`

在CRC数据集上对CellSAM模型进行零样本推理和评估。

- `CRC Dataset Package` (module) - 加载CRC数据集配置，包括数据拆分、增强和HV图生成设置。

### `notebooks/benchmarks/CellposeSAM/cellposesam_zeroshot.ipynb`

在CRC数据集上对Cellpose-SAM模型进行零样本推理和评估。

- `CRC Dataset Package` (module) - 加载CRC数据集配置。

### `notebooks/benchmarks/CellposeSAM/vitaminp-cellposesam.ipynb`

加载Cellpose-SAM模型并评估其在24个案例上的分割性能，计算Dice分数。

- `cellpose.models` (module) - 加载和运行Cellpose-SAM模型。

### `notebooks/benchmarks/Pathologist/cellposesam.ipynb`

安装和验证Cellpose依赖项，可能用于病理学家评估。

### `notebooks/benchmarks/Pathologist/cellsam.ipynb`

安装和验证CellSAM依赖项，并加载模型进行推理。

- `cellSAM.get_model` (function) - 获取CellSAM模型实例。
- `cellSAM.segment_cellular_image` (function) - 对细胞图像执行分割。

### `notebooks/benchmarks/vitamin-p/flex-TTA.ipynb`

在PanNuke数据集上对VitaminPFlex模型进行测试时增强（TTA）评估。

- `CRC Dataset Package` (module) - 加载数据集配置，包括数据拆分和补丁索引构建。

### `notebooks/convert-zarr-png.ipynb`

将Zarr格式存储的图像数据（HE或MIF模态）转换为PNG图像以便可视化。

- `zarr.open` (function) - 打开Zarr数组并读取数据块。
- `PIL.Image` (class) - 将numpy数组转换为图像并保存为PNG。

### `notebooks/data_preprocessing/TNBC.ipynb`

将TNBC数据集切片转换为Zarr格式，并按训练/验证/测试集进行拆分。

- `Zarr Data Conversion` (process) - 将图像切片和掩码转换为Zarr数组，并保存为tnbc_train/val/test目录。

### `notebooks/data_preprocessing/Xenium_CRC.ipynb`

验证Xenium数据集文件夹结构，确保每个样本包含HE和MIF子文件夹及掩码。

- `verify_folder_structure` (function) - 检查根目录下样本文件夹的完整性。

### `notebooks/data_preprocessing/dataset.ipynb`

加载和索引多个数据集（包括CRC、Xenium等）以构建训练、验证和测试加载器。

- `CRC Dataset Package` (module) - 配置和创建多数据集加载器，构建补丁索引。

### `notebooks/figures/Figure_2f.ipynb`

生成用于论文图2f的可视化结果，可能涉及分割掩码的叠加显示。

### `notebooks/inference-Syn.ipynb`

执行WSI推理，使用VitaminPDual模型生成合成MIF图像并进行细胞分割。

- `VitaminPDual` (class) - 双模态模型，包含H&E和MIF编码器，支持合成MIF生成。
- `WSIPredictor` (class) - 初始化预测器，处理WSI切片提取、重叠推理和结果聚合。

### `notebooks/metrics-Instance.ipynb`

安装依赖项并计算实例分割指标（如Dice、AJI、PQ等）。

### `notebooks/metricsSyn.ipynb`

安装依赖项并计算合成MIF生成相关的指标。

### `notebooks/time_benchmarks/cellposesam.ipynb`

对Cellpose-SAM模型进行时间性能基准测试。

### `notebooks/time_benchmarks/cellsam.ipynb`

对CellSAM模型进行时间性能基准测试。

- `cellSAM.get_model` (function) - 获取CellSAM模型。
- `cellSAM.segment_cellular_image` (function) - 执行分割并测量时间。

### `notebooks/time_benchmarks/vitamin-p-dual.ipynb`

VitaminPDual模型的时间基准测试（当前为空）。

### `notebooks/time_benchmarks/vitaminp-flex.ipynb`

对VitaminPFlex模型进行时间基准测试，包含样本提取功能。

- `extract_region_from_ome_tiff` (function) - 从OME-TIFF文件中提取指定区域并保存为TIFF。

### `notebooks/wsi.ipynb`

安装依赖项并执行WSI相关的处理任务。

## Key Concepts

- **VitaminPFlex**: 一种基于Vision Transformer的分割架构，采用共享编码器和多个独立解码器的设计，适用于多任务或多模态病理图像分割。
- **VitaminPDual**: 双模态模型，包含H&E和MIF两个编码器，能够生成合成MIF图像，用于在仅有H&E数据的情况下进行细胞分割。
- **Zarr数据格式**: 用于高效存储和访问大规模病理图像及其掩码的数组格式，支持分块读取和并行处理。
- **WSI推理**: 对全切片图像进行分块处理，通过重叠窗口预测并聚合结果，以处理超出显存容量的大尺寸图像。
- **基准对比**: 将Vitamin-P框架与Cellpose-SAM、CellSAM等现有方法进行零样本或微调后的性能对比，评估Dice、AJI、PQ等指标。

## Internal Relationships

- `notebooks/data_preprocessing/dataset.ipynb` → `notebooks/benchmarks/vitamin-p/flex-TTA.ipynb`: dataset.ipynb构建的数据加载器被flex-TTA.ipynb用于模型评估。
- `notebooks/Xenium/inference.ipynb` → `notebooks/data_preprocessing/Xenium_CRC.ipynb`: inference.ipynb依赖Xenium_CRC.ipynb验证的数据结构。
- `notebooks/inference-Syn.ipynb` → `notebooks/data_preprocessing/dataset.ipynb`: inference-Syn.ipynb可能使用dataset.ipynb中定义的数据配置。
- `notebooks/benchmarks/CellposeSAM/vitaminp-cellposesam.ipynb` → `notebooks/metrics-Instance.ipynb`: vitaminp-cellposesam.ipynb的计算结果可能需要metrics-Instance.ipynb中的指标进行汇总。
