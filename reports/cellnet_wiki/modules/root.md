# root

> CellNet 项目的根模块，用于在相差显微镜图像中利用稀疏和噪声中心点标注定位细胞。

该模块包含一个 Python 包 `cellnet`，提供细胞计数和定位功能。核心功能包括模型初始化、图像加载、推理和评估。项目支持通过命令行或 Python API 使用预训练模型，也包含完整的训练流程、数据预处理脚本和评估工具。主要依赖 PyTorch 和 segmentation-models-pytorch 构建 U-Net 架构的深度学习模型，输入为相差显微镜图像，输出为细胞密度图，通过峰值检测提取细胞中心点。

## Files

### `README.md`

项目文档，包含安装、使用、训练和发布指南。

### `pyproject.toml`

项目依赖配置和打包设置，定义 Python 版本、依赖包及可选的 CPU/CUDA 支持。

### `cellnet.yml`

Conda 环境配置文件，用于创建包含 PyTorch、CUDA 及相关科学计算库的虚拟环境。

### `labelstudio.yml`

Label Studio 标注工具的 Conda 环境配置。

### `preprocess_annotations.py`

将 Label Studio 导出的标注数据转换为内部训练格式（点标注和掩码），并保存到缓存目录。

- `convert_labelstudio_project` (function) - 解析单个 Label Studio 项目 JSON，提取点标注和刷选掩码，保存为 numpy 文件。
- `main` (function) - 遍历 data/annotations 目录，批量转换所有标注文件，并为缺失标注的图像生成空文件。

### `preprocess_annotations_livecell.py`

将 LIVECell 数据集的 COCO 格式标注转换为内部点标注格式。

- `convert_coco_project` (function) - 读取 COCO 标注文件，计算每个掩码的中心点，保存为 numpy 文件。
- `main` (function) - 处理指定的 COCO 文件，生成点标注缓存。

### `train.py`

主训练脚本，配置实验参数、数据分割，并启动模型训练流程。

- `experiments` (dictionary) - 定义不同实验模式（如 default, draft, release）及超参数搜索范围。
- `CFG` (object) - 根据环境变量和模式动态构建的训练配置对象。

### `train_livecell.py`

针对 LIVECell 数据集的训练脚本，结构与 train.py 类似但数据路径不同。

- `experiments` (dictionary) - 定义实验配置。
- `CFG` (object) - LIVECell 数据集的训练配置对象。

### `eval.py`

在单张图像上评估 CellNet 模型性能，生成可视化结果和指标。

- `init_model` (function) - 初始化本地模型。
- `load_image` (function) - 加载并预处理图像。
- `load_points` (function) - 加载点标注数据。

### `eval_livecell.py`

在 LIVECell 测试集上批量评估 CellNet 模型，输出 CSV 格式评估结果。

- `get_test_images` (function) - 从 COCO 文件加载测试图像列表。
- `infer` (function) - 执行模型推理。

### `cpsam-livecell.py`

使用 Cellpose-SAM 作为基线模型在 LIVECell 数据集上进行评估。

- `get_test_images` (function) - 获取测试图像列表。

### `eval_countess.py`

对比 CellNet 与 Countess 仪器计数结果的脚本，计算皮尔逊相关系数并绘图。

### `cellnet-vs-countess-all.csv`

存储 CellNet 与 Countess 计数结果对比数据。

### `evaluations_cpsam_livecell.csv`

存储 Cellpose-SAM 基线模型的评估结果。

## Key Concepts

- **稀疏噪声点标注**: 训练数据使用稀疏且含噪声的中心点标注，而非完整的像素级掩码，模型需从这些不精确的标注中学习细胞定位。
- **密度图回归**: 模型输出为细胞密度图，通过高斯核将点标注平滑为连续密度图，训练目标为最小化预测密度图与目标密度图之间的损失（如 MSE+BCE）。
- **峰值检测**: 推理阶段使用 skimage.feature.peak_local_max 从预测密度图中提取细胞中心点，需设置最小距离和阈值以避免重复检测。
- **模型版本管理**: 通过 init_model 函数支持自动下载最新模型或指定版本，模型文件缓存在 ~/.cache/cellnet 目录。
- **实验配置系统**: train.py 和 train_livecell.py 使用字典定义实验参数，支持通过环境变量切换模式（draft, release, crossval）和超参数搜索。

## Internal Relationships

- `train.py` → `cellnet.data`: train.py 导入 cellnet.data 模块以获取数据加载、图像 ID 处理等工具函数。
- `eval.py` → `cellnet.release`: eval.py 导入 cellnet.release 中的 init_model 和 load_image 函数来初始化和加载模型及图像。
- `eval_livecell.py` → `cellnet.release`: eval_livecell.py 导入 cellnet.release 中的 infer 函数执行推理。
- `preprocess_annotations.py` → `cellnet.data`: preprocess_annotations.py 使用 cellnet.data 中的工具函数处理标注数据。
- `cpsam-livecell.py` → `cellnet.data`: cpsam-livecell.py 使用 cellnet.data 中的 masks2centers 和 load_points 函数。
- `cpsam-livecell.py` → `cellnet.evaluate`: cpsam-livecell.py 导入 cellnet.evaluate 计算评估指标。
- `eval.py` → `cellnet.evaluate`: eval.py 导入 cellnet.evaluate 计算 sMAPE、MAE、精确率、召回率和 F1 分数。
- `eval_livecell.py` → `cellnet.evaluate`: eval_livecell.py 导入 cellnet.evaluate 计算批量评估指标。
