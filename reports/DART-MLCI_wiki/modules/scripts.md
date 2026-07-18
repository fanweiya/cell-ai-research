# scripts

> 提供从图像预处理、芯片校准、实验处理到结果分析和可视化的完整命令行工具链

该模块包含一系列Python脚本和Shell脚本，用于支持微流控芯片蓝图文本与显微镜图像的对齐和实时细胞分析。核心功能包括：批量图像掩膜处理、芯片校准、时间序列实验处理、生长分析、基准测试以及演示视频生成。这些脚本是DART-MLCI项目的用户接口，封装了底层dart_mlci库的功能，并处理文件I/O、参数解析和结果输出。

## Files

### `scripts/analyze_growth.py`

分析处理后的实验输出，计算细胞生长统计并生成图表

- `parse_args` (function) - 解析命令行参数，支持输出目录、配置JSON、面积过滤、生长曲线拟合等选项
- `_load_all` (function) - 加载并过滤所有cells.csv文件，返回包含统计数据和数据框的字典
- `OKABE_ITO` (constant) - 色盲安全调色板，用于区分不同实验组

### `scripts/batch_masking.py`

批量处理图像掩膜流程，提供详细的通过/失败报告和调试输出

- `BatchMaskingRunner` (class) - 对多张图像运行掩膜流程的类，支持不同腔室类型
- `ImageResult` (dataclass) - 存储单张图像处理结果的类，包含成功状态、错误信息和部分结果
- `_get_chamber_components` (method) - 获取或创建特定腔室类型的流程组件

### `scripts/benchmark.py`

测量掩膜流程每个步骤的执行时间和GPU内存使用

- `PipelineBenchmark` (class) - DMC掩膜流程的基准测试运行器
- `warmup` (method) - 运行预热迭代以稳定GPU/JIT编译
- `run_benchmark` (method) - 执行基准测试并收集性能数据

### `scripts/calibrate_map.py`

从已知显微镜台位置的校准图像中估计地图变换

- `calibrate_map` (function) - 主校准函数，处理校准图像并生成显微镜坐标下的Map
- `crop_calibration_image` (function) - 使用无旋转掩膜方法裁剪校准图像
- `process_calibration_image` (function) - 处理单个校准图像的包装函数

### `scripts/calibrate_pixel_scale.py`

通过比较检测到的标记距离与物理距离来验证像素校准

- `main` (function) - 主函数，加载配置并计算实际像素大小

### `scripts/generate_chip_config.py`

从遗留文件生成统一的芯片配置文件

- `main` (function) - 读取chamber_structure.json和blueprint_map.csv，输出统一的芯片配置JSON

### `scripts/generate_dart_frame_video.py`

为单个Dart实验帧渲染流程演示视频

- `_parse_args` (function) - 解析输入模式（元数据或TIFF堆栈）和流程配置参数

### `scripts/generate_golden_files.py`

为回归测试生成黄金文件

- `generate_calibration_golden` (function) - 运行校准并保存校准位置、变换参数和图像结果的JSON文件

### `scripts/generate_sak_videos.py`

为所有SAK腔室类型生成流程演示视频和/或静态图像

- `generate_pipeline_video` (function) - 渲染流程步骤的视频
- `load_image` (function) - 加载图像并处理.tif格式归一化
- `_add_scalebar_cv` (function) - 在帧的右下角绘制物理长度比例尺

### `scripts/make_demo_assets.sh`

从MP4生成README的演示媒体（英雄GIF和每个腔室的缩略图）

- `main` (function) - 使用ffmpeg处理视频，生成优化的GIF和缩略图

### `scripts/prepare_calibration_data.py`

为可重复性准备校准数据zip文件

- `select_validation_images` (function) - 使用贪婪最远点采样策略选择空间分布的验证图像
- `build_calibration_config` (function) - 构建calibration_config.json内容

### `scripts/process_experiment.py`

使用完整的DMC掩膜和细胞分割流程处理实验数据集

- `render_cropped_visualization` (function) - 渲染带有彩色细胞、腔室掩膜和比例尺的可视化图像
- `render_uncropped_visualization` (function) - 渲染未裁剪的可视化，突出显示ROI并叠加细胞

### `scripts/process_folder.py`

处理按腔室类型组织的文件夹中的时间序列TIFF堆栈

- `collect_files` (function) - 从配置的文件夹中收集所有TIFF文件
- `process_stack` (function) - 处理单个TIFF堆栈，执行掩膜和细胞分割
- `render_frame_visualization` (function) - 渲染单帧的细胞可视化

### `scripts/process_image.py`

通过DMC掩膜流程处理单张图像

- `process_image` (function) - 在图像上运行完整的掩膜流程，返回裁剪图像、掩膜和计时
- `print_success` (function) - 打印结构化的成功消息

### `scripts/run_timelapse_full.sh`

完整的时间序列堆叠管道（所有ROI）

- `main` (function) - 执行process_experiment.py处理所有ROI

### `scripts/run_timelapse_stacking.sh`

时间序列堆叠管道，支持可选的配准

- `main` (function) - 构建并执行处理命令

### `scripts/test_api_endpoints.py`

测试DMC掩膜API端点

- `test_health` (function) - 测试/health端点
- `test_chamber_types` (function) - 测试/chamber-types端点
- `test_process_image` (function) - 测试/process-image端点

### `scripts/test_timelapse_quick.sh`

快速测试时间序列堆叠管道（仅1个ROI）

- `main` (function) - 运行process_experiment.py处理单个ROI

### `scripts/validate_map.py`

比较计算的腔室位置与校准地图

- `run_validation_cli` (function) - 运行完整的验证流程
- `process_validation_image` (function) - 处理单个验证图像

## Key Concepts

- **DMC掩膜流程**: 检测标记（cross/circle）→ 匹配标记 → 计算旋转角度 → 旋转图像 → 应用ROI掩膜 → 可选细胞分割
- **芯片配置**: 统一的JSON文件，包含腔室多边形、标记位置、ROI模式和蓝图文本映射
- **校准地图**: 将图像坐标映射到显微镜物理坐标的仿射变换，通过已知台位置的校准图像计算
- **时间序列处理**: 支持TIFF堆栈的时间序列处理，包括帧间配准和堆叠
- **腔室类型**: 不同微流控芯片结构（如NormaleBox、BigBox、OpenBox、Mothermachine）有特定的标记模式和ROI形状

## Internal Relationships

- `scripts/analyze_growth.py` → `dart_mlci.analysis`: 导入compute_growth_stats、load_cells_data等分析函数
- `scripts/batch_masking.py` → `dart_mlci`: 使用ChamberPipelineCache、MarkerDetectionStep等核心组件
- `scripts/calibrate_map.py` → `dart_mlci.calibration`: 调用process_calibration_image和run_calibration函数
- `scripts/generate_sak_videos.py` → `dart_mlci.visualization`: 使用render_markers_to_frame、add_step_title等可视化函数
- `scripts/process_experiment.py` → `scripts/process_folder.py`: 两者都使用类似的渲染和流程处理逻辑
- `scripts/process_folder.py` → `dart_mlci.mask`: 使用filter_segmentation_by_area和filter_segmentation_by_mask
- `scripts/process_image.py` → `dart_mlci`: 直接使用MarkerDetectionStep、MarkerMatchingStep等步骤类
- `scripts/validate_map.py` → `dart_mlci.calibration.validation`: 导入ValidationResult和process_validation_image
