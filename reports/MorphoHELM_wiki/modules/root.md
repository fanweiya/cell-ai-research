# root

> MorphoHELM Cell Painting 基准测试与特征提取流水线的根模块，提供项目文档、依赖配置及元数据管理。

该模块作为整个项目的入口和配置中心，包含项目说明、依赖列表、版本控制配置及合规文档。它定义了从数据下载、预处理、转换为 HuggingFace 格式、推理、聚合、标准化到基准测试和生成图表的完整流水线。核心功能包括通过 `data_installation/download_illum_corrected.py` 下载并校正 CPG0016 和 BBBC036 数据集的图像，生成 uint8 PNG 格式的输出，并管理相关的元数据缓存。

## Files

### `README.md`

项目主文档，描述流水线步骤、安装指南、命令行参数及数据集细节。

- `download_illum_corrected.py` (script) - 用户-facing 的数据下载脚本，支持 CPG0016 和 BBBC036 数据集，执行光照校正并保存为 uint8 PNG。

### `requirements.txt`

定义项目所需的 Python 依赖包，包括核心库、ML 框架及本地 HuggingFace 加载器。

- `huggingface_loader` (local_package) - 本地 HuggingFace 加载器包，通过 -e 方式安装。

### `.gitattributes`

配置 Git LFS 以存储大型二进制基准资产（如 .parquet, .pt, .pth 文件）。

### `.gitignore`

定义 Git 忽略规则，排除 Python 缓存、环境文件、日志、临时输出及未版本化的中间数据产品。

### `CODE_OF_CONDUCT.md`

项目行为准则，采用 Microsoft 开源行为准则。

### `LICENSE`

项目许可证，采用 MIT License。

### `SECURITY.md`

安全策略文档，指导如何报告安全漏洞。

### `SUPPORT.md`

项目支持文档，说明如何提交问题及获取帮助。

## Key Concepts

- **光照校正 (Illumination Correction)**: 预处理阶段的核心步骤，用于校正图像的光照不均匀性，输出为全尺寸 uint8 PNG 图像。
- **数据集 (CPG0016 & BBBC036)**: 项目支持的两个主要细胞成像数据集，具有不同的目录结构和图像命名规范。
- **HuggingFace 格式转换**: 将预处理后的图像和元数据转换为 HuggingFace Datasets 格式，以便后续推理和特征提取。
- **基准测试流水线**: 从数据下载到生成图表的完整自动化流程，包含推理、聚合、标准化和质量控制步骤。

## Internal Relationships

- `README.md` → `data_installation/download_illum_corrected.py`: README 描述了 download_illum_corrected.py 的用法和参数，该脚本是数据下载和预处理的核心入口。
- `requirements.txt` → `huggingface_loader/`: requirements.txt 通过 -e 标志本地安装 huggingface_loader 包，该包用于将预处理后的数据转换为 HuggingFace 格式。
- `.gitattributes` → `data/main_paper_inputs`: .gitattributes 配置 Git LFS 以版本控制 data/main_paper_inputs 等目录下的基准输入文件。
- `.gitignore` → `data/corrected_images`: .gitignore 忽略 data/corrected_images 等中间数据产品，这些文件由流水线生成且应在本地重新生成。
