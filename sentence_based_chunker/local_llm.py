"""ローカル LLM サーバー (llama.cpp メタルビルド等) へのラッパー"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict

import aiohttp

from .config import Config
from .exceptions import LLMCallError

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
    try:
        async with aiohttp.ClientSession(timeout=_TIMEOUT) as session:
            async with session.post(url, json=payload) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise LLMCallError(f"ローカル LLM サーバーからエラーコード {resp.status} が返されました: {text}")
                data = await resp.json()
    except aiohttp.ClientError as e:
        raise LLMCallError(f"ローカル LLM サーバーへの接続に失敗しました: {e}") from e
    except Exception as e:  # pylint: disable=broad-except
        raise LLMCallError(f"ローカル LLM 応答の処理中にエラーが発生しました: {e}") from e

    content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
    if content == "":
        raise LLMCallError("ローカル LLM から空のレスポンスが返されました")
    return content


def generate(prompt: str, cfg: Config) -> str:
    """同期ヘルパー"""
    return asyncio.run(_call_local(prompt, cfg))