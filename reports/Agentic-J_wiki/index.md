# Agentic-J

> 在容器中运行 ImageJ 的 AI 智能体，用于规划、编写并执行显微图像分析工作流。

Agentic-J 将 Fiji（ImageJ）与基于 LLM 的聊天界面结合，并封装在 Docker 容器中。它通过规划步骤、生成 Groovy 宏、安装插件并报告结果来分析显微图像。用户可通过 noVNC Web 界面或命令行与系统交互，只需将图像放入共享数据文件夹，智能体即可自动处理。

## 技术栈

- **Python** 3.13+（编程语言）
- **Fiji** 最新版（软件）
- **Docker** 最新版（容器）
- **OpenAI API** 不适用（服务）
- **Groovy** 3.0+（编程语言）

## 核心功能

- 自动化图像分析规划与宏生成
- 预配置 Fiji，集成 20+ 种生物图像分析插件
- 持久化向量数据库，支持插件文档检索
- 基于 Web 的 VNC 界面，实现图形界面交互
- 支持批量处理与自定义模型集成

## 快速开始

1. 安装 Git LFS 并克隆仓库
2. 将 `.env.template` 复制为 `.env` 并填入您的 API 密钥
3. 运行 `docker compose up` 启动容器
4. 在浏览器中打开 http://localhost:6080/vnc.html