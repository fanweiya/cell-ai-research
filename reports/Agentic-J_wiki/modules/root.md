# root

> 编排一个容器化的 AI 代理部署，该代理可自动化 ImageJ/Fiji 显微图像分析工作流。

根模块提供了在 Docker 容器内运行基于大语言模型（LLM）代理的基础设施。它将预构建的 ImageJ 环境与基于 Python 的代理系统（LangChain/LangGraph）相结合，用于规划、编写并执行用于生物图像分析的 Groovy 宏。该设置处理了复杂的依赖关系，包括 Java、OpenCL、用于远程桌面访问的 VNC，以及用于插件和向量数据库的持久化存储。

## 文件

### `Dockerfile`

构建包含 ImageJ/Fiji、系统依赖项和所需插件的容器镜像。

- `base-cpu`（阶段）- 使用 Miniconda3 作为 CPU 执行的基础阶段。
- `cpu`（阶段）- 最终阶段，安装 X11、VNC、Java 依赖项和 Fiji。
- `TARGETARCH`（参数）- 架构参数，用于选择正确的 Fiji 二进制文件（arm64 与 x64）。

### `docker-compose.yml`

定义容器运行时配置、网络、卷和资源限制。

- `imagentj`（服务）- 运行代理和 Fiji 的主要服务。
- `volumes`（配置）- 在重启之间持久化 Fiji 插件、JAR 文件、脚本、Qdrant 数据库和 Cellpose 模型。

### `docker-entrypoint.sh`

在容器启动时初始化容器，填充卷并应用关键补丁。

- `_seed_volume`（函数）- 将镜像中的插件/JAR 种子文件复制到命名卷中，跳过已存在的文件。
- `TrackMate-StarDist 补丁`（逻辑）- 确保使用已修补的 JAR 文件以防止 ClassCastException。
- `CSBDeep 补丁`（逻辑）- 为 CSBDeep 插件应用 ARM64 TensorFlow Java 补丁。

### `micromamba_shim.sh`

将 TrackMate 中硬编码的 micromamba 调用重定向到正确的 Conda 环境。

- `CMD`（变量）- 命令参数（run、env 等）。
- `ENV_NAME`（变量）- 提取的环境名称，用于路由到正确的 Conda 前缀。

### `setup_wizard.py`

当在 `.env` 中未找到 API 密钥时，用于首次配置 API 密钥的 PySide6 GUI。

- `SetupWizard`（类）- 用于输入 OpenAI 或 OpenRouter API 密钥的主窗口。
- `validate_key`（函数）- 验证 OpenAI 或 OpenRouter API 密钥的格式。

### `run.py`

具有流式输出功能的交互式代理循环的 CLI 入口点。

- `interactive_loop`（函数）- 处理代理交互和检查点的主要循环。
- `handle_event`（函数）- 处理来自 LangGraph 的流式事件以打印 AI 思维过程和工具调用。

### `gui_runner.py`

提供聊天界面和使用跟踪的 PySide6 GUI 应用程序。

- `ImagentJGUI`（类）- 管理聊天气泡、历史记录和代理连接的主 GUI 类。
- `_md_to_html`（函数）- 将 Markdown 文本转换为 HTML 以便在 QLabel 中显示。

### `environment.yml`

定义包含所有 Python、Java 和数据科学依赖项的 Conda 环境。

- `dependencies`（列表）- 包含 pyimagej、langchain、langgraph、pyside6 以及各种图像处理库。

### `pyproject.toml`

`imagentj` 包的 Python 项目元数据和构建配置。

- `imagentj`（包）- 位于 src/ 中的 Python 包名称。

### `.dockerignore`

从 Docker 构建上下文中排除不必要的文件，以减小体积并防止泄露。

### `.env.template`

环境变量模板，主要用于 API 密钥和可选设置。

### `.gitattributes`

为大型二进制文件（如 Qdrant 向量数据库）配置 Git LFS。

### `.gitignore`

从版本控制中排除构建产物、日志和敏感数据。

### `README.md`

项目文档、快速入门指南和架构概览。

### `LICENSE`

Apache License 2.0 条款。

### `NOTICE`

ISAS e.V. 的版权声明。

## 核心概念

- **容器化 ImageJ**：Fiji 安装在 Docker 容器内，并配有虚拟 X 服务器（Xvfb）和 VNC（noVNC），以便通过浏览器进行远程 GUI 访问。
- **持久化卷**：命名卷（fiji_plugins、fiji_jars、qdrant_data 等）在容器重启之间保留状态，避免重新下载插件或重新索引文档。
- **RAG 插件搜索**：代理使用 Qdrant 向量数据库在运行时检索相关的插件文档和使用示例，以实现上下文感知的脚本编写。
- **环境模拟（Shimming）**：`micromamba_shim.sh` 将 TrackMate 中硬编码的环境调用重定向到正确的 Conda 环境（cellpose、stardist），以确保兼容性。
- **代理架构**：使用 LangGraph 创建一个主管代理，用于规划任务、调用工具（ImageJ 宏、文件操作），并迭代直到实现用户目标。

## 内部关系

- `docker-compose.yml` → `Dockerfile`：docker-compose 构建由 Dockerfile 定义的镜像，并配置运行时资源。
- `docker-entrypoint.sh` → `docker-compose.yml`：docker-compose 将 `docker-entrypoint.sh` 挂载到容器中，以便在启动时运行。
- `run.py` → `src/imagentj`：`run.py` 从 `src/imagentj` 包导入主要的代理逻辑和工具。
- `gui_runner.py` → `src/imagentj`：`gui_runner.py` 从 `src/imagentj` 导入代理初始化和工具定义。
- `micromamba_shim.sh` → `docker-compose.yml`：docker-compose 将模拟脚本绑定挂载到容器中，以覆盖 TrackMate 的 micromamba 调用。
- `setup_wizard.py` → `docker-compose.yml`：docker-compose 将向导脚本绑定挂载到容器中，以便在未配置 API 密钥时运行。