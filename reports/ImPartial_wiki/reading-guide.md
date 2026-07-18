# Reading Guide

本指南旨在帮助开发者快速理解 ImPartial 项目，这是一个基于部分标注的交互式实例分割深度学习框架。建议从配置和入口点入手，逐步深入到核心逻辑和工具模块，最后通过文档和插件了解完整生态。

## Step 1: 理解项目概览与快速开始 (~10 min)

**Files:** `README.md`, `QUICK_START.md`

首先阅读 README.md 了解项目的整体目标、技术栈和架构概览，然后查看 QUICK_START.md 获取快速启动指南，明确运行环境和基本命令。

## Step 2: 配置环境与依赖 (~10 min)

**Files:** `Dockerfile`, `requirements.txt`, `setup.py`, `config/default.ini`

查看 Dockerfile 了解容器化部署方式，requirements.txt 和 setup.py 确认 Python 依赖，default.ini 了解默认配置参数，为后续代码阅读奠定基础。

## Step 3: 探索 API 入口与核心服务 (~15 min)

**Files:** `monailabel-app/api/main.py`, `monailabel-app/api/README.md`

main.py 是 API 服务的入口点，重点关注路由定义、中间件和核心处理逻辑；README.md 补充说明 API 的使用方法和接口规范。

## Step 4: 深入核心模块：ImPartial 框架 (~20 min)

**Files:** `impartial/general/config.py`, `impartial/README.md`

config.py 管理全局配置和参数解析，是理解框架行为的关键；同时查看该模块的 README 了解子模块结构和核心功能。

## Step 5: 理解数据加载与处理流程 (~15 min)

**Files:** `data/README.md`, `config/cpdmi_nc.ini`, `config/tissuenet_all.ini`

data/README.md 说明数据集结构和加载逻辑，配置文件展示不同数据集（如 CPDMI、TissueNet）的具体参数配置，理解数据如何被框架处理。

## Step 6: 学习训练与模型配置 (~15 min)

**Files:** `config/cpdmi_no_rec.ini`, `config/tissuenet_orig_iterative.ini`

这些配置文件详细定义了训练超参数、模型架构和损失函数，对比不同配置可以深入理解框架的灵活性和可定制性。

## Step 7: 掌握图像插件与用户交互 (~10 min)

**Files:** `imagej-plugin/README.md`, `imagej-plugin/pom.xml`

imagej-plugin 模块提供了与 ImageJ 的交互能力，通过 README 了解插件功能，pom.xml 确认 Java 依赖和构建配置，理解前后端协作方式。

## Step 8: 熟悉辅助工具与代码管理 (~5 min)

**Files:** `.codegraph/.gitignore`, `.gitignore`, `.gitattributes`

查看这些文件了解项目的代码图管理、版本控制规则和忽略文件策略，有助于理解项目的开发工作流和协作规范。

## Tips

- 在阅读代码时，优先关注函数签名和注释，快速把握接口设计意图。
- 结合配置文件和代码逻辑一起阅读，能更直观地理解参数如何影响系统行为。
- 遇到不熟悉的模块时，先查看其 README 或文档，建立整体认知后再深入细节。
- 利用 Dockerfile 和 requirements.txt 快速搭建本地开发环境，边运行边调试学习效果更佳。
