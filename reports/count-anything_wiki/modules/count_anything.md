# count_anything

> 文本引导跨域目标计数模型的公共接口与核心实现

该模块封装了基于SAM3架构的CountAnything模型，提供模型构建、推理、评估、训练及可视化的完整功能。核心通过像素级密集计数器（PDC）和区域级稀疏计数器（RSC）实现文本引导的目标检测与计数，支持LoRA微调、多源结果融合及结果可视化。

## Files

### `count_anything/__init__.py`

包入口，暴露公共API

- `build_count_anything_model` (function) - 构建CountAnything模型的工厂函数
- `CountAnything` (function) - 返回推理类实例

### `count_anything/inference.py`

推理逻辑与结果处理

- `CountAnythingResult` (class) - 推理结果数据类，包含计数、预测点及保存/展示方法
- `CountAnything` (class) - 推理主类，调用命令行执行模型预测并返回结果列表
- `_slugify` (function) - 将文本查询转换为安全的文件名

### `count_anything/model_builder.py`

模型构建入口

- `build_count_anything_model` (function) - 封装SAM3模型构建器，暴露PDC分支、LoRA等CountAnything特有参数

### `count_anything/model/__init__.py`

模型模块别名

- `CountAnythingModel` (class) - CountAnythingModel别名，指向Sam3Image
- `PixelLevelDenseCounter` (class) - 像素级密集计数器类

### `count_anything/model/count_anything.py`

模型类别名

- `CountAnythingModel` (class) - 指向sam3.model.sam3_image.Sam3Image，保持checkpoint键名兼容

### `count_anything/model/pixel_dense_counter.py`

PDC核心组件实现

- `PDCResidualAdapterBlock` (class) - PDC残差适配器块，含两个卷积层和GroupNorm
- `DenseCountingFeatureAdapter` (class) - 密集计数特征适配器，可选坐标卷积
- `DensePointRegressionHead` (class) - 密集点回归头，输出锚点坐标
- `DensePointClassificationHead` (class) - 密集点分类头，输出目标存在性概率

### `count_anything/model/fusion.py`

多源融合接口

- `complementary_count_fusion` (function) - 互补计数融合算法，结合PDC和RSC结果
- `SOURCE_PDC` (constant) - PDC源标识
- `SOURCE_RSC` (constant) - RSC源标识

### `count_anything/model/lora.py`

LoRA工具

- `LoRAMultiheadAttention` (class) - LoRA多头注意力模块
- `wrap_mha_for_lora` (function) - 为多头注意力包装LoRA

### `count_anything/eval/__init__.py`

评估模块公共接口

- `CountAnythingPostProcessor` (class) - 后处理器，执行NMS和融合

### `count_anything/eval/postprocessor.py`

后处理逻辑

- `CountAnythingPostProcessor` (class) - 后处理类，包含PDC/RSC结果融合逻辑
- `complementary_count_fusion` (function) - 互补计数融合函数

### `count_anything/eval/visualizer.py`

可视化函数

- `save_pdc_visualization` (function) - 保存PDC可视化结果
- `save_rsc_visualization` (function) - 保存RSC可视化结果
- `save_ccf_visualization` (function) - 保存互补计数融合可视化结果

### `count_anything/eval/counting_meter.py`

计数指标计算

- `CountingMeter` (class) - 计数评估指标计算器

### `count_anything/train/__init__.py`

训练模块入口

- `Trainer` (class) - 训练器类

### `count_anything/train/loss/__init__.py`

损失函数别名

- `CountAnythingLossWrapper` (class) - CountAnything损失包装器
- `PDCPointSetLoss` (class) - PDC点集损失
- `RSCBoxLoss` (class) - RSC框损失
- `RSCPointLoss` (class) - RSC点损失

### `count_anything/train/loss/pdc_loss.py`

PDC损失与匹配器

- `PDCSparseMatcher` (class) - PDC稀疏匹配器，使用匈牙利算法匹配预测点与真值

### `count_anything/train/loss/rsc_loss.py`

RSC损失别名

- `RSCBoxLoss` (class) - RSC框损失，指向Boxes
- `RSCMatcher` (class) - RSC匹配器，指向DensePointHungarianMatcher

### `count_anything/train/matcher.py`

匹配器接口

- `BinaryOneToManyMatcher` (class) - 二对多匹配器
- `DensePointHungarianMatcher` (class) - 密集点匈牙利匹配器

### `count_anything/train/train.py`

训练CLI入口

- `cli_main` (function) - 命令行主函数，解析参数并调用SAM3训练主流程

## Key Concepts

- **PDC (Pixel-level Dense Counter)**: 像素级密集计数器，通过密集预测点回归和分类实现细粒度计数，使用DenseCountingFeatureAdapter处理特征，输出锚点坐标和分类概率。
- **RSC (Region-level Sparse Counter)**: 区域级稀疏计数器，基于SAM3的框预测分支，输出目标边界框和点，使用匈牙利匹配器进行训练。
- **Complementary Count Fusion (CCF)**: 互补计数融合算法，结合PDC和RSC的结果，利用两者优势提高跨域计数鲁棒性。
- **LoRA微调**: 针对编码器交叉注意力模块的LoRA适配器，支持高效微调而不改变主干参数。
- **文本引导**: 模型通过文本查询（text query）引导目标检测，实现开放词汇计数。

## Internal Relationships

- `count_anything/__init__.py` → `count_anything/model_builder.py`: 导入build_count_anything_model作为公共API
- `count_anything/__init__.py` → `count_anything/inference.py`: 导入CountAnything推理类
- `count_anything/model_builder.py` → `sam3.model_builder`: 调用SAM3底层模型构建器，透传PDC和LoRA参数
- `count_anything/model/count_anything.py` → `sam3.model.sam3_image`: CountAnythingModel直接别名Sam3Image
- `count_anything/model/fusion.py` → `sam3.eval.counting_postprocessor`: 导入互补计数融合函数及源标识
- `count_anything/eval/postprocessor.py` → `sam3.eval.counting_postprocessor`: 导入后处理器和融合函数
- `count_anything/eval/visualizer.py` → `sam3.eval.counting_visualizer`: 导入各类可视化保存函数
- `count_anything/eval/counting_meter.py` → `sam3.eval.counting_meter`: 导入CountingMeter指标类
- `count_anything/train/loss/pdc_loss.py` → `sam3.train.loss.loss_fns`: 导入LossWithWeights基类
- `count_anything/train/loss/rsc_loss.py` → `sam3.train.matcher`: 导入RSC匹配器和损失函数别名
- `count_anything/train/train.py` → `sam3.train.train`: 调用SAM3训练主函数
- `count_anything/inference.py` → `count_anything/model_builder.py`: 推理时通过build_count_anything_model构建模型
