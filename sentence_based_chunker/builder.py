"""チャンク構築モジュール"""

from __future__ import annotations

from typing import Iterable, List
from dataclasses import dataclass, field


@dataclass
class Chunk:
    """チャンクを構成する文の集合"""

    sentences: List[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        return "".join(self.sentences)


def build_chunks(sentences: Iterable[str], boundaries: Iterable[bool], cfg) -> List[Chunk]:
    """境界フラグに従い sentences をチャンクにまとめる"""
    current: List[str] = []
    result: List[Chunk] = []
    for sent, boundary in zip(sentences, boundaries):
        current.append(sent)
        if boundary:
            result.append(Chunk(sentences=current))
            current = []
    if current:
        result.append(Chunk(sentences=current))
    return result