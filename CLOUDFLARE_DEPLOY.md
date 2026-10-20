# Cloudflare Pages 自动发布

页面图片保存在 `data/figures/originals/` 下，`index.html` 直接引用原始文件。
首次迁移旧缓存时执行：

```bash
cd /mnt/c/workspace/cell-ai-research
/home/fanweiya/miniconda3/bin/python generate_index.py \
  --no-translate --no-code-analysis --refresh-images
```

发布脚本只上传 `index.html` 和原图目录，不会上传论文 PDF、克隆代码或日志。

## 一次性配置

创建仅当前用户可读的环境文件：

```bash
mkdir -p ~/.config/hermes
cat > ~/.config/hermes/cf-pages.env <<'EOF'
CLOUDFLARE_API_TOKEN=Cloudflare_Pages_Edit_token
CLOUDFLARE_ACCOUNT_ID=Cloudflare_account_id
CF_PAGES_PROJECT=cell-ai-research
EOF
chmod 600 ~/.config/hermes/cf-pages.env
mkdir -p ~/.config/systemd/user/hermes-gateway.service.d
cat > ~/.config/systemd/user/hermes-gateway.service.d/cf-pages.conf <<'EOF'
[Service]
EnvironmentFile=%h/.config/hermes/cf-pages.env
EOF
systemctl --user daemon-reload
systemctl --user restart hermes-gateway
```

先在 Cloudflare Pages 创建同名项目。测试发布时把同一环境文件加载到当前 shell：

```bash
cd /mnt/c/workspace/cell-ai-research
set -a
source ~/.config/hermes/cf-pages.env
set +a
bash publish_cf_pages.sh
```

## 定时任务联动

凭据配置完成后，`cell-ai-research-daily` 每次实际更新页面数据后执行：

```bash
/home/fanweiya/miniconda3/bin/python /mnt/c/workspace/cell-ai-research/generate_index.py \
  --no-translate --no-code-analysis
bash /mnt/c/workspace/cell-ai-research/publish_cf_pages.sh
```

没有论文或页面变化时不发布。发布失败不回滚研究数据，Cron 最终报告单独记录失败原因。
