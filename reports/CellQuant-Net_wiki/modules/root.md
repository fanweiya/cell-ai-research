# root

> 提供 CellQuant-Net 项目的入口、安装脚本及运行流程控制。

根模块包含项目文档、依赖管理、环境安装脚本以及主运行入口。它协调 WSI-QA（质量评估）和 CP-Net（核检测与分类）两个核心子模块的执行流程，确保用户能够便捷地部署和运行端到端的核定量分析流水线。

## Files

### `README.md`

项目文档，包含功能介绍、安装步骤、快速测试指南及输出结构说明。

### `requirements.txt`

定义项目运行所需的所有 Python 依赖包及其版本。

### `LICENSE`

声明项目采用 MIT 许可证，规定使用、修改和分发的权利与义务。

### `install.sh`

自动化安装脚本，负责创建 Conda 环境、安装依赖、下载并编译 CUTLASS 扩展。

- `install.sh` (script) - 执行环境创建、依赖安装及 CUTLASS 深度卷积扩展的编译与安装。

### `verify_installation.py`

验证脚本，检查系统环境、GPU 状态及所有关键依赖库是否安装成功。

- `verify_installation.py` (script) - 导入并测试 PyTorch、CuPy、OpenSlide 等库，输出系统资源及依赖状态。

### `run_cellquant_net.py`

主运行入口，按顺序调用 WSI-QA 和 CP-Net 子模块的测试脚本。

- `run_cmd` (function) - 封装 subprocess.run，用于执行子命令并打印状态信息。
- `main` (function) - 解析命令行参数，构建 WSI-QA 和 CP-Net 的启动命令，并顺序执行。

## Key Concepts

- **WSI-QA**: Whole-Slide Image Quality Assessment，用于筛选高质量图像切片，排除伪影区域。
- **CP-Net**: CellPriorNet，基于轻量级 CNN 和 H 通道先验的核检测与分类网络。
- **CUTLASS 扩展**: 用于加速深度可分离卷积的 C++/CUDA 扩展，需通过 install.sh 编译安装。
- **Conda 环境**: 隔离的 Python 运行环境 cellquantnet，确保依赖版本一致性。

## Internal Relationships

- `run_cellquant_net.py` → `WSI_QA/test_qa.py`: run_cellquant_net.py 通过 subprocess 调用 WSI_QA/test_qa.py 执行质量评估。
- `run_cellquant_net.py` → `CP-Net/test_cp_net.py`: run_cellquant_net.py 通过 subprocess 调用 CP-Net/test_cp_net.py 执行核检测与分类。
- `install.sh` → `requirements.txt`: install.sh 使用 pip install -r requirements.txt 安装 Python 依赖。
- `verify_installation.py` → `depthwise_conv2d_implicit_gemm`: verify_installation.py 尝试导入由 install.sh 编译的 CUTLASS 扩展模块。
