# configs

> 集中管理细胞形态学基准测试与特征提取流水线的所有配置参数、路径定义和运行模式。

该模块通过一系列YAML文件定义了从数据安装、预处理、推理、标准化到基准测试和图表生成的完整流水线配置。所有路径默认相对于仓库根目录解析，支持本地和AMLT远程环境切换。配置文件被其他Python脚本直接读取以驱动各个处理阶段，确保实验的可复现性和环境解耦。

## Files

### `configs/benchmarks.yaml`

定义基准测试的扫描配置，包括数据路径、模型列表、QC参数和富集分析设置。

- `profiles.default` (string) - 默认使用的标准化配置文件名称（CSAll_Plate__PCA64__MADCtrl_Plate__NoSph）。
- `models` (list) - 参与基准测试的模型列表，包括CellProfiler、Cloome、DINO、ResNet等。
- `enrichment` (dict) - 富集分析配置，控制是否运行CRISPR、CPG MoA和BBBC036 MoA分析。

### `configs/data_installation.yaml`

定义MorphoHELM数据安装的默认参数，包括输出根目录、处理工作数和归档策略。

- `cpg0016` (dict) - CPG0016数据集的安装配置，指定输出目录和工作线程数。
- `bbbc036` (dict) - BBBC036数据集的安装配置，包含原始数据解压路径和归档保留策略。

### `configs/inference_splits.yaml`

配置多数据集切片的推理参数，支持本地和AMLT两种执行模式，定义模型批大小和输出路径。

- `split_inference.splits` (dict) - 定义不同数据集切片（cpg-crispr, bbbc036等）的数据路径和元数据路径。
- `models` (dict) - 各推理模型（DINO, ResNet, OpenPhenom等）的启用状态、批大小和工作线程配置。
- `aggregation.output_root` (dict) - 推理结果聚合后的输出根目录，区分本地和AMLT环境。

### `configs/normalize_splits.yaml`

定义特征标准化流水线配置，包含多种标准化配置文件（Profile）和切片控制参数。

- `profiles` (dict) - 包含多种标准化策略，如CSAll_Plate__PCA64__MADCtrl_Plate__NoSph，定义中心化、PCA、MAD和球化参数。
- `splits` (dict) - 定义不同数据集切片的控制列、控制值及元数据路径。

### `configs/paper_graphs.yaml`

配置论文图表再生流程，整合基准测试、QC和富集分析的输出路径及生成选项。

- `normalization` (dict) - 定义默认标准化配置文件和附录配置文件列表。
- `exports` (dict) - 控制需要生成的图表类型，如QC热图、Jaccard指数、CRISPR数据库条形图等。

### `configs/pipeline.yaml`

定义整个MorphoHELM流水线的主顺序和默认配置文件映射。

- `stages` (list) - 流水线执行阶段顺序：数据安装、预处理、HuggingFace转换、推理、聚合、标准化、QC、基准测试、图表生成。
- `configs` (dict) - 将流水线阶段映射到具体的配置文件路径。

## Key Concepts

- **Profile-driven Normalization**: 通过normalize_splits.yaml定义多种标准化配置文件（如CSAll_Plate__PCA64__MADCtrl_Plate__NoSph），允许灵活组合中心化、PCA降维、MAD标准化和球化步骤。
- **Environment Abstraction**: 配置文件中通过local和amlt键区分本地与远程AMLT环境的路径，实现代码与环境的解耦。
- **Split-based Inference**: inference_splits.yaml支持对同一数据集的不同切片（如cpg-crispr, cpg-moa）分别进行推理，并聚合结果。
- **Config-driven Pipeline**: 整个流水线由pipeline.yaml编排，各阶段读取对应的YAML配置，确保实验流程的可复现性和参数集中管理。

## Internal Relationships

- `configs/pipeline.yaml` → `configs/inference_splits.yaml`: pipeline.yaml引用inference_splits.yaml作为推理阶段的配置源。
- `configs/pipeline.yaml` → `configs/normalize_splits.yaml`: pipeline.yaml引用normalize_splits.yaml作为标准化阶段的配置源。
- `configs/benchmarks.yaml` → `configs/normalize_splits.yaml`: benchmarks.yaml引用normalize_splits.yaml中的默认profile来运行基准测试。
- `configs/paper_graphs.yaml` → `configs/benchmarks.yaml`: paper_graphs.yaml复用benchmarks.yaml中的路径和QC配置以生成论文图表。
