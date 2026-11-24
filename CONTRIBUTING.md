# 贡献指南

感谢关注并参与维护 Cell AI Research 项目。本项目旨在建立具备证据支持的细胞生物学与人工智能交叉领域前沿论文索引、评测体系与可视化站点。

## 开发环境准备

### 系统要求

- Python 3.10 及以上版本
- Node.js 20 及以上版本
- Git

### 安装步骤

1. 克隆仓库并切换至对应分支：
   ```bash
   git clone https://github.com/fanweiya/cell-ai-research.git
   cd cell-ai-research
   ```

2. 安装 Python 依赖：
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov ruff
   ```

3. 安装前端与测试依赖：
   ```bash
   npm install
   ```

4. 配置本地环境变量：
   复制配置文件模板并按需填写服务密钥：
   ```bash
   cp .env.example .env
   ```

## 运行自动化测试

提交代码前，必须确保全部测试执行通过：

```bash
# 运行前端与 DOM 交互测试
npm test

# 运行 Python 单元与集成测试
pytest tests/
```

## 代码规范

- Python 代码使用 Ruff 进行静态检查与格式验证：
  ```bash
  ruff check .
  ```
- 代码标识符保持英文原名，中文注释清晰准确。
- 所有异常与错误处理保持快速失败原则，在出现问题的位置及时终止并给出明确提示信息。

## 提交规范

建议遵循约定式提交（Conventional Commits）标准：

- `feat`: 新增功能特性（如新分析维度、新抓取管道）
- `fix`: 修复程序缺陷
- `docs`: 文档增补与修订
- `test`: 测试用例增补与调整
- `refactor`: 重构且不改变外部行为

### 提交 data/translations.json 前必做（见 #402）

翻译缓存是直接展示的数据，入库前必须校验，提交信息必须如实写范围：

```bash
python3 tools/validate_translations.py --since HEAD
```

- 校验不通过（任一条目无有效中文或疑似供应商错误文本，如额度耗尽提示）
  时不得提交，先清空/重译该条目。
- 提交信息须列出本次新增的全部论文编号（用 `--since` 输出的清单，不要
  只写其中两条）；改动旧条目时另注明改动条数。

## Pull Request 流程

1. 基于 `main` 分支创建功能分支：
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. 完成修改并确保本地所有测试通过。
3. 提交代码并推送至个人远程仓库。
4. 发起 Pull Request，按模板填写变动说明与验证结果。
