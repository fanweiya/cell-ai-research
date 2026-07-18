# root

> CBVCC挑战赛的评估与分析工具包，用于处理细胞行为视频分类任务的指标计算、结果评估及可视化。

该项目旨在为细胞行为视频分类挑战赛（CBVCC）提供完整的分析流水线。主要功能包括：基于文件夹结构生成标签CSV、计算视频质量指标（信噪比SNR、跟踪细胞数N.TRACKS）、评估参赛队伍的预测结果（Phase 1验证集和Phase 2测试集），并生成ROC曲线、分数与细胞数量/信噪比关系图等可视化报告。核心流程由run_analysis.py编排，依赖metrics子模块进行数据处理和绘图。

## Files

### `run_analysis.py`

主入口脚本，负责加载数据、调用评估函数并生成所有可视化图表。

- `load_analysis` (function) - 加载特定阶段（Phase 1或2）的数据，包括跟踪计数、真实标签和提交预测，执行模型评估并将结果保存为CSV。
- `main` (function) - 解析命令行参数，按顺序处理Phase 2和Phase 1数据，调用metrics子模块绘制ROC曲线、分数-细胞数曲线、分数-SNR曲线及分布直方图。

### `metrics/generate_gt.py`

根据数据集文件夹结构自动生成包含视频文件名和类别标签（0或1）的CSV文件。

### `metrics/compute_quality_metrics.py`

计算视频质量指标，包括信噪比（SNR）和跟踪到的细胞数量（N.TRACKS）。

### `metrics/upload_files.py`

提供数据加载和预处理工具函数，用于读取跟踪文件、真实标签和提交预测。

- `load_track_counts` (function) - 加载跟踪CSV文件并提取细胞数量信息。
- `load_gt` (function) - 加载真实标签CSV文件。
- `preprocess_submission` (function) - 预处理参赛队伍的提交预测文件。
- `build_file_timestamp_dict` (function) - 根据时间戳模式匹配提交文件。
- `build_all_data` (function) - 整合提交数据、时间戳和真实标签，构建完整的分析数据集。

### `metrics/roc_curves.py`

负责绘制ROC曲线。

- `plot_roc_curves` (function) - 根据评估数据绘制ROC曲线并保存图像。
- `clean_model_name` (function) - 清理模型名称以便在图表中显示。

### `metrics/overall_metrics.py`

计算模型的整体性能指标（如准确率、精确率、召回率、AUC等）。

- `evaluate_models` (function) - 对整合后的数据进行批量评估，返回包含各项指标的DataFrame。

### `metrics/ncell_curves.py`

绘制模型分数与跟踪细胞数量（N.TRACKS）关系的散点图。

- `plot_score_vs_cells` (function) - 生成分数随细胞数量变化的可视化图表。

### `metrics/snr_curves.py`

绘制模型分数与信噪比（SNR）关系的散点图。

- `plot_score_vs_snr` (function) - 生成分数随信噪比变化的可视化图表。

### `metrics/descriptives.py`

生成描述性统计图表，包括类别分布和指标分布。

- `plot_class_distribution` (function) - 绘制训练、验证和测试集的类别分布直方图。
- `plot_metric_distributions` (function) - 绘制质量指标（如SNR、N.TRACKS）的分布直方图。

### `eval_code.php`

独立的PHP脚本，用于计算分类指标（TP, FP, FN, TN, AUC等），非Python流水线的一部分。

- `calculate_metrics` (function) - 计算混淆矩阵各项指标、AUC及平衡准确率。
- `parse_csv` (function) - 解析CSV文件为关联数组。

## Key Concepts

- **CBVCC挑战**: 细胞行为视频分类挑战赛，目标是区分细胞运动模式突变与线性运动、静止或纯背景的视频。
- **Phase 1 & Phase 2**: 挑战赛的验证阶段（Phase 1）和测试阶段（Phase 2），分别对应不同的数据集和评估标准。
- **质量指标**: SNR（信噪比）和N.TRACKS（跟踪细胞数），用于分析模型性能与视频质量的相关性。
- **ROC与AUC**: 受试者工作特征曲线（ROC）和曲线下面积（AUC），用于评估分类器在不同阈值下的性能。

## Internal Relationships

- `run_analysis.py` → `metrics/upload_files.py`: 导入数据加载和预处理函数。
- `run_analysis.py` → `metrics/roc_curves.py`: 导入绘图函数以生成ROC曲线。
- `run_analysis.py` → `metrics/overall_metrics.py`: 导入模型评估函数以计算性能指标。
- `run_analysis.py` → `metrics/ncell_curves.py`: 导入函数以绘制分数与细胞数的关系图。
- `run_analysis.py` → `metrics/snr_curves.py`: 导入函数以绘制分数与SNR的关系图。
- `run_analysis.py` → `metrics/descriptives.py`: 导入函数以生成类别和指标分布图。
