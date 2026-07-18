# examples

> 存储单点击细胞类型实例分割实验的数据和结果

该模块用于保存和展示单点击细胞类型实例分割方法的实验结果，包括AJI曲线数据、具体样本的分割步骤和指标。数据以JSON格式存储，便于后续分析和可视化。

## Files

### `examples/figure2/aji_curve.json`

存储AJI曲线数据，包含不同方法在迭代过程中的性能变化

- `T` (constant) - 最大迭代次数
- `N` (constant) - 实例总数
- `cop_curve` (object) - COP方法的AJI曲线数据，包含x坐标、y值、类型ID和颜色
- `sam3_curve` (object) - SAM3方法的AJI曲线数据，包含x坐标和y值

### `examples/figure2/figure2_data.json`

存储单个样本的详细分割过程和结果

- `dataset` (constant) - 数据集名称
- `stem` (constant) - 样本标识符
- `cell_types` (object) - 细胞类型分布，键为类型ID，值为数量
- `cop_steps` (array) - COP方法的分割步骤列表，包含每一步的指标、用户点击和RTP点

## Key Concepts

- **AJI**: Aggregate Jaccard Index，用于评估实例分割质量的指标
- **COP**: Click-based Object Propagation，基于点击的对象传播方法
- **SAM3**: Segment Anything Model 3，用于对比的分割模型
- **RTP points**: Region Tracking Points，区域跟踪点，用于指导分割过程

## Internal Relationships

- `examples/figure2/aji_curve.json` → `examples/figure2/figure2_data.json`: 两者都存储同一实验的数据，aji_curve.json提供整体曲线，figure2_data.json提供详细步骤
