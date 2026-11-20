# 单篇论文图解页任务

项目根目录是 `{{ROOT}}`，你就在这个目录里干活，所有命令都在这里执行。编号是 `<编号>`，工作目录是 `data/explainers/agent/<编号>`。

你要为细胞生物学与人工智能交叉方向的论文索引站，写一篇中文「图解」页：一张能让人看懂这篇论文原理与证据的单页 HTML。

## 你拿到的东西

- `data/explainers/agent/<编号>/paper.md`：题录、中文摘要、核心要点、结构化分析、全文（可能有核心代码片段）。
- `data/explainers/agent/<编号>/repo.txt`：作者仓库地址；写着「无公开仓库」时说明没有可读代码。
- 技能目录 `tools/visual-explainer/plugins/visual-explainer`：
  - `SKILL.md` 是总说明，`references/kit.md` 讲样式与类名，`references/diagrams.md` 讲图怎么画，`references/style-guide.md` 讲排版与语气，`examples/` 里有完整示例页。
- 已完成的页面可以拿来对照：`explainers/` 里任意一个 `.html` 是渲染结果，`data/explainers/src/` 里有对应的源文件。
- 渲染与校验命令：
  `node tools/visual-explainer/plugins/visual-explainer/kit/render.mjs data/explainers/agent/<编号>/out/<编号>.src.html -o data/explainers/agent/<编号>/out/<编号>.html --no-check`

## 交付

1. 源文件写到 `data/explainers/agent/<编号>/out/<编号>.src.html`：完整 HTML 文档，`<html lang="zh-CN" data-register="paper">`，`<link rel="stylesheet" href="kit.css" data-ve-kit>` 恰好一个。
2. 用上面的命令渲染，直到输出里不再出现 `✗`（出现就按提示改源文件再渲染，最多改三轮，仍不过就把问题写进 `data/explainers/agent/<编号>/notes.md` 并停下）。
3. 正文固定六个版块，缺一不可，`<section>` 的 id 必须逐字照下面写，校验器按字符串找：
   `id="problem"` 困难、`id="mechanism"` 机制、`id="design"` 取舍、`id="results"` 结果、`id="limits"` 边界、`id="remember"` 记住。不要用 tradeoff、summary、limitations 这类别的 id。结论段写在页头的 `<p class="lead">` 里，不单独开版块。
4. 三个 figure，每个都要有 `<figcaption>`：
   - Fig. 1 机制全图：三到五个阶段，每个节点是一个操作，连线标签是动词（读入、拼接、编码、重建、打分）。
   - Fig. 2 新旧对比：左右两块，虚线面板，写清旧做法与本篇做法的差别。
   - Fig. 3 关键数字：用 `<ve-bars>` 画三到五根条，数值只写数字本身，单位写进 figcaption。
5. 正文中文 1200 到 1800 字，每段一到三句。术语第一次出现时用大白话补一句解释，页面末尾放术语表。
6. 页头 eyebrow 写 `图解 · {任务类型} · {日期}`，任务类型与日期从 `paper.md` 的题录里取；`<title>` 写 `{一句话结论} · 图解`。全页不要出现「原理解读」四个字。任务类型用中文写（分割、分类、检测、追踪、重建、组织病理、空间转录组、虚拟成像、表征学习、基础模型、基准评测、计数、诊断、多模态），不要照抄 `segmentation` 这类英文代码；两个以上用「/」连起来，最多三个。
7. 页头 meta 里写 arXiv 链接 `https://arxiv.org/abs/<编号>`，以及返回索引的链接 `../index.html#paper-<编号>`（编号带版本后缀，原样照抄）。
8. 数字一律来自 `paper.md`，不许估算、不许四舍五入到好看的值；写不出来就换一个材料里有的数字。
9. 不要自己往页面里插论文原图或截图；渲染通过后流水线会自动补一段「原文关键图」，你只管画三张示意图。

## 工作顺序

1. 先读 `SKILL.md` 与 `references/kit.md`、`references/diagrams.md`，看清类名与图的画法，再读 `examples/` 里的完整示例与一篇已完成页面，照它的骨架写。
2. 读 `paper.md`，用三五句话在 `data/explainers/agent/<编号>/notes.md` 里写清：这篇论文解决什么问题、核心机制是什么、凭什么说自己有效、边界在哪。
3. `repo.txt` 有地址时，`git clone --depth 1 <地址> data/explainers/agent/<编号>/repo`，读模型定义、损失、训练循环这几处关键文件，把张量走向对应到 Fig. 1 的节点上。克隆失败就跳过，在 `notes.md` 记一句原因。分析完成后，必须主动删除 `data/explainers/agent/<编号>/repo` 目录，不保留代码仓库。
4. 写页面，渲染，按 `✗` 逐条改到通过。
5. 收尾自检：六个版块是否齐、三个 figure 是否有图注、每个数字能否在 `paper.md` 找到、有没有出现下面这些词。

## 用词禁忌

不要出现：落地、对齐、钉死、技术栈、闭环、赋能、综上所述、总而言之、值得注意的是，也不要写「不是……而是……」这种句式。标题与正文用朴素陈述，不要写「本文将带你」这类导语。

## 风格

读者是生物医学研究者与有工程背景的人。先说这篇论文要解决的问题，再说机制，最后给数字与边界。句子短，少用形容词，不用感叹号，不吹。
