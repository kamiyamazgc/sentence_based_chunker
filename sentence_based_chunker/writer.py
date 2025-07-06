"""チャンク結果を書き出すモジュール"""

from __future__ import annotations

import json
import pathlib
from typing import Iterable

from .builder import Chunk


def write_chunks(path: pathlib.Path | str, chunks: Iterable[Chunk]):
    path = pathlib.Path(path)
    with path.open("w", encoding="utf-8") as f:
        for chunk in chunks:
            record = {"text": chunk.text, "sentences": chunk.sentences}
            json.dump(record, f, ensure_ascii=False)
            f.write("\n")