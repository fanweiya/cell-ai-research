# src

> 提供时间分辨显微图像细胞追踪的核心算法、数据处理、结果格式化和可视化功能。

该模块实现了从原始图像读取、预处理（重缩放、裁剪、配准）、单细胞检测（基于单色信号和形态学滤波）、光流追踪到CTC格式输出及性能评估的完整流水线。包含参数扫描工具用于优化检测阈值和细胞尺寸，以及用于生成出版级图表的可视化函数。

## Files

### `algo_funcs.py`

核心算法库，包含图像I/O、预处理、配准和追踪的基础函数。

- `read_images` (function) - 读取目录下的图像序列，支持灰度或彩色模式，返回numpy数组列表。
- `save_images` (function) - 将图像数组列表保存为TIF文件，支持通配符文件名模式。
- `rescale_rgb_to_255` (function) - 将指定通道的图像数据线性重缩放至0-255范围，用于标准化显示。
- `clip_images` (function) - 基于百分位数裁剪图像亮度，抑制异常高亮值并重新归一化。
- `image_registration` (function) - 使用ITK将移动图像配准到固定图像，支持单通道或全图配准。

### `algo_funcs_old.py`

包含较旧的或备选的图像处理算法，如单色信号滤波和细胞检测。

- `create_monogenic_filters_log_gabor` (function) - 构建基于对数高斯滤波器的单色信号分析滤波器组。
- `monogenic_signal` (function) - 计算图像的单色信号分量（偶分量、Riesz变换奇分量）。
- `local_energy` (function) - 计算单色信号局部能量，用于细胞边缘或核检测。
- `monogenic_filter_single_image` (function) - 对单张图像应用单色滤波和形态学处理，输出增强后的图像。
- `monogenic_filter_images` (function) - 并行处理图像列表，应用单色滤波。

### `ctc_reformat.py`

负责将追踪结果转换为CTC标准格式并生成可视化掩膜。

- `save_track_images` (function) - 根据追踪路径生成每帧的彩色掩膜图像，用于可视化。
- `generate_mask` (function) - 合并多个对象的分割掩膜和追踪路径，生成时间序列标签图。
- `save_ctc_format` (function) - 将追踪数据保存为CTC标准格式，包括每帧标签图像和res_track.txt文件。

### `display_funcs.py`

提供数据可视化工具，特别是均方位移(MSD)分析图表。

- `calculate_mean_square_displacement` (function) - 计算细胞追踪路径的均方位移(MSD)曲线。
- `plot_mean_square_displacement_filtered` (function) - 绘制包含所有细胞和筛选后细胞的MSD曲线及均值±标准误，用于发表级图表。

### `parameter_scan.py`

执行参数扫描并可视化不同参数组合下的追踪性能指标。

- `plot_parameter_surfaces` (function) - 生成3D曲面图，展示检测率(DET)和追踪率(TRA)随细胞尺寸和裁剪阈值的变化。
- `plot_parameter_metrics` (function) - 生成参数指标的热力图或等高线图（代码截断，功能推断）。

### `utils.py`

主执行脚本，整合各模块完成端到端的细胞追踪流程。

- `main` (function) - 读取图像和掩膜，执行细胞检测、光流追踪，保存CTC格式结果，并计算评估指标(DET, TRA, SEG)。

## Key Concepts

- **单色信号分析 (Monogenic Signal Analysis)**: 利用对数高斯滤波器和Riesz变换提取图像的局部能量和相位信息，用于在低对比度显微图像中检测细胞核或边缘。
- **光流追踪 (Optical Flow Tracking)**: 基于图像序列的像素运动估计，将单帧检测到的细胞中心点连接成时间轨迹。
- **CTC格式 (CTC Format)**: 细胞追踪竞赛标准格式，包含每帧的标签图像和res_track.txt文件，用于评估检测率和追踪率。
- **均方位移 (MSD)**: 衡量细胞运动性的指标，通过计算位移平方的平均值随时间的变化来量化细胞的迁移模式。

## Internal Relationships

- `utils.py` → `algo_funcs.py`: utils.py 导入 algo_funcs 用于读取图像、执行光流追踪和保存结果。
- `utils.py` → `ctc_reformat.py`: utils.py 导入 ctc_reformat 用于将追踪数据保存为CTC标准格式。
- `parameter_scan.py` → `algo_funcs.py`: parameter_scan.py 导入 algo_funcs 进行图像预处理和追踪操作。
- `parameter_scan.py` → `ctc_reformat.py`: parameter_scan.py 导入 ctc_reformat 用于格式化输出。
- `algo_funcs_old.py` → `algo_funcs.py`: algo_funcs_old.py 与 algo_funcs.py 功能重叠，可能作为旧版本或特定算法的补充。
