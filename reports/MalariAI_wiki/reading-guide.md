# Reading Guide

这是一个疟疾血涂片分析项目，包含从数据探索到Web部署的完整流程。建议按开发阶段顺序阅读，先理解业务目标，再深入模型细节，最后查看部署方式。

## Step 1: 理解项目概览与部署配置 (~15 min)

**Files:** `README.md`, `Phase4-WebApp/Dockerfile`, `Phase4-WebApp/requirements.txt`

首先阅读README.md了解项目背景、疟疾检测的业务目标和整体架构。然后查看Dockerfile和requirements.txt，了解项目依赖、环境配置和部署方式，为后续代码阅读建立上下文。

## Step 2: 探索数据特征与预处理 (~20 min)

**Files:** `Phase1-EDA/dataset.py`, `Phase1-EDA/eda.py`

查看dataset.py了解数据加载、预处理和增强策略，这是所有模型的基础。通过eda.py理解数据分布、类别平衡和关键特征，这些决策直接影响后续模型选择。

## Step 3: 掌握基线模型实现 (~30 min)

**Files:** `Phase2-BaselineA/train_frcnn.py`, `Phase2-BaselineA/Phase2_FasterRCNN_Kaggle.ipynb`

train_frcnn.py包含Faster R-CNN模型的训练逻辑、损失函数和优化器配置。Jupyter Notebook展示了实验过程和结果分析，理解模型架构选择的原因和训练技巧。

## Step 4: 学习改进版Pipeline (~25 min)

**Files:** `Phase3-PipelineB/gradcam.py`, `Phase3-PipelineB/stage2_inference.py`

gradcam.py实现可解释性推理，展示模型决策依据。stage2_inference.py包含改进网络B0的分类逻辑和推理流程，对比基线模型理解性能提升的关键改进。

## Step 5: 理解Web应用入口 (~15 min)

**Files:** `Phase4-WebApp/app.py`

app.py是Flask应用入口，查看如何集成模型推理、处理用户请求、管理文件上传和返回结果。理解API设计、错误处理和响应格式，这是用户与系统交互的界面。

## Step 6: 分析推理结果与评估 (~10 min)

**Files:** `Phase3-PipelineB/results/v1/inference/results.json`, `Phase2-BaselineA/checkpoints-local-20epoch/metrics.json`

查看不同阶段的推理结果JSON文件，理解模型输出格式、置信度阈值和评估指标。对比不同checkpoint的metrics.json，分析模型训练过程中的性能变化。

## Tips

- 重点关注数据预处理部分，因为医学图像的质量直接影响模型性能
- 对比Phase2和Phase3的代码差异，理解模型改进的具体实现
- 注意Grad-CAM可视化代码，这对医学诊断的可解释性至关重要
- Web应用代码相对简单，重点理解模型推理的集成方式
- 结果文件很大，重点关注关键指标而非全部内容
