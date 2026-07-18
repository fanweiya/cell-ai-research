# HistoBIT3D_Code

> 基于GAN的3D组织虚拟H&E染色框架

这是一个用于3D组织图像虚拟染色的深度学习框架，核心基于UVCGANv2实现。项目包含完整的训练、评估、推理脚本，支持CycleGAN、Pix2Pix、Autoencoder等多种模型架构，并针对3D病理切片（如BIT到HE染色）进行了专门优化，包括相邻切片一致性损失、风格融合等高级功能。

## Files

### `HistoBIT3D_Code/uvcgan2/__init__.py`

模块入口，导出核心训练函数和自定义数据集

- `train` (function) - 启动模型训练的主函数
- `AdjacentZPairDataset` (class) - 3D相邻切片对数据集类

### `HistoBIT3D_Code/uvcgan2/config/config.py`

配置管理核心，解析和验证训练参数

- `Config` (class) - 主配置类，包含所有训练超参数和数据设置
- `parse_data_config` (function) - 解析数据集配置
- `ModelConfig` (class) - 模型架构配置类

### `HistoBIT3D_Code/uvcgan2/cgan/__init__.py`

模型选择工厂，注册所有GAN模型变体

- `CGAN_MODELS` (dict) - 模型名称到类的映射字典
- `construct_model` (function) - 根据配置创建模型实例

### `HistoBIT3D_Code/uvcgan2/cgan/uvcgan2_3D_emb_sub_stylefusion.py`

3D风格融合模型实现，核心创新模块

- `UVCGAN2_3D_stylefusion` (class) - 支持3D流一致性和风格融合的GAN模型
- `STYLE_FUSION_STATE_NAME` (constant) - 风格状态持久化文件名

### `HistoBIT3D_Code/uvcgan2/data/adjacent_pair_dataset.py`

3D相邻切片数据集实现

- `AdjacentZPairDataset` (class) - 从3D组织切片中提取相邻Z轴对的数据集

### `HistoBIT3D_Code/scripts/train_3D_embedding_style_loss_WSL.py`

3D模型训练脚本入口

- `parse_cmdargs` (function) - 解析训练命令行参数
- `train` (function) - 调用核心训练流程

### `HistoBIT3D_Code/scripts/eval_all_epochs_A2B_metrics_style.py`

全周期评估脚本，支持风格融合模型

- `parse_args` (function) - 解析评估参数
- `main` (function) - 执行全周期评估流程

### `HistoBIT3D_Code/uvcgan2/models/generator/vitmodnet.py`

ViT+ModNet混合生成器实现

- `ViTModNetGenerator` (class) - 结合Vision Transformer和ModNet的生成器

### `HistoBIT3D_Code/uvcgan2/torch/layers/transformer.py`

Transformer层实现，支持像素级注意力

- `TransformerEncoder` (class) - Transformer编码器
- `img_to_tokens` (function) - 图像转token转换

### `HistoBIT3D_Code/uvcgan2/torch/layers/modnet.py`

ModNet实现，支持风格调制卷积

- `ModulatedConv2d` (class) - 调制卷积层
- `StyleBlock` (class) - 风格调制块

### `HistoBIT3D_Code/uvcgan2/train/train.py`

训练循环主逻辑

- `training_epoch` (function) - 单轮训练循环
- `train` (function) - 完整训练流程控制

### `HistoBIT3D_Code/uvcgan2/cgan/model_base.py`

所有GAN模型的基类

- `ModelBase` (class) - 定义模型生命周期和通用接口

### `HistoBIT3D_Code/uvcgan2/base/networks.py`

基础网络架构（ResNet, U-Net等）

- `ResnetGenerator` (class) - ResNet生成器
- `UnetGenerator` (class) - U-Net生成器

### `HistoBIT3D_Code/scripts/finetune_from_checkpoint_3D.py`

从检查点微调脚本

- `_load_base_weights_into_model` (function) - 加载基础模型权重

### `HistoBIT3D_Code/scripts/reconstruct_bit_vhe_from_metadata.py`

从补丁重建完整3D图像

- `reconstruct_image_from_patches_JUST_BIT` (function) - 基于元数据重建图像

### `HistoBIT3D_Code/uvcgan2/torch/queue.py`

高效队列实现，用于一致性损失

- `FastQueue` (class) - 高性能张量队列

### `HistoBIT3D_Code/uvcgan2/torch/gradient_penalty.py`

WGAN-GP梯度惩罚实现

- `GradientPenalty` (class) - 梯度惩罚计算类

## Key Concepts

- **3D流一致性**: 通过相邻Z轴切片对训练，确保3D体积内组织结构的连续性和一致性
- **风格融合**: 将源域的风格特征注入到目标域生成过程中，实现更自然的染色效果
- **ViT-ModNet混合架构**: 结合Vision Transformer的全局注意力和ModNet的局部风格调制能力
- **批量头部（Batch Head）**: 在判别器中引入批量统计信息，增强对生成质量的判别能力
- **EMA平均模型**: 使用指数移动平均的生成器权重进行推理，提高生成稳定性
- **梯度惩罚**: WGAN-GP技术，通过梯度惩罚项稳定训练过程
- **图像补丁重建**: 支持大尺寸3D图像的补丁式处理和重建

## Internal Relationships

- `scripts/train_3D_embedding_style_loss_WSL.py` → `uvcgan2/__init__.py`: 训练脚本导入train函数和AdjacentZPairDataset
- `uvcgan2/cgan/__init__.py` → `uvcgan2/cgan/uvcgan2_3D_emb_sub_stylefusion.py`: 模型工厂注册3D风格融合模型
- `uvcgan2/cgan/uvcgan2_3D_emb_sub_stylefusion.py` → `uvcgan2/models/generator/vitmodnet.py`: 风格融合模型使用ViTModNet作为生成器
- `uvcgan2/data/data.py` → `uvcgan2/data/adjacent_pair_dataset.py`: 数据集构建器选择相邻切片数据集
- `uvcgan2/train/train.py` → `uvcgan2/cgan/model_base.py`: 训练循环调用模型基类的方法
- `uvcgan2/cgan/uvcgan2.py` → `uvcgan2/torch/queue.py`: UVCGAN2模型使用队列存储历史特征用于一致性损失
- `scripts/eval_all_epochs_A2B_metrics_style.py` → `uvcgan2/cgan/uvcgan2_3D_emb_sub_stylefusion.py`: 评估脚本专门处理风格融合模型的状态加载
- `uvcgan2/models/generator/vitmodnet.py` → `uvcgan2/torch/layers/modnet.py`: ViTModNet生成器使用ModNet作为骨干网络
- `uvcgan2/models/generator/vitmodnet.py` → `uvcgan2/torch/layers/transformer.py`: ViTModNet在ModNet瓶颈处嵌入Transformer编码器
