"""LLM プロバイダのルーティングを行うモジュール"""

from __future__ import annotations

from typing import Literal

from .config import Config
from . import local_llm, remote_llm


class ProviderRouter:
    """local / remote / auto を切り替えるラッパー"""

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.mode: Literal["local", "remote", "auto"] = cfg.llm.provider

    async def call(self, prompt: str) -> str:
        if self.mode == "remote":
            return await _async_remote(prompt, self.cfg)
        if self.mode == "local":
            return await _async_local(prompt, self.cfg)
        # auto: デフォルトはローカル。
        return await _async_local(prompt, self.cfg)


# ---- 内部 async ラッパ ------------------
import asyncio


async def _async_local(prompt: str, cfg: Config) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, local_llm.generate, prompt, cfg)


async def _async_remote(prompt: str, cfg: Config) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, remote_llm.generate, prompt, cfg)