# metrics

> 计算视频质量指标、评估模型性能并生成可视化报告。

该模块用于处理细胞行为视频，计算信噪比（SNR）、细胞密度等质量指标，评估不同模型在分类任务上的表现（AUC、精确率、召回率等），并生成分布图、ROC曲线和按细胞数量/SNR分组的性能分析图。

## Files

### `metrics/compute_quality_metrics.py`

读取视频和追踪数据，计算每个视频帧的质量指标（SNR、对比度、异质性、密度、细胞数量）。

- `load_paths` (function) - 扫描数据集目录，匹配视频文件（.avi）和追踪文件（.csv），返回公共键值的字典。
- `process_videos` (function) - 核心处理函数。遍历视频，提取前景/背景区域，计算SNR、CR、HET、密度（DEN）和细胞数量（NUM），并将结果存入数组。

### `metrics/descriptives.py`

生成数据集类别分布和指标分布的可视化图表。

- `plot_class_distribution` (function) - 绘制训练集、验证集、测试集中不同类别（0/1）的视频片段数量分布柱状图。
- `plot_metric_distributions` (function) - 绘制细胞数量（N.TRACKS）和信噪比（SNR）在不同数据集划分中的直方图分布。

### `metrics/generate_gt.py`

根据目录结构自动生成包含文件名和类别标签的CSV文件。

- `generate_label_csv` (function) - 递归遍历根目录下的子集和类别文件夹，提取.avi文件名并标记类别（0或1），输出为CSV。

### `metrics/ncell_curves.py`

按细胞数量分组评估模型性能，并绘制分数随细胞数量变化的曲线及排名图。

- `compute_score_per_cell_count` (function) - 将模型预测数据与细胞数量数据合并，按细胞数量分桶计算AUC、精确率、召回率等指标，并计算综合得分。
- `plot_score_vs_cells` (function) - 绘制各模型在不同细胞数量下的综合得分曲线，并在下方子图中绘制排名条形图。

### `metrics/overall_metrics.py`

计算所有模型在测试集上的整体评估指标。

- `evaluate_models` (function) - 遍历数据集中的预测列，计算AUC、精确率、召回率、平衡准确率及混淆矩阵，生成按综合得分排序的指标DataFrame。

### `metrics/roc_curves.py`

绘制所有模型的ROC曲线并计算AUC值。

- `clean_model_name` (function) - 清理模型名称，移除括号内容并将长名称缩写。
- `plot_roc_curves` (function) - 计算并绘制各模型的ROC曲线，标注AUC值，按AUC降序排列图例。

### `metrics/snr_curves.py`

按信噪比（SNR）分组评估模型性能，并绘制分数随SNR变化的曲线及排名图。

- `compute_score_by_snr` (function) - 将模型数据与SNR指标合并，按SNR分桶计算各模型的综合得分。
- `plot_score_vs_snr` (function) - 绘制各模型在不同SNR区间下的综合得分曲线，并在下方子图中绘制排名条形图。

### `metrics/upload_files.py`

加载和预处理提交文件，构建包含所有模型预测和真实标签的合并数据集。

- `load_track_counts` (function) - 读取追踪CSV文件，统计每个视频中的唯一细胞ID数量。
- `preprocess_submission` (function) - 清洗提交数据，过滤无效分数，去重，转换时间戳格式。
- `build_all_data` (function) - 将多个团队的预测文件与真实标签（gt）合并，生成包含所有文件ID和模型预测列的统一DataFrame。

## Key Concepts

- **综合得分 (Score)**: 由0.4*AUC + 0.2*(Precision + Recall + Balanced Accuracy)计算得出，用于平衡评估模型性能。
- **信噪比 (SNR)**: 前景平均强度与背景标准差之比，用于衡量视频图像质量。
- **细胞密度 (DEN)**: 通过计算细胞间最近邻距离来量化视频帧中细胞的密集程度。
- **数据合并 (Merge)**: 将预测文件、追踪计数、真实标签通过file_id进行外连接，形成统一的评估数据集。

## Internal Relationships

- `metrics/upload_files.py` → `metrics/overall_metrics.py`: upload_files.py构建的all_data DataFrame被overall_metrics.py用于计算整体指标。
- `metrics/upload_files.py` → `metrics/ncell_curves.py`: upload_files.py生成的all_data和counts数据被ncell_curves.py用于按细胞数量分析性能。
- `metrics/upload_files.py` → `metrics/snr_curves.py`: upload_files.py生成的all_data和quality_metric数据被snr_curves.py用于按SNR分析性能。
- `metrics/compute_quality_metrics.py` → `metrics/descriptives.py`: compute_quality_metrics.py计算的质量指标（如SNR, N.TRACKS）被descriptives.py用于绘制分布图。
- `metrics/generate_gt.py` → `metrics/upload_files.py`: generate_gt.py生成的gt.csv被upload_files.py中的load_gt函数读取以构建真实标签数据。
