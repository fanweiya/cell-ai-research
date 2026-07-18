# Agentic-J — 综合分析报告

- **GitHub**: MMV-Lab/Agentic-J
- **评分**: 8.5/10
- **分析时间**: 2026-07-15T18:23:11.124043

---

## CodeGraph 知识图谱分析


## RepoWiki 文档生成

- ✅ 扫描成功
- 📁 Wiki 目录: `/mnt/c/workspace/cell-ai-research/reports/Agentic-J_wiki`
- 📄 生成文件:
  - architecture.md
  - dependencies.md
  - index.md
  - reading-guide.md
  - _sidebar.md
  - modules/.codegraph.md
  - modules/config.md
  - modules/data.md
  - modules/docs.md
  - modules/imagentj.md
- 输出: Project: imagentj
Files:   250
Lines:   46,743
      Languages       
┏━━━━━━━━━━━━┳━━━━━━━┓
┃ Language   ┃ Files ┃
┡━━━━━━━━━━━━╇━━━━━━━┩
│ markdown   │   147 │
│ unknown    │    59 │
│ python     │    32 │
│ yaml       │     2 │
│ shell      │     2 │
│ json       │     2 │
│ dockerfile │     1 │
│ toml       │     1 │
│ javascript │     1 │
│ css        │     1 │
└────────────┴───────┘
imagentj/
├── ⚙️ Dockerfile (dockerfile)
├── ⚙️ README.md (markdown)
├── ⚙️ docker-compose.yml (yaml)
├── 📁 docs/
│   ├── ⚙️ README.md (markdown)
│   ├── 📄 js/main.js (javascript)
│   ├── 📄 DEPLOY.md (markdown)
│   ├── 📄 SCREENSHOTS.md (markdown)
│   ├── 📄 css/styles.css (css)
│   └── 📄 index.html (html)
├── ⚙️ pyproject.toml (toml)
├── 📁 user_guide/
│   └── ⚙️ README.md (markdown)
├── 📄 run.py (python)
├── 📁 .codegraph/
│   └── 📄 .gitignore (unknown)
├── 📄 .dockerignore (unknown)
├── 📄 .env.template (unknown)
├── 📄 .gitattributes (unknown)
├── 📄 .gitignore (unknown)
├── 📄 LICENSE (unknown)
├── 📄 NOTI

## 原有子代理分析报告

```
现在我已经收集了足够的信息来分析这个仓库。让我开始编写结构化报告。

## 项目概述

Agentic-J 是一个由 AI 驱动的多智能体系统，专为生物显微镜图像分析设计。该项目来自论文 **"Agentic-J: An AI Agent for Biological Microscopy Image Analysis"** (arXiv:2606.02080，2026年6月)。

**核心问题**：生物图像分析需要整合多种异构工具、编程环境和领域知识，这对研究者构成了巨大挑战。Agentic-J 通过将多智能体系统与 ImageJ/Fiji 封装进 Docker 容器，将自然语言请求转化为可追溯的分割、追踪、定量、质量检查和报告流程。

**主要特点**：
- 容器化部署（Docker），提供 noVNC 远程桌面界面
- 多智能体协作架构（ supervisor + 专用 subagents）
- 基于 RAG 的持续学习机制（记录错误和解决方案）
- 完整的状态追踪（state ledger）确保可复现性
- 支持 30+  Fiji 插件（StarDist、Cellpose、TrackMate 等）

## 架构分析

### 目录结构
```
Agentic-J/
├── src/imagentj/           # 核心 Python 包
│   ├── agents.py           # 智能体定义和协调
│   ├── imagej_context.py   # ImageJ/Fiji 初始化
│   ├── prompts.py          # 系统提示词
│   ├── tracker.py          # 使用指标跟踪
│   ├── tools/              # 工具实现
│   │   ├── state_ledger.py # 状态账本（核心持久化机制）
│   │   ├── script_tools.py # 脚本执行和错误处理
│   │   ├── rag_tools.py    # RAG 检索和持久化
│   │   └── ...
│   └── rag/                # RAG 系统
├── skills/                 # 插件文档包（200+ SKILL.md 文件）
├── bundled_jars/           # 离线 JAR 依赖
├── data/                   # 数据和输出目录
├── models/                 # Cellpose 模型
├── Dockerfile              # 容器构建
├── docker-compose.yml      # 容器编排
└── environment.yml         # Conda 环境
```

### 主要模块
1. **Supervisor Agent**：中央协调者，负责任务分解和阶段控制
2. **Coder Agent**：生成 ImageJ/Fiji Groovy 脚本
3. **Debugger Agent**：修复失败的脚本
4. **Data Analyst Agent**：Python 统计分析
5. **QA Reporter Agent**：质量检查
6. **Plugin Manager Agent**：插件推荐和安装
7. **State Ledger**：JSON 形态的项目状态持久化
8. **RAG 系统**：基于 Qdrant 的文档、错误和经验检索

### 依赖关系
- **Java/Fiji**： ImageJ/Fiji 作为分析引擎
- **Python 3.10/3.11/3.13**：多个 Conda 环境（cellpose, stardist, cellpose4）
- **LLM**： OpenAI GPT-5 系列或 OpenRouter
- **向量数据库**：Qdrant（存储在 Git LFS 中）
- **Docker**：容器化部署

## 核心算法

### 1. 智能体协作模式
采用 **Supervisor-Subagent 架构**：
- Supervisor 接收用户请求，分解为 Pipeline Plan
- 通过 State Ledger 记录每个阶段的执行状态
- 根据阶段进度调用相应的 subagent 工具

### 2. 状态管理（State Ledger）
使用 `state_ledger.json` 实现**可追溯的流水线**：
```json
{
  "scientific_goal": "...",
  "completed_steps": [
    {"phase": "2", "step": "thresholding", "status": "completed", 
     "script_path": "...", "outputs": ["mask.tif"]}
  ],
  "key_decisions": [...],
  "image_metadata": {...}
}
```
- 原子写入保证数据完整性
- 紧凑格式（~800 tokens）适合 LLM 上下文
- 跨会话持久化

### 3. 脚本执行与错误处理
`script_tools.py` 实现了**健壮的 Groovy 执行环境**：
- 实时监控 ImageJ 窗口（错误对话框、结果表、信息窗口）
- 自动分类窗口内容：ERROR/RESULTS/INFO
- 失败时自动关闭新窗口，支持重试
- 捕获 IJ.log、STDOUT、STDERR 多源输出

### 4. RAG 持续学习
**三种向量集合**：
- **Docs**：BioimageAnalysisDocs（静态文档）
- **Mistakes**：codingerrors_and_solutions（错误→修复规则）
- **Recipes**：code_recipes（可复用脚本模板）

**关键设计**：
- 仅嵌入**症状描述**（rule），代码存储在 metadata 中
- 检索时应用**和相关性阈值**，避免噪声
- **去重机制**：相似经验合并 `times_seen` 计数

### 5. 插件推荐机制
Plugin Manager 使用 `SkillsMiddleware` 扫描 `skills/` 目录，根据科学任务推荐最佳插件，并强制 Coder 使用推荐插件。

## 代码质量

### 优点
1. **模块化设计**：工具包（`tools/`）职责清晰，每个工具都有明确的 `WHEN TO USE` 说明
2. **文档完整性**：200+ SKILL.md 文件覆盖所有 Fiji 插件，用户指南详尽
3. **错误处理**：完善的错误分类、捕获和修复机制
4. **可测试性**：状态账本、RAG 系统等核心组件易于独立验证
5. **原子操作**：文件写
```

> 完整报告: [reports/Agentic-J.md](Agentic-J.md)