# 视频制作技能改进设计

## 需求分析

### 现状
- **idiom-story-video** — 成语故事专用流水线，从成语名到成片。流程：plan_scenes → TTS → generate_images → verify → assemble_video
- **video-production-pipeline** — 通用旁白+配图短视频生产线，支持无旁白纯视觉短片

### DramaClaw 能力映射

| DramaClaw 能力 | 现有技能现状 | 改进价值 |
|---|---|---|
| 故事图谱（角色/关系/时间线） | script.json 扁平结构，无角色关系建模 | 中等 |
| 资产库（角色/场景/道具/声线） | 无持久化资产系统，每项目从零开始 | **高** |
| 风格模板（图片→风格参数自动提取） | STYLE_ID 硬编码，无参考图→风格映射 | **高** |
| 场景一致性（3GS/导演世界） | 每场景独立生成，无空间一致性 | 中低 |
| 审校循环 | 依赖外部 GPT-5.5 审校，非内建 | 低（已有 workflow） |
| 双线模式（画布+主线） | 纯线性流水线 | 低 |
| IndexTTS2 配音 | 用 MiMo VoiceDesign | 中等（备选 TTS） |

### 确定改进范围

**高优先级（本次实施）：**
1. **风格模板系统** — 上传参考图自动提取风格参数并应用到项目
2. **轻量资产库** — 角色资产 JSON 持久化，跨项目复用

**中优先级（后续）：**
3. 故事图谱 — script.json 增加角色关系字段
4. IndexTTS2 配音备选

**本次不实施：**
- 场景一致性（3GS）— 需要 3D 场景建模，和现有流程不匹配
- 双线模式/无限画布 — 过度设计
- 审校循环 — 已有 GPT-5.5 工作流已足够

## 架构设计

### 1. 风格模板系统

```
templates/                    # 风格模板根目录
├── ink-wash/                 # 水墨风格
│   ├── template.json         # 风格参数（prompt modifiers, color palette, etc）
│   └── reference.png         # 参考图
├── ink-brush/                # 工笔风格
├── q-cartoon/                # Q版卡通
└── custom/                   # 用户上传自定义模板
```

`template.json` 结构：
```json
{
  "name": "水墨绘本",
  "style_prompt": "Chinese ink wash painting style, traditional brush strokes, ...",
  "color_palette": ["#2c1810", "#8b7355", "#d4c5a9", "#f5f0e1"],
  "negative_prompt": "photorealistic, 3D render, Western art style",
  "character_style": "ink wash character design, traditional Chinese painting",
  "background_style": "misty mountains, bamboo, traditional architecture",
  "ken_burns_zoom": 1.05,
  "subtitle_font": "STKaiti",
  "subtitle_color": "#2c1810",
  "description": "传统水墨风格"
}
```

新增功能：
- `scripts/apply_style_template.py` — 应用风格模板到项目
- `scripts/extract_style_from_image.py` — 上传参考图→LLM 分析→生成 template.json

### 2. 轻量资产库

```
assets/                       # 资产库根目录
├── characters/               # 角色资产
│   ├── farmer/               # 农夫
│   │   ├── base.json         # 角色基础设定
│   │   ├── portrait.png      # 肖像
│   │   └── appearances.json  # 跨项目角色外貌描述
│   └── rabbit/               # 兔子
└── props/                    # 道具资产
```

`base.json` 结构：
```json
{
  "id": "farmer",
  "name_zh": "农夫",
  "name_en": "Farmer",
  "type": "character",
  "source_story": "守株待兔",
  "appearance": {
    "gender": "male",
    "age": "middle-aged",
    "clothing": "traditional Han Chinese farmer clothing, straw hat, patched coarse cloth robe",
    "features": "weathered face, straw sandals, carries a hoe"
  },
  "voice_profile": {
    "style": "稳重中年",
    "voicedesign_keywords": "middle-aged farmer, weathered but kind, steady voice"
  },
  "used_in": ["守株待兔"]
}
```

### 3. 项目集成

两种技能的 scripts 目录已有以下脚本，需要新增/修改：

**idiom-story-video / scripts/:**
- ✅ plan_scenes.py（已有）
- ✅ generate_tts.py（已有）
- ✅ generate_images.py（已有）
- ✅ verify_images.py（已有）
- ✅ assemble_video.py（已有）
- ✅ auto_bgm.py（已有）
- ➕ **apply_style_template.py** — 新建
- ➕ **extract_style_from_image.py** — 新建
- ➕ **asset_manager.py** — 新建（角色资产读写）
- 🔄 **plan_scenes.py** — 修改（集成资产查询）
- 🔄 **generate_images.py** — 修改（读取样式模板+资产库）

**video-production-pipeline / scripts/:**
- 同上

## 实施计划

### Wave 1: 风格模板系统（并行 2 Worker）
- **Worker A**: `apply_style_template.py` + 模板示例文件
- **Worker B**: `extract_style_from_image.py`（调用 VLM 分析参考图）

### Wave 2: 轻量资产库（并行 2 Worker）
- **Worker A**: `asset_manager.py`（核心 CRUD + 搜索）
- **Worker B**: `plan_scenes.py` 和 `generate_images.py` 集成

### Wave 3: SKILL.md 更新 + 测试
- 更新两个 SKILL.md 文档
- Asset 示例文件

## 自检

1. ✅ 占位符扫描：无 TBD
2. ✅ 内部一致性：改进范围聚焦，不冲突
3. ✅ 范围检查：2 个独立子系统，可并行开发
4. ✅ 歧义检查：明确 Wave 1 → Wave 2 → Wave 3 顺序
5. ✅ YAGNI：3GS、双线模式、审校循环已排除