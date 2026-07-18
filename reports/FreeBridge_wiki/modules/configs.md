# configs

> 管理实验配置和训练流程的Hydra配置文件模块。

该模块使用Hydra管理单细胞扰动响应建模的超参数和运行时设置。configs/experiment/bbbc021.yaml 定义特定数据集（BBBC021）的专用配置，包括数据路径、网络结构、桥接匹配算法（BM loss）和条件SOC参数。configs/train.yaml 是主入口配置，通过defaults机制组合实验配置，并设置全局优化器、Hydra作业调度（submitit_slurm）及输出目录结构。两个配置文件均包含数据加载路径、优化参数和随机种子设置，确保实验可复现性。

## Files

### `configs/experiment/bbbc021.yaml`

定义BBBC021数据集的专用实验配置，涵盖数据、网络、算法和训练超参数。

### `configs/train.yaml`

主训练配置文件，组合实验配置并设置全局训练参数、Hydra作业调度及输出路径。

## Key Concepts

- **Hydra配置组合**: 使用defaults列表将实验特定配置与全局配置合并，支持动态参数覆盖。
- **条件SOC算法**: configs/experiment/bbbc021.yaml中的csoc部分定义条件随机最优控制算法参数，用于生成扰动响应。
- **桥接匹配损失**: matching.loss: bm 指定使用桥接匹配损失函数进行Schrödinger桥学习。
- **作业调度集成**: train.yaml配置submitit_slurm launcher，支持在集群环境中提交分布式训练任务。

## Internal Relationships

- `configs/train.yaml` → `configs/experiment/bbbc021.yaml`: train.yaml通过defaults机制导入并覆盖experiment配置，形成完整训练设置。
