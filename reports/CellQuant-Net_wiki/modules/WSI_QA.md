# WSI_QA

> 提供全切片图像（WSI）的核检测、分类和质量评估流水线

WSI_QA 模块是一个用于病理全切片图像分析的完整流程，包含图像预处理、组织区域检测、图像分块、基于深度学习的分割网络推理以及最终的质量评估。该模块支持多种骨干网络（Swin Transformer, ConvNeXt, ResNet等）和分割架构（U-Net, U-Net++, U-Net3+, TransFuse, UPerNet），能够自动识别WSI中的有效组织区域，提取图像块进行分类和分割，最终输出质量评估结果和分割掩码。

## Files

### `WSI_QA/config.py`

定义和加载训练/推理配置参数

- `_C` (variable) - 全局配置对象，使用yacs CfgNode实现，包含DATA, MODEL, TRAIN, AUG等配置层级
- `get_config` (function) - 从YAML配置文件加载配置并返回配置对象

### `WSI_QA/configs/DHUnet_224.yaml`

DHUnet模型的特定配置参数

- `MODEL` (section) - 模型配置，指定使用Swin Tiny骨干网络及具体参数

### `WSI_QA/datasets/dataset.py`

定义图像和掩码的数据集类及数据增强操作

- `RandomVerticalFlip` (class) - 随机垂直翻转图像和掩码的增强类
- `RandomHorizontalFlip` (class) - 随机水平翻转图像和掩码的增强类
- `RandomRotation` (class) - 随机旋转图像和掩码的增强类
- `ColorJitter` (class) - 颜色抖动增强类
- `Normalize` (class) - 图像标准化增强类
- `ToTensor` (class) - 将图像转换为Tensor的增强类
- `resize_img_msk` (class) - 调整图像和掩码尺寸的增强类

### `WSI_QA/network/DHUnet.py`

定义DHUnet网络架构，结合Swin Transformer和ConvNeXt骨干网络

- `PatchExpand_X2_cel` (class) - 2倍上采样模块，使用转置卷积进行特征图扩展
- `FinalPatchExpand_X4_cel` (class) - 4倍上采样模块，用于最终输出分辨率恢复
- `Get_encoder` (function) - 根据配置选择并创建编码器骨干网络（ConvNeXt或SwinTransformer）

### `WSI_QA/network/ConvNeXt/ConvNeXt.py`

实现ConvNeXt骨干网络的基本块和主网络

- `LayerNorm` (class) - 支持channels_last和channels_first两种数据格式的LayerNorm
- `Block` (class) - ConvNeXt基本块，包含深度卷积、LayerNorm、点卷积和GELU激活
- `ConvNeXt` (class) - ConvNeXt主网络，由下采样层和四个特征阶段组成

### `WSI_QA/network/ConvNeXt/ConvNeXtUnet.py`

基于ConvNeXt的U-Net分割网络

- `ConvNeXtUnet` (class) - ConvNeXt编码器+U-Net解码器的分割网络
- `load_from` (method) - 加载预训练权重并处理模型结构差异

### `WSI_QA/network/SwinTransformer/SwinTransformer.py`

实现Swin Transformer的基本组件

- `Mlp` (class) - 多层感知机模块
- `window_partition` (function) - 将特征图分割成窗口
- `window_reverse` (function) - 将窗口特征图重组为原始特征图
- `WindowAttention` (class) - 基于窗口的多头自注意力机制

### `WSI_QA/network/SwinTransformer/SwinUnet.py`

基于Swin Transformer的U-Net分割网络

- `SwinUnet` (class) - Swin Transformer编码器+U-Net解码器的分割网络
- `load_from` (method) - 加载预训练Swin Transformer权重

### `WSI_QA/network/TransFuse/TransFuse.py`

实现TransFuse网络，融合CNN和Transformer特征

- `BiFusion_block` (class) - 双向融合块，结合通道注意力和空间注意力
- `TransFuse_S` (class) - TransFuse小型网络，使用ResNet34和DeiT作为骨干

### `WSI_QA/network/UNet/Unet.py`

标准U-Net分割网络实现

- `Unet` (class) - 经典U-Net架构，包含编码器和解码器路径

### `WSI_QA/network/UNet/Unet2Plus.py`

实现U-Net++网络，通过嵌套跳跃连接改进特征融合

- `Unet2Plus` (class) - U-Net++网络，包含多尺度跳跃连接

### `WSI_QA/network/UNet/Unet3Plus.py`

实现U-Net3+网络，使用全尺度跳跃连接

- `Unet3Plus` (class) - U-Net3+网络，通过深度监督和多尺度融合提升性能

### `WSI_QA/network/UperNet/upernet_convnext_tiny.py`

基于ConvNeXt的UPerNet分割网络

- `upernet_ConvNeXt_tiny` (class) - ConvNeXt骨干+UPerHead解码器的分割网络

### `WSI_QA/patch_analyze.py`

提供数据集预处理和质量统计功能

- `count_stats` (function) - 统计数据集中各类别的分布比例
- `gleason_preprocess` (function) - Gleason数据集预处理，过滤无效图像和掩码
- `bcss_preprocess` (function) - BCSS数据集预处理，过滤全零掩码

### `WSI_QA/test_qa.py`

主程序入口，执行WSI质量评估推理流程

- `inference` (function) - 执行模型推理，处理所有WSI文件
- `set_seed` (function) - 设置随机种子以保证结果可复现

### `WSI_QA/utils.py`

提供WSI处理、图像分块和质量评估的工具函数

- `find_Tissue_regions` (function) - 检测WSI中的组织区域，确定有效分析范围
- `create_patches` (function) - 从WSI中提取图像块
- `test_single_patch` (function) - 对单个图像块进行模型推理
- `fill_holes_wsi_seg` (function) - 填充分割掩码中的空洞
- `data_generator` (function) - 数据生成器，为模型推理准备批次数据

## Key Concepts

- **全切片图像（WSI）处理**: WSI是高分辨率病理图像，通常达到数十亿像素。处理时需要分块（patch）策略，先检测组织区域，再提取有效图像块进行分析。
- **多尺度特征融合**: U-Net及其变体（U-Net++, U-Net3+）通过跳跃连接融合编码器不同尺度的特征，提升分割精度。
- **混合架构**: TransFuse和DHUnet等网络结合CNN（提取局部特征）和Transformer（捕捉全局依赖）的优势。
- **质量评估**: 通过分割网络识别图像块的质量类别（如组织、背景、模糊等），进而评估整个WSI的质量。
- **预训练权重迁移**: 利用在ImageNet等大规模数据集上预训练的权重（Swin, ConvNeXt, ResNet）进行迁移学习，提升小数据集上的性能。

## Internal Relationships

- `test_qa.py` → `config.py`: test_qa.py导入get_config函数加载配置文件
- `test_qa.py` → `network/DHUnet.py`: test_qa.py实例化DHUnet模型进行推理
- `test_qa.py` → `utils.py`: test_qa.py调用utils中的函数处理WSI和图像块
- `network/DHUnet.py` → `network/ConvNeXt/ConvNeXt.py`: DHUnet导入ConvNeXt作为可选编码器
- `network/DHUnet.py` → `network/SwinTransformer/SwinTransformer.py`: DHUnet导入SwinTransformer作为可选编码器
- `network/ConvNeXt/ConvNeXtUnet.py` → `network/ConvNeXt/ConvNeXt.py`: ConvNeXtUnet导入ConvNeXt骨干网络
- `network/SwinTransformer/SwinUnet.py` → `network/SwinTransformer/SwinTransformer.py`: SwinUnet导入SwinTransformer组件
- `network/TransFuse/TransFuse.py` → `network/TransFuse/DeiT.py`: TransFuse导入DeiT作为Transformer骨干
- `datasets/dataset.py` → `test_qa.py`: dataset.py中的增强类可能被test_qa.py的数据加载流程使用
