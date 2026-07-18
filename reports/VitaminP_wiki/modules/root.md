# root

> 项目根目录，包含Docker环境配置、安装脚本、文档和许可证，用于部署和分发基于Vision Transformer的病理细胞分割框架VitaminP。

该模块是VitaminP项目的顶层结构，主要提供容器化部署方案、Python包安装配置及项目元数据。Dockerfile定义了基于CUDA 12.1和Ubuntu 22.04的完整运行环境，预装了PyTorch、OpenCV、OpenSlide等依赖，并自动下载预训练权重。setup.py定义了Python包的元数据、核心依赖及可选扩展（如WSI支持、开发工具）。README.md提供项目概述、安装指南和API用法。requirements.txt列出运行时依赖，.gitignore排除缓存和临时文件，LICENSE采用MIT协议。

## Files

### `Dockerfile`

构建包含CUDA 12.1、PyTorch 2.1.0及所有依赖的Docker镜像，并预下载预训练权重。

### `README.md`

项目文档，包含功能介绍、模型说明、快速开始指南和API示例。

### `requirements.txt`

列出Python运行时依赖包及其版本约束。

### `setup.py`

定义Python包的元数据、安装依赖和可选扩展，用于通过pip安装vitaminp。

- `setup` (function) - 调用setuptools.setup()配置包名称、版本、依赖和元数据。

### `.gitignore`

指定Git忽略的文件和目录，如缓存、构建产物和临时文件。

### `LICENSE`

MIT许可证文本，定义软件使用、修改和分发的法律条款。

## Key Concepts

- **容器化部署**: 通过Dockerfile提供包含CUDA、PyTorch及所有依赖的完整环境，确保跨平台一致性。
- **预训练权重集成**: Docker构建时自动从HuggingFace下载vitamin_p_dual.pth和vitamin_p_flex.pth权重，无需运行时下载。
- **可选依赖**: setup.py定义wsi、gan、dev等可选扩展，允许用户按需安装WSI处理或开发工具。
- **多模态分割**: 项目支持H&E、MIF、IHC等多种病理图像模态的细胞和细胞核分割。

## Internal Relationships

- `Dockerfile` → `requirements.txt`: Dockerfile中手动安装依赖，requirements.txt作为参考清单。
- `setup.py` → `README.md`: setup.py读取README.md作为包的长描述。
- `Dockerfile` → `setup.py`: Dockerfile在构建时安装依赖，setup.py定义Python包的依赖结构。
