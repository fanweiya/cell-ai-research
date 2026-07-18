# vitaminp

> 基于Vision Transformer的病理细胞分割与合成框架

Vitamin-P 是一个完整的病理图像分析框架，核心功能包括：1) 使用 DINOv2 作为骨干网络的双编码器 U-Net 模型，支持 H&E 和 MIF 图像的细胞核与细胞分割；2) 基于 Pix2Pix 的 GAN 模型，用于从 H&E 图像合成 MIF 图像；3) 针对全切片图像 (WSI) 的流式推理系统，包含 Tile 处理、重叠清洗和 GPU 加速的后处理。

## Files

### `vitaminp/__init__.py`

模块入口，导出所有公共 API

- `VitaminPDual` (class) - 双编码器模型，同时处理 H&E 和 MIF 图像
- `load_model` (function) - 从 HuggingFace 加载预训练模型权重
- `available_models` (function) - 获取可用模型列表

### `vitaminp/models.py`

定义核心分割模型架构

- `VitaminPDual` (class) - 双编码器 U-Net，包含 H&E 和 MIF 两个独立编码器及共享解码器
- `VitaminPSyn` (class) - 合成 MIF 分割模型，基于 Dual 架构但仅使用 H&E 输入
- `VitaminPFlex` (class) - 灵活多通道模型，支持不同输入组合

### `vitaminp/backbone.py`

DINOv2 骨干网络封装

- `DINOv2Backbone` (class) - 提取 DINOv2 的多尺度特征，支持 3 通道 (H&E) 和 2 通道 (MIF) 输入

### `vitaminp/blocks.py`

模型构建块，包含卷积模块和注意力机制

- `ConvBlock` (class) - 双卷积块，包含 GroupNorm、GELU 和 SE 通道注意力
- `SELayer` (class) - Squeeze-and-Excitation 通道注意力层
- `ASPP` (class) - 空洞空间金字塔池化，捕获多尺度上下文

### `vitaminp/losses.py`

定义分割和 HV 图预测的损失函数

- `DiceFocalLoss` (class) - Dice 损失与 Focal 损失的组合，用于分割任务
- `HVLoss` (class) - HoVer-Net 风格的损失，结合 MSE 和 MSGE 用于距离图预测
- `MSGELossMaps` (class) - 均方梯度误差损失，强制细胞边界分离

### `vitaminp/trainer.py`

模型训练器，管理训练循环和验证

- `VitaminPTrainer` (class) - 训练主类，集成优化器、调度器和 W&B 日志
- `TestEvaluator` (class) - 测试集评估器，计算 Dice、IoU 和 PQ 指标

### `vitaminp/utils.py`

通用工具函数，包括预处理和指标计算

- `SimplePreprocessing` (class) - 图像预处理，支持百分位归一化和颜色增强
- `compute_dice` (function) - 计算 Dice 系数

### `vitaminp/pretrained.py`

预训练模型加载与缓存管理

- `load_model` (function) - 自动从 HuggingFace 下载并加载模型权重
- `MODEL_REGISTRY` (dict) - 模型名称到 HuggingFace 文件名的映射表

### `vitaminp/gan/__init__.py`

GAN 模块入口

- `Pix2PixTrainer` (class) - Pix2Pix GAN 训练器

### `vitaminp/gan/models.py`

GAN 生成器和判别器架构

- `Pix2PixGenerator` (class) - U-Net 生成器，支持注意力门和残差块
- `PatchGANDiscriminator` (class) - PatchGAN 判别器，使用谱归一化

### `vitaminp/gan/losses.py`

GAN 损失函数

- `GANLoss` (class) - GAN 对抗损失
- `PerceptualLoss` (class) - 基于 VGG 的感知损失
- `SSIMLoss` (class) - 结构相似性损失

### `vitaminp/gan/augmentations.py`

配对数据增强，确保 H&E 和 MIF 同步变换

- `PairedGANAugmentation` (class) - 对 H&E 和 MIF 图像应用相同的几何变换

### `vitaminp/inference/__init__.py`

推理模块入口

- `WSIPredictor` (class) - 全切片图像预测器

### `vitaminp/inference/predictor.py`

WSI 预测主逻辑，协调 Tile 处理、GAN 合成和结果导出

- `WSIPredictor` (class) - 高层预测接口，支持真实 MIF 和合成 MIF 模式

### `vitaminp/inference/tile_processor.py`

Tile 级别的流式处理

- `TileProcessor` (class) - 将大图像切分为 Tile 并逐个处理，避免内存溢出

### `vitaminp/inference/wsi_handler.py`

多格式 WSI 文件加载器

- `MultiFormatImageLoader` (class) - 支持 SVS、NDPI、OME-TIFF 等格式的加载

### `vitaminp/inference/channel_config.py`

MIF 通道配置，定义核与膜通道的选择与组合

- `ChannelConfig` (class) - 配置 MIF 图像的核通道和膜通道（支持单通道或多通道组合）

### `vitaminp/inference/overlap_cleaner.py`

去除重叠 Tile 产生的重复检测

- `OverlapCleaner` (class) - 基于 Shapely 的 IoU 去重算法

### `vitaminp/inference/postprocessing.py`

GPU 加速的实例分割后处理

- `process_model_outputs` (function) - 使用 HoVer-Net 方法从 HV 图提取细胞实例

### `vitaminp/inference/constrained_watershed.py`

HV 约束的水墨分割算法

- `apply_hv_constrained_watershed` (function) - 基于核种子和 HV 边界的约束分水岭分割

### `vitaminp/inference/utils.py`

推理工具函数，包括日志和结果导出

- `ResultExporter` (class) - 将检测结果导出为 JSON 或 GeoJSON 格式
- `setup_logger` (function) - 配置日志记录器

### `vitaminp/postprocessing/__init__.py`

后处理模块入口

### `vitaminp/postprocessing/hv_postprocess.py`

HV 图后处理核心算法

- `HVPostProcessor` (class) - GPU 加速的 HV 图实例分割处理器

## Key Concepts

- **DINOv2 Backbone**: 使用 DINOv2 视觉 Transformer 作为特征提取器，支持不同尺寸 (small/base/large/giant) 和输入通道数 (3 或 2)。通过修改第一个卷积层适配不同模态。
- **Dual Encoder Architecture**: VitaminPDual 模型包含两个独立的编码器分别处理 H&E 和 MIF 图像，在浅层特征后融合，然后通过共享的深层编码器和四个独立的解码器分支输出核与细胞的分割结果。
- **HoVer-Net Style HV Maps**: 模型预测水平和垂直距离图 (HV maps)，用于通过分水岭算法分离紧密接触的细胞。结合 MSGE 损失强制边界清晰。
- **Synthetic MIF Generation**: 使用 Pix2Pix GAN 从 H&E 图像生成合成 MIF 图像，使模型仅需 H&E 输入即可进行多模态分割推理。采用感知损失和 SSIM 损失提升质量。
- **WSI Streaming Inference**: 针对全切片图像 (WSI) 的内存优化策略。将图像切分为 512x512 的 Tile，逐个加载、推理、后处理，最后合并结果并去除边界重叠。
- **GPU-Accelerated Postprocessing**: 使用 CuPy 加速距离变换、连通域标记等后处理步骤，显著加快从 HV 图到实例 mask 的转换速度。

## Internal Relationships

- `vitaminp/models.py` → `vitaminp/backbone.py`: 模型使用 DINOv2Backbone 作为特征提取器
- `vitaminp/models.py` → `vitaminp/blocks.py`: 模型解码器使用 ConvBlock 和 ASPP 等构建块
- `vitaminp/trainer.py` → `vitaminp/losses.py`: 训练器使用 DiceFocalLoss 和 HVLoss 计算损失
- `vitaminp/inference/predictor.py` → `vitaminp/gan/models.py`: 预测器在需要时调用 GAN 生成器合成 MIF 图像
- `vitaminp/inference/predictor.py` → `vitaminp/inference/tile_processor.py`: 预测器通过 TileProcessor 流式处理大图像
- `vitaminp/inference/tile_processor.py` → `vitaminp/inference/wsi_handler.py`: TileProcessor 使用 MultiFormatImageLoader 读取图像块
- `vitaminp/inference/predictor.py` → `vitaminp/inference/postprocessing.py`: 预测器对每个 Tile 的模型输出进行后处理以提取实例
- `vitaminp/inference/predictor.py` → `vitaminp/inference/overlap_cleaner.py`: 预测器在收集所有 Tile 结果后调用 OverlapCleaner 去重
- `vitaminp/inference/predictor.py` → `vitaminp/inference/channel_config.py`: 预测器使用 ChannelConfig 处理 MIF 通道选择
- `vitaminp/pretrained.py` → `vitaminp/models.py`: 预训练加载器实例化 models.py 中的模型类并加载权重
