# root

> EffiCell-Seg 是一个基于冻结 DINOv3 骨干网络和 SAM 风格解码器的提示引导细胞实例分割框架，支持多种几何解码范式。

该项目实现了一个高效的细胞分割系统，核心在于利用 DINOv3 提取的图像特征和类 token 相似性生成自提示，驱动一个双分支解码器（二值前景分支和几何分支）。几何分支支持四种可切换范式（tsfd, hovernet, stardist, cellpose），分别输出距离图、水平/垂直图、径向距离或流场。系统支持两种运行模式：在线模式（实时运行骨干网络，可选 LoRA/CLS 微调）和缓存模式（预计算骨干特征，仅训练解码器）。

## Files

### `README.md`

项目文档，包含概述、安装指南、数据准备和快速启动说明。

### `dataloader.py`

提供统一的数据加载器，处理图像读取、几何目标生成（距离图、HoVer-Net 图等）及数据增强。

- `UnifiedCellDataset` (class) - 继承自 torch.utils.data.Dataset，支持在线和缓存模式，根据 paradigm 参数生成不同的几何目标。
- `gen_dist_map` (method) - 生成 TSFD 范式所需的归一化实例内距离图。
- `gen_hv_map` (method) - 生成 HoVer-Net 范式所需的水平和垂直距离图。

### `model.py`

定义模型架构，包括 DINOv3 骨干包装器、EffiCellSeg 主模型及几何分支。

- `DinoV3BackboneWrapper` (class) - 封装 timm 创建的 DINOv3 模型，处理特征提取、LoRA/CLS 微调策略及输出空间特征与类 token。
- `EffiCellSeg` (class) - 主模型类，继承 BaseCellSeg，整合提示编码器、双路 Transformer 解码器及可切换的几何分支。

### `train.py`

训练脚本，管理分布式训练、损失计算（二值损失与几何损失）、优化器调度及日志记录。

- `Trainer` (class) - 封装训练循环，处理 DDP 初始化、混合精度训练、多任务损失加权及验证指标计算。
- `_msge_loss` (method) - 计算 HoVer-Net 的均方梯度误差，用于监督水平/垂直距离图的回归。

### `eval.py`

评估脚本，计算二值分割指标（Dice, IoU, NSD, HD95）和实例分割指标（PQ, AJI）。

- `compute_tp_fp_fn` (function) - 计算真阳性、假阳性和假阴性数量，用于实例分割的匹配。
- `compute_binary_nsd` (function) - 计算二值掩码的归一化表面距离（NSD）。

### `extract_features.py`

特征提取脚本，用于缓存模式。遍历数据集，使用 DINOv3 骨干网络提取特征并保存为 .pt 文件。

- `GenericImageDataset` (class) - 通用图像数据集类，支持从目录扫描或列表加载图像。

### `metrics.py`

实现高效的实例分割评估指标，包括 AJI 和 PQ 的计算。

- `get_fast_aji` (function) - 快速计算实例分割的 AJI 指标，基于成对 IoU 匹配。
- `remap_label` (function) - 重映射标签，确保实例 ID 连续，以满足 AJI 计算要求。

### `utils.py`

提供模型构建的通用组件，如 LayerNorm2d、MLP、CrossAttentionModule 及 BaseCellSeg 基类。

- `CrossAttentionModule` (class) - 实现两个特征图之间的双向交叉注意力机制，用于融合二值分支和几何分支的特征。
- `BaseCellSeg` (class) - 细胞分割模型的基类，定义共享属性和接口。

## Key Concepts

- **自提示 (Self-Prompting)**: 利用 DINOv3 骨干提取的 patch 特征和类 token 的相似性，结合 PCA 降维，自动生成驱动 SAM 风格提示编码器的提示向量，无需外部提示。
- **可切换几何范式 (Switchable Geometric Paradigms)**: 解码器的几何分支可配置为四种不同的输出形式（TSFD, HoVer-Net, StarDist, Cellpose），每种范式对应不同的后处理算法来提取实例掩码。
- **缓存模式 (Cached Mode)**: 针对超大骨干网络（如 DINOv3 7B），预先计算并保存所有图像的特征，训练阶段仅加载特征并训练解码器，大幅减少显存占用和重复计算。
- **双分支解码器 (Two-Branch Decoder)**: 包含二值前景分支和几何分支，通过交叉注意力模块融合特征，最终从几何分支输出中恢复实例分割结果。

## Internal Relationships

- `train.py` → `dataloader.py`: train.py 导入 UnifiedCellDataset 以加载训练和验证数据。
- `train.py` → `model.py`: train.py 导入 EffiCellSeg 模型类进行实例化和训练。
- `eval.py` → `model.py`: eval.py 导入 EffiCellSeg 模型进行推理和评估。
- `eval.py` → `metrics.py`: eval.py 导入 get_fast_pq, get_fast_aji, remap_label 用于计算实例分割指标。
- `model.py` → `utils.py`: model.py 导入 BaseCellSeg, MLP, CrossAttentionModule, LayerNorm2d 等基础组件。
- `extract_features.py` → `dataloader.py`: extract_features.py 可能复用 GenericImageDataset 或类似的图像加载逻辑（虽未直接导入，但功能相似）。
