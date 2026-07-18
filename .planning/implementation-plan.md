# 视频制作技能改进 - 实施计划

## Wave 1: 风格模板系统（并行 2 Worker）

### Worker A: 风格模板基础设施
**文件**: `scripts/apply_style_template.py` （idiom-story-video 和 video-production-pipeline 各一份）
- 读取 `templates/<name>/template.json`
- 输出到项目 `style.json`（由 generate_images.py、assemble_video.py 读取）
- 字段：style_prompt, negative_prompt, color_palette, character_style, background_style, ken_burns_zoom, subtitle_font, subtitle_color
- 创建示例模板：ink-wash（水墨），ink-brush（工笔），q-cartoon（Q版卡通），ancient-chinese（古风插画）

### Worker B: 参考图风格提取
**文件**: `scripts/extract_style_from_image.py`
- 输入：参考图片路径
- 调用 VLM（SenseNova 6.7 Flash Lite 或本地模型）分析图片风格
- 输出：template.json 文件
- 分析维度：画风描述、配色方案、线条风格、色彩饱和度、光影特点

## Wave 2: 轻量资产库（串行 2 Worker）

### Worker A: asset_manager.py
**文件**: `scripts/asset_manager.py`
- JSON 文件读写（字符集 assets/characters/<id>/base.json）
- 函数：load_asset(id), save_asset(data), search_assets(query), list_assets(type)
- 角色字段：id, name_zh, type, appearance, voice_profile, used_in

### Worker B: 集成到 generate_images.py
- 读取项目 `character.json`（plan_scenes.py 输出已有角色信息）
- 查询 asset_manager.py 获取历史角色外貌
- 首次出现角色：保存到资产库
- 后续使用：从资产库读取，保持跨故事一致

## Wave 3: SKILL.md 更新
- 更新 idiom-story-video/SKILL.md 和 video-production-pipeline/SKILL.md
- 新增模板系统使用说明
- 新增资产库使用说明