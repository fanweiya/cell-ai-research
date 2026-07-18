# config

> 集中管理AI代理运行所需的外部依赖配置、环境变量和检索参数。

该模块负责定义和初始化系统运行所需的所有配置项，包括ImageJ/Fiji路径、LangSmith追踪密钥、Qdrant向量数据库设置、嵌入模型参数、混合检索策略以及文档 ingestion 规则。它确保代理在不同环境（Docker容器或本地）下能正确获取外部资源并执行RAG（检索增强生成）流程。

## Files

### `src/config/imagej_config.py`

配置ImageJ/Fiji的路径，支持Docker和本地环境。

- `FIJI_JAVA_HOME` (variable) - 从环境变量FIJI_PATH读取Fiji安装路径，默认值为/opt/Fiji.app（Docker环境）。

### `src/config/keys_template.py`

设置LangSmith追踪和OpenAI API密钥的环境变量。

- `gpt_key` (variable) - 获取OPENAI_API_KEY环境变量，若未设置则使用占位符字符串。

### `src/config/rag_config.py`

定义RAG系统的核心参数，包括向量库路径、检索阈值、模型设置和文档处理策略。

- `BASE_DIR` (variable) - 通过Path解析确定项目根目录，确保路径在容器和主机间兼容。
- `QDRANT_DATA_PATH` (variable) - 指定Qdrant向量数据库的存储路径，优先使用/app/qdrant_data。
- `DOCS_COLLECTION_NAME` (variable) - 定义存储生物图像分析文档的Qdrant集合名称。
- `MISTAKES_COLLECTION_NAME` (variable) - 定义存储代码错误及解决方案的Qdrant集合名称。
- `RECIPES_COLLECTION_NAME` (variable) - 定义存储代码配方的Qdrant集合名称。
- `MIN_RECIPIE_SCORE` (variable) - 混合检索（RRF）的最低分数阈值，低于此值视为无匹配结果。
- `DEDUP_SIMILARITY_THRESHOLD` (variable) - 用于去重的余弦相似度阈值，超过此值视为重复文档。
- `EMBEDDING_MODEL` (variable) - 指定使用的稠密向量嵌入模型名称。
- `SPARSE_MODEL` (variable) - 指定用于稀疏向量检索的模型名称。
- `CONTENT_CHUNKING_STRATEGY` (variable) - 定义不同文件类型（代码、文档、笔记本）的切片大小、重叠量和策略。

## Key Concepts

- **混合检索 (Hybrid Search)**: 结合稠密向量（Dense）和稀疏向量（Sparse）检索，通过RRF（Reciprocal Rank Fusion）算法融合结果，提高召回率和准确性。
- **容器化路径兼容**: 通过BASE_DIR和特定路径（如/app/qdrant_data）处理Docker容器与宿主机之间的路径差异，确保配置在两种环境下均有效。
- **RAG去重机制**: 在文档入库前通过余弦相似度计算（DEDUP_SIMILARITY_THRESHOLD）识别并合并高度相似的文档，避免向量数据库冗余。
- **内容感知切片**: 根据文件类型（代码、文档、Notebook）采用不同的切片策略和参数，以优化语义保留和检索效果。

## Internal Relationships

- `src/config/rag_config.py` → `src/config/imagej_config.py`: rag_config.py 不直接导入 imagej_config.py，但两者共同服务于主代理逻辑，分别处理向量检索和ImageJ执行环境。
- `src/config/keys_template.py` → `src/config/rag_config.py`: keys_template.py 设置LangSmith追踪环境变量，rag_config.py 可能间接依赖这些环境变量进行日志记录。
