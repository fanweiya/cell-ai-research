# root

> 实现白细胞图像细粒度像素级形态标注与分割的完整训练、评估与预测流程

该模块提供WBCAtt+数据集的复现代码，包含属性预测基线训练、语义分割模型训练、多任务损失计算、模型评估及预测功能。核心流程包括：使用AttDatasetSeg加载图像与分割掩码，通过SegBasedAggLayer聚合分割特征，利用MultiTaskLoss计算多任务损失，最终通过evaluate和predict模块进行模型评估与属性预测。

## Files

### `att_dataset_seg.py`

定义AttDatasetSeg数据集类，负责加载图像、分割掩码及属性标注，并应用数据增强

- `AttDatasetSeg` (class) - 继承自torch.utils.data.Dataset，整合图像、分割掩码和属性标注，支持随机裁剪、翻转等增强操作
- `create_attribute_encoders` (method) - 为每个属性列创建值到索引的映射字典
- `__getitem__` (method) - 返回单个样本的图像、掩码、属性标签及索引

### `modelsseg.py`

定义基于分割的聚合层和属性预测模型

- `SegBasedAggLayer` (class) - 根据分割掩码提取图像特征并进行聚合（平均、最大、加权、注意力等），输出统一特征表示
- `forward` (method) - 执行前向传播，对每个分割类别应用掩码并编码，然后聚合特征
- `AttributePredictorSeg` (class) - 属性预测模型，结合分割聚合层和分类头

### `multi_task_loss.py`

实现多任务损失计算模块，支持加权组合多个任务损失

- `MultiTaskLoss` (class) - 接收多个损失函数及其权重，计算总损失或返回各任务损失字典
- `forward` (method) - 遍历输出与目标，应用对应损失函数并加权求和

### `evaluation_loop.py`

提供模型评估函数，计算多种分类指标

- `evaluate` (function) - 在验证/测试集上运行模型，计算准确率、F1、精确率、召回率等指标
- `metrics` (variable) - 定义多个评估指标的lambda函数，包括acc、f1_macro、pre_macro等

### `train_att.py`

训练属性预测基线模型的主脚本

- `setup_args` (function) - 解析命令行参数，配置数据集路径、模型结构、训练超参数等
- `main` (function) - 执行训练流程，包括数据加载、模型构建、训练循环、验证与保存

### `predict_att.py`

加载训练好的模型并对新数据进行属性预测

- `setup_args` (function) - 解析预测任务所需的参数，如模型路径、输入CSV、输出目录等
- `main` (function) - 加载模型权重，对输入图像进行推理，保存预测结果到CSV

### `main_seg.py`

训练和测试语义分割模型的主脚本，基于PyTorch Lightning和MMSegmentation

- `cli_main` (function) - 初始化LightningCLI，支持fit和test命令，加载配置文件训练或测试分割模型
- `JPEGCompressionTransform` (class) - 模拟JPEG压缩的数据增强变换
- `SynchronizedRandomFlips` (class) - 同步对图像和掩码进行随机水平/垂直翻转

### `predict_seg.py`

对图像进行分割预测并保存掩码结果

- `main` (function) - 加载分割模型，读取输入CSV，对每张图像生成分割掩码并保存

### `main_adapt.py`

用于模型适配的脚本，包含数据增强和Lightning模块定义

- `JPEGCompressionTransform` (class) - 与main_seg.py中定义相同，用于模拟压缩噪声
- `SynchronizedRandomFlips` (class) - 同步翻转图像和掩码

### `README.md`

项目说明文档，包含数据集介绍、环境配置、训练与测试命令

### `environment.yml`

定义项目依赖的conda环境配置文件

## Key Concepts

- **分割引导的属性预测**: 利用语义分割掩码将图像按细胞结构区域（如细胞核、细胞质）分割，分别编码后聚合，再输入分类器进行多属性预测
- **多任务学习**: 同时预测多个形态学属性（如细胞大小、核质比、颗粒类型等），使用MultiTaskLoss加权组合各属性损失
- **特征聚合策略**: 支持多种聚合方式：无聚合（仅全图）、拼接、最大池化、平均池化、加权平均、自注意力聚合
- **PyTorch Lightning集成**: 训练脚本基于LightningCLI构建，支持配置驱动的训练流程和模块化模型定义
- **MMSegmentation后端**: 语义分割模型使用MMSegmentation框架，支持FCN、SegFormer、Swin、ConvNext等架构

## Internal Relationships

- `train_att.py` → `att_dataset_seg.py`: train_att.py导入AttDatasetSeg用于构建训练和验证数据加载器
- `train_att.py` → `modelsseg.py`: train_att.py导入AttributePredictorSeg和SegBasedAggLayer定义模型结构
- `train_att.py` → `multi_task_loss.py`: train_att.py导入MultiTaskLoss作为训练过程中的损失函数
- `train_att.py` → `evaluation_loop.py`: train_att.py导入evaluate函数在验证集上评估模型性能
- `predict_att.py` → `att_dataset_seg.py`: predict_att.py导入AttDatasetSeg加载待预测数据
- `predict_att.py` → `modelsseg.py`: predict_att.py导入AttributePredictorSeg和SegBasedAggLayer加载模型权重
- `predict_att.py` → `evaluation_loop.py`: predict_att.py可能复用evaluate或predict函数进行推理
- `main_seg.py` → `att_dataset_seg.py`: main_seg.py可能使用AttDatasetSeg或类似数据集类处理分割任务
- `main_seg.py` → `main_adapt.py`: main_seg.py和main_adapt.py共享JPEGCompressionTransform和SynchronizedRandomFlips等增强类
- `predict_seg.py` → `main_seg.py`: predict_seg.py导入main_seg的cli_main来初始化分割模型
