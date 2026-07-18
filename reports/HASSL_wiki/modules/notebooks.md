# notebooks

> 提取单细胞显微图像嵌入并评估模型性能

该模块包含用于从单细胞显微图像中提取特征嵌入的Jupyter Notebook。它加载DINOv3模型，对测试数据集进行预处理，提取图像嵌入，并支持后续的kNN评估。

## Files

### `notebooks/extract_embeddings.ipynb`

提取单细胞显微图像嵌入并评估模型

- `extract_embeddings` (function) - 从dinov3.eval.tSNE模块导入，用于提取图像嵌入
- `NCells` (class) - 单细胞图像数据集类，用于加载和管理测试数据
- `load_backbone` (function) - 从dinov3.models.backbone_loader导入，加载DINOv3骨干网络
- `evaluate_simple_knn` (function) - 从dinov3.eval.simpleKNN导入，执行简单的k近邻评估
- `make_transform` (function) - 创建图像预处理管道，包括调整大小、归一化等操作

## Key Concepts

- **DINOv3骨干网络**: 
- **单细胞数据集**: 
- **嵌入提取**: 
- **kNN评估**: 

## Internal Relationships

- `notebooks/extract_embeddings.ipynb` → `dinov3.eval.tSNE.extract_embeddings`: notebook导入extract_embeddings函数用于提取图像嵌入
- `notebooks/extract_embeddings.ipynb` → `dinov3.data.datasets.NCells`: notebook导入NCells数据集类用于加载单细胞图像数据
- `notebooks/extract_embeddings.ipynb` → `dinov3.models.backbone_loader.load_backbone`: notebook导入load_backbone函数用于加载DINOv3模型
- `notebooks/extract_embeddings.ipynb` → `dinov3.eval.simpleKNN.evaluate_simple_knn`: notebook导入evaluate_simple_knn函数用于模型性能评估
