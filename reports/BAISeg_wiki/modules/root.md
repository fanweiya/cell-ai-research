# root

> 实现基于符号距离函数（SDF）和边界感知损失显微镜图像细胞实例分割的完整训练与推理框架。

该项目是一个基于PyTorch Lightning的模块化实现，用于在显微镜图像中分割单个细胞。核心思想是预测符号距离函数（SDF）而非二值掩码，通过可学习的Sigmoid映射将SDF转换为概率图和软边界，并使用改进的Hausdorff距离（MHD）损失来优化边界对齐和相邻细胞的分离。框架支持2D、2.5D和3D数据，通过YAML配置文件管理实验，并集成Wandb进行日志记录。

## Files

### `README.md`

项目文档，包含概述、安装、使用指南和引用信息。

### `requirements.txt`

定义项目依赖包及其版本。

### `LICENSE`

项目的MIT开源许可证。

### `dataset.py`

定义数据加载模块，处理显微镜图像和分割掩码的读取、增强及预处理。

- `CropWithVoxelThreshold` (class) - 自定义Transform，尝试随机裁剪直到分割掩码中有效体素超过阈值，确保裁剪区域包含足够细胞。
- `SliceWiseNorm` (class) - 对3D图像的每个切片进行独立的均值-方差归一化。
- `CELL3DDataModule` (class) - PyTorch Lightning DataModule，管理训练、验证和测试数据集的加载、批处理及数据增强流程。

### `train_unet.py`

主训练脚本，负责解析配置、初始化模型、启动训练循环或执行推理。

- `ModelCheckpointSaveLast` (class) - 自定义Callback，在训练结束时保存最后一个检查点，支持版本控制。
- `init_logger` (function) - 初始化Wandb日志记录器，将配置参数同步到实验元数据。
- `get_criterion` (function) - 根据配置文件动态实例化损失函数列表，支持自定义损失。

### `unet2d.yml`

YAML配置文件，定义数据路径、模型架构、损失权重、优化器及训练超参数。

### `utils.py`

提供通用工具函数，包括自定义损失、张量转换、形态学操作及后处理。

- `FocalBCEWithLogits` (class) - 实现Focal Loss与BCE的组合，用于解决类别不平衡问题。
- `convert_3d_to_2_5d` (function) - 将3D体积数据转换为2.5D表示（当前切片+前后邻域），以便在2D网络上处理3D数据。
- `convert_2_5d_to_3d` (function) - 将2.5D处理后的结果重组回3D张量。
- `erode` (function) - 使用深度卷积实现张量的腐蚀操作。
- `dilate` (function) - 使用深度卷积实现张量的膨胀操作。

## Key Concepts

- **符号距离函数 (SDF)**: 用连续函数表示细胞轮廓，正值表示外部，负值表示内部，零值表示边界。相比二值掩码，SDF能提供更平滑的几何表示，利于优化边界。
- **边界感知 MHD 损失**: 改进的Hausdorff距离损失，包含左向（LMHD）和右向（RMHD）项，直接优化预测边界与真实边界之间的对齐，特别有助于分离接触或重叠的细胞。
- **2.5D 处理**: 一种在2D网络上处理3D数据的技术，将当前切片与其上下邻域切片组合成3通道输入，在保持计算效率的同时利用部分上下文信息。
- **PyTorch Lightning 模块化**: 使用LightningDataModule管理数据，Callback管理训练逻辑（如检查点），实现训练流程与业务逻辑解耦。

## Internal Relationships

- `train_unet.py` → `dataset.py`: train_unet.py 导入 CELL2DDataModule 和 CELL3DDataModule 以构建数据加载器。
- `train_unet.py` → `utils.py`: train_unet.py 导入 FocalBCEWithLogits 作为自定义损失，并可能使用其他工具函数。
- `train_unet.py` → `models/unet.py`: train_unet.py 导入 Unet2dWrap, Unet2_5dWrap, Unet3dWrap 以实例化分割模型。
- `dataset.py` → `utils.py`: dataset.py 可能依赖 utils.py 中的形态学或转换函数进行数据预处理。
- `train_unet.py` → `unet2d.yml`: train_unet.py 读取 unet2d.yml 获取所有超参数和配置信息。
