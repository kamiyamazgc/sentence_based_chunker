"""チャンク結果を書き出すモジュール"""

from __future__ import annotations

import json
import pathlib
from typing import Iterable

from .builder import Chunk
from .exceptions import FileWriteError


def write_chunks(path: pathlib.Path | str, chunks: Iterable[Chunk]):
    """チャンク結果をファイルに書き出す。

    書き込みに失敗した場合は ``FileWriteError`` を送出する。
    """
    path = pathlib.Path(path)
    try:
        with path.open("w", encoding="utf-8") as f:
            for chunk in chunks:
                record = {"text": chunk.text, "sentences": chunk.sentences}
                json.dump(record, f, ensure_ascii=False)
                f.write("\n")
    except Exception as e:  # pylint: disable=broad-except
        raise FileWriteError(f"出力ファイルへの書き込みに失敗しました: {e}") from e