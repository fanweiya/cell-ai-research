# configs

> 存储和定义不同语义分割模型训练所需的配置参数。

该模块包含5个YAML配置文件，分别对应不同的分割模型架构（BMC-Adapt、ConvNeXt、FCN、SegFormer、Swin Transformer）。每个配置文件详细指定了PyTorch Lightning训练器参数、模型超参数、数据路径、优化器设置及检查点策略。这些配置被主训练脚本读取，用于实例化对应的模型和数据加载器，支持在相同数据集上对不同架构进行公平比较和微调。

## Files

### `configs/bmcseg_adapt.yaml`

定义BMC-Adapt模型的训练配置，该模型基于DINOv2 backbone和DeepLabV3+结构，支持域自适应。

### `configs/convnext.yaml`

定义基于ConvNeXt backbone的UperNet分割模型训练配置。

### `configs/fcn.yaml`

定义基于ResNet50的FCN分割模型训练配置。

### `configs/segformer.yaml`

定义基于SegFormer（MIT-B5）的分割模型训练配置。

### `configs/swin.yaml`

定义基于Swin Transformer的UperNet分割模型训练配置。

## Key Concepts

- **Lightning配置**: 所有配置均遵循PyTorch Lightning 2.2.1的 Trainer 参数规范，包括加速器、精度（16-mixed）、日志记录器和回调设置。
- **模型架构复用**: 除bmcseg_adapt外，其余模型均通过config_url和checkpoint_url引用OpenMMLab MMSegmentation的预训练配置和权重，实现即插即用。
- **上采样策略**: 配置项upsample_in和upsample_out控制特征图上采样行为，不同模型采用不同的上采样倍数（4或8）以适应输出分辨率。
- **域自适应支持**: bmcseg_adapt.yaml包含adapt_data和adapt_image_dir字段，用于指定自适应训练数据，这是其他配置所不具备的。

## Internal Relationships

- `configs/*.yaml` → `main.py / train.py`: 配置文件被主训练脚本通过OmegaConf或PyYAML加载，用于初始化LightningModule和DataModule。
