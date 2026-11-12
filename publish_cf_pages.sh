#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SITE_DIR="$ROOT_DIR/.cf-pages-site"
PROJECT_NAME="${CF_PAGES_PROJECT:-cell-ai-research}"

# CLOUDFLARE_DEPLOY.md 记录的 Pages 专用凭据文件优先加载；
# 缺失的变量随后从 Hermes 的环境文件补齐，已有值保持不变。
if [[ -f "$HOME/.config/hermes/cf-pages.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$HOME/.config/hermes/cf-pages.env"
  set +a
fi
if [[ -f "$HOME/.hermes/.env" ]]; then
  # 逐个变量读取，跳过已经存在的名称，避免覆盖专用凭据。
  while IFS='=' read -r key value; do
    [[ "$key" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]] || continue
    if [[ -z "$(printenv "$key" || true)" ]]; then
      export "$key=$value"
    fi
  done < <(grep -E '^[A-Za-z_][A-Za-z0-9_]*=' "$HOME/.hermes/.env")
fi

if [[ -z "${CLOUDFLARE_API_TOKEN:-}" ]]; then
  echo "CLOUDFLARE_API_TOKEN is not set; refusing to publish." >&2
  exit 2
fi
if [[ -z "${CLOUDFLARE_ACCOUNT_ID:-}" ]]; then
  echo "CLOUDFLARE_ACCOUNT_ID is not set; refusing to publish." >&2
  exit 2
fi

rm -rf "$SITE_DIR"
mkdir -p "$SITE_DIR/data/figures"
cp "$ROOT_DIR/index.html" "$SITE_DIR/index.html"
cp "$ROOT_DIR/_headers" "$SITE_DIR/_headers"
cp -R "$ROOT_DIR/vendor" "$SITE_DIR/vendor"
mkdir -p "$SITE_DIR/web"
cp "$ROOT_DIR/web/paper-math.js" "$SITE_DIR/web/paper-math.js"
if [[ -d "$ROOT_DIR/data/evidence" ]]; then
  cp -R "$ROOT_DIR/data/evidence" "$SITE_DIR/data/evidence"
fi
if [[ -d "$ROOT_DIR/data/figures/previews" ]]; then
  # 页面列表只加载这些小尺寸预览，原图仍随站点发布供灯箱查看。
  cp -R "$ROOT_DIR/data/figures/previews" "$SITE_DIR/data/figures/previews"
fi
if [[ -d "$ROOT_DIR/data/figures/originals" ]]; then
  cp -R "$ROOT_DIR/data/figures/originals" "$SITE_DIR/data/figures/originals"
fi

file_count="$(find "$SITE_DIR" -type f | wc -l)"
site_size="$(du -sh "$SITE_DIR" | cut -f1)"
echo "Publishing $file_count files ($site_size) to Cloudflare Pages project '$PROJECT_NAME'..."

cd "$ROOT_DIR"
WRANGLER_BIN="$HOME/.cf-pages-publisher/node_modules/.bin/wrangler"
if [[ -d "$HOME/.nvm/versions/node" ]]; then
  NODE_BIN_DIR="$(find "$HOME/.nvm/versions/node" -mindepth 2 -maxdepth 2 -type d -name bin 2>/dev/null | sort -V | tail -n 1 || true)"
  if [[ -n "$NODE_BIN_DIR" ]]; then
    export PATH="$NODE_BIN_DIR:$PATH"
  fi
fi
if [[ ! -x "$WRANGLER_BIN" ]]; then
  echo "WSL Wrangler not found at $WRANGLER_BIN." >&2
  exit 3
fi
"$WRANGLER_BIN" pages deploy "$SITE_DIR" \
  --project-name "$PROJECT_NAME" \
  --branch main \
  --commit-dirty=true
