"""外部 LLM (OpenAI など) へのラッパーモジュール"""

from __future__ import annotations

import asyncio
import json
import sys
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
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            async with aiohttp.ClientSession(timeout=_TIMEOUT) as session:
                async with session.post(url, json=payload, headers=headers) as resp:
                    if resp.status == 401:
                        print(f"エラー: 外部LLM APIの認証に失敗しました", file=sys.stderr)
                        print(f"APIキーまたは認証情報を確認してください", file=sys.stderr)
                        return "no"  # フォールバック: 境界なしとして処理
                    elif resp.status == 429:
                        print(f"警告: 外部LLM APIのレート制限に達しました (試行 {attempt + 1}/{max_retries})", file=sys.stderr)
                        if attempt == max_retries - 1:
                            print(f"エラー: レート制限により外部LLM API呼び出しが失敗しました", file=sys.stderr)
                            return "no"  # フォールバック: 境界なしとして処理
                        wait_time = 5 * (attempt + 1)
                        print(f"{wait_time}秒待機してリトライします...", file=sys.stderr)
                        await asyncio.sleep(wait_time)
                        continue
                    elif resp.status != 200:
                        error_text = await resp.text()
                        print(f"警告: 外部LLM APIからエラーレスポンス (試行 {attempt + 1}/{max_retries}): {resp.status}", file=sys.stderr)
                        print(f"エラー詳細: {error_text}", file=sys.stderr)
                        if attempt == max_retries - 1:
                            print(f"エラー: 外部LLM API呼び出しが完全に失敗しました", file=sys.stderr)
                            return "no"  # フォールバック: 境界なしとして処理
                        await asyncio.sleep(2 * (attempt + 1))
                        continue
                    
                    try:
                        data = await resp.json()
                    except json.JSONDecodeError as e:
                        print(f"警告: 外部LLM APIからの無効なJSONレスポンス (試行 {attempt + 1}/{max_retries})", file=sys.stderr)
                        response_text = await resp.text()
                        print(f"レスポンス内容: {response_text[:500]}...", file=sys.stderr)
                        if attempt == max_retries - 1:
                            print(f"エラー: 外部LLM APIからの無効なJSONレスポンス", file=sys.stderr)
                            return "no"  # フォールバック: 境界なしとして処理
                        await asyncio.sleep(1 * (attempt + 1))
                        continue
                    
                    # レスポンス構造の検証（OpenAI 仕様を想定）
                    if not isinstance(data, dict):
                        print(f"警告: 外部LLM APIからの予期しないレスポンス形式 (試行 {attempt + 1}/{max_retries})", file=sys.stderr)
                        if attempt == max_retries - 1:
                            return "no"  # フォールバック: 境界なしとして処理
                        await asyncio.sleep(1 * (attempt + 1))
                        continue
                    
                    if "error" in data:
                        error_info = data["error"]
                        print(f"警告: 外部LLM APIエラー (試行 {attempt + 1}/{max_retries}): {error_info}", file=sys.stderr)
                        if attempt == max_retries - 1:
                            print(f"エラー: 外部LLM APIエラーにより処理が失敗しました", file=sys.stderr)
                            return "no"  # フォールバック: 境界なしとして処理
                        await asyncio.sleep(2 * (attempt + 1))
                        continue
                    
                    choices = data.get("choices", [])
                    if not choices:
                        print(f"警告: 外部LLM APIからの空のchoicesレスポンス (試行 {attempt + 1}/{max_retries})", file=sys.stderr)
                        if attempt == max_retries - 1:
                            return "no"  # フォールバック: 境界なしとして処理
                        await asyncio.sleep(1 * (attempt + 1))
                        continue
                    
                    content = choices[0].get("message", {}).get("content", "")
                    if not content:
                        print(f"警告: 外部LLM APIからの空のcontentレスポンス (試行 {attempt + 1}/{max_retries})", file=sys.stderr)
                        if attempt == max_retries - 1:
                            return "no"  # フォールバック: 境界なしとして処理
                        await asyncio.sleep(1 * (attempt + 1))
                        continue
                    
                    return content
                    
        except asyncio.TimeoutError:
            print(f"警告: 外部LLM APIへの接続がタイムアウトしました (試行 {attempt + 1}/{max_retries})", file=sys.stderr)
            if attempt == max_retries - 1:
                print(f"エラー: 外部LLM APIへの接続が完全に失敗しました", file=sys.stderr)
                return "no"  # フォールバック: 境界なしとして処理
            await asyncio.sleep(3 * (attempt + 1))
            
        except aiohttp.ClientConnectorError:
            print(f"警告: 外部LLM APIに接続できませんでした (試行 {attempt + 1}/{max_retries})", file=sys.stderr)
            print(f"API URL: {url}", file=sys.stderr)
            if attempt == max_retries - 1:
                print(f"エラー: 外部LLM APIへの接続が完全に失敗しました", file=sys.stderr)
                return "no"  # フォールバック: 境界なしとして処理
            await asyncio.sleep(3 * (attempt + 1))
            
        except Exception as e:
            print(f"警告: 外部LLM API呼び出し中に予期しないエラーが発生しました (試行 {attempt + 1}/{max_retries})", file=sys.stderr)
            print(f"詳細: {e}", file=sys.stderr)
            if attempt == max_retries - 1:
                print(f"エラー: 外部LLM API呼び出しが完全に失敗しました", file=sys.stderr)
                return "no"  # フォールバック: 境界なしとして処理
            await asyncio.sleep(2 * (attempt + 1))
    
    return "no"  # 念のためのフォールバック


def generate(prompt: str, cfg: Config) -> str:
    try:
        return asyncio.run(_call_remote(prompt, cfg))
    except Exception as e:
        print(f"エラー: 外部LLM呼び出しでエラーが発生しました", file=sys.stderr)
        print(f"詳細: {e}", file=sys.stderr)
        return "no"  # フォールバック: 境界なしとして処理