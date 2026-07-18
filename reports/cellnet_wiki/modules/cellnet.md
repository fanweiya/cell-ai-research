# cellnet

> 稀疏噪声点标注定位相差显微镜图像中的细胞

cellnet 是一个用于在相差显微镜图像中定位细胞的深度学习模块。它通过加载预训练模型，处理图像数据，将稀疏噪声点标注转换为细胞位置预测。模块支持模型自动下载与版本管理、数据增强、训练评估、结果可视化以及与 GitHub API 的交互。核心流程包括：初始化模型、加载和预处理图像、执行前向推理、将预测的 heatmap 转换为点坐标，并计算评估指标。

## Files

### `cellnet/__init__.py`

模块入口，导出公共 API 并定义版本信息。

- `init_model` (function) - 初始化并返回预训练模型，支持从 GitHub 自动下载指定版本或最新兼容版本。
- `count` (function) - 对输入图像进行细胞计数和定位的主函数。
- `__model_api_version__` (constant) - 当前模块兼容的模型 API 版本号。
- `__version__` (constant) - cellnet 软件版本号。

### `cellnet/data.py`

提供数据加载、预处理、增强及格式转换的工具函数。

- `label2int` (dictionary) - 标签文本到整数类别的映射。
- `gpu` (function) - 将 numpy 数组转换为张量并移动到指定设备。
- `cpu` (function) - 将张量或列表转换回 numpy 数组。
- `imgid` (function) - 从文件路径提取图像 ID（文件名茎）。
- `batched` (function) - 装饰器，将函数应用于批次中的每个样本。
- `wrap_padded` (function) - 装饰器，对输入进行填充以满足模型对尺寸的要求，并裁剪输出。
- `ls` (function) - 列出目录中符合扩展名的文件。
- `_try_load` (function) - 尝试加载文件，失败时返回默认值或抛出异常。
- `load_image` (function) - 加载图像文件为 numpy 数组。

### `cellnet/debug.py`

提供执行时间统计和调试工具。

- `timeit` (decorator) - 装饰器，记录函数的执行时间并存储到全局字典。
- `print_times` (function) - 打印所有被装饰函数的平均和总执行时间。

### `cellnet/evaluate.py`

提供细胞定位任务的评估指标计算函数。

- `sMAPE_MAE_counts` (function) - 计算预测计数与真实计数的对称平均绝对百分比误差 (sMAPE) 和平均绝对误差 (MAE)。
- `sMAPE_MAE` (function) - 基于预测点和真实点列表计算 sMAPE 和 MAE。
- `prec_rec_f1` (function) - 基于点到点的匹配计算精确率、召回率和 F1 分数。

### `cellnet/internet.py`

封装 GitHub API 调用和文件下载功能。

- `GHAPI` (class) - GitHub API 客户端类，支持请求封装和分页处理。
- `get_latest_release` (method) - 获取仓库最新发布的标签名。
- `get_all_releases` (method) - 获取所有发布版本并按日期排序。
- `download` (function) - 带进度条的文件下载函数，支持断点续传和异常处理。

### `cellnet/plot.py`

提供图像和热力图的可视化函数。

- `heatmap` (function) - 将热力图叠加到图像上，支持透明度和颜色映射。
- `points` (function) - 在轴上绘制点坐标，支持自定义颜色和标记。
- `image` (function) - 显示图像，自动处理通道顺序和归一化。
- `overlay` (function) - 叠加图像、热力图、点坐标等多层信息。
- `diff` (function) - 显示目标热力图与预测热力图的差异。

### `cellnet/release.py`

管理模型版本、下载、初始化和图像加载逻辑。

- `is_compatible` (function) - 检查模型版本是否与当前 API 版本兼容。
- `get_newest_compatible_model_version` (function) - 从 GitHub 获取最新兼容的模型版本。
- `init_model` (function) - 下载、缓存并加载预训练模型，返回模型实例。
- `load_image` (function) - 从文件或路径加载图像，支持多种格式。

## Key Concepts

- **模型版本管理**: 通过 GitHub Releases 管理预训练模型，支持自动下载、缓存和版本兼容性检查，确保软件与模型的协同工作。
- **稀疏噪声点标注**: 使用稀疏的噪声点作为标注信号，通过深度学习模型学习将噪声点转换为准确的细胞位置，适用于标注成本高的场景。
- **数据增强与预处理**: 利用 albumentations 库进行图像增强，自动处理 BHWC 与 BCHW 格式转换，确保输入符合模型要求。
- **评估指标**: 提供 sMAPE、MAE 用于计数误差评估，精确率、召回率、F1 分数用于点定位精度评估，支持全面性能分析。
- **可视化**: 提供热力图叠加、点坐标绘制、差异比较等可视化功能，便于直观理解模型预测结果。

## Internal Relationships

- `cellnet/__init__.py` → `cellnet/release.py`: __init__.py 从 release.py 导入 init_model 和 count 作为公共 API。
- `cellnet/release.py` → `cellnet/data.py`: release.py 导入 data 模块用于图像加载和数据预处理。
- `cellnet/release.py` → `cellnet/internet.py`: release.py 使用 internet.py 中的 GHAPI 和 download 函数管理模型下载。
- `cellnet/release.py` → `cellnet/plot.py`: release.py 导入 plotting 模块用于结果可视化。
- `cellnet/evaluate.py` → `cellnet/data.py`: evaluate.py 可能使用 data.py 中的点坐标处理逻辑进行指标计算。
- `cellnet/plot.py` → `cellnet/data.py`: plot.py 可能依赖 data.py 中的图像 ID 提取和点坐标格式。
