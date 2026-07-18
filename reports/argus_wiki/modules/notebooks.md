# notebooks

> 提供时间分辨显微图像细胞追踪的交互式实验与评估流程

notebooks 模块包含两个核心 Jupyter Notebook，分别负责细胞轨迹的计算与 CTC 指标评估。compute_cell_paths.ipynb 用于从原始图像序列中恢复细胞位置并生成轨迹，依赖 src 模块中的算法函数；format_tracks_for_CTC.ipynb 则加载预测轨迹，将其转换为 CTC 评估工具所需格式，并计算 DET、SEG、TRA 三项指标。两个 notebook 均通过 sys.path 动态导入 src 模块，实现数据读取、预处理、轨迹生成与结果验证的完整工作流。

## Files

### `notebooks/compute_cell_paths.ipynb`

读取时间序列显微图像，执行细胞分割与追踪，生成细胞轨迹数据

- `algo.read_images` (function) - 按指定模式读取图像序列，支持灰度与彩色通道处理
- `algo.batch_rescale_rgb_to_255` (function) - 将图像批量归一化至 [0,255] 范围
- `IMAGE_PATHS_PATTERN` (variable) - 定义图像文件路径的通配符模式，需包含前导零的时间编号
- `IMAGE_CHANNEL` (variable) - 指定用于分析的图像通道（0=红，1=绿，2=蓝）

### `notebooks/format_tracks_for_CTC.ipynb`

将追踪结果转换为 CTC 评估格式并计算检测、分割与追踪指标

- `ctc_metrics.evaluate_sequence` (function) - 执行 CTC 指标评估，返回 DET、SEG、TRA 评分
- `ctc_metrics.validate_sequence` (function) - 验证轨迹数据格式是否符合 CTC 要求
- `GRAPH_OUTPUT_PATH` (variable) - 存储预测轨迹图的输出目录

## Key Concepts

- **CTC 指标评估**: 采用 Cell Tracking Challenge 标准，通过 DET（检测）、SEG（分割）、TRA（追踪）三项量化追踪性能
- **时间序列图像模式匹配**: 使用通配符模式（如 t*.tif）加载按时间顺序编号的图像序列，要求编号含前导零以确保正确排序
- **模块动态加载**: 通过修改 sys.path 将 src 目录加入导入路径，使 notebook 能访问核心算法与工具模块

## Internal Relationships

- `notebooks/compute_cell_paths.ipynb` → `src/algo_funcs.py`: 导入 algo_funcs 模块以调用图像读取、预处理及追踪算法函数
- `notebooks/format_tracks_for_CTC.ipynb` → `src/ctc_metrics.py`: 导入 ctc_metrics 模块以验证和评估追踪结果
- `notebooks/compute_cell_paths.ipynb` → `notebooks/format_tracks_for_CTC.ipynb`: 前者生成的轨迹数据是后者评估的输入来源
