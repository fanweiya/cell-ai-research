# root

> Count Anything 项目的根目录，提供跨域文本引导目标计数模型的完整代码、配置和文档。

该目录包含项目的核心入口脚本、依赖管理、文档和启动脚本。README.md 和 README_CN.md 分别提供英文和中文的项目介绍、快速开始指南及数据集说明。requirements.txt 列出了所有 Python 依赖。test.sh、train.sh 和 val.sh 是用于在单节点或多 GPU 环境下启动测试、训练和验证流程的 Shell 脚本，它们均调用 count_anything.train.train 模块并加载对应的 YAML 配置文件。

## Files

### `README.md`

项目英文主文档，介绍模型功能、核心特性、主要结果及快速开始步骤。

### `README_CN.md`

项目中文主文档，功能与 README.md 相同，面向中文用户。

### `requirements.txt`

定义项目运行所需的所有 Python 包及其版本约束。

### `.gitignore`

指定 Git 版本控制中应忽略的文件和目录，如编译产物、虚拟环境、模型权重和日志文件。

### `LICENSE`

声明项目采用 Apache License 2.0 开源协议。

### `test.sh`

执行测试脚本，加载 count_anything_test_cloc.yaml 配置对模型进行测试。

### `train.sh`

执行训练脚本，加载 count_anything_train_cloc.yaml 配置启动模型训练。

### `val.sh`

执行验证脚本，加载 count_anything_val_cloc.yaml 配置对模型进行验证。

## Key Concepts

- **Count Anything**: 一种通用的跨域文本引导目标计数模型，通过实例级点集输出实现可解释的计数。
- **CLOC 数据集**: 跨域大规模目标计数数据集，包含约 22 万张图像、619 个类别和 1500 万个实例。
- **双粒度实例枚举**: 结合区域级稀疏计数器 (RSC) 和像素级密集计数器 (PDC) 以处理不同尺度和密度的目标。
- **点中心监督**: 将异构标注转换为计数点，每个有效实例由一个点监督，边界框仅作为辅助。
- **互补计数融合 (CCF)**: 无参数融合 RSC 和 PDC 结果，抑制重复计数并保留互补性。

## Internal Relationships

- `test.sh` → `train.py`: test.sh 通过 python -m count_anything.train.train 调用训练模块，但传入测试配置。
- `train.sh` → `train.py`: train.sh 通过 python -m count_anything.train.train 调用训练模块，并传入训练配置。
- `val.sh` → `train.py`: val.sh 通过 python -m count_anything.train.train 调用训练模块，并传入验证配置。
- `test.sh` → `config/count_anything_test_cloc.yaml`: test.sh 默认加载测试配置文件。
- `train.sh` → `config/count_anything_train_cloc.yaml`: train.sh 默认加载训练配置文件。
- `val.sh` → `config/count_anything_val_cloc.yaml`: val.sh 默认加载验证配置文件。
