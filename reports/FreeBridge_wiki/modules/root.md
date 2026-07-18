# root

> FreeBridge 项目的根目录，提供单细胞扰动响应建模的完整环境配置、训练入口、采样脚本及项目文档。

该目录包含 FreeBridge 项目的核心基础设施。setup.py 定义包结构；environment.yml 指定 PyTorch 2.0.1 及依赖库（如 hydra-core, pytorch-lightning, torchdiffeq, geomloss）；.gitignore 排除模型权重、中间数据及日志。README.md 阐述基于 Schrödinger Bridges 的无轨迹单细胞状态转移方法。index.html 为项目展示页面。sample_bbbc021_latents.py 用于从训练好的 checkpoint 前向采样目标潜变量；train.py 为基于 Hydra 和 PyTorch Lightning 的主训练入口，负责初始化 FreeBridgeLitModule、配置分布式环境及保存检查点。

## Files

### `setup.py`

定义 Python 包 'freebridge' 的安装元数据。

- `setuptools.setup` (function) - 配置包名、版本、描述及自动发现 packages。

### `environment.yml`

定义 conda 环境依赖，确保复现性。

- `dependencies` (list) - 包含 Python 3.9, PyTorch 2.0.1, CUDA 11.7 及 hydra, lightning, torchdiffeq 等关键库。

### `sample_bbbc021_latents.py`

从训练好的模型 checkpoint 采样生成目标细胞潜变量。

- `main` (function) - 解析命令行参数，加载模型与配置，从源分布采样初始状态，调用 model.sample 进行前向传输，保存生成的潜变量到 .npy 文件。
- `restore_model` (function) - 从 freebridge.utils 导入，用于从 checkpoint 恢复模型实例和配置。
- `get_dist_boundary` (function) - 从 freebridge.dataset 导入，获取源 (p0) 和目标 (p1) 分布的边界数据。

### `train.py`

主训练脚本，集成 Hydra 配置管理与 PyTorch Lightning。

- `main` (function) - Hydra 入口函数。设置随机种子，初始化设备，获取分布边界 (get_dist_boundary)，实例化 FreeBridgeLitModule，可选记录边界可视化，启动 Lightning Trainer 进行训练。
- `seed_all` (function) - 跨 Lightning 版本兼容的随机种子设置。
- `maybe_slurm_plugin` (function) - 检测并配置 SLURM 环境插件以支持分布式训练。
- `should_log_boundary` (function) - 根据配置决定是否需要记录边界可视化日志。

## Key Concepts

- **Schrödinger Bridge**: 一种随机最优传输框架，用于在源分布（对照细胞）和目标分布（扰动细胞）之间构建随机漂移，实现无轨迹数据下的状态转移建模。
- **Support Cost**: 几何惩罚项，强制中间状态保持在观测到的形态流形上，防止生成不符合生物形态的细胞。
- **Endpoint-only Data**: 模型仅利用终点（t=0 和 t=1）的细胞状态数据，无需中间时间步的轨迹观测。
- **Hydra + PyTorch Lightning**: 项目采用 Hydra 管理超参数配置，PyTorch Lightning 封装训练循环，支持多 GPU 和 SLURM 集群部署。

## Internal Relationships

- `train.py` → `freebridge.pl_model`: train.py 导入 FreeBridgeLitModule 以构建 Lightning 模块。
- `train.py` → `freebridge.dataset`: train.py 调用 get_dist_boundary 获取训练所需的数据分布。
- `sample_bbbc021_latents.py` → `freebridge.utils`: sample 脚本调用 restore_model 加载模型权重和配置。
- `sample_bbbc021_latents.py` → `freebridge.dataset`: sample 脚本调用 get_dist_boundary 获取源分布以生成初始样本。
- `train.py` → `sample_bbbc021_latents.py`: train.py 生成 checkpoint，sample 脚本消费该 checkpoint 进行推理采样。
