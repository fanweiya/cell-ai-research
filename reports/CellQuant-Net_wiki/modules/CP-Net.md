# CP-Net

> 用于全切片图像(WSI)中细胞核检测、分类及质量评估的端到端推理流水线。

CP-Net 是一个基于深度学习的细胞核分析系统，通过双通道输入（HE 染色图像 + 提取的 H 通道）实现高精度的细胞核分割与分类。系统包含预处理、模型推理、后处理、空间关系分析及结果导出功能，支持 20x 和 40x 不同放大倍率，输出符合 QuPath 标准的 GeoJSON 文件及可视化图像。

## Files

### `CP-Net/cell_connectivitey.py`

处理细胞核的空间关系分析，构建邻域图并计算免疫浸润评分。

- `build_radius_graph` (function) - 基于欧氏距离半径构建细胞核邻域图，节点包含坐标、类型及原始 ID。
- `immune_infiltration_score` (function) - 计算肿瘤细胞周围免疫细胞的平均比例，量化免疫浸润程度。
- `save_geojson` (function) - 将特征数据保存为 GeoJSON 格式，用于 QuPath 导入。

### `CP-Net/configs/configs_test.yaml`

存储模型推理的配置参数，包括数据路径、模型结构、后处理阈值及颜色映射。

- `postprocessing` (config_section) - 定义不同放大倍率下的形态学处理参数，如腐蚀半径、最小面积等。
- `model` (config_section) - 指定骨干网络（unireplknet_n）及分类头参数（4类：背景、肿瘤、TILs、其他）。

### `CP-Net/dataset.py`

定义数据集类与数据加载逻辑，负责 HE 图像与 H 通道的预处理及增强。

- `extract_H_channel` (function) - 从 RGB 图像中通过光密度转换提取 H 通道（Hematoxylin），用于增强核特征。
- `Load_Dataset` (class) - 继承自 torch.utils.data.Dataset，处理图像路径管理、H 通道生成及 Albumentations 增强。

### `CP-Net/model/model.py`

定义 CP-Net 主网络架构，整合 UniRepLKNet 骨干与双任务解码头。

- `CellPriorNet` (class) - 主模型类，接收 RGB 和 H 通道输入，输出二值掩膜和类型分类图。
- `RingBank` (class) - 环形核模块，用于提取多尺度环形特征，增强核边缘检测能力。
- `get_conv2d` (function) - 根据环境配置选择标准卷积或优化的 iGEMM 大核卷积实现。

### `CP-Net/model/unirepLKnet.py`

实现 UniRepLKNet 骨干网络，支持大核深度卷积以提升感受野和特征提取能力。

- `GRNwithNHWC` (class) - 全局响应归一化层，基于 ConvNeXt V2，用于特征重校准。
- `get_conv2d` (function) - 决定使用原生卷积还是 iGEMM 加速的大核卷积。

### `CP-Net/post_process.py`

执行模型输出后处理，包括实例分割、大小分类及距离图计算。

- `gpu_split_small_med_big_vbig_binary` (function) - 在 GPU 上将二值掩膜按面积分割为小、中、大、超大四类实例。
- `torch_to_cupy` (function) - 通过 DLPack 在 torch 张量和 CuPy 数组间零拷贝转换，加速形态学操作。
- `process_mask_batch_dist_map` (function) - 批量处理掩膜并计算实例间的距离图。

### `CP-Net/qupath_jsn.py`

生成 QuPath 兼容的 GeoJSON 文件，将检测结果转换为细胞对象。

- `make_qupath_cell_feature` (function) - 将单个细胞核的坐标和类型转换为 QuPath 的 Feature 对象。
- `save_qupath_geojson` (function) - 将特征列表保存为 GeoJSON 文件。

### `CP-Net/spli_H.py`

独立脚本，用于批量预处理图像，提取 H 通道并保存。

- `normalize_staining_H` (function) - 实现 H 通道提取算法，基于光密度变换和主成分分析。

### `CP-Net/test_cp_net.py`

主推理入口脚本，协调数据加载、模型预测、后处理及结果保存。

- `infer_magnification_from_ckpt_name` (function) - 根据检查点文件名自动推断图像放大倍率（20x/40x）。
- `_forward_flexible` (function) - 处理模型输入，支持双通道或四通道拼接输入。
- `save_classify_dots` (function) - 在原始图像上绘制分类点并保存可视化结果。

## Key Concepts

- **双通道输入 (HE + H)**: 模型同时接收标准 RGB 图像和提取的 H 通道（苏木精染色通道），利用 H 通道增强细胞核对比度，提高分割精度。
- **UniRepLKNet 骨干**: 采用大核卷积网络（Large-Kernel ConvNet）作为特征提取器，通过堆叠大卷积核扩大感受野，捕捉长距离依赖。
- **GPU 加速后处理**: 使用 CuPy 和 DLPack 实现 torch 张量与 GPU 数组的零拷贝交互，加速形态学操作和连通域分析。
- **QuPath 兼容性**: 输出结果包含 GeoJSON 格式的空间标注和可视化图像，可直接导入 QuPath 进行病理学分析。

## Internal Relationships

- `test_cp_net.py` → `dataset.py`: test_cp_net 导入 Load_Dataset 进行数据加载和预处理。
- `test_cp_net.py` → `model/model.py`: test_cp_net 实例化 CellPriorNet 模型并执行前向推理。
- `test_cp_net.py` → `post_process.py`: test_cp_net 调用后处理函数对模型输出进行实例分割和类型分配。
- `test_cp_net.py` → `cell_connectivitey.py`: test_cp_net 使用邻域分析函数计算空间关系指标。
- `test_cp_net.py` → `qupath_jsn.py`: test_cp_net 将最终检测结果转换为 QuPath 格式并保存。
- `dataset.py` → `spli_H.py`: dataset.py 中的 extract_H_channel 函数逻辑与 spli_H.py 中的 normalize_staining_H 高度相似，用于 H 通道提取。
- `model/model.py` → `model/unirepLKnet.py`: model.py 导入 UniRepLKNet 作为骨干网络。
