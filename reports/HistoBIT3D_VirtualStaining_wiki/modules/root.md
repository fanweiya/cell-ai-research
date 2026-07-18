# root

> HistoBIT3D项目的根目录，包含虚拟3D H&E染色框架的完整实现、数据集、训练脚本及实验评估代码。

该模块实现了一个基于生成对抗网络（GAN）的3D组织虚拟H&E染色框架，旨在从无标记的相位对比背光干涉层析成像（BIT）数据中生成具有临床可解释性的H&E染色图像。核心创新包括双向多尺度内容一致性以保持组织结构，以及基于AdaIN的跨域风格复用以生成逼真的H&E外观。项目提供了首个体素级配对的BIT-荧光核数据集，并支持零样本Cellpose验证。

## Files

### `README.md`

项目说明文档，介绍研究背景、方法概述、网络架构、结果展示及引用信息。

### `data/dataset.py`

定义HistoBIT3D数据集加载类，处理BIT体积数据与荧光核标签的配对读取、预处理及数据增强。

- `HistoBIT3DDataset` (class) - 继承自torch.utils.data.Dataset，负责加载和预处理3D BIT图像及其对应的荧光核掩码。
- `transform_volume` (function) - 对3D体积数据进行归一化、裁剪和随机翻转等增强操作。

### `models/network.py`

实现虚拟染色生成器（Generator）和判别器（Discriminator）的核心网络架构。

- `Generator3D` (class) - 生成器网络，包含编码器-解码器结构，集成双向多尺度内容一致性模块和AdaIN风格注入层。
- `Discriminator3D` (class) - 判别器网络，采用多尺度判别策略以评估生成图像的逼真度。
- `AdaINLayer` (class) - 自适应实例归一化层，用于跨域风格迁移，将H&E风格统计量注入到生成特征中。
- `BidirectionalConsistencyLoss` (class) - 实现双向多尺度内容一致性损失，确保生成图像与输入BIT图像在结构上保持一致。

### `train/train_loop.py`

定义模型训练循环，管理生成器与判别器的交替优化、损失计算及模型保存。

- `train_epoch` (function) - 执行单个训练轮次，计算生成损失、对抗损失和内容一致性损失。
- `validate` (function) - 在验证集上评估模型性能，计算PSNR、SSIM等指标。

### `utils/evaluation.py`

提供定量评估工具，包括与荧光核真值进行零样本Cellpose分割对比的脚本。

- `compute_nuclei_metrics` (function) - 计算生成图像中核分割的Dice系数、Jaccard指数等指标，与荧光真值对比。
- `run_cellpose_zero_shot` (function) - 在生成的虚拟H&E图像上运行预训练的Cellpose模型进行核分割。

### `config/config.yaml`

存储实验配置参数，包括学习率、批次大小、网络层数、损失权重等。

## Key Concepts

- **双向多尺度内容一致性**: 一种结构保持机制，通过比较生成图像与输入BIT图像在多个尺度上的特征一致性，确保虚拟染色不破坏原始组织形态。
- **AdaIN跨域风格复用**: 利用自适应实例归一化将H&E染色的统计风格（均值和方差）迁移到生成特征上，实现逼真的染色外观。
- **零样本Cellpose验证**: 使用在自然图像上预训练的Cellpose模型直接分割虚拟H&E图像中的核，无需针对新数据微调，以此评估结构保真度。
- **体素级配对数据集**: HistoBIT3D数据集提供同一组织块在BIT成像和荧光核标记下的精确体素对齐数据，用于监督学习。

## Internal Relationships

- `train/train_loop.py` → `models/network.py`: 训练循环导入生成器和判别器类以实例化模型并执行前向/反向传播。
- `train/train_loop.py` → `data/dataset.py`: 训练循环加载HistoBIT3DDataset以获取训练批次数据。
- `utils/evaluation.py` → `models/network.py`: 评估脚本加载训练好的生成器模型对虚拟染色结果进行核分割分析。
- `models/network.py` → `config/config.yaml`: 网络架构参数（如通道数、层数）从配置文件中读取并初始化。
