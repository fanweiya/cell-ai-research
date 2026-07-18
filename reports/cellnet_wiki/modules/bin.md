# bin

> 提供项目构建、提交、同步和测试的脚本工具集

该模块包含一系列 Shell 脚本，用于管理稀疏噪声点标注定位相差显微镜图像项目。它处理与高性能计算集群（HPC）的交互、环境配置、数据同步、作业提交以及发布流程。核心功能包括：配置不同集群（如 SCC、UTHPC）的资源参数，通过 rsync 同步数据，将 Jupyter Notebook 转换为可执行脚本并在集群上运行，以及自动化发布流程。

## Files

### `bin/clean`

清理构建产物和临时文件

### `bin/code-tunnel`

在 HPC 上安装并启动 VSCode Code Tunnel

### `bin/data-sync`

在本地与 HPC 之间同步数据

### `bin/imports.sh`

定义 HPC 集群参数和环境变量

### `bin/install`

安装或更新项目依赖

### `bin/job-ipynb`

执行 Jupyter Notebook 并管理输出

### `bin/normalize_paths`

将文件夹中的文件名空格替换为下划线

### `bin/release`

创建并发布模型版本

### `bin/submit-job`

提交作业到本地或远程集群

### `bin/test-release`

测试发布流程并验证结果

## Key Concepts

- **HPC 作业调度**: 脚本支持多种作业调度系统（SLURM、LSF），通过 bin/imports.sh 中的变量定义资源请求（CPU、内存、GPU），并使用 sbatch 或 bsub 提交作业。
- **环境隔离**: 使用 uv 和 conda/micromamba 管理 Python 环境，确保作业在隔离的虚拟环境中运行，避免依赖冲突。
- **远程执行**: 通过 SSH 将作业转发到远程 HPC 集群执行，支持本地和远程两种模式，便于在本地开发时直接提交到集群。
- **数据同步**: 使用 rsync 在本地和 HPC 之间同步数据和结果，支持 push 和 pull 操作，保持数据一致性。

## Internal Relationships

- `bin/data-sync` → `bin/imports.sh`: data-sync 导入 imports.sh 以获取 HPC 主机配置
- `bin/submit-job` → `bin/imports.sh`: submit-job 导入 imports.sh 以获取集群作业参数
- `bin/job-ipynb` → `bin/imports.sh`: job-ipynb 依赖 imports.sh 中的环境变量来配置 GPU 资源
- `bin/test-release` → `bin/install`: test-release 调用 install 脚本进行环境安装
- `bin/submit-job` → `bin/job-ipynb`: submit-job 调用 job-ipynb 来执行具体的 Notebook 作业
