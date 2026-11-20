"""调用本地 OpenAI 兼容端点，供解读页生成器使用。

配置优先级：环境变量 CELL_AI_EXPLAINER_BASE / CELL_AI_EXPLAINER_KEY / CELL_AI_EXPLAINER_MODEL，
其次读取仓库根目录的 .explainer-config.json（已加入 .gitignore）。
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / ".explainer-config.json"

DEFAULTS = {
    "base": "http://127.0.0.1:3425/v1",
    "model": "marvis/deepseek-v4-1-flash-261017",
}


def load_config() -> dict:
    config = dict(DEFAULTS)
    if CONFIG_PATH.exists():
        stored = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        config.update({k: v for k, v in stored.items() if v})
    env_map = {
        "base": "CELL_AI_EXPLAINER_BASE",
        "key": "CELL_AI_EXPLAINER_KEY",
        "model": "CELL_AI_EXPLAINER_MODEL",
    }
    for field, name in env_map.items():
        value = os.environ.get(name)
        if value:
            config[field] = value
    if not config.get("key"):
        raise RuntimeError(
            "缺少接口密钥：设置 CELL_AI_EXPLAINER_KEY，或在 "
            f"{CONFIG_PATH} 写入 {{\"base\": ..., \"key\": ..., \"model\": ...}}"
        )
    return config


def chat(
    messages: list[dict],
    *,
    temperature: float = 0.35,
    max_tokens: int = 16000,
    json_object: bool = False,
    attempts: int = 4,
) -> str:
    config = load_config()
    payload = {
        "model": config["model"],
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if json_object:
        payload["response_format"] = {"type": "json_object"}
    url = config["base"].rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {config['key']}",
        "Content-Type": "application/json; charset=utf-8",
    }
    last_error = None
    for attempt in range(1, attempts + 1):
        started = time.time()
        try:
            response = requests.post(
                url,
                headers=headers,
                data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                timeout=(10, 900),
            )
        except requests.RequestException as error:
            last_error = f"{type(error).__name__}: {error}"
        else:
            if response.status_code >= 500 or response.status_code == 429:
                last_error = f"HTTP {response.status_code}: {response.text[:300]}"
            elif response.status_code >= 400:
                raise RuntimeError(
                    f"接口返回 {response.status_code}：{response.text[:500]}"
                )
            else:
                body = response.json()
                choices = body.get("choices") or []
                content = choices[0].get("message", {}).get("content") or "" if choices else ""
                if not choices:
                    last_error = f"空 choices 响应：{json.dumps(body, ensure_ascii=False)[:300]}"
                elif not content.strip():
                    last_error = "空响应"
                else:
                    elapsed = time.time() - started
                    usage = body.get("usage") or {}
                    print(
                        f"    调用完成 {elapsed:.1f}s  prompt={usage.get('prompt_tokens', '?')}"
                        f" completion={usage.get('completion_tokens', '?')}",
                        flush=True,
                    )
                    return content
        if attempt < attempts:
            time.sleep(min(30, 4 * attempt))
    raise RuntimeError(f"接口连续 {attempts} 次未返回可用内容：{last_error}")


def model_name() -> str:
    return load_config()["model"]
