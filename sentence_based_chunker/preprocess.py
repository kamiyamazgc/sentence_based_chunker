"""前処理モジュール: 入力テキストを文単位のストリームに変換する"""

from __future__ import annotations

import pathlib
import re
import sys
from typing import Generator, List

_SENT_SPLIT_REGEX = re.compile(r"(?<=[。．！？!?])")


def _split_sentences(text: str) -> List[str]:
    """日本語用の簡易文分割"""
    sentences = [s.strip() for s in _SENT_SPLIT_REGEX.split(text) if s.strip()]
    return sentences


def stream_sentences(path: pathlib.Path | str) -> Generator[str, None, None]:
    """ファイルを読み込み、文を逐次 yield する"""
    path = pathlib.Path(path)
    
    # ファイル存在チェック
    if not path.exists():
        print(f"エラー: ファイルが見つかりません: {path}", file=sys.stderr)
        raise FileNotFoundError(f"指定されたファイルが見つかりません: {path}")
    
    # ファイル読み込み可能性チェック
    if not path.is_file():
        print(f"エラー: 指定されたパスはファイルではありません: {path}", file=sys.stderr)
        raise ValueError(f"指定されたパスはファイルではありません: {path}")
    
    try:
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                for sent in _split_sentences(line):
                    yield sent
    except PermissionError:
        print(f"エラー: ファイルへの読み取り権限がありません: {path}", file=sys.stderr)
        raise PermissionError(f"ファイルへの読み取り権限がありません: {path}")
    except UnicodeDecodeError as e:
        print(f"エラー: ファイルの文字エンコーディングに問題があります: {path}", file=sys.stderr)
        print(f"詳細: {e}", file=sys.stderr)
        raise UnicodeDecodeError(e.encoding, e.object, e.start, e.end, 
                                f"ファイルの文字エンコーディングに問題があります: {path}")
    except OSError as e:
        print(f"エラー: ファイル読み込み中にシステムエラーが発生しました: {path}", file=sys.stderr)
        print(f"詳細: {e}", file=sys.stderr)
        raise OSError(f"ファイル読み込み中にシステムエラーが発生しました: {path}") from e
    except Exception as e:
        print(f"エラー: ファイル読み込み中に予期しないエラーが発生しました: {path}", file=sys.stderr)
        print(f"詳細: {e}", file=sys.stderr)
        raise RuntimeError(f"ファイル読み込み中に予期しないエラーが発生しました: {path}") from e