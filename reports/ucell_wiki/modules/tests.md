# tests

> 验证通用细胞分割模型FRM在不同检查点格式下的加载与权重一致性

该模块专注于测试FRM模型在多种检查点场景下的加载正确性，包括基础模型字典检查点、序列化模块对象检查点、LoRA微调检查点（合并后加载）、遗留的融合gate_up_proj检查点（加载时拆分）以及融合gate_up_proj与LoRA的组合场景。通过构造小型配置和辅助函数，确保模型权重在保存和加载后保持一致，并验证LoRA适配器在加载时的合并逻辑。

## Files

### `tests/test_checkpoint_loading.py`

测试FRM模型在不同检查点格式下的加载路径和权重一致性

- `_small_config` (function) - 生成一个极小的FRM配置字典，用于快速测试，包含patch_size=8、hidden_size=64等参数
- `_make_model` (function) - 基于_small_config创建FRM模型实例
- `_small_wrapper_config` (function) - 生成包含LoRA配置的FRMWrapper配置，用于测试LoRA相关功能
- `_round_trip` (function) - 将给定模型的state_dict加载到新模型中并返回，用于权重对比
- `_weights_equal` (function) - 比较两个模型的所有参数是否相等，返回布尔值和第一个不匹配的参数量名称
- `test_base_dict_checkpoint` (function) - 测试基础模型字典检查点（如{'model': state_dict}）的加载和权重一致性
- `test_module_object_checkpoint` (function) - 测试序列化模块对象检查点（final_ema.pt风格）的加载，使用load_checkpoint方法
- `test_lora_checkpoint_merge` (function) - 测试LoRA检查点加载：将带有LoRA适配器的模型保存后，加载到纯FRM模型中应自动合并权重

## Key Concepts

- **检查点格式兼容性**: 测试覆盖多种检查点保存和加载格式，确保模型在不同训练阶段和保存方式下能正确恢复
- **LoRA权重合并**: 验证LoRA适配器在加载到基础模型时能正确合并到原始权重中，无需额外步骤
- **权重一致性验证**: 通过_round_trip和_weights_equal函数确保模型状态在保存和加载后完全一致

## Internal Relationships

- `tests/test_checkpoint_loading.py` → `ucell.frm`: 导入FRM和FRMWrapper类用于创建和测试模型
- `tests/test_checkpoint_loading.py` → `ucell.lora`: 导入inject_lora函数用于向模型注入LoRA适配器
- `tests/test_checkpoint_loading.py` → `ml_collections`: 导入ConfigDict用于构建测试配置
