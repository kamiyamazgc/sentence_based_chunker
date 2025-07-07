"""外部 LLM (OpenAI など) へのラッパーモジュール"""

from __future__ import annotations

import asyncio
from typing import Any, Dict

import aiohttp

from .config import Config
from .exceptions import LLMCallError

_TIMEOUT = aiohttp.ClientTimeout(total=120)


async def _call_remote(prompt: str, cfg: Config) -> str:
    url = cfg.llm.remote.endpoint  # type: ignore[attr-defined]
    headers = {"Content-Type": "application/json"}
    payload: Dict[str, Any] = {
        "model": cfg.llm.remote.model,  # type: ignore[attr-defined]
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
    }
    try:
        async with aiohttp.ClientSession(timeout=_TIMEOUT) as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise LLMCallError(f"LLM API からエラーコード {resp.status} が返されました: {text}")
                data = await resp.json()
    except aiohttp.ClientError as e:
        raise LLMCallError(f"LLM への接続に失敗しました: {e}") from e
    except Exception as e:  # pylint: disable=broad-except
        raise LLMCallError(f"LLM 応答の処理中にエラーが発生しました: {e}") from e

    try:
        # OpenAI 仕様を想定
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        raise LLMCallError(f"期待した形式でレスポンスが取得できませんでした: {data}") from e


def generate(prompt: str, cfg: Config) -> str:
    return asyncio.run(_call_remote(prompt, cfg))