# results

> 存储和报告白细胞图像细粒度形态标注与分割实验结果的Markdown表格文件。

该模块包含三个Markdown文件，分别记录基线模型、基于预测分割图的细胞结构感知识别模型、以及基于真实分割图的细胞结构感知识别模型在不同属性上的性能指标。所有表格均包含精确率(Precision)、召回率(Recall)和F-measure，并标注了标准差。这些结果用于论文第4节和第6节的实验分析。

## Files

### `results/tab_baseline_attpred.md`

记录基线模型（VGG16和ResNet50）在各项细胞形态属性上的分类性能，对应论文第4节。

### `results/tab_predsegbased_attpred.md`

记录使用预测分割图作为输入的细胞结构感知识别模型在不同聚合策略下的性能，对应论文第6节。

### `results/tab_segbased_attpred.md`

记录使用真实分割图（Ground-truth）作为输入的细胞结构感知识别模型在不同聚合策略下的性能，对应论文第6节。

## Key Concepts

- **基线模型 (Baseline Models)**: 直接使用VGG16或ResNet50骨干网络对白细胞图像进行属性分类，不利用分割掩码信息。
- **细胞结构感知识别 (Cell Structure-aware Recognition)**: 结合分割掩码（预测或真实）与图像特征进行属性识别的模型，通过不同聚合策略（注意力、平均池化、拼接、最大池化、加权平均）融合信息。
- **细粒度属性 (Fine-grained Attributes)**: 包括细胞大小、形状、核形状、核质比、染色质密度、细胞质纹理/颜色/空泡、颗粒颜色/类型等20+种形态学特征。
