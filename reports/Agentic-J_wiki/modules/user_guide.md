# user_guide

> 提供Agentic-J项目的完整用户文档，涵盖安装、界面操作、提示工程、数据管理及安全规范。

该模块包含一系列Markdown文档，旨在指导用户从环境搭建到高级工作流使用的全部流程。文档详细解释了基于Docker的容器化部署、noVNC浏览器界面操作、多智能体架构（Supervisor与Specialist）、提示词编写技巧、项目数据持久化机制以及安全隔离策略。所有文档均为静态文本，无代码逻辑，但共同构成了系统的核心使用手册。

## Files

### `user_guide/README.md`

作为模块入口，提供导航索引和联系方式。

### `user_guide/01_getting_started.md`

指导用户完成前置条件检查、环境变量配置、镜像启动及更新流程。

### `user_guide/02_interface_and_agents.md`

详解浏览器界面功能、剪贴板交互、智能体架构（Supervisor/Plugin Manager/Coder/Debugger/Python Analyst/QA Reporter）及工具能力。

### `user_guide/03_prompting.md`

提供提示词工程最佳实践，包括上下文要素、示例及常见错误避免。

### `user_guide/04_data_history_and_reports.md`

说明项目目录结构、聊天历史存储机制、使用报告导出及问题报告流程。

### `user_guide/05_security.md`

阐述容器安全模型、权限控制、API密钥管理及数据隐私保护策略。

## Key Concepts

- **Supervisor + Specialist 架构**: 系统采用主从智能体模式，Supervisor负责规划工作流和调用工具，Specialist（如Plugin Manager、ImageJ Coder、Debugger等）负责执行具体任务，用户不直接与Specialist交互。
- **noVNC 浏览器界面**: 通过浏览器访问localhost:6080/vnc.html，无需安装本地软件即可在虚拟桌面中运行Fiji/ImageJ，并集成聊天面板。
- **Docker 持久化**: 利用Docker命名卷和挂载的./data目录，确保脚本、模型、聊天记录和图像数据在容器重启或更新后不丢失。
- **安全隔离**: 容器以非root用户运行，仅开放localhost端口，限制资源使用，且Agent只能访问./data目录，防止系统级风险。
- **QA Reporter**: 可选的智能体，在 workflow 结束后对项目和图像发布标准进行审计，生成QA_Checklist_Report.md。

## Internal Relationships

- `user_guide/README.md` → `user_guide/01_getting_started.md`: README作为索引链接到01_getting_started.md，引导新用户开始。
- `user_guide/01_getting_started.md` → `user_guide/02_interface_and_agents.md`: 启动容器后，用户需参考02_interface_and_agents.md了解界面操作和智能体架构。
- `user_guide/02_interface_and_agents.md` → `user_guide/03_prompting.md`: 了解智能体架构后，用户需学习03_prompting.md以编写有效指令。
- `user_guide/03_prompting.md` → `user_guide/04_data_history_and_reports.md`: 执行分析任务后，用户需参考04_data_history_and_reports.md管理输出数据和历史记录。
- `user_guide/04_data_history_and_reports.md` → `user_guide/05_security.md`: 在涉及数据管理和报告发送时，需遵循05_security.md中的安全规范。
