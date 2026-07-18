# output

> 负责将核检测、分类和质量评估的结果持久化存储为JSON格式文件。

该模块封装了结果数据的序列化与写入逻辑。它接收来自上游处理模块的结构化数据（如核的坐标、类别标签、质量分数），将其转换为符合特定Schema的JSON对象，并统一保存到指定输出目录。模块确保输出文件命名规范，并处理可能的IO异常。

## Files

### `output.py`

提供结果保存的核心类与函数，处理JSON序列化和文件写入。

- `save_results` (function) - 接收原始结果字典和输出路径，执行JSON序列化并写入文件。
- `format_output` (function) - 将内部数据模型转换为标准化的JSON输出格式。
- `ensure_directory` (function) - 检查并创建输出目录，若不存在则自动创建。

## Key Concepts

- **JSON Schema**: 定义输出数据结构的严格规范，确保下游分析工具能正确解析结果。
- **原子写入**: 采用先写临时文件再重命名的策略，防止写入过程中程序崩溃导致文件损坏。

## Internal Relationships

- `output.py` → `utils/io_utils.py`: output.py 导入 io_utils 中的路径处理函数以标准化文件路径。
- `pipeline.py` → `output/output.py`: 主流程脚本 pipeline.py 调用 output 模块来保存最终处理结果。
