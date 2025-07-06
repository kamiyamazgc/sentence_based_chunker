"""外部 LLM (OpenAI など) へのラッパーモジュール"""

from __future__ import annotations

import asyncio
from typing import Any, Dict

import aiohttp

from .config import Config

_TIMEOUT = aiohttp.ClientTimeout(total=120)


async def _call_remote(prompt: str, cfg: Config) -> str:
    url = cfg.llm.remote.endpoint  # type: ignore[attr-defined]
    headers = {"Content-Type": "application/json"}
    payload: Dict[str, Any] = {
        "model": cfg.llm.remote.model,  # type: ignore[attr-defined]
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0,
    }
    async with aiohttp.ClientSession(timeout=_TIMEOUT) as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data = await resp.json()
    # OpenAI 仕様を想定
    return data["choices"][0]["message"]["content"]


def generate(prompt: str, cfg: Config) -> str:
    return asyncio.run(_call_remote(prompt, cfg))