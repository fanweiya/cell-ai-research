# segment_anything

> 实现基于提示引导的细胞实例分割框架的核心模块，使用冻结的DINOv3骨干网络和SAM风格解码器。

该模块提供了完整的分割一切模型（SAM）实现，包括模型构建、推理预测器和自动掩码生成器。核心架构由图像编码器（ViT变体）、提示编码器（处理点、框和掩码输入）和掩码解码器（基于Transformer的掩码预测）组成。模块支持通过点、框等提示进行交互式分割，以及全自动的实例分割。

## Files

### `segment_anything/__init__.py`

模块入口，导出主要API。

- `build_sam` (function) - 默认构建SAM模型（ViT-H），支持加载预训练权重。
- `SamPredictor` (class) - 交互式预测器，用于对单张图像进行多次提示式掩码预测。
- `SamAutomaticMaskGenerator` (class) - 自动掩码生成器，对整张图像进行无监督的实例分割。

### `segment_anything/build_sam.py`

定义模型构建工厂函数和注册表。

- `build_sam_vit_h` (function) - 构建ViT-H大模型，embed_dim=1280, depth=32。
- `build_sam_vit_l` (function) - 构建ViT-L模型，embed_dim=1024, depth=24。
- `build_sam_vit_b` (function) - 构建ViT-B模型，embed_dim=768, depth=12。
- `sam_model_registry` (dict) - 模型注册表，键为模型类型，值为对应的构建函数。

### `segment_anything/predictor.py`

实现SamPredictor类，用于高效交互式预测。

- `SamPredictor` (class) - 封装模型推理流程，缓存图像嵌入，支持重复预测。
- `set_image` (method) - 预处理图像并计算图像嵌入。
- `predict` (method) - 根据点坐标、标签、框等提示生成掩码和IoU预测。

### `segment_anything/automatic_mask_generator.py`

实现SamAutomaticMaskGenerator类，用于全自动实例分割。

- `SamAutomaticMaskGenerator` (class) - 通过网格点采样、多尺度裁剪和非极大值抑制生成全图掩码。
- `generate` (method) - 执行自动掩码生成流程，返回MaskData对象。

### `segment_anything/modeling/sam.py`

定义SAM主模型类，整合编码器和解码器。

- `Sam` (class) - 端到端掩码预测模型，包含图像编码器、提示编码器和掩码解码器。
- `forward` (method) - 模型前向传播，接收批处理输入并返回掩码和IoU预测。

### `segment_anything/modeling/image_encoder.py`

实现基于ViT的图像编码器。

- `ImageEncoderViT` (class) - 使用PatchEmbed和ViT Block提取图像特征，通过Neck降维。
- `PatchEmbed` (class) - 将图像分割为patch并投影到嵌入空间。
- `Block` (class) - ViT Block，支持窗口注意力或全局注意力。

### `segment_anything/modeling/prompt_encoder.py`

实现提示编码器，将点、框和掩码输入转换为嵌入。

- `PromptEncoder` (class) - 编码稀疏提示（点、框）和密集提示（掩码输入）。
- `get_dense_pe` (method) - 生成图像尺寸密度的位置编码。
- `_embed_points` (method) - 将点坐标和标签编码为嵌入向量。
- `_embed_boxes` (method) - 将边界框坐标编码为嵌入向量。

### `segment_anything/modeling/mask_decoder.py`

实现掩码解码器，基于Transformer预测掩码。

- `MaskDecoder` (class) - 接收图像嵌入和提示嵌入，输出多张掩码及其质量评分。
- `predict_masks` (method) - 核心推理逻辑，通过Transformer和上采样网络生成掩码。

### `segment_anything/modeling/transformer.py`

实现TwoWayTransformer，用于图像-提示交互。

- `TwoWayTransformer` (class) - 双向Transformer解码器，处理点查询与图像特征的交互。
- `TwoWayAttentionBlock` (class) - 包含自注意力、交叉注意力和MLP的Transformer块。

### `segment_anything/modeling/common.py`

提供通用网络组件。

- `MLPBlock` (class) - 两层MLP模块，含GELU激活。
- `LayerNorm2d` (class) - 2D批量归一化层，对通道进行归一化。

### `segment_anything/utils/amg.py`

提供自动掩码生成器所需的工具函数和数据结构。

- `MaskData` (class) - 批量存储掩码及相关数据的容器，支持过滤和拼接。
- `calculate_stability_score` (function) - 计算掩码的稳定性分数，用于过滤低质量掩码。
- `remove_small_regions` (function) - 移除面积过小的掩码区域或孔洞。
- `batched_nms` (function) - 批量非极大值抑制，去重重叠掩码。

### `segment_anything/utils/transforms.py`

提供图像和坐标变换工具。

- `ResizeLongestSide` (class) - 将图像长边缩放到指定长度，并同步变换坐标和框。

### `segment_anything/utils/onnx.py`

提供ONNX导出所需的模型包装类。

- `SamOnnxModel` (class) - 用于ONNX导出的SAM模型变体，支持固定尺寸推理。

## Key Concepts

- **SAM架构**: 分割一切模型由图像编码器（ViT）、提示编码器（处理点、框、掩码）和掩码解码器（Transformer）组成，实现从图像和提示到掩码的端到端预测。
- **提示编码**: 将稀疏提示（点、框）和密集提示（掩码输入）转换为统一嵌入空间，结合位置编码后输入解码器。
- **双向Transformer**: 解码器核心，通过自注意力处理点查询，通过交叉注意力关联图像特征，实现提示与图像的交互。
- **交互式预测**: SamPredictor缓存图像嵌入，允许对同一图像反复进行不同提示的掩码预测，提高效率。
- **自动掩码生成**: 通过网格点采样、多尺度裁剪和NMS后处理，实现无需人工提示的全自动实例分割。
- **掩码后处理**: 包括稳定性评分、小区域移除、NMS去重等步骤，提升掩码质量。

## Internal Relationships

- `segment_anything/__init__.py` → `segment_anything/build_sam.py`: 导出模型构建函数和注册表。
- `segment_anything/__init__.py` → `segment_anything/predictor.py`: 导出交互式预测器。
- `segment_anything/__init__.py` → `segment_anything/automatic_mask_generator.py`: 导出自动掩码生成器。
- `segment_anything/build_sam.py` → `segment_anything/modeling/sam.py`: 实例化Sam模型并配置各组件。
- `segment_anything/build_sam.py` → `segment_anything/modeling/image_encoder.py`: 配置图像编码器参数。
- `segment_anything/build_sam.py` → `segment_anything/modeling/prompt_encoder.py`: 配置提示编码器参数。
- `segment_anything/build_sam.py` → `segment_anything/modeling/mask_decoder.py`: 配置掩码解码器参数。
- `segment_anything/predictor.py` → `segment_anything/modeling/sam.py`: 使用Sam模型进行推理。
- `segment_anything/predictor.py` → `segment_anything/utils/transforms.py`: 使用ResizeLongestSide进行图像预处理。
- `segment_anything/automatic_mask_generator.py` → `segment_anything/predictor.py`: 复用SamPredictor进行批量点提示推理。
- `segment_anything/automatic_mask_generator.py` → `segment_anything/utils/amg.py`: 使用MaskData存储结果，使用AMG工具进行后处理。
- `segment_anything/modeling/sam.py` → `segment_anything/modeling/image_encoder.py`: 包含图像编码器实例。
- `segment_anything/modeling/sam.py` → `segment_anything/modeling/prompt_encoder.py`: 包含提示编码器实例。
- `segment_anything/modeling/sam.py` → `segment_anything/modeling/mask_decoder.py`: 包含掩码解码器实例。
- `segment_anything/modeling/mask_decoder.py` → `segment_anything/modeling/transformer.py`: 使用TwoWayTransformer进行特征交互。
- `segment_anything/modeling/image_encoder.py` → `segment_anything/modeling/common.py`: 使用LayerNorm2d和MLPBlock组件。
- `segment_anything/modeling/prompt_encoder.py` → `segment_anything/modeling/common.py`: 使用LayerNorm2d组件。
- `segment_anything/modeling/mask_decoder.py` → `segment_anything/modeling/common.py`: 使用LayerNorm2d组件。
