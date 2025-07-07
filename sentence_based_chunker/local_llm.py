"""ローカル LLM サーバー (llama.cpp メタルビルド等) へのラッパー"""

from __future__ import annotations

import asyncio
import json
import sys
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
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession(timeout=_TIMEOUT) as session:
                async with session.post(url, json=payload) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        print(f"警告: ローカルLLMサーバーからエラーレスポンス (試行 {attempt + 1}/{max_retries}): {resp.status}", file=sys.stderr)
                        print(f"エラー詳細: {error_text}", file=sys.stderr)
                        if attempt == max_retries - 1:
                            raise aiohttp.ClientError(f"ローカルLLMサーバーエラー: {resp.status} - {error_text}")
                        await asyncio.sleep(1 * (attempt + 1))  # 指数バックオフ
                        continue
                    
                    try:
                        data = await resp.json()
                    except json.JSONDecodeError as e:
                        print(f"警告: ローカルLLMサーバーからの無効なJSONレスポンス (試行 {attempt + 1}/{max_retries})", file=sys.stderr)
                        print(f"レスポンス内容: {await resp.text()}", file=sys.stderr)
                        if attempt == max_retries - 1:
                            raise ValueError(f"ローカルLLMサーバーからの無効なJSONレスポンス") from e
                        await asyncio.sleep(1 * (attempt + 1))
                        continue
                    
                    # レスポンス構造の検証
                    if not isinstance(data, dict):
                        print(f"警告: ローカルLLMサーバーからの予期しないレスポンス形式 (試行 {attempt + 1}/{max_retries})", file=sys.stderr)
                        if attempt == max_retries - 1:
                            raise ValueError(f"ローカルLLMサーバーからの予期しないレスポンス形式")
                        await asyncio.sleep(1 * (attempt + 1))
                        continue
                    
                    choices = data.get("choices", [])
                    if not choices:
                        print(f"警告: ローカルLLMサーバーからの空のchoicesレスポンス (試行 {attempt + 1}/{max_retries})", file=sys.stderr)
                        if attempt == max_retries - 1:
                            return "no"  # フォールバック: 境界なしとして処理
                        await asyncio.sleep(1 * (attempt + 1))
                        continue
                    
                    content = choices[0].get("message", {}).get("content", "")
                    if not content:
                        print(f"警告: ローカルLLMサーバーからの空のcontentレスポンス (試行 {attempt + 1}/{max_retries})", file=sys.stderr)
                        if attempt == max_retries - 1:
                            return "no"  # フォールバック: 境界なしとして処理
                        await asyncio.sleep(1 * (attempt + 1))
                        continue
                    
                    return content
                    
        except asyncio.TimeoutError:
            print(f"警告: ローカルLLMサーバーへの接続がタイムアウトしました (試行 {attempt + 1}/{max_retries})", file=sys.stderr)
            if attempt == max_retries - 1:
                print(f"エラー: ローカルLLMサーバーへの接続が完全に失敗しました", file=sys.stderr)
                return "no"  # フォールバック: 境界なしとして処理
            await asyncio.sleep(2 * (attempt + 1))
            
        except aiohttp.ClientConnectorError:
            print(f"警告: ローカルLLMサーバーに接続できませんでした (試行 {attempt + 1}/{max_retries})", file=sys.stderr)
            print(f"サーバーURL: {url}", file=sys.stderr)
            if attempt == max_retries - 1:
                print(f"エラー: ローカルLLMサーバーへの接続が完全に失敗しました", file=sys.stderr)
                return "no"  # フォールバック: 境界なしとして処理
            await asyncio.sleep(2 * (attempt + 1))
            
        except Exception as e:
            print(f"警告: ローカルLLM API呼び出し中に予期しないエラーが発生しました (試行 {attempt + 1}/{max_retries})", file=sys.stderr)
            print(f"詳細: {e}", file=sys.stderr)
            if attempt == max_retries - 1:
                print(f"エラー: ローカルLLM API呼び出しが完全に失敗しました", file=sys.stderr)
                return "no"  # フォールバック: 境界なしとして処理
            await asyncio.sleep(1 * (attempt + 1))
    
    return "no"  # 念のためのフォールバック


def generate(prompt: str, cfg: Config) -> str:
    """同期ヘルパー"""
    try:
        return asyncio.run(_call_local(prompt, cfg))
    except Exception as e:
        print(f"エラー: ローカルLLM呼び出しでエラーが発生しました", file=sys.stderr)
        print(f"詳細: {e}", file=sys.stderr)
        return "no"  # フォールバック: 境界なしとして処理