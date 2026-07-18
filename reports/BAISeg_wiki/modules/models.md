# models

> 实现基于有符号距离函数预测和边界感知损失显微镜细胞分割的深度学习模型架构与训练逻辑。

该模块负责定义用于细胞分割的神经网络模型及其训练流程。核心思想是预测有符号距离函数（SDF），并通过边界感知损失优化模型，以精确分割细胞边界。模块包含基础训练框架、可复用的网络构建块（如DoubleConv、UpBlock、DenseBlock）以及具体的U-Net变体实现（Unet3d、DenseUnet3d）。

## Files

### `models/base_model.py`

定义基于PyTorch Lightning的基础模型类，封装训练、验证和优化的通用逻辑。

- `BaseModel` (class) - 继承自pl.LightningModule，管理模型配置、优化器、学习率调度器及训练/验证步骤。
- `configure_optimizers` (function) - 动态配置优化器（默认Adam）和可选的学习率调度器（如ReduceLROnPlateau）。
- `training_step` (function) - 执行单步训练，调用predict_batch获取预测，计算损失并记录日志。
- `validation_step` (function) - 执行单步验证，计算验证损失并记录。

### `models/blocks.py`

提供构建U-Net架构所需的模块化网络层，包括卷积块、上采样块和密集连接块。

- `DoubleConv2D` (class) - 双卷积块，包含两个卷积层、BatchNorm和GELU激活，用于特征提取。
- `Up2DBlock` (class) - 2D上采样块，使用反卷积（ConvTranspose2d）进行上采样，并融合跳跃连接。
- `Up2DBlock2` (class) - 2D上采样块变体，使用双线性插值上采样替代反卷积。
- `Dense2DBlock` (class) - 2D密集连接块，通过多层连接增强特征复用（代码片段被截断，但意图明显）。

### `models/unet.py`

实现具体的3D U-Net模型架构，用于预测有符号距离图和二值分割图。

- `Unet3d` (class) - 标准3D U-Net实现，包含下采样路径、瓶颈层和上采样路径，输出有符号距离图（x_signDist）和经过线性变换的二值分割图（x_binSeg）。
- `DenseUnet3d` (class) - 基于密集连接（DenseNet风格）的3D U-Net变体，支持标记点输入（with_markers），增强特征传播。
- `forward` (function) - 模型前向传播，处理输入图像，通过编码器-解码器结构生成距离场和分割掩码。

## Key Concepts

- **有符号距离函数 (SDF)**: 模型不直接预测分割掩码，而是预测每个像素到最近边界的距离（内部为正，外部为负），通过阈值化（alpha*x + beta）得到最终分割，能更精确地捕捉细胞边界。
- **U-Net 架构**: 采用经典的编码器-解码器结构，配合跳跃连接（Skip Connections）将浅层细节信息传递到深层，保持空间分辨率。
- **PyTorch Lightning**: 使用Lightning框架简化训练流程，自动处理分布式训练、日志记录和回调机制。
- **密集连接 (Dense Connections)**: 在DenseUnet3d中，通过密集块（DenseBlock）连接相邻层，促进特征复用并缓解梯度消失问题。

## Internal Relationships

- `models/unet.py` → `models/base_model.py`: unet.py 中的模型类（如Unet3d）继承自base_model.py中的BaseModel，复用训练循环逻辑。
- `models/unet.py` → `models/blocks.py`: unet.py 导入blocks.py中的DoubleConv3D、Up3DBlock等组件来构建具体的网络层。
- `models/unet.py` → `utils`: unet.py 导入utils模块中的辅助函数（如distance_transform_edt, watershed_labels_from_binary）用于后处理和评估。
