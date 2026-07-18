# config

> 存储和管理深度学习训练、模型、数据及损失函数的配置参数。

该模块通过多个INI配置文件定义不同实验场景的超参数。每个文件对应特定的数据集或实验设置（如CPDMI、TissueNet、Vectra），包含训练循环参数（epochs, lr, batch_size）、损失函数权重（seg_fore, rec）、模型架构（depth, base）和数据路径。配置由主程序加载，用于动态初始化训练流程和模型结构。

## Files

### `config/cpdmi_nc.ini`

定义CPDMI数据集上包含噪声和缺失标注的交互式分割实验配置，支持多尺度patch采样和特定输出通道数。

### `config/cpdmi_no_rec.ini`

定义CPDMI数据集上关闭重建任务（rec=0.0）的基准实验配置，使用更大的batch size和worker数量。

### `config/default.ini`

作为默认配置模板，定义基础训练参数和全标注数据集路径，用于快速启动实验。

### `config/tissuenet_all.ini`

配置TissueNet全量数据集的训练参数，针对2通道图像和较小的patch size优化。

### `config/tissuenet_orig_iterative.ini`

专为TissueNet迭代实验设计的配置，仅用于评估（rebuttal），不保存输出。

### `config/vectra_2ch_nomc.ini`

配置Vectra 2通道数据集的实验，关闭MC Dropout（mcdrop_it=3但可能逻辑不同）并设置特定输出维度。

## Key Concepts

- **mcdrop_it**: Monte Carlo Dropout迭代次数，用于不确定性估计。
- **num_patches_per_image**: 每张图像采样的patch数量，控制数据增强和训练样本密度。
- **seg_fore/seg_back**: 分割任务中前景和背景的损失权重，平衡类别不平衡。
- **rec_channels**: 重建任务使用的输入通道索引，用于多模态数据融合。

## Internal Relationships

- `main.py` → `config/cpdmi_nc.ini`: 主程序加载特定INI文件以获取超参数并初始化训练器。
- `train.py` → `config/default.ini`: 训练脚本读取默认配置作为基础，允许命令行参数覆盖部分设置。
