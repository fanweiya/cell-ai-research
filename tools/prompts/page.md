# 任务

把给定的「原理底稿」JSON 写成一个自包含的中文 HTML 页面。这个页面属于一个论文索引站，读者从索引点进来，要在十秒内看懂这篇论文的核心机制。页面使用 visual-explainer 技能提供的 kit 与 paper 记录（衬线标题、窄文字栏、宽图、Fig. N 编号）。

# 输入

- 底稿 JSON：全部文案与数字的唯一来源
- 论文题录：标题、作者、日期、任务类型、arXiv 编号、是否有代码
- 摘要与核心要点：补充语境

底稿之外不新增事实、数字、数据集名称或结论。底稿里的数字原样使用。

# 输出

只输出一个完整的 HTML 文档，从 <!doctype html> 开始，到 </html> 结束。不要 Markdown 代码块，不要解释，不要注释。

# 固定骨架

下面的结构固定，占位内容按底稿填写。style 块逐字保留，不要增删规则。

<!doctype html>
<html lang="zh-CN" data-register="paper">
<head>
<title>{one_line 原样，若末尾有句号去掉} · 图解</title>
<link rel="stylesheet" href="kit.css" data-ve-kit>
<style>
  body{font-family:'Atkinson Hyperlegible Next','Source Han Serif SC','Noto Serif SC','Songti SC','SimSun',serif}
  h1,h2{font-family:'Newsreader','Source Han Serif SC','Noto Serif SC','Songti SC','SimSun',serif}
  .ve-svg text{font-family:'Source Han Serif SC','Noto Serif SC','Songti SC',sans-serif}
  .ve-n .sub,.ve-kind,.ve-el,.ve-tag,.ve-label,.meta,.fig-n,.eyebrow{font-family:'Geist Mono','Source Han Serif SC',monospace}
  .lead{font-size:1.15rem}
  .stage-list{list-style:none;padding:0;display:grid;gap:var(--s-5)}
  .stage-list li{display:grid;grid-template-columns:2.2rem minmax(0,1fr);gap:var(--s-3)}
  .stage-num{width:2.2rem;height:2.2rem;border-radius:50%;background:var(--accent);color:var(--bg);font:700 15px/2.2rem var(--font-mono);text-align:center}
  .stage-list h3{margin:0 0 var(--s-1)}
  .stage-list p{margin:0;color:var(--text-dim)}
  .stage-list .io{font:500 var(--t-label) var(--font-mono);color:var(--text-dim);margin-top:var(--s-2)}
  .stage-badge circle{fill:var(--accent)}
  .stage-badge text{fill:var(--bg);font:700 15px var(--font-mono);text-anchor:middle;dominant-baseline:central}
  .kpis{margin:var(--s-4) 0 var(--s-5)}
  footer.src{margin-top:var(--s-8);border-top:1px solid var(--border);padding-top:var(--s-4);color:var(--text-dim);font-size:var(--t-small)}
  footer.src a{color:var(--accent)}
</style>
</head>
<body>
<nav class="ve-toc" aria-label="Sections"><div>
<a href="#problem">困难</a><a href="#mechanism">机制</a><a href="#design">取舍</a><a href="#results">结果</a><a href="#limits">边界</a><a href="#remember">记住</a>
</div><span class="pos"></span></nav>
<main>
<header>
  <p class="eyebrow">图解 · {任务类型} · {日期}</p>
  <h1>{one_line}</h1>
  <p class="lead">{intuition}</p>
  <p class="meta">{作者前三位等} · arXiv {编号} · <a href="https://arxiv.org/abs/{编号}">原文</a> · <a href="../index.html#paper-{编号原样，带 v1 这类版本后缀}">返回论文索引</a></p>
</header>

<figure>
  <div class="frame"><svg class="ve-svg" viewBox="0 0 960 400" role="img" aria-label="{一句话描述这张图}">
    <!-- 先画连线，再画节点，最后画编号徽章 -->
  </svg></div>
  <figcaption><span class="fig-n">Fig. 1</span>{一句话结论，陈述句}</figcaption>
</figure>

<section id="problem">
  <div class="sec-head"><p class="ve-label caps">问题</p><h2>{小标题，陈述这篇论文要解的困难}</h2></div>
  <p>{problem 展开为两段，每段一到三句}</p>
  <figure>
    <div class="frame"><svg class="ve-svg" viewBox="0 0 960 360" role="img" aria-label="{旧做法与新做法的差别}">
      <!-- 左右两块虚线边界，各自画流程 -->
    </svg></div>
    <figcaption><span class="fig-n">Fig. 2</span>{旧做法卡在哪，新做法改了什么}</figcaption>
  </figure>
</section>

<section id="mechanism">
  <div class="sec-head"><p class="ve-label caps">机制</p><h2>{机制的一句话结论}</h2></div>
  <ol class="stage-list">
    <li><span class="stage-num">1</span><div><h3>{stages[0].name}：{stages[0].action}</h3><p>{stages[0].detail}</p><p class="io">输入 {stages[0].input} → 输出 {stages[0].output}</p></div></li>
    <!-- 每个 stage 一项，编号与 Fig. 1 上的徽章一致 -->
  </ol>
</section>

<section id="design">
  <div class="sec-head"><p class="ve-label caps">取舍</p><h2>{设计选择的一句话结论}</h2></div>
  <div class="ve-table"><table>
    <thead><tr><th>采用</th><th>放弃的选项</th><th>原因</th></tr></thead>
    <tbody>
      <!-- design_choices 每条一行 -->
    </tbody>
  </table></div>
</section>

<section id="results">
  <div class="sec-head"><p class="ve-label caps">结果</p><h2>{结果的一句话结论}</h2></div>
  <div class="kpis">
    <!-- key_facts 每项一个 .kpi：<div class="kpi"><span class="ve-label">label</span><span class="val">value</span><span class="ve-label">note</span></div> -->
  </div>
  <figure>
    <!-- 数字图：优先 <ve-bars>，无法成图时用 .cases 画两个使用场景 -->
    <figcaption><span class="fig-n">Fig. 3</span>{数字说明的结论，含对比}</figcaption>
  </figure>
</section>

<section id="limits">
  <div class="sec-head"><p class="ve-label caps">边界</p><h2>{什么条件下结论会变化}</h2></div>
  <ul>
    <!-- limits 每条一项，写成具体条件 -->
  </ul>
</section>

<section id="remember">
  <div class="sec-head"><p class="ve-label caps">记住</p><h2>{takeaway}</h2></div>
  <div class="ve-table"><table>
    <thead><tr><th>术语</th><th>中文</th><th>一句话解释</th></tr></thead>
    <tbody><!-- terms 每条一行 --></tbody>
  </table></div>
  <details><summary>原文依据</summary><ul><!-- evidence 每条：<li>“quote”——claim</li> --></ul></details>
</section>

<footer class="src">
  <p>本页依据论文原文与结构化分析生成，机制图为示意，细节以 <a href="https://arxiv.org/abs/{编号}">arXiv {编号}</a> 为准。</p>
</footer>
</main>
</body>
</html>

# 用词禁忌

全文不许出现这些词与句式：「落地」「对齐」「钉死」「技术栈」「闭环」「赋能」「综上所述」「总而言之」「值得注意的是」「不是……而是……」。要表达对应关系就写「一一对应」「同一套坐标」「合到一张图上」，要表达推进就写「实施」「接入」「上线」。校验器会逐条扫描，出现一次就要重写整页。

# 图怎么画

数值条 <ve-bars> 的每根条后面只写数字本身，写成 88.1、97.6、0.976 这样，不带百分号、不带单位、不带空格、不带汉字，小数最多三位，合计不超过 6 个字符；单位与口径写进 label 与 figcaption。写成「0.565 mIoU」「0.9762分」「88.1%」都会被渲染器判超长而整页退回。

Fig. 1 画机制全图，节点数量等于 stages 数量，节点顺序与 stages 一致，每个节点左上角放编号徽章，编号与正文阶段编号一致。节点之间用带箭头的连线连接，每条连线上方写动词（编码、检索、打分、回填、拼接这类具体的动作），不能写"处理""转换"这种空词。

坐标规则：viewBox 宽度固定 960。节点矩形宽 170 到 200，高 96，圆角 8，水平间距至少 70。3 个阶段排一行，viewBox 高度 400，节点 y=150；4 个阶段排一行，viewBox 高度 400，节点 y=150；5 个阶段排成 3 加 2 两行，viewBox 高度 560，第一行节点 y=110，第二行节点 y=330，第二行用回折连线，箭头从第一行末端向下再向左指回。所有节点必须落在画布内：节点 y 加 96 不能超过 viewBox 高度减 8。节点内的文字居中：<text x="节点中心x" y="44">，副标题 <text class="sub" x="节点中心x" y="70">。

连线的写法：

<path class="ve-e" d="M250 160H330"/>
<text class="ve-el" x="290" y="142">编码</text>

箭头由 kit 的 .ve-e 自动加上，线的终点要停在下一个节点左边缘前 10 像素。主线用 class="ve-e is-hot"，旁路与异步用 class="ve-e is-async"。

节点的写法（以第一个为例，x 从 60 起）：

<g class="ve-n is-key" transform="translate(60 120)"><rect class="sh" width="180" height="96" rx="8"/><text class="ve-kind" x="90" y="24">输入</text><text x="90" y="50">明场图像</text><text class="sub" x="90" y="72">2048 × 2048</text></g>
<g class="stage-badge" transform="translate(60 120)"><circle r="14"/><text>1</text></g>

is-key 只给最重要的那个节点，is-hot 只给最关键的一条连线，全页各一处。

五种结构的排布方式：

- linear：从左到右一条主线
- encoder_decoder：左塔两个节点上下叠放（编码器与输入），中间一个窄的潜变量节点，右塔两个节点上下叠放（解码器与输出）
- iterative：三个节点围成环，环上一条回边写"迭代 N 次"，环心写迭代目标
- branch_merge：左一个节点分成两条支路，右端汇合，支路各写一个条件
- retrieval：下方一个宽的外部库节点，查询节点向上取回，回边写"取回 k 条"

Fig. 2 画对比，viewBox 960 宽 360 高。左右各画一个虚线边界 <rect class="ve-bnd" x="40" y="60" width="400" height="250" rx="10"/> 与标签 <text class="ve-bnd-t" x="56" y="88">原有做法</text>，右侧同样。每边画两三个小节点（宽 140、高 70）与一条连线，旧做法在失败的那条连线上画 <text class="ve-x" x="…" y="…">✕</text>，新做法把改动的节点用 is-new 标出。

Fig. 3 用数字。指标与基线单位相同时：

<figure>
  <ve-bars unit="%" max="100" label="本方法在三个数据集上的准确率都高于基线"><ve-bar value="86" hot>本方法</ve-bar><ve-bar value="71">基线</ve-bar></ve-bars>
  <figcaption><span class="fig-n">Fig. 3</span>{结论}</figcaption>
</figure>

ve-bars 的两个字段有硬上限，超一个字符渲染器直接报错：条后的数值标签最多 6 个字符（空格也算），条左侧的名字最多 9 个字符（空格也算）。名字用短名：方法名压到 6 个字符以内（Pic2Spec、MedCLIP、CellViT、本方法、基线），数据集名超过 9 个字符就换成缩写（CityScapes 写 City、Camelyon16 写 Cam16）。同一张图共用一个 max 与一个 unit，bar 从零起。数字无法成图时，用 <div class="cases"> 与 <div class="case"> 画两个使用场景，每个 case 里放一个 <svg class="ve-mini" viewBox="0 0 240 128"> 与一句说明。

# 文字要求

- 正文（图注、表格、页脚之外）1200 到 1800 个汉字
- 每段一到三句，一句一个意思，主动语态，现在时
- 小标题陈述结论，不写"方法介绍""实验结果"这类话题名
- 数字后面不空行，数字与单位之间用 &nbsp;
- 中文引号用“”，范围用 –，负号用 −
- 不使用"不是……而是……"的对比句式，不使用"综上所述""总而言之""值得注意的是"
- 不使用 emoji
- 正文里出现的每个数字都必须来自底稿
- 正文提到某个阶段时，用与 Fig. 1 相同的编号

# 自检

输出前核对：只有一个 kit 链接；每个 figure 都有 figcaption；每个 svg 都有 aria-label 与 viewBox；Fig. 1 的节点数量等于 stages 数量；每条连线都有动词标签；正文数字都能在底稿里找到；页面里没有 <script>、没有外部图片、没有 Google Fonts 链接。
