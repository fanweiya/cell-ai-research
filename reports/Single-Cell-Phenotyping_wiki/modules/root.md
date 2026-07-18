# root

> 实现无标签单细胞表型分类与蛋白表达回归的多任务学习框架

该项目是一个统一的深度学习框架，用于从无标签的微分干涉相差（DPC）显微镜图像中联合执行白细胞（WBC）分类和连续蛋白表达回归。核心架构采用混合CNN-ViT设计，结合局部纹理特征和全局空间依赖，通过任务自适应门控机制实现可控制的跨任务信息交换。项目包含数据加载、模型定义、损失函数、训练流程、评估脚本及LLM可解释性模块，支持BSCCM和BCCD数据集。

## Files

### `README.md`

项目文档，包含概述、架构说明、安装指南、数据集下载、预训练模型使用及训练命令

### `requirements.txt`

定义项目依赖，包括PyTorch核心库、数据处理库、可视化工具及可选的LLM和W&B集成

### `.gitignore`

配置版本控制忽略规则，排除虚拟环境、数据、模型检查点、训练输出及临时文件

### `LICENSE`

MIT许可证，规定软件使用、修改和分发的权利与责任

### `bccd_data_loading.py`

加载和预处理BCCD数据集，将Kaggle的4类标签映射到项目的3类标签（淋巴细胞、粒细胞、单核细胞）

- `KAGGLE_TO_MODEL_MAPPING` (constant) - 定义Kaggle标签到模型标签的映射关系
- `load_kaggle_bccd_dataset` (function) - 从目录结构加载BCCD数据集，按TRAIN/TEST/TEST_SIMPLE划分训练、验证和测试集

### `data_loading.py`

为BSCCM数据集提供多任务数据加载，支持多通道DPC图像和蛋白表达标签

- `BSCCMMultiTaskDataset` (class) - 多任务学习数据集类，返回图像、细胞类型标签和蛋白表达值
- `load_bsccm_dataset` (function) - 加载BSCCM数据集并返回处理后的数据对象
- `create_train_val_test_splits` (function) - 创建训练、验证和测试集划分
- `create_data_loaders` (function) - 根据划分创建PyTorch DataLoader

### `model.py`

定义混合CNN-ViT多任务模型架构，包含共享ECA注意力、CNN分支、ViT分支、跨模态融合及任务特定头

- `EfficientChannelAttention` (class) - 高效通道注意力模块，自适应加权不同DPC方向
- `InceptionModule` (class) - 简化的Inception模块，包含残差连接
- `LightweightViT` (class) - 轻量级Vision Transformer分支
- `CrossModalFusion` (class) - 跨模态融合模块，结合CNN和ViT特征
- `TaskGating` (class) - 任务自适应门控，控制分类和回归路径间的信息交换
- `create_model` (function) - 工厂函数，创建并初始化多任务模型

### `losses.py`

实现多任务学习损失函数，包括改进的回归损失、自适应任务权重、Focal Loss和标签平滑

- `ImprovedRegressionLoss` (class) - 结合MSE和Pearson相关性的回归损失，增强梯度
- `AdaptiveMultiTaskLoss` (class) - 基于不确定性的自适应多任务损失，自动平衡分类和回归权重
- `FocalLoss` (class) - 解决类别不平衡的分类损失
- `CombinedClassificationLoss` (class) - Focal Loss与标签平滑的混合分类损失

### `train.py`

训练脚本，实现多任务模型的训练循环，支持Mixup增强、W&B日志记录和模型保存

- `mixup_data` (function) - Mixup数据增强函数
- `ImprovedMultiTaskTrainer` (class) - 改进的多任务训练器，管理训练、验证、日志记录和模型保存

### `evaluate.py`

评估脚本，计算分类指标（准确率、混淆矩阵、ROC）和回归指标（MSE、Pearson相关性），生成可视化结果

- `MultiTaskEvaluator` (class) - 多任务模型评估器，执行完整评估并计算各项指标

### `llm_summarizer.py`

LLM集成模块，将模型预测转换为生物学的自然语言摘要，支持OpenAI API和本地LLM

- `format_predictions_for_llm` (function) - 将模型预测格式化为LLM可处理的字典结构
- `build_llm_prompt` (function) - 根据格式化预测构建LLM提示词

## Key Concepts

- **混合CNN-ViT架构**: 结合CNN提取局部纹理特征和ViT捕获全局空间依赖，通过跨模态融合和任务门控实现高效特征整合
- **多任务学习**: 同时优化白细胞分类（离散）和蛋白表达回归（连续）两个任务，通过自适应损失权重平衡任务间梯度冲突
- **任务自适应门控**: 可学习的门控机制，根据样本动态调整分类和回归路径间的信息交换强度
- **改进回归损失**: 结合Huber损失和Pearson相关性损失，提高蛋白表达预测的鲁棒性和相关性
- **无标签表型分类**: 仅使用DPC显微镜图像，无需荧光染色即可预测细胞类型和蛋白表达水平

## Internal Relationships

- `train.py` → `model.py`: train.py导入create_model函数来实例化多任务模型
- `train.py` → `losses.py`: train.py导入ImprovedRegressionLoss、AdaptiveMultiTaskLoss等损失函数
- `train.py` → `data_loading.py`: train.py导入load_bsccm_dataset、create_data_loaders等数据加载函数
- `evaluate.py` → `model.py`: evaluate.py导入create_model加载评估模型
- `evaluate.py` → `data_loading.py`: evaluate.py导入数据加载函数以获取测试集
- `bccd_data_loading.py` → `data_loading.py`: 两者都处理细胞数据集，但bccd_data_loading.py专门处理BCCD数据集的标签映射
- `llm_summarizer.py` → `evaluate.py`: llm_summarizer.py可接收evaluate.py的预测结果生成自然语言摘要
