# DriftST — 综合分析报告

- **GitHub**: https://github.com/yyh030806/DriftST
- **分析时间**: 2026-07-16T09:29:11.416602

---

## CodeGraph 知识图谱分析

### 关键符号
- `[1m`
- `Search Results for "class":`
- `[0m`
- `[36mmethod      [0m[37mclassifier[0m`
- `[2m  code/wbcattplus/utils/utils_dino_bloom.py:158[0m`
- `[2m  (self, x)[0m`
- `[36mmethod      [0m[37mclass_summary[0m`
- `[2m  code/MalariAI/Phase1-EDA/dataset.py:296[0m`
- `[1m`
- `Search Results for "def ":`
### 索引状态
```
[1m
CodeGraph Status
[0m
[36mProject:[0m /mnt/c/workspace/cell-ai-research

[1mIndex Statistics:[0m
  Files:     2,586
  Nodes:     39,223
  Edges:     94,585
  DB Size:   139.12 MB
  Backend:   [32mnode:sqlite — built-in (full WAL)[0m
  Journal:   [32mwal[0m

[1mNodes by Kind:[0m
  import          14,342
  method          9,930
  function        6,744
  variable        3,201
  class           2,674
  file            2,190
  field           101
  namespace       24
  constant        
```

## RepoWiki 文档生成

- ✅ 扫描成功
- 📁 Wiki 目录: `/mnt/c/workspace/cell-ai-research/reports/DriftST_wiki`
- 📄 生成文件:
  - architecture.md
  - dependencies.md
  - index.md
  - reading-guide.md
  - _sidebar.md
  - modules/process.md
  - modules/root.md
  - modules/scripts.md
  - modules/src.md
- 输出: Project: DriftST
Files:   22
Lines:   3,378
     Languages      
┏━━━━━━━━━━┳━━━━━━━┓
┃ Language ┃ Files ┃
┡━━━━━━━━━━╇━━━━━━━┩
│ python   │    13 │
│ shell    │     4 │
│ unknown  │     2 │
│ markdown │     1 │
│ text     │     1 │
│ yaml     │     1 │
└──────────┴───────┘
DriftST/
├── ⚙️ README.md (markdown)
├── ⚙️ requirements.txt (text)
├── 📁 scripts/
│   ├── 📄 run_spot_level_train.sh (shell)
│   ├── 📄 run_xenium_cell_level_preprocess.sh (shell)
│   ├── 📄 run_xenium_cell_level_train.sh (shell)
│   └── 📄 run_xenium_coad_cell_level_train.sh (shell)
├── 📄 .gitignore (unknown)
├── 📄 LICENSE (unknown)
├── 📄 environment.yml (yaml)
├── 📁 process/
│   ├── 📄 compute_spatial_variable_genes.py (python)
│   ├── 📄 generate_xenium_cell_level_splits.py (python)
│   ├── 📄 preprocess_spot_level.py (python)
│   ├── 📄 preprocess_xenium_cell_level.py (python)
│   ├── 📄 select_xenium_cell_level_genes.py (python)
│   └── 📄 select_xenium_cell_level_hvg.py (python)
├── 📁 src/
│   ├── 📄 dataset.py (python)

## 原有子代理分析报告

暂无原有分析报告