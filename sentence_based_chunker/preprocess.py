"""前処理モジュール: 入力テキストを文単位のストリームに変換する"""

from __future__ import annotations

import pathlib
import re
from typing import Generator, List

_SENT_SPLIT_REGEX = re.compile(r"(?<=[。．！？!?]\s?)")


def _split_sentences(text: str) -> List[str]:
    """日本語用の簡易文分割"""
    sentences = [s.strip() for s in _SENT_SPLIT_REGEX.split(text) if s.strip()]
    return sentences


def stream_sentences(path: pathlib.Path | str) -> Generator[str, None, None]:
    """ファイルを読み込み、文を逐次 yield する"""
    path = pathlib.Path(path)
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            for sent in _split_sentences(line):
                yield sent