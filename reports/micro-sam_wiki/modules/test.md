# test

> 测试 micro-sam 项目的核心功能、CLI 工具、模型集成及 GUI 组件。

该模块包含一系列单元测试和集成测试，用于验证 micro-sam 在图像分割、跟踪、提示生成、模型导出及命令行接口方面的正确性。测试覆盖 2D/3D 自动分割、基于提示的分割、实例分割、多尺度分割、PEFT 模型微调、生物图像格式导出以及 Napari 插件的 GUI 交互。

## Files

### `test/test_automatic_segmentation.py`

测试自动实例分割功能，包括标准模式和分块模式，支持 2D 和 3D 数据。

- `TestAutomaticSegmentation` (class) - 测试类，生成合成数据并验证 automatic_instance_segmentation 函数的输出形状和正确性。
- `_get_2d_inputs` (method) - 静态方法，生成包含三个对象的 2D 合成掩码和图像。
- `_get_3d_inputs` (method) - 类方法，通过堆叠带位移的 2D 切片生成 3D 合成数据。

### `test/test_bioimageio/test_model_export.py`

测试将 SAM 模型导出为 bioimage.io 规范格式的功能。

- `TestModelExport` (class) - 测试类，验证 export_sam_model 函数能否成功生成有效的导出文件。

### `test/test_cli.py`

测试命令行接口 (CLI) 命令的存在性及基本功能，如 annotator、precompute_embeddings 和 automatic_segmentation。

- `TestCLI` (class) - 测试类，验证 CLI 命令是否可执行并检查输出文件的有效性。
- `test_precompute_embeddings` (method) - 测试 precompute_embeddings 命令对单张图像和图像栈的处理，验证嵌入文件结构。
- `test_automatic_segmentation` (method) - 测试 automatic_segmentation 命令的 AMG 模式输出。

### `test/test_instance_segmentation.py`

测试实例分割模块，包括 AutomaticMaskGenerator 的初始化、生成、状态序列化及分块处理。

- `TestInstanceSegmentation` (class) - 测试类，验证实例分割流程的完整性和状态保持能力。
- `_test_instance_segmentation` (method) - 通用测试方法，检查分割精度、可重复性及状态序列化/反序列化。

### `test/test_models/test_peft_sam.py`

测试基于 PEFT (Parameter-Efficient Fine-Tuning) 的 SAM 模型变体，包括 LoRA、FacT 等。

- `TestPEFTSam` (class) - 测试类，验证不同 PEFT 模块 (LoRASurgery, FacTSurgery 等) 与 SAM 集成的输出形状。

### `test/test_models/test_sam_3d_wrapper.py`

测试 3D SAM 包装器模型，验证其输入输出张量形状是否符合 3D 分割要求。

- `TestSAM3DWrapper` (class) - 测试类，检查 get_sam_3d_model 生成的模型能否正确处理 3D 输入。

### `test/test_models/test_simple_sam_3d_wrapper.py`

测试简化版 3D SAM 包装器模型，验证其基本推理功能。

- `TestSimpleSAM3DWrapper` (class) - 测试类，检查 get_simple_sam_3d_model 生成的模型输出。

### `test/test_multi_dimensional_segmentation.py`

测试多维分割功能，包括 3D 实例分割的合并 (merge) 和跨帧跟踪 (track)。

- `TestMultiDimensionalSegmentation` (class) - 测试类，验证 merge_instance_segmentation_3d 和 track_across_frames 的逻辑正确性。

### `test/test_prompt_based_segmentation.py`

测试基于提示的分割功能，包括点提示、框提示和掩码提示在不同图像尺寸和分块模式下的表现。

- `TestPromptBasedSegmentation` (class) - 测试类，验证 segment_from_points 等函数在不同提示组合下的分割精度。

### `test/test_prompt_generators.py`

测试提示生成器，验证点/框提示生成器能否正确生成与真实标签一致的坐标和标签。

- `TestPromptGenerators` (class) - 测试类，检查 PointAndBoxPromptGenerator 生成的提示是否与 ground truth 匹配。

### `test/test_sam_annotator/test_annotator_2d.py`

集成测试 2D 标注器 GUI 组件，验证其在 Napari 中的初始化和显示。

- `test_annotator_2d` (function) - 测试函数，启动 annotator_2d 并检查图层初始化状态。

### `test/test_sam_annotator/test_annotator_3d.py`

集成测试 3D 标注器 GUI 组件，验证其在 Napari 中的初始化和显示。

- `test_annotator_3d` (function) - 测试函数，启动 annotator_3d 并检查图层初始化状态。

### `test/test_sam_annotator/test_annotator_tracking.py`

集成测试跟踪标注器 GUI 组件，验证其在 Napari 中的初始化和显示。

- `test_annotator_tracking` (function) - 测试函数，启动 annotator_tracking 并检查图层初始化状态。

### `test/test_sam_annotator/test_image_series_annotator.py`

集成测试图像序列和文件夹标注器，验证批量处理流程的 GUI 集成。

- `test_image_series_annotator` (function) - 测试函数，验证 image_series_annotator 的初始化。
- `test_image_folder_annotator` (function) - 测试函数，验证 image_folder_annotator 的初始化。

### `test/test_sam_annotator/test_imports.py`

测试 Napari 插件清单中所有命令的导入性，确保插件加载时不会因导入错误而崩溃。

- `test_napari_manifest_command_importable` (function) - 参数化测试函数，检查每个命令目标是否可解析。

### `test/test_sam_annotator/test_state.py`

测试标注器状态管理 (AnnotatorState) 的初始化和状态检查逻辑。

- `TestState` (class) - 测试类，验证 AnnotatorState 在交互分割和跟踪模式下的状态。

### `test/test_sam_annotator/test_widgets.py`

测试 Napari 插件中的 EmbeddingWidget 组件，验证嵌入计算和保存功能。

- `test_embedding_widget` (function) - 测试函数，检查 EmbeddingWidget 的推理、状态存储及文件输出。

### `test/test_training.py`

测试训练相关功能，包括数据集构建和模型训练流程（部分测试在 CI 中被跳过）。

- `TestDataset` (class) - 测试类，验证 default_sam_dataset 生成的数据集结构和形状。
- `TestTraining` (class) - 测试类，集成测试 SAM 模型的训练流程（通常被跳过）。

### `test/test_util.py`

测试工具函数，包括模型获取、IoU 计算、NMS 应用及预计算嵌入设置。

- `TestUtil` (class) - 测试类，验证 util 模块中核心函数的正确性。
- `test_model_registry` (method) - 检查模型注册表中所有 URL 的有效性。
- `test_get_sam_model` (method) - 验证 get_sam_model 返回的预测器类型和属性。
- `test_apply_nms_tiled_border_masks` (method) - 测试 apply_nms 函数在分块边界掩码处理上的正确性。

### `test/test_vendored.py`

测试 vendored 模块中的底层算子，如 mask_to_box 和 mask_to_rle_pytorch，确保其与 SAM 官方实现一致。

- `TestVendored` (class) - 测试类，验证 batched_mask_to_box 和 mask_to_rle_pytorch 的输出正确性。

## Key Concepts

- **Automatic Mask Generator (AMG)**: 无需用户提示即可自动检测图像中所有实例的分割模块，测试覆盖其 2D/3D 及分块推理模式。
- **Prompt-Based Segmentation**: 基于点、框或掩码提示进行交互式分割的功能，测试验证不同提示组合下的分割精度。
- **State Management**: 标注器应用中的状态持久化机制，支持分割状态的保存、加载和序列化，确保交互连续性。
- **PEFT (Parameter-Efficient Fine-Tuning)**: 对 SAM 模型进行高效微调的技术，测试涵盖 LoRA、FacT 等多种微调策略的集成。
- **3D Segmentation & Tracking**: 处理三维体积数据及时间序列数据的分割与跟踪功能，包括实例合并和跨帧关联。
- **Napari Plugin Integration**: 将 micro-sam 功能集成到 Napari 图像查看器中的 GUI 组件测试，包括标注器和小部件。

## Internal Relationships

- `test/test_automatic_segmentation.py` → `micro_sam.automatic_segmentation`: 导入并测试 automatic_instance_segmentation 和 get_predictor_and_segmenter 函数。
- `test/test_instance_segmentation.py` → `micro_sam.instance_segmentation`: 导入并测试 AutomaticMaskGenerator 类及其相关功能。
- `test/test_prompt_based_segmentation.py` → `micro_sam.prompt_based_segmentation`: 导入并测试 segment_from_points 等提示分割函数。
- `test/test_sam_annotator/*.py` → `micro_sam.sam_annotator`: 导入并测试 Napari 插件的 GUI 组件、状态管理和小部件。
- `test/test_util.py` → `micro_sam.util`: 导入并测试核心工具函数，如模型加载、嵌入预计算和 IoU 计算。
- `test/test_models/*.py` → `micro_sam.models`: 导入并测试 PEFT SAM、3D SAM 包装器等模型变体。
- `test/test_multi_dimensional_segmentation.py` → `micro_sam.multi_dimensional_segmentation`: 导入并测试 3D 分割合并和跟踪函数。
