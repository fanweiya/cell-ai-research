# scripts

> 提供单细胞扰动响应建模实验的自动化训练脚本和配置入口。

该模块包含用于启动 Schrödinger Bridges 模型训练流程的 Shell 脚本和 Python 入口文件。train.sh 脚本通过 Hydra 框架批量执行不同超参数（如 support_weight）下的实验，确保实验可复现性。train.py 作为核心执行入口，解析实验配置并调用模型训练逻辑。

## Files

### `scripts/train.sh`

执行支持权重消融实验的 Shell 脚本。

- `train.sh` (script) - 通过循环调用 train.py 并传递不同 state_cost.support_weight 参数（0.0, 0.3, 0.5），在 BBBC021 数据集上运行支持权重消融实验。

### `scripts/train.py`

模型训练的主入口脚本。

- `main` (function) - 脚本入口点，使用 Hydra 加载 YAML 配置（如 experiment=bbbc021），初始化 Schrödinger Bridges 模型，执行端到端训练流程并保存结果。

## Key Concepts

- **Schrödinger Bridges**: 一种基于最优传输理论的生成模型方法，用于从终点数据推断扰动响应分布。
- **Hydra 配置**: 用于动态管理实验参数（如数据集、损失函数权重）的配置框架，支持命令行覆盖配置项。
- **支持权重 (support_weight)**: 控制正则化项中支持集重要性的超参数，用于平衡模型对观测数据的拟合程度。

## Internal Relationships

- `scripts/train.sh` → `scripts/train.py`: train.sh 通过 subprocess 调用 train.py 来执行具体的训练任务。
- `scripts/train.py` → `src/models`: train.py 导入 src/models 中的模型定义和训练逻辑来执行实际计算。
