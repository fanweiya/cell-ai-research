# root

> ARGUS 项目的根目录，提供时间分辨显微图像细胞追踪的完整框架、文档和依赖配置。

ARGUS 是一个鲁棒、通用且计算高效的细胞追踪框架，旨在处理时间分辨显微图像数据。根目录包含项目文档 (README.md)、依赖列表 (requirements.txt)、版本控制配置 (.gitignore) 和许可证 (LICENSE)。核心算法实现位于 src/ 目录，交互式演示和分析通过 notebooks/ 目录中的 Jupyter 笔记本进行。该框架整合了经典图像处理、光流方法和现代追踪算法，提供从预处理、检测到追踪、分析和可视化的完整流水线。

## Files

### `README.md`

项目主文档，描述 ARGUS 框架的功能、特性、目录结构、安装指南和使用方法。

### `requirements.txt`

定义项目运行所需的所有 Python 依赖包及其版本，包括图像处理库 (bm3d, itk, opencv)、数值计算库 (numpy, pandas)、可视化工具 (matplotlib) 和追踪算法库 (munkres, networkx)。

### `.gitignore`

指定 Git 版本控制系统应忽略的文件和目录，避免将编译产物、虚拟环境、临时文件和个人配置提交到仓库。

### `LICENSE`

项目许可证文件，采用 MIT 许可证，允许自由使用、修改和分发代码。

## Key Concepts

- **模块化架构**: 框架将预处理、检测、追踪、分析和可视化组件解耦，允许独立使用每个模块。
- **鲁棒性与通用性**: 设计目标是适应多样化的成像条件和细胞形态，最小化参数调整需求。
- **计算效率**: 针对长时间序列和高通量工作流程进行优化，确保处理大规模数据的能力。
- **混合方法**: 结合经典图像处理（如小波去噪、局部最大值检测）与现代追踪算法（光流辅助链接、距离关联）。

## Internal Relationships

- `README.md` → `requirements.txt`: README.md 指导用户通过 requirements.txt 安装依赖。
- `README.md` → `notebooks/`: README.md 指向 notebooks/ 目录中的示例笔记本作为使用起点。
- `README.md` → `src/`: README.md 说明 src/ 包含核心检测与追踪算法实现。
