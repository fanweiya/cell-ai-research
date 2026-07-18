# root

> 项目根目录，包含文档、依赖、许可证及数据集说明，用于支持无训练实例分割的演示与评估。

该模块是 Chain-of-Prompts (CoP) 项目的根目录，提供训练无关的推理核心、统一的 SAM 接口、演示 notebook 和基准测试拆分。项目旨在通过每个细胞类型仅需一次点击，将交互复杂度从 O(N) 降低至 O(T)，在 11 个细胞/细胞核实例分割基准上实现超过 90% 的每实例上限性能，同时平均减少 97.6% 的标注点击量。

## Files

### `README.md`

项目主文档，介绍方法、结果、TL;DR 及引用链接。

### `requirements.txt`

定义项目依赖，包括 PyTorch、核心库、SAM 接口、Hugging Face Hub 及演示工具。

### `.gitignore`

配置 Git 忽略规则，排除编译文件、虚拟环境、模型权重及临时输出。

### `DATASETS.md`

详细说明 11 个基准数据集的分组、目录结构、许可状态及统计信息。

### `LICENSE`

声明项目采用 CC BY-NC 4.0 开源许可。

## Key Concepts

- **Chain-of-Prompts (CoP)**: 一种无需训练的提示链方法，将每个细胞类型的单次点击传播到所有同类实例，实现组提示而非实例提示。
- **训练无关 (Training-free)**: 方法不修改冻结的骨干网络参数，直接利用预训练模型进行推理。
- **O(T) 交互复杂度**: 将交互次数从与实例数量 N 成正比降低为与细胞类型数量 T 成正比。
- **统一 SAM 接口**: 为不同版本的 SAM 模型提供标准化的接口，支持组提示功能。

## Internal Relationships

- `requirements.txt` → `README.md`: requirements.txt 列出的依赖支持 README 中描述的功能实现。
- `DATASETS.md` → `README.md`: DATASETS.md 提供 README 中结果表格所需的数据集细节和统计信息。
