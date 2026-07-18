# data

> 存储和管理AI代理运行ImageJ所需的容器环境快照、依赖配置及运行时元数据。

该模块负责维护容器化ImageJ环境的精确状态记录，包括Python环境依赖、系统组件版本、Cellpose模型别名映射以及运行时配置。核心文件container_snapshot.md作为静态文档，详细列出了2026-04-30的容器快照信息，涵盖Cellpose不同版本（v3/v4）的模型别名、系统运行时组件（Java, ImageJ, Fiji, Xvfb等）及主conda环境（local_imagent_J）的完整pip依赖列表。此数据为AI代理规划、编写和执行显微图像分析工作流提供基础环境上下文，确保操作在已知且一致的容器环境中进行。

## Files

### `data/environment/container_snapshot.md`

记录容器环境快照，包含Cellpose模型别名、系统组件版本及Python依赖列表。

## Key Concepts

- **容器快照**: 对特定时间点容器内所有软件版本、依赖和配置的静态记录，确保环境可复现性。
- **Cellpose别名映射**: 将用户常用的模型名称（如'cellpose sam', 'cyto3'）映射到具体的环境（env）和包版本，解决命名歧义。
- **CPU-only容器**: 当前容器配置为纯CPU运行，无CUDA支持，影响模型推理性能。
- **ImageJ/Fiji集成**: 容器内预装ImageJ 1.x和Fiji (imagej2)，作为图像分析的核心执行引擎。
