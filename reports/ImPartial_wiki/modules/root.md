# root

> ImPartial 项目的根目录，提供交互式实例分割框架的部署、配置、训练脚本及文档。

该模块是 ImPartial 框架的顶层结构，集成了基于 MONAI Label 的交互式分割流程。核心功能包括：通过 Docker 容器化部署、使用配置文件定义训练与数据参数、执行模型训练与推理、以及与 ImageJ/Fiji 插件的交互。主要文件包括 Dockerfile 用于环境构建，requirements.txt 和 setup.py 用于依赖管理和安装，train_impartial.py 作为主训练入口，以及多个文档文件说明使用方法和架构。

## Files

### `Dockerfile`

定义容器化环境，基于 MONAI Label 镜像构建 ImPartial 运行环境。

### `README.md`

项目说明文档，介绍 ImPartial 框架的目标、方法、结果及集成特性。

### `requirements.txt`

指定项目运行所需的 Python 依赖包及其版本。

### `setup.py`

定义 Python 包的元数据，用于安装 ImPartial 包。

- `setup` (function) - 配置包名、版本、作者、描述及依赖，执行 find_packages 查找子包。

### `train_impartial.py`

主训练脚本，负责解析配置、初始化 MLflow、加载数据、构建模型并执行训练或推理。

- `get_output_size` (function) - 根据分类任务配置计算模型输出层的大小。
- `plot_patches_sample` (function) - 从数据加载器中采样并保存图像块样本到文件。
- `init_mlflow` (function) - 初始化 MLflow 实验跟踪。
- `main` (function) - 脚本入口，解析命令行参数，读取配置文件，初始化训练器并启动训练或评估流程。

### `QUICK_START.md`

快速开始指南，说明 ImageJ 插件安装、云执行及用户操作流程。

### `.gitignore`

定义 Git 版本控制中忽略的文件和目录。

### `.gitattributes`

配置 Git 对特定文件类型的属性处理。

### `LICENSE.md`

项目许可证，采用 Apache 2.0 附带 Commons Clause 条款。

## Key Concepts

- **部分标注 (Partial Annotations)**: 框架核心，利用稀疏的 scribbles（涂鸦）和有限的监督信号进行训练，而非全像素标注。
- **盲点插补 (Blind Spot Imputation)**: 将图像块分为插补块和盲点块，通过 U-Net 恢复成分混合和统计信息，利用自监督目标对齐分割任务。
- **MONAI Label 集成**: 框架与 MONAI Label 服务器深度集成，支持交互式标注、主动学习和模型迭代更新。
- **多用户云部署**: 支持用户注册、会话管理、模型上传与共享，可在云端进行无代码执行。
- **ImageJ/Fiji 插件**: 提供用户友好的图形界面，允许用户在本地图像软件中直接进行标注和推理。

## Internal Relationships

- `train_impartial.py` → `impartial/dataprocessing/datasets.py`: 导入自定义数据集类以加载和处理图像及标注数据。
- `train_impartial.py` → `impartial/general/networks.py`: 导入 UNet 网络架构用于分割任务。
- `train_impartial.py` → `impartial/general/losses.py`: 导入 ImpartialLoss 损失函数以计算分割和插补损失。
- `train_impartial.py` → `impartial/general/config.py`: 导入配置类以解析 INI 格式的配置文件。
- `setup.py` → `requirements.txt`: setup.py 依赖 requirements.txt 中列出的包进行安装。
- `Dockerfile` → `requirements.txt`: Docker 构建过程中通过 requirements.txt 安装 Python 依赖。
