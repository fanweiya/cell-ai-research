# Cell AI Research

细胞计算与生物医学 AI 学术前沿智能追踪与评测平台。系统通过自动化工作流持续监测 arXiv 与 bioRxiv 相关最新论文，提取论文全文与图示，结合远程代码仓库静态分析与多阶段推断评估，生成高可读性的交互式文献检索门户与分析报告。

## 核心能力

- **多阶段文献分析**：对通过相关性初筛的论文，执行任务定义、算法推断、代码实现评估与批判性推断四个阶段的深入分析。
- **免克隆远程代码审计**：基于 `gread` HTTP 接口对开源代码仓库执行树形分析、关键字检索与关键源码阅读，避免拉取大型完整仓库。
- **多模态图示解析**：从 arXiv HTML 文档直接提取论文关键插图，并通过多模态视觉模型筛选与核心结论强相关的图示。
- **静态证据分块与校验**：通过 SHA256 数字摘要导出切片式原文证据（`data/evidence/`），确保交互式回答具有可追溯的原文凭据。
- **高性能交互式门户**：单文件构建整合 KaTeX 离线数学公式渲染、文献多维度筛选、深浅主题切换与 Copilot 交互助手。
- **增量构建与自动发布**：与 Cloudflare Pages 及定时任务系统结合，支持数据增量更新、构建状态挂起及自动重试。

## 目录结构

```text
.
├── papers.json               # 核心文献元数据库（收录论文元数据与处理状态）
├── generate_index.py         # 门户网站构建核心脚本（生成 index.html）
├── daily_site_update.py      # 增量构建与定时发布状态管控
├── evidence_export.py        # 论文原文切片与 SHA256 凭据导出
├── gread_remote.py           # 远程 GitHub 代码仓库静态审计客户端
├── subagent.py               # 多阶段学术分析调度器
├── backfill_analysis.py      # 缺失分析阶段增量补偿工具
├── text_render.py            # LaTeX 宏清理与安全文本渲染
├── publish_cf_pages.sh       # Cloudflare Pages 自动化发布脚本
├── CLOUDFLARE_DEPLOY.md      # Cloudflare 凭据配置与部署指南
├── web/                      # 前端样式、列表交互与 Copilot 逻辑
├── vendor/                   # 离线第三方库（KaTeX 资源）
├── data/                     # 文献分析缓存、翻译与原文凭据
├── knowledge/                # 细胞 AI 领域知识图谱与分类总结
├── reports/                  # 各重点论文的独立分析 Wiki
├── results/                  # 结构化阶段分析输出 JSON
└── tests/                    # 完整自动化测试套件（Python + Node.js）
```

## 运行与验证

### 1. 运行测试套件

Python 单元测试：
```bash
python3 -m unittest discover -s tests
```

Node.js 前端行为测试：
```bash
node --test tests/*.test.cjs
```

### 2. 本地重新生成门户网页

```bash
python3 generate_index.py --no-translate --no-code-analysis
```
执行后将在项目根目录下更新 `index.html`。这两项只用于本地快速预览页面：每日发布用的重建必须完整执行，不要传 `--no-images` 或 `--no-code-analysis`，让缺失或无效的翻译、图示与代码分析缓存自动重试。

### 3. 发布至 Cloudflare Pages

配置好环境变量凭据后执行：
```bash
bash publish_cf_pages.sh
```
具体凭据配置细节参见 [CLOUDFLARE_DEPLOY.md](CLOUDFLARE_DEPLOY.md)。
