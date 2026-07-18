# config

> 定义文本引导跨域目标计数模型的训练、验证和测试配置参数。

该模块包含三个YAML配置文件，分别用于测试、训练和验证阶段。它们定义了数据路径、模型超参数、数据增强策略、损失函数配置以及训练阶段设置。三个文件结构高度相似，主要区别在于路径设置（如实验日志目录、预训练权重路径）和特定的训练/验证目标。配置文件通过路径指向数据注解文件，并详细指定了图像预处理流程（如随机缩放、裁剪、标准化）和复杂的损失函数组合（包括PDC点集损失、RSC框损失、RSC点损失和质量BCE损失）。

## Files

### `config/count_anything_test_cloc.yaml`

配置测试阶段参数，使用测试集注解和特定实验目录。

### `config/count_anything_train_cloc.yaml`

配置训练阶段参数，使用训练集和验证集注解，并指向预训练的SAM3权重。

### `config/count_anything_val_cloc.yaml`

配置验证阶段参数，使用训练集和验证集注解，并指向已训练的模型检查点。

## Key Concepts

- **数据增强管道**: 通过嵌套的Transform API定义，包含随机选择、缩放、裁剪/填充、张量转换和标准化，支持训练和验证的不同策略。
- **复合损失函数**: 使用CountAnythingLossWrapper封装多种损失，包括PDC点集分类与定位损失、RSC边界框损失、RSC点损失以及RSC质量BCE损失，通过权重字典控制各部分贡献。
- **训练阶段控制**: 通过scratch.training_stage参数指定为joint_counter_adaptation，启用分割和PDC分支，并设置分辨率和归一化参数。

## Internal Relationships

- `config/count_anything_train_cloc.yaml` → `config/count_anything_val_cloc.yaml`: 两者共享相同的数据注解路径和大部分模型配置，但训练配置包含预训练权重路径，而验证配置指向已训练的检查点。
- `config/count_anything_test_cloc.yaml` → `config/count_anything_train_cloc.yaml`: 测试配置使用独立的测试集注解路径和实验日志目录，与训练配置在数据划分上分离。
