# Phase1-EDA

> 执行疟疾血涂片数据的探索性分析，为后续模型架构决策提供数据支撑。

该模块负责解析原始JSON标注文件，统计类别分布、图像尺寸、边界框大小及标注密度，并生成可视化图表。其核心目的是在编写任何模型代码前，通过数据洞察确定处理策略（如数据增强、类别不平衡处理），确保后续Phase 2（Faster R-CNN）和Phase 3（EfficientNet）的架构设计基于实际数据特征。

## Files

### `dataset.py`

定义PyTorch Dataset类，直接解析JSON文件以支持检测和分类任务，无需中间CSV文件。

- `MalariaDataset` (class) - 用于目标检测（Faster R-CNN）的整图数据集类，返回图像张量和包含边界框、标签的目标字典。
- `MalariaCropDataset` (class) - 用于细胞分类（EfficientNet）的裁剪数据集类，返回单个细胞的裁剪图像张量和类别索引。
- `get_detection_transform` (function) - 为Faster R-CNN返回仅包含PIL到Tensor转换的变换，避免重复归一化。
- `get_classification_transform` (function) - 为EfficientNet返回分类变换，训练时包含随机翻转、旋转和颜色抖动以模拟染色变化，验证时仅包含缩放和归一化。

### `eda.py`

执行探索性数据分析脚本，统计并可视化数据集特征，输出设计决策摘要。

- `parse_annotations` (function) - 解析单个JSON标注文件，提取图像名称、类别、边界框坐标及图像尺寸，过滤无效和困难标注。
- `plot_class_distribution` (function) - 绘制类别分布柱状图，展示各类别样本数量及不平衡比率。
- `visualize_samples` (function) - 加载8张样本图像并在其上绘制真实边界框，保存至输出目录。
- `generate_design_summary` (function) - 基于分析结果打印关键设计决策摘要，用于论文或文档记录。

## Key Concepts

- **直接JSON解析**: 数据集类和EDA脚本均直接从原始JSON文件读取数据，避免维护中间CSV文件，减少系统复杂度和数据同步问题。
- **染色不变性增强**: 在分类任务的变换中引入ColorJitter（亮度、对比度、饱和度抖动），强制模型学习细胞形态特征而非依赖染色颜色，以解决实验室间的域偏移问题。
- **困难样本过滤**: 通过SKIP_LABELS忽略标注为'difficult'的样本，确保模型训练和评估仅关注清晰可辨的目标。
- **数据驱动决策**: EDA模块通过量化分析（如类别不平衡比、边界框尺寸分布）为后续模型选择、损失函数设计及数据增强策略提供实证依据。

## Internal Relationships

- `dataset.py` → `shared/label_map.py`: dataset.py 导入 label_map 以获取类别标签到整数索引的映射（LABEL_TO_INT, INT_TO_LABEL）及类别常量。
- `eda.py` → `shared/label_map.py`: eda.py 导入 label_map 以获取标签映射、前景名称及颜色定义，用于统计和可视化。
- `dataset.py` → `eda.py`: 两者共享相同的JSON解析逻辑和标签过滤规则（SKIP_LABELS），但dataset.py侧重于构建数据加载器，eda.py侧重于统计分析。
