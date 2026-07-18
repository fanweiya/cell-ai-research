# root

> MalariAI 项目的根目录，包含核心算法实现、数据预处理、模型训练与推理、以及 Web 应用部署的完整代码结构。

该模块实现了疟疾血涂片细胞分割与分期分类的端到端系统。核心采用两阶段解耦架构：第一阶段基于距离变换引导的分水岭算法进行无监督细胞分割（Stage 1 v2 引入 CLAHE 和分辨率感知峰值检测）；第二阶段使用 EfficientNet-B0 配合 Focal Loss 进行多类感染阶段分类，并利用 Grad-CAM++ 生成可解释性热力图。系统支持 NIH BBBC041 和 MP-IDB 数据集，具备跨数据集零样本泛化能力。

## Files

### `README.md`

项目文档，阐述研究背景、方法创新、实验结果及部署链接。

### `.gitignore`

定义 Git 忽略规则，排除虚拟环境、数据集、模型权重及内部文档，仅保留代码与论文源文件。

### `Phase1-Stage1/segment.py`

实现分水岭分割算法，包含距离变换、峰值检测及细胞实例提取逻辑。

- `distance_transform_watershed` (function) - 执行距离变换并应用分水岭算法分割重叠细胞
- `clahe_normalization` (function) - 应用限制对比度自适应直方图均衡化增强图像对比度

### `Phase2-Stage2/classify.py`

加载 EfficientNet-B0 模型进行细胞分期分类，集成 Focal Loss 处理类别不平衡。

- `EfficientNetB0Classifier` (class) - 基于 EfficientNet-B0 的分类器，支持 Focal Loss 训练
- `predict_stage` (function) - 对分割后的细胞 ROI 进行感染阶段预测

### `Phase2-Stage2/explain.py`

利用 Grad-CAM++ 生成分类决策的空间注意力热力图，提供可解释性证据。

- `generate_gradcam_pp` (function) - 计算并可视化 Grad-CAM++ 热力图

### `Phase3-PipelineB/evaluate.py`

执行端到端评估，计算分割召回率、分类准确率及跨数据集泛化性能。

- `compute_metrics` (function) - 计算 IoU、Centroid-in-box、mAP 等关键指标

### `Phase4-WebApp/app.py`

构建 Flask Web 应用，提供用户上传血涂片图像并获取分割与分类结果的交互界面。

- `upload_and_process` (function) - 处理上传图像并返回分割掩码与分类结果

## Key Concepts

- **Annotation-Agnostic Segmentation**: 第一阶段分水岭算法不依赖标注数据，通过距离变换自动分离重叠细胞，解决标注不完整问题。
- **Focal Loss**: 在第二阶段分类中用于缓解红血球与寄生虫细胞间严重的类别不平衡（537:1）。
- **Grad-CAM++**: 为每个细胞的分类预测生成空间注意力图，提供临床可解释的视觉证据。
- **Cross-Dataset Zero-Shot**: 在 MP-IDB 数据集上无需重新训练即可验证模型泛化能力，证明算法对不同染色和实验室条件的鲁棒性。

## Internal Relationships

- `Phase3-PipelineB/evaluate.py` → `Phase1-Stage1/segment.py`: 调用分割模块获取细胞实例以评估分割性能
- `Phase3-PipelineB/evaluate.py` → `Phase2-Stage2/classify.py`: 调用分类模块对分割出的细胞进行分期预测
- `Phase2-Stage2/explain.py` → `Phase2-Stage2/classify.py`: 依赖分类模型的特征图生成可解释性热力图
- `Phase4-WebApp/app.py` → `Phase1-Stage1/segment.py`: 在 Web 端集成分割算法处理用户上传图像
- `Phase4-WebApp/app.py` → `Phase2-Stage2/classify.py`: 在 Web 端集成分类模型输出诊断结果
