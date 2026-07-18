# Reading Guide

本代码库是一个基于容器的AI代理系统，用于自动化ImageJ/Fiji显微镜图像分析工作流。建议按从宏观配置到核心逻辑的顺序阅读，优先理解部署架构和入口点，再深入模块功能。

## Step 1: 理解项目概览与部署架构 (~15 min)

**Files:** `README.md`, `docker-compose.yml`, `Dockerfile`

首先通过README.md了解项目目标和整体架构，然后查看docker-compose.yml理解服务编排和依赖关系，最后阅读Dockerfile了解容器构建细节和运行环境配置。

## Step 2: 掌握环境变量与配置管理 (~10 min)

**Files:** `.env.template`, `pyproject.toml`, `config/`

查看.env.template了解必需的环境变量和配置项，通过pyproject.toml理解Python依赖和项目元数据，浏览config目录了解AI代理运行所需的外部依赖配置和检索参数。

## Step 3: 探索应用入口与启动流程 (~15 min)

**Files:** `run.py`, `docker-entrypoint.sh`

run.py是Python应用的主入口，理解其如何初始化AI代理和连接外部服务；docker-entrypoint.sh是容器启动脚本，了解容器化部署的初始化流程和命令执行逻辑。

## Step 4: 理解核心模块：ImageJ集成 (~20 min)

**Files:** `imagentj/`

浏览imagentj模块的所有文件，重点关注ImageJ/Fiji的Java桥接实现、脚本执行机制和图像分析API封装，这是AI代理与图像分析工具交互的核心层。

## Step 5: 学习技能模块与AI代理能力 (~25 min)

**Files:** `skills/`

skills模块包含188个文件，是AI代理的具体能力实现。重点关注技能定义、提示工程模板和工具调用逻辑，理解代理如何规划任务并调用ImageJ功能。

## Step 6: 掌握脚本管理与执行机制 (~15 min)

**Files:** `scripts/`, `patch_stardist/`

scripts目录存储ImageJ/Groovy脚本及其元数据，了解脚本如何被AI代理调用和执行；patch_stardist包含对TrackMate-StarDist的修复，理解特定插件的兼容性问题处理。

## Step 7: 理解数据管理与向量检索 (~10 min)

**Files:** `data/`, `qdrant_data/`

data目录存储容器环境快照和运行时元数据，qdrant_data管理向量数据库配置。了解AI代理如何存储和检索知识，以及环境状态的持久化机制。

## Step 8: 熟悉代码图与监控机制 (~10 min)

**Files:** `.codegraph/`

.codegraph目录管理代码图数据的本地缓存、守护进程和通信套接字，了解项目如何维护和查询代码结构信息，这对AI代理理解代码库很重要。

## Tips

- 先阅读文档再深入代码，特别是user_guide/README.md和docs/DEPLOY.md
- 重点关注AI代理如何与ImageJ交互，这是系统的核心创新点
- 注意容器化部署的特殊性，理解docker-entrypoint.sh和Dockerfile的协同工作
- 遇到复杂逻辑时，结合调试日志和实际运行场景理解
