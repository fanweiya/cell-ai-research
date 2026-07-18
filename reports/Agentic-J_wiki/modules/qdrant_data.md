# qdrant_data

> 管理Qdrant向量数据库的集合配置和元数据。

该模块负责定义和维护Qdrant向量数据库的集合结构，包括BioimageAnalysisDocs和codingerrors_and_solutions两个集合。每个集合配置了3072维的稠密向量索引，使用余弦相似度进行距离计算，并启用了稀疏向量索引的完整扫描阈值和磁盘存储选项。此模块为AI代理提供语义搜索和错误解决方案检索的基础设施。

## Files

### `meta.json`

定义Qdrant数据库集合的静态配置元数据

- `collections` (object) - 包含两个集合配置：BioimageAnalysisDocs用于存储生物图像分析文档，codingerrors_and_solutions用于存储编码错误及解决方案
- `dense` (object) - 稠密向量配置，包含3072维大小和余弦距离度量
- `sparse` (object) - 稀疏向量索引配置，启用磁盘存储和完整扫描阈值

## Key Concepts

- **向量集合**: Qdrant中用于存储和检索向量数据的逻辑容器，每个集合有独立的索引配置
- **稠密向量**: 固定长度的数值数组，用于表示文本或图像的语义嵌入，本模块使用3072维
- **余弦相似度**: 向量相似性度量方法，计算两个向量夹角的余弦值，值越接近1表示越相似
- **稀疏向量索引**: 针对稀疏向量数据优化的索引结构，支持磁盘存储以提高大规模数据检索效率
