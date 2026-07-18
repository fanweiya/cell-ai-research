# notebooks

> 存储和分析疟疾血涂片数据集的探索性数据分析（EDA）与实验结果。

该模块包含用于处理 NIH BBBC041 疟疾数据集的 Jupyter Notebook 及其生成的 Markdown 报告。核心目的是分析数据分布、图像尺寸、标注密度和类别不平衡问题，为后续的水坑算法（Watershed）分割和 Faster R-CNN 分类阶段提供参数依据和理论支撑。

## Files

### `notebooks/EDA_Overview.md`

汇总 EDA 分析结果，记录数据集统计特征及关键发现。

- `Class Distribution` (data_finding) - 揭示数据集极度不平衡，RBC 与 Gametocyte 比例为 537:1，驱动了 Focal Loss 的使用。
- `Annotation Density` (data_finding) - 11% 的图像包含超过 100 个标注框，证明 NMS 在密集场景下会失效，支持引入 Stage 1 水坑算法。
- `Cell Size Stats` (data_finding) - 确定中位细胞宽度为 108px，据此推荐 EfficientNet 使用 64x64 裁剪及水坑算法的 AREA_MIN 阈值。

## Key Concepts

- **类别不平衡 (Class Imbalance)**: 健康红细胞数量远超寄生虫阶段，需采用 Focal Loss 和逆频率加权。
- **标注不完整 (Incomplete Annotations)**: 训练集中大量健康 RBC 未标注，必须依赖无监督的水坑算法进行全细胞分割。
- **密集遮挡 (Dense Occlusion)**: 高标注密度导致 NMS 误删真实目标，需通过预处理分割解决粘连问题。
