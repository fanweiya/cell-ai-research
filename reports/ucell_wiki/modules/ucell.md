# ucell

> 通用细胞分割模型，支持微调与推理

ucell 模块是一个基于深度学习的细胞分割框架，核心包含 FRM（Flow-based Reconstruction Model）架构。它通过扩散流（flows）将细胞掩码转换为向量场，利用 Transformer 进行特征提取与预测，支持 LoRA 微调以适配不同任务。模块涵盖从数据预处理、模型前向传播、损失计算到指标评估的完整流程。

## Files

### `ucell/dynamics.py`

实现基于扩散的流场生成算法，将细胞掩码转换为用于训练或推理的向量场。

- `_extend_centers_gpu` (function) - 在 GPU 上运行扩散过程生成流场，用于训练图像或质量控制。
- `masks_to_flows_gpu` (function) - 将标签掩码转换为流场，核心函数，通过从掩码中心像素扩散生成 4D 流数组。
- `get_centers` (function) - 计算掩码中每个实例的中心坐标及扩展范围。

### `ucell/frm.py`

定义 FRM 模型架构及其前向传播逻辑，是模型的核心组件。

- `FRM` (class) - FRM 模型主类，包含 Patch Embedding、Transformer 层、任务嵌入及输出头。
- `FRMBlock` (class) - FRM 的基本构建块，包含自注意力机制和 SwiGLU 前馈网络。
- `FrmCarry` (dataclass) - 用于存储 FRM 迭代过程中的状态数据。

### `ucell/layers.py`

提供 FRM 模型所需的底层神经网络层实现，包括注意力机制、归一化和自定义初始化。

- `Attention` (class) - 实现多头自注意力机制，支持旋转位置编码（RoPE）。
- `CastedLinear` (class) - 支持动态类型转换的线性层，确保权重与输入类型一致。
- `CastedEmbedding` (class) - 支持动态类型转换的嵌入层。
- `trunc_normal_init_` (function) - 实现截断正态分布初始化，替代 PyTorch 默认方法以匹配 JAX 行为。

### `ucell/lora.py`

实现 LoRA（Low-Rank Adaptation）微调机制，允许在冻结主干网络的情况下高效微调模型。

- `LoRALinear` (class) - LoRA 线性层，包装原始线性层并添加低秩适配器。
- `inject_lora` (function) - 递归地将模块中的线性层替换为 LoRALinear。
- `mark_only_lora_trainable` (function) - 冻结所有参数，仅保留 LoRA 适配器参数可训练。

### `ucell/metrics.py`

计算分割结果的评估指标，如 IoU、Dice 系数等。

- `box_intersection` (function) - 计算成对边界框的交集面积。
- `mask_intersection` (function) - 计算两个分割掩码之间的实际像素交集。
- `LabelMetrics` (class) - 基于标签计算各种分割指标（Dice, IoU）的类。

### `ucell/utils.py`

提供数据预处理、掩码后处理及通用工具函数。

- `remove_small_instances` (function) - 移除掩码中面积小于指定阈值的实例。
- `clean_up_mask` (function) - 确保掩码 ID 的连续性。
- `pad_channel` (function) - 将图像通道数填充或转换为 3 通道。
- `to_patches` (function) - 将图像切分为固定大小的补丁（patches）以便批量处理。

## Key Concepts

- **扩散流场 (Diffusion Flows)**: 通过从细胞中心向外扩散生成向量场，将离散的细胞掩码转换为连续的梯度场，作为模型输入。
- **FRM 架构**: 基于 Transformer 的 Flow-based Reconstruction Model，使用 Patch Embedding 和 RoPE 位置编码处理图像块序列。
- **LoRA 微调**: 通过低秩矩阵适配器在冻结主干网络权重的情况下高效微调模型，减少显存占用并加速收敛。
- **掩码后处理**: 包含移除小实例、清理 ID 连续性、边界实例移除等操作，确保分割结果的纯净度。

## Internal Relationships

- `ucell/frm.py` → `ucell/layers.py`: frm.py 导入 layers.py 中的 Attention、CastedLinear、CastedEmbedding 等组件构建 FRM 模型。
- `ucell/frm.py` → `ucell/lora.py`: frm.py 使用 lora.py 中的 inject_lora 和 mark_only_lora_trainable 进行模型微调配置。
- `ucell/dynamics.py` → `ucell/utils.py`: dynamics.py 导入 utils.py 中的 remove_small_instances 进行掩码预处理。
- `ucell/metrics.py` → `ucell/utils.py`: metrics.py 依赖 utils.py 中的 clean_up_mask 进行掩码标准化。
- `ucell/frm.py` → `ucell/dynamics.py`: frm.py 在推理或训练阶段可能调用 dynamics.py 生成流场数据。
