# Cell AI Research (细胞计算与生物医学 AI 学术前沿智能追踪平台)

<div align="center">

**前沿学术文献智能追踪 · 免克隆代码审计 · 证据切片凭据 · 学术 Copilot 交互门户**

[![Demo](https://img.shields.io/badge/Demo-cell--ai--research.pages.dev-6366F1?style=flat&logo=cloudflare)](https://cell-ai-research.pages.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Deployment-Cloudflare%20Pages-F38020?style=flat&logo=cloudflarepages)](https://cell-ai-research.pages.dev/)

[在线演示平台 (Demo)](https://cell-ai-research.pages.dev/) · [功能特性](#-功能特性) · [系统架构](#-系统架构) · [本地运行与测试](#-本地运行与测试) · [开源协议](#-开源协议)

</div>

---

## 📖 项目简介

生物医学与单细胞计算科学领域（如单细胞转录组学 scRNA-seq、空间转录组学 Spatial Transcriptomics、显微细胞影像分割、细胞图谱与基础大模型等）的前沿论文呈爆发式增长。研究人员往往需要频繁检索预印本、验证论文提出的算法机制、核查开源代码实现完整度以及追溯核心实验证据。

**Cell AI Research** 是一个自动化、证据化驱动的学术前沿追踪与智能研读平台。系统具备定时持续监控、免克隆远程代码审计、多阶段深度推断评估、原文切片证据指纹生成与现代化单页静态交互门户能力。

- **在线交互演示体验**：[https://cell-ai-research.pages.dev/](https://cell-ai-research.pages.dev/)

---

## ✨ 功能特性

### 1. 自动化前沿追踪流水线
- **多源数据持续监测**：自动监测 arXiv、bioRxiv 等前沿预印本平台，通过关键词匹配与领域分类模型筛选高价值论文。
- **全文与图示解析**：自动解析 arXiv 论文源码与 HTML 结构，提取关键章节、数学公式以及高清实验插图，通过视觉分析定位与核心结论紧密关联的关键图示。

### 2. 四阶段深度学术推断与评估
针对每一篇入库文献，系统流水线自动执行四个维度的结构化评测：
1. **任务定义与研究贡献**：提炼论文面对的生物学挑战、解决的核心科学问题与理论贡献。
2. **核心算法推断与数学推导**：解析方法网络结构、损失函数设计、注意力机制与理论合理性。
3. **免克隆代码实现评估**：基于 `gread` 远程接口直接对 GitHub 代码仓库进行树形遍历与关键模块解析，免除下载大体积仓库开销，客观评测代码可复现性、核心模块完整度与环境依赖。
4. **批判性分析与潜在局限性**：推断基线实验充分度、算力消耗瓶颈与数据分布偏差。

### 3. 原文切片与数字凭据体系
- 生成切片式证据分块（存放于 `data/evidence/`），包含段落原文内容、元数据及 SHA-256 唯一指纹。
- 为后续的 AI 问答提供可追溯的锚点，确保学术推断每一条关键结论均对应原文出处。

### 4. 现代化学术交互门户与内置 Copilot
- **高性能前端交互**：单页架构，集成深浅主题切换、多维度标签分类、月份翻阅与关键词毫秒级实时检索。
- **离线数学公式渲染**：集成 KaTeX 离线渲染方案，保障复杂矩阵与生信公式极速清晰呈现。
- **学术交互助手 (Copilot)**：
  - 支持单篇论文或自由勾选多篇论文创建对比研究会话。
  - 自动注入论文精准切片证据，支持多篇文献对比分析、技术细节横向评测与表格生成。
  - 支持快捷跳转与证据定位锚点联动。

### 5. 持续集成与边缘发布
- 支持基于 Cloudflare Pages 进行边缘分发加速，支持定时任务增量构建与发布更新。

---

## 🗂 目录结构

```text
.
├── papers.json               # 核心文献元数据库（结构化元数据与阶段评测状态）
├── generate_index.py         # 门户构建核心程序（生成单页 index.html）
├── daily_site_update.py      # 自动化增量构建与发布状态管控调度
├── evidence_export.py        # 论文原文切片与 SHA-256 证据凭据导出
├── gread_remote.py           # 远程 GitHub 开源代码仓库静态审计客户端
├── subagent.py               # 多阶段学术深度分析调度器
├── backfill_analysis.py      # 缺失分析阶段增量补偿工具
├── text_render.py            # LaTeX 宏清理与安全文本渲染
├── publish_cf_pages.sh       # Cloudflare Pages 边缘自动化发布脚本
├── CLOUDFLARE_DEPLOY.md      # Cloudflare 凭据配置与部署详细指南
├── web/                      # 前端组件资源（样式表、交互脚本与 Copilot 逻辑）
│   ├── copilot.js            # 学术 Copilot 会话、证据检索与流式交互
│   ├── copilot.css           # Copilot 侧边抽屉与消息流样式
│   ├── paper-list.js         # 论文卡片列表渲染、过滤与筛选交互
│   └── theme.js              # 深色/浅色主题切换管控
├── vendor/                   # 离线第三方静态资源（KaTeX 字体与样式）
├── data/                     # 文献分析缓存、翻译映射与原文凭据库
├── knowledge/                # 细胞计算与 AI 领域知识图谱与分类总结
├── reports/                  # 重点文献的独立分析报告
├── results/                  # 结构化阶段分析输出 JSON
└── tests/                    # 完整自动化测试套件（Python 单元测试与 Node.js 行为测试）
```

---

## 🚀 本地运行与测试

### 环境依赖
- **Python**: 3.10 或更高版本
- **Node.js**: 18.0 或更高版本（用于前端行为测试与本地部署验证）

安装 Python 运行依赖：
```bash
pip install -r requirements.txt
```

### 1. 运行自动化测试套件

执行 Python 单元测试：
```bash
python -m unittest discover -s tests
```

执行 Node.js 前端交互行为测试：
```bash
node --test tests/*.test.cjs
```

### 2. 本地构建生成门户页面

执行以下命令快速生成前端门户页面：
```bash
python generate_index.py --no-translate --no-code-analysis
```
命令完成后会在项目根目录生成单页文件 `index.html`，可直接通过浏览器打开查看，或使用轻量 HTTP 服务预览：
```bash
npx serve .
```

### 3. 发布至 Cloudflare Pages

配置好 Cloudflare 账号凭据与项目名称后，执行一键发布脚本：
```bash
bash publish_cf_pages.sh
```
部署配置说明参见 [CLOUDFLARE_DEPLOY.md](CLOUDFLARE_DEPLOY.md)。

---

## 🌐 在线体验

欢迎访问已部署在 Cloudflare Pages 上的实时演示站点：  
👉 [https://cell-ai-research.pages.dev/](https://cell-ai-research.pages.dev/)

---

## 📜 开源协议

本项目基于 [MIT License](LICENSE) 开源发布。
