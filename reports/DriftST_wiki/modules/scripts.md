# scripts

> 提供从H&E组织切片推断空间转录组的一站式训练与预处理脚本

该模块包含三个核心Shell脚本，用于自动化执行DriftST模型的数据预处理和训练流程。脚本封装了参数配置、数据集路径管理、模型训练调用及日志记录，支持Spot-level（HEST风格）和Cell-level（Xenium）两种数据格式，并集成WandB实验跟踪。

## Files

### `scripts/run_spot_level_train.sh`

处理并训练基于Spot-level的HEST风格数据集（如her2st, prad, kidney）

- `main` (shell script) - 解析命令行参数（数据集、fold、跳过预处理等），设置环境变量，调用preprocess_spot_level.py进行数据预处理，然后启动train.py进行模型训练。支持多数据集配置和WandB离线模式。

### `scripts/run_xenium_cell_level_preprocess.sh`

准备默认的Xenium乳腺癌处理数据集

- `main` (shell script) - 执行两个Python脚本：select_xenium_cell_level_genes.py用于选择基因列表，preprocess_xenium_cell_level.py用于将原始Xenium数据转换为模型输入格式。支持指定滑片（slides）和测试滑片（test_slide）。

### `scripts/run_xenium_cell_level_train.sh`

在Xenium乳腺癌处理数据集上训练DriftST模型

- `main` (shell script) - 循环遍历指定的folds，为每个fold创建实验目录，计算空间可变基因（SVG）排名（基于Moran's I），构建训练参数列表并调用train.py。支持邻居信息、快照保存、WandB配置等高级选项。

### `scripts/run_xenium_coad_cell_level_train.sh`

在Xenium COAD数据集上训练DriftST模型

- `main` (shell script) - 设置特定环境变量（OUTPUT_DIR, EXP_DIR, SVG_SLIDE）后，直接调用run_xenium_cell_level_train.sh脚本，复用其训练逻辑以适配COAD数据集。

## Key Concepts

- **Fold交叉验证**: 脚本通过FOLD参数支持K折交叉验证，从splits.json中读取测试滑片，确保模型在不同数据划分上的泛化能力。
- **WandB实验跟踪**: 集成Weights & Biases，支持在线/离线模式，自动记录训练指标和超参数配置。
- **空间可变基因（SVG）**: 基于Moran's I统计量计算基因的空间表达模式，用于筛选具有空间信息的基因作为模型输入。
- **DriftST模型训练**: 核心训练流程，包含门控机制（use_gate）、漂移步长（drift_step）、银行大小（bank_size）等超参数，用于从H&E图像推断空间转录组。

## Internal Relationships

- `scripts/run_spot_level_train.sh` → `process/preprocess_spot_level.py`: run_spot_level_train.sh调用preprocess_spot_level.py执行Spot-level数据的预处理步骤。
- `scripts/run_spot_level_train.sh` → `train.py`: run_spot_level_train.sh最终调用train.py执行模型训练任务。
- `scripts/run_xenium_cell_level_preprocess.sh` → `process/select_xenium_cell_level_genes.py`: run_xenium_cell_level_preprocess.sh调用select_xenium_cell_level_genes.py生成基因列表。
- `scripts/run_xenium_cell_level_preprocess.sh` → `process/preprocess_xenium_cell_level.py`: run_xenium_cell_level_preprocess.sh调用preprocess_xenium_cell_level.py完成Xenium细胞级数据的预处理。
- `scripts/run_xenium_cell_level_train.sh` → `process/compute_spatial_variable_genes.py`: run_xenium_cell_level_train.sh在训练前调用compute_spatial_variable_genes.py计算空间可变基因排名。
- `scripts/run_xenium_cell_level_train.sh` → `train.py`: run_xenium_cell_level_train.sh循环调用train.py对每个fold进行训练。
- `scripts/run_xenium_coad_cell_level_train.sh` → `scripts/run_xenium_cell_level_train.sh`: run_xenium_coad_cell_level_train.sh作为封装层，调用run_xenium_cell_level_train.sh处理COAD数据集。
