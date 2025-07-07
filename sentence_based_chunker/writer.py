"""チャンク結果を書き出すモジュール"""

from __future__ import annotations

import json
import pathlib
import sys
from typing import Iterable

from .builder import Chunk


def write_chunks(path: pathlib.Path | str, chunks: Iterable[Chunk]):
    path = pathlib.Path(path)
    
    # 出力ディレクトリの存在確認・作成
    try:
        output_dir = path.parent
        output_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        print(f"エラー: 出力ディレクトリの作成権限がありません: {output_dir}", file=sys.stderr)
        raise PermissionError(f"出力ディレクトリの作成権限がありません: {output_dir}")
    except Exception as e:
        print(f"エラー: 出力ディレクトリの作成に失敗しました: {output_dir}", file=sys.stderr)
        print(f"詳細: {e}", file=sys.stderr)
        raise RuntimeError(f"出力ディレクトリの作成に失敗しました: {output_dir}") from e
    
    chunk_count = 0
    try:
        with path.open("w", encoding="utf-8") as f:
            for chunk in chunks:
                chunk_count += 1
                try:
                    record = {"text": chunk.text, "sentences": chunk.sentences}
                    json.dump(record, f, ensure_ascii=False)
                    f.write("\n")
                except (TypeError, ValueError) as e:
                    print(f"エラー: チャンク {chunk_count} のJSON変換に失敗しました", file=sys.stderr)
                    print(f"詳細: {e}", file=sys.stderr)
                    print(f"チャンク内容: text長={len(chunk.text)}, sentences数={len(chunk.sentences)}", file=sys.stderr)
                    raise ValueError(f"チャンク {chunk_count} のJSON変換に失敗しました") from e
                except Exception as e:
                    print(f"エラー: チャンク {chunk_count} の書き込み中に予期しないエラーが発生しました", file=sys.stderr)
                    print(f"詳細: {e}", file=sys.stderr)
                    raise RuntimeError(f"チャンク {chunk_count} の書き込み中にエラーが発生しました") from e
                    
    except PermissionError:
        print(f"エラー: 出力ファイルへの書き込み権限がありません: {path}", file=sys.stderr)
        raise PermissionError(f"出力ファイルへの書き込み権限がありません: {path}")
    except OSError as e:
        if "No space left on device" in str(e):
            print(f"エラー: ディスク容量が不足しています", file=sys.stderr)
            print(f"出力先: {path}", file=sys.stderr)
            raise OSError(f"ディスク容量が不足しています: {path}") from e
        else:
            print(f"エラー: ファイル書き込み中にシステムエラーが発生しました: {path}", file=sys.stderr)
            print(f"詳細: {e}", file=sys.stderr)
            raise OSError(f"ファイル書き込み中にシステムエラーが発生しました: {path}") from e
    except Exception as e:
        print(f"エラー: ファイル書き込み中に予期しないエラーが発生しました: {path}", file=sys.stderr)
        print(f"詳細: {e}", file=sys.stderr)
        print(f"処理済みチャンク数: {chunk_count}", file=sys.stderr)
        raise RuntimeError(f"ファイル書き込み中にエラーが発生しました: {path}") from e