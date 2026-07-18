# root

> 配置和文档根目录，用于定义项目结构、依赖、许可及运行环境。

该模块包含 HASSL 项目的核心配置文件和文档。README.md 是项目的主入口，详细阐述了 HASSL 框架的动机、双教师蒸馏和层次感知对比损失两大核心组件，以及训练流程和数据集信息。pyproject.toml 和 setup.py 定义了 Python 包元数据、依赖项和安装配置。requirements.txt 和 conda.yaml 分别指定了 pip 和 conda 环境的具体依赖版本。hubconf.py 提供了通过 PyTorch Hub 加载预训练模型的接口。LICENSE.md、CODE_OF_CONDUCT.md 和 CONTRIBUTING.md 分别规定了法律许可、行为准则和贡献指南。

## Files

### `README.md`

项目主文档，介绍 HASSL 框架、安装步骤、训练流程和数据集。

### `pyproject.toml`

配置代码质量工具（mypy, pylint, ruff）的规则和排除项。

### `requirements.txt`

列出项目运行时所需的所有 Python 依赖包及其版本。

### `setup.py`

定义 Python 包的元数据、依赖项和安装逻辑，用于构建和分发 dinov3 包。

- `get_requirements` (function) - 解析 requirements.txt 文件，返回依赖列表和额外索引 URL。
- `get_package_version` (function) - 从 dinov3/__init__.py 中读取并返回包的版本号。
- `setup` (function) - 调用 setuptools 配置包安装信息。

### `.docstr.yaml`

配置 docstr-coverage 工具，用于检查文档字符串覆盖率。

### `.gitignore`

定义 Git 版本控制中需要忽略的文件和目录模式。

### `CODE_OF_CONDUCT.md`

规定项目社区的行为准则和举报机制。

### `CONTRIBUTING.md`

指导开发者如何向项目提交贡献（PR、Issue、CLA）。

### `LICENSE.md`

声明 DINOv3 项目的许可条款和使用限制。

### `MODEL_CARD.md`

提供 DINOv3 模型的技术细节、用途、偏见风险和快速入门指南。

### `conda.yaml`

定义使用 conda 创建项目环境所需的依赖包。

### `hubconf.py`

暴露 PyTorch Hub 接口，允许用户通过 torch.hub.load 加载预训练模型。

- `dinov3_vits16` (function) - 加载 dinov3_vits16 模型。
- `dinov3_vit7b16` (function) - 加载 dinov3_vit7b16 模型。
- `dinov3_convnext_tiny` (function) - 加载 dinov3_convnext_tiny 模型。

### `requirements-dev.txt`

列出开发环境所需的额外工具依赖（如 linting, type checking）。

## Key Concepts

- **HASSL (Hierarchy-Aware Self-Supervised Learning)**: 一种针对单细胞显微图像的层次感知自监督学习框架，旨在解决粗粒度成像因素掩盖细粒度形态学信号的问题。
- **Double-Teacher Distillation**: HASSL 的核心组件之一，结合标准 EMA 图像教师和一个基于零样本分割掩码（CellposeSAM）的分割教师，以引导模型关注细胞形态而非成像模态。
- **Hierarchy-Aware Contrastive Loss**: HASSL 的另一个核心组件，利用 HDBSCAN 在批次嵌入上构建聚类树，并通过稳定性加权（λ）在每一层级挖掘正负原型，实现层次一致的对比学习。
- **DINOv3**: HASSL 构建的基础视觉基础模型系列，提供高质量的密集特征，支持多种下游任务。
- **PyTorch Hub Integration**: 通过 hubconf.py 实现与 PyTorch Hub 的无缝集成，方便用户直接加载和使用预训练模型。

## Internal Relationships

- `setup.py` → `requirements.txt`: setup.py 读取 requirements.txt 以获取安装依赖。
- `setup.py` → `dinov3/__init__.py`: setup.py 读取 dinov3/__init__.py 以获取版本号。
- `hubconf.py` → `dinov3.hub.backbones`: hubconf.py 从 dinov3.hub.backbones 模块导入模型加载函数。
- `hubconf.py` → `dinov3.hub.classifiers`: hubconf.py 从 dinov3.hub.classifiers 模块导入分类器模型。
- `hubconf.py` → `dinov3.hub.segmentors`: hubconf.py 从 dinov3.hub.segmentors 模块导入分割模型。
- `README.md` → `conda.yaml`: README.md 中的安装指南引用 conda.yaml 来创建环境。
- `README.md` → `requirements.txt`: README.md 中的安装指南引用 requirements.txt 作为依赖列表。
