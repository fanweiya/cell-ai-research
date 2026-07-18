# root

> 定义 micro_sam 项目的结构、依赖、安装和发布配置。

根目录包含项目的元数据、构建配置、环境定义和文档生成脚本。pyproject.toml 和 setup.cfg 定义了包名、版本、依赖项和入口点，使 micro_sam 可作为 napari 插件和命令行工具安装。environment.yaml 提供了基于 conda 的依赖环境，requirements-dev.txt 列出了开发测试工具。README.md 和 RELEASE_OVERVIEW.md 提供项目介绍和使用说明。build_doc.py 脚本用于生成和验证文档完整性。

## Files

### `README.md`

项目的主文档，介绍功能、安装、贡献和引用信息。

### `pyproject.toml`

定义构建系统、测试配置（pytest）、代码格式化工具（black、ruff）和排除规则。

### `setup.cfg`

配置包元数据、依赖项、Python 版本要求、napari 插件入口点和命令行脚本。

### `.gitignore`

指定版本控制中忽略的文件和目录，如缓存、构建产物、数据文件和日志。

### `LICENSE`

项目的 MIT 许可证文本，定义使用、修改和分发的权利。

### `MANIFEST.in`

控制打包时包含的文件，确保 LICENSE 和 README.md 被包含。

### `RELEASE_OVERVIEW.md`

记录每个版本的变更历史和新增功能。

### `build_doc.py`

生成项目文档并检查文档文件的完整性。

- `check_docs_completeness` (function) - 检查 doc 目录下的所有 markdown 和 rst 文件是否已在 micro_sam.__init__.py 的文档字符串中引用。

### `environment.yaml`

定义 conda 环境依赖，包括 PyTorch、napari、Segment Anything 等核心库。

### `requirements-dev.txt`

列出开发所需的额外工具，如 pytest、coverage、pdoc 等。

## Key Concepts

- **napari 插件集成**: 
- **命令行工具**: 
- **依赖管理**: 
- **文档自动化**: 

## Internal Relationships

- `setup.cfg` → `pyproject.toml`: setup.cfg 定义包元数据和入口点，pyproject.toml 定义构建系统和代码质量工具配置，两者共同完成包的构建和发布。
- `build_doc.py` → `micro_sam/__init__.py`: build_doc.py 通过导入 micro_sam 模块并检查其 __doc__ 字符串来验证文档完整性。
- `environment.yaml` → `setup.cfg`: environment.yaml 提供开发环境依赖，setup.cfg 定义运行时依赖，两者需保持一致以确保环境兼容性。
