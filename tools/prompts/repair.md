# 修复

上一版页面没有通过校验。下面是校验器给出的问题清单，逐条修掉，只改与问题相关的部分，其余内容保持不变。

只输出修好的完整 HTML 文档，从 <!doctype html> 开始，到 </html> 结束。不要解释，不要 Markdown 代码块。

常见问题的改法：

- 缺少 figcaption：给该 figure 补一句陈述句结论，用 <figcaption><span class="fig-n">Fig. N</span>…</figcaption>
- svg 缺少 aria-label：在 <svg …> 上加 aria-label="一句话说明这张图画了什么"
- kit 链接重复或缺失：head 里只保留一个 <link rel="stylesheet" href="kit.css" data-ve-kit>
- ve-bars 报错：label 不超过 9 个字，value 非负，max 不小于最大值且为正数，一张图只用一个 unit
- 正文太短：把阶段说明写具体，补上输入输出的含义，不要靠堆形容词
- 出现禁用短语：换一种写法，直接陈述
- 连线缺少动词：在该连线上方补 <text class="ve-el" x="…" y="…">动词</text>
