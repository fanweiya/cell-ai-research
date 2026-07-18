# docs

> 提供 Agentic-J 项目的静态着陆页、部署指南和截图规范。

docs 模块包含一个完全静态的网站，用于展示 Agentic-J 的功能、架构和快速开始指南。该网站设计为无依赖、无构建步骤，可直接托管在 GitHub Pages 上。模块核心文件包括 HTML 页面、CSS 样式表、JavaScript 交互脚本以及相关的文档说明。

## Files

### `docs/README.md`

项目文档的入口索引，概述了网站结构、本地预览方法和部署步骤。

### `docs/js/main.js`

实现着陆页的渐进增强交互功能，包括滚动显现、代码复制和导航高亮。

- `IntersectionObserver (reveal-on-scroll)` (function) - 监听带有 .reveal 类的元素，当进入视口时添加 .in 类以触发动画。
- `Copy-code buttons` (function) - 为代码块添加复制按钮，点击后将代码文本写入剪贴板并反馈状态。
- `Active nav link (scrollspy)` (function) - 监听页面滚动，根据当前可见的 section 高亮对应的导航链接。

### `docs/DEPLOY.md`

详细说明了将静态网站部署到 GitHub Pages 的三种方案：手动一次性部署、子树持续部署和 GitHub Actions 自动部署。

### `docs/SCREENSHOTS.md`

规定了生成着陆页所需四张关键截图的捕获方法、尺寸要求和文件名规范。

### `docs/css/styles.css`

定义现代科学风格的暗色主题样式，包含 CSS 变量、重置样式、背景网格和组件样式。

### `docs/index.html`

单页着陆页的 HTML 结构，包含导航栏、英雄区域、功能介绍、架构说明和快速开始部分。

## Key Concepts

- **无构建静态站点**: 网站由纯 HTML/CSS/JS 组成，无需 Node.js 构建工具，可直接部署。
- **渐进增强**: JS 脚本在基础 HTML 之上提供交互增强，即使 JS 加载失败页面仍可用。
- **GitHub Pages 托管**: 支持通过 gh-pages 分支或 GitHub Actions 自动部署到 GitHub Pages。
- **暗色科学主题**: 使用深色背景、渐变强调色和现代字体，符合科学软件的专业形象。

## Internal Relationships

- `docs/index.html` → `docs/css/styles.css`: HTML 引入 CSS 文件以应用暗色主题和布局样式。
- `docs/index.html` → `docs/js/main.js`: HTML 在页面加载后执行 JS 脚本，启用滚动动画、代码复制和导航交互。
- `docs/README.md` → `docs/DEPLOY.md`: README 引导用户阅读 DEPLOY.md 以了解部署流程。
- `docs/README.md` → `docs/SCREENSHOTS.md`: README 引导用户阅读 SCREENSHOTS.md 以获取截图指南。
