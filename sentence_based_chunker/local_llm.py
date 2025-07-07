"""ローカル LLM サーバー (llama.cpp メタルビルド等) へのラッパー"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict

import aiohttp

from .config import Config

# グローバルタイムアウトを明示する（linters の警告回避）
_TIMEOUT = aiohttp.ClientTimeout(total=120)


async def _call_local(prompt: str, cfg: Config) -> str:
    """非同期でローカル LLM サーバーに問い合わせる"""
    url = f"{cfg.llm.local.server_url}/v1/chat/completions"  # type: ignore[attr-defined]
    payload: Dict[str, Any] = {
        "model": "gemma-3n-e2b-it-text",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 64,
        "temperature": 0,
    }
    async with aiohttp.ClientSession(timeout=_TIMEOUT) as session:
        async with session.post(url, json=payload) as resp:
            data = await resp.json()
    return data.get("choices", [{}])[0].get("message", {}).get("content", "")


def generate(prompt: str, cfg: Config) -> str:
    """同期ヘルパー"""
    return asyncio.run(_call_local(prompt, cfg))