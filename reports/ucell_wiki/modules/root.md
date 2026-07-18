# root

> 通用细胞分割模型 UCell 的根模块，提供训练、推理、评估及少样本适配的全流程脚本与配置。

该模块实现了基于 FRM (Flow-based Region Model) 的细胞分割模型。核心功能包括：通过 config.py 定义模型与训练超参数；data.py 处理图像数据加载与增强；train.py 使用 PyTorch Lightning Fabric 进行分布式训练与检查点管理；predict.py 执行推理并输出分割掩码；eval.py 计算分割指标；few_shot_adapt.py 封装了从验证集采样、微调、推理到评估的自动化少样本适配流程。模型支持 LoRA 微调，并可通过 Docker 部署为 gRPC 服务。

## Files

### `README.md`

项目说明文档，包含使用指南、微调命令及模型链接。

### `config.py`

定义模型架构、训练策略及 LoRA 配置的 ConfigDict 对象。

- `base` (function) - 返回包含默认超参数的 ConfigDict 实例，涵盖模型尺寸、优化器、LoRA 设置等。
- `get_config` (function) - 根据配置名称（如 'train', 'train_emb'）返回调整后的配置对象。

### `data.py`

数据加载、预处理与增强逻辑，支持 HuggingFace Dataset 与文件夹格式。

- `format_and_augment` (function) - 对图像和标签进行归一化、填充、随机翻转、缩放及裁剪等增强操作。
- `get_sz` (function) - 计算掩码中细胞轴长的平均值，用于数据增强时的缩放参考。
- `compute_label` (function) - 将流场或掩码数据转换为包含流场和分割图的标签格式。
- `load_img_folder` (function) - 根据 config.data_dir 创建 HuggingFace Dataset，支持预存数据集、带元数据的文件夹及纯图像-掩码对三种格式。

### `eval.py`

评估分割结果，计算指标并生成 CSV 报告。

- `run` (function) - 遍历测试目录下的 *_label.tif 文件，读取预测掩码，计算 LabelMetrics 指标并保存 report.csv。

### `few_shot_adapt.py`

自动化少样本适配流程脚本。

- `rebuild_train_split` (function) - 从验证集中采样指定数量的样本构建训练集，并生成 metadata.csv。
- `run` (function) - 执行完整管道：重建训练集、调用 train.py、加载最终检查点运行 predict.py、执行 eval.py 并保存报告。

### `predict.py`

模型推理脚本，支持本地文件与 gRPC 远程调用。

- `load_model` (function) - 加载 FRMWrapper 模型检查点，处理 LoRA 缩放因子并编译模型。
- `_compute_masks` (function) - 基于流场和细胞概率计算最终分割掩码，包含迭代去噪与错误过滤。
- `grpc_call` (function) - 通过 gRPC 协议调用远程生物图像处理服务。
- `run` (function) - 遍历输入图像，执行推理并将预测掩码保存至输出目录。

### `train.py`

分布式训练主脚本，集成 Wandb 日志与 EMA 模型管理。

- `AverageMetric` (class) - 用于在训练过程中累积和计算平均指标的工具类。
- `create_dataloader` (function) - 初始化并设置数据加载器。
- `save_state` (function) - 保存训练状态（模型、优化器、EMA 模型）到检查点。
- `resume_state` (function) - 从最新检查点恢复训练状态，支持 LoRA 适配器的非严格加载。
- `setup` (function) - 初始化日志、模型、优化器，注入 LoRA 适配器并启动训练循环。

### `pyproject.toml`

项目依赖配置、构建系统及代码风格工具设置。

### `.gitignore`

定义 Git 版本控制中忽略的文件与目录模式。

### `lora.md`

LoRA 微调功能的说明文档。

## Key Concepts

- **FRMWrapper**: 封装 Flow-based Region Model 的包装类，负责模型前向传播、检查点加载及 LoRA 适配器的管理。
- **LoRA 微调**: 通过低秩分解适配器（LoRA）对模型线性层进行微调的技术，无需更新基础模型权重，显著减少显存和计算需求。配置中通过 config.lora.rank > 0 启用。
- **EMA 模型**: 指数移动平均（Exponential Moving Average）模型，在训练过程中维护一个平滑后的模型副本，通常在推理时提供比原始模型更稳定的性能。
- **流场与分割**: 模型输出细胞质心流向（flow）和细胞概率图（cell_prob），后处理步骤通过流场积分和阈值分割生成最终的细胞实例掩码。
- **少样本适配流程**: few_shot_adapt.py 实现的自动化管道，从验证集采样少量样本构建训练集，执行 LoRA 微调，并自动评估性能，适用于快速适应新数据集。

## Internal Relationships

- `train.py` → `config.py`: train.py 导入 config.py 获取训练超参数配置。
- `train.py` → `data.py`: train.py 通过 data.py 的 get_dataloader 函数创建训练和验证数据加载器。
- `train.py` → `ucell.frm`: train.py 实例化 FRMWrapper 模型类。
- `predict.py` → `config.py`: predict.py 加载配置以初始化模型。
- `predict.py` → `ucell.frm`: predict.py 使用 FRMWrapper 加载模型权重并执行推理。
- `predict.py` → `ucell.dynamics`: predict.py 调用 dynamics 模块中的 compute_masks 和 remove_bad_flow_masks 生成最终分割。
- `few_shot_adapt.py` → `train.py`: few_shot_adapt.py 在重建训练集后调用 train.py 进行微调。
- `few_shot_adapt.py` → `predict.py`: few_shot_adapt.py 在训练完成后调用 predict.py 生成预测结果。
- `few_shot_adapt.py` → `eval.py`: few_shot_adapt.py 在预测完成后调用 eval.py 计算指标。
- `data.py` → `ucell.utils`: data.py 导入 pad_channel 等工具函数处理图像。
- `data.py` → `ucell.dynamics`: data.py 在 compute_label 中调用 masks_to_flows_gpu 生成流场标签。
