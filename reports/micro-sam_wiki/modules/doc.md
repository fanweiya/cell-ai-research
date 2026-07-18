# doc

> 提供 micro-sam 项目的用户文档、API 参考、安装指南和模型说明。

该模块包含一系列 Markdown 文件，用于文档化 micro-sam 工具的各项功能。内容涵盖交互式标注工具（2D/3D/跟踪）、自动分割模式（AMG/AIS/APG）、命令行接口 (CLI)、Python 库使用、微调模型介绍、数据集详情、安装步骤、常见问题解答 (FAQ) 以及贡献指南。这些文档旨在帮助用户快速上手、理解核心概念并有效利用软件进行显微图像分割。

## Files

### `doc/annotation_tools.md`

介绍交互式标注工具的使用，包括 2D、3D 和跟踪功能，以及如何在 napari 插件、命令行和 Python 脚本中启动它们。

### `doc/apg.md`

解释自动提示生成 (APG) 分割模式，对比 AMG 和 AIS，并说明如何配置和运行。

### `doc/band.md`

指导用户如何在 BAND 云平台上启动和使用 micro-sam。

### `doc/bioimageio/em_organelles_v2.md`

描述针对电子显微镜线粒体和细胞核分割的 v2 微调模型。

### `doc/bioimageio/em_organelles_v4.md`

描述针对电子显微镜线粒体和细胞核分割的 v4 微调模型（架构更新版）。

### `doc/bioimageio/histopathology_v1.md`

描述针对组织病理学数据核分割的 v1 微调模型。

### `doc/bioimageio/inference_parameters.md`

列出不同显微图像数据集（如 LIVECell, DeepBacs 等）上微调模型的推荐推理参数。

### `doc/bioimageio/lm_v2.md`

描述针对光显微镜细胞和细胞核分割的 v2 微调模型。

### `doc/bioimageio/lm_v3.md`

描述针对光显微镜细胞和细胞核分割的 v3 微调模型。

### `doc/bioimageio/lm_v4.md`

描述针对光显微镜细胞和细胞核分割的 v4 微调模型（架构更新版）。

### `doc/cli_tools.md`

文档化 micro-sam 的命令行接口 (CLI) 脚本，包括嵌入预计算、标注器启动、模型微调和自动分割等命令。

### `doc/contributing.md`

提供贡献指南，包括环境设置、代码修改、测试和提交 Pull Request 的流程。

### `doc/data_submission.md`

说明社区如何提交数据以改进 micro-sam 模型。

### `doc/datasets/em_organelles_v2.md`

列出用于训练 EM Organelle v2 模型的数据集详情。

### `doc/datasets/em_organelles_v4.md`

列出用于训练 EM Organelle v4 模型的数据集详情。

### `doc/datasets/lm_v2.md`

列出用于训练 LM Generalist v2 模型的数据集详情。

### `doc/datasets/lm_v3.md`

列出用于训练 LM Generalist v3 模型的数据集详情。

### `doc/datasets/lm_v4.md`

列出用于训练 LM Generalist v4 模型的数据集详情。

### `doc/deprecated/development.md`

（已废弃）开发者指南，描述软件模块结构和标注工具设计。

### `doc/faq.md`

解答关于安装、系统要求和基本使用的常见问题。

### `doc/finetuned_models.md`

介绍所有可用的微调模型，包括模型类型、尺寸及选择方法。

### `doc/installation.md`

提供通过 pip、conda、源码和安装程序四种方式安装 micro-sam 的详细步骤。

### `doc/python_library.md`

文档化 Python 库的功能，包括提示分割、实例分割、训练和评估模块。

### `doc/start_page.md`

项目主页文档，包含快速开始指南、核心组件介绍和引用信息。

## Key Concepts

- **交互式标注 (Interactive Annotation)**: 通过 napari 插件提供的工具，允许用户使用点、框或形状提示来交互式地分割图像中的对象。支持 2D、3D 和时序跟踪。
- **自动实例分割 (Automatic Instance Segmentation)**: 无需用户交互即可分割图像中所有实例的方法。micro-sam 支持三种模式：自动掩码生成 (AMG)、自动实例分割 (AIS) 和自动提示生成 (APG)。
- **微调模型 (Finetuned Models)**: 在原始 SAM 模型基础上，使用大量显微图像数据（光镜、电镜、病理）进行微调的模型，针对特定生物医学成像任务优化。
- **napari 插件 (napari Plugin)**: micro-sam 的标注工具作为 napari 图像查看器的插件运行，利用 napari 的图层和交互功能。
- **推理参数 (Inference Parameters)**: 用于控制自动分割后处理过程的参数（如 IoU 阈值、稳定性分数阈值），针对不同数据集有推荐的最佳配置。

## Internal Relationships

- `doc/finetuned_models.md` → `doc/bioimageio/lm_v4.md`: finetuned_models.md 引用并链接到具体的模型说明文档（如 lm_v4.md）。
- `doc/annotation_tools.md` → `doc/python_library.md`: annotation_tools.md 提及 Python 库用于脚本调用标注工具。
- `doc/cli_tools.md` → `doc/finetuned_models.md`: cli_tools.md 说明 CLI 命令可以使用不同的微调模型。
- `doc/start_page.md` → `doc/installation.md`: start_page.md 提供快速安装链接，指向详细的 installation.md。
