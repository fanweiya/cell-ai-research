# monailabel-app

> 基于部分标注的交互式实例分割深度学习框架

该模块实现了ImPartial交互式分割应用，集成在Monai Label框架中。它支持使用部分标注（scribbles）进行细胞分割和阈值处理，通过混合损失函数（分割损失、重建损失、正则化损失）训练模型，并提供推理接口。核心功能包括数据加载、模型配置、训练流程和推理引擎。

## Files

### `api/main.py`

Monai Label应用的主入口，初始化Impartial应用并加载模型配置。

- `Impartial` (class) - 继承自MONAILabelApp，负责初始化数据源、推理任务和训练任务。
- `init_datastore` (method) - 返回LocalDatastore实例，管理图像和标注数据。
- `init_infers` (method) - 初始化推理任务字典，加载预训练模型。
- `init_trainers` (method) - 初始化训练任务字典，配置训练流程。

### `Impartial_classes.py`

定义ImPartial配置类，包含网络结构、训练参数和损失函数设置。

- `ImPartialConfig` (class) - 继承argparse.Namespace，存储所有超参数，如UNet深度、批量大小、损失权重等。

### `Impartial_dataloaders.py`

实现数据加载逻辑，包括补丁采样和盲点处理。

- `sample_patches` (function) - 从图像和标注中随机采样补丁，优先选择包含scribbles的区域。
- `compute_probability_map` (function) - 计算每个像素被采样的概率，基于scribbles分布。
- `random_crop` (function) - 根据概率图随机裁剪图像和标注补丁。
- `blind_spot_patch` (function) - 对输入图像应用盲点掩码，用于重建损失训练。

### `Impartial_functions.py`

提供损失计算和输出处理函数。

- `compute_impartial_losses` (function) - 计算混合损失，包括前景分割、背景分割、重建和正则化损失。
- `save_outputs` (function) - 将模型输出保存为PNG图像。

### `api/lib/configs/__init__.py`

定义不同通道数的配置类，继承自ImPartialConfig。

- `Vectra2Ch` (class) - 针对2通道Vectra数据集的配置。
- `Config_CH1` (class) - 1通道配置。
- `Config_CH2` (class) - 2通道配置。
- `Config_CH3` (class) - 3通道配置。

### `api/lib/configs/impartial.py`

实现TaskConfig接口，配置网络、推理和训练任务。

- `Impartial` (class) - TaskConfig实现，初始化UNet网络并返回推理和训练任务。
- `init` (method) - 设置标签、模型路径和network实例。
- `infer` (method) - 返回InferTask实例。
- `trainer` (method) - 返回TrainTask实例。

### `api/lib/infers/impartial.py`

实现推理引擎，处理图像加载、预处理、模型推理和后处理。

- `Impartial` (class) - 继承BasicInferTask，实现图像读取、补丁推理和结果聚合。
- `pre_transforms` (method) - 定义推理前的预处理步骤，如加载图像、归一化。
- `post_transforms` (method) - 定义推理后的后处理步骤，如输出解析、熵计算。
- `writer` (method) - 将推理结果写入ZIP文件。

### `api/lib/trainers/impartial.py`

实现训练引擎，管理数据预处理、训练循环和验证。

- `Impartial` (class) - 继承BasicTrainTask，实现训练和验证逻辑。
- `pre_process` (method) - 预处理数据列表，归一化图像并转换标注为scribbles。
- `train_pre_transforms` (method) - 训练前的增强变换，如盲点补丁、随机翻转。
- `loss_function` (method) - 返回ImpartialLoss实例，计算混合损失。

### `api/lib/transforms.py`

提供自定义Monai Transform类，用于数据增强和输出处理。

- `PercentileNormalization` (class) - 基于百分位的图像归一化变换。
- `SampleImage` (class) - 采样图像补丁的变换。
- `BlindSpotPatch` (class) - 应用盲点掩码的变换。
- `GetImpartialOutputs` (class) - 解析模型输出为任务特定的格式。

### `test.py`

测试脚本，批量推理并评估模型性能。

- `infer` (function) - 调用API对单张图像进行推理。
- `main` (function) - 遍历图像目录，批量推理并计算性能指标。

## Key Concepts

- **部分标注（Scribbles）**: 用户仅提供少量像素级标注（scribbles），模型通过重建和分割任务学习完整分割。
- **混合损失函数**: 结合分割损失（foreground/background）、重建损失和正则化损失，提升模型泛化能力。
- **补丁采样策略**: 优先采样包含scribbles的图像区域，加速收敛并提高标注效率。
- **盲点掩码（Blind Spot）**: 在重建任务中随机遮蔽部分像素，迫使模型学习上下文信息。
- **Monai Label集成**: 通过TaskConfig接口实现与Monai Label平台的无缝对接，支持交互式标注和模型训练。

## Internal Relationships

- `api/main.py` → `api/lib/configs/impartial.py`: main.py导入Impartial类并实例化应用。
- `api/lib/configs/impartial.py` → `api/lib/configs/__init__.py`: impartial.py导入Config_CH1/2/3等配置类。
- `api/lib/configs/impartial.py` → `api/lib/infers/impartial.py`: impartial.py创建InferTask实例。
- `api/lib/configs/impartial.py` → `api/lib/trainers/impartial.py`: impartial.py创建TrainTask实例。
- `api/lib/trainers/impartial.py` → `Impartial_dataloaders.py`: 训练器导入sample_patches和blind_spot_patch函数。
- `api/lib/trainers/impartial.py` → `Impartial_functions.py`: 训练器导入compute_impartial_losses函数。
- `api/lib/trainers/impartial.py` → `api/lib/transforms.py`: 训练器使用BlindSpotPatch和GetImpartialOutputs变换。
- `api/lib/infers/impartial.py` → `api/lib/transforms.py`: 推理器使用GetImpartialOutputs等变换。
