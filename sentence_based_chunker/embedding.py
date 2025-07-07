"""埋め込みベクトル生成モジュール"""

from __future__ import annotations

import itertools
import sys
from typing import Generator, Iterable, List

import numpy as np
import torch
from sentence_transformers import SentenceTransformer

from .config import Config


_model_cache: dict[str, SentenceTransformer] = {}


def _get_model(device: str) -> SentenceTransformer:
    """デバイスに応じて SentenceTransformer モデルを取得/キャッシュ"""
    key = f"{device}"
    if key not in _model_cache:
        try:
            print(f"モデルを読み込み中: sentence-transformers/all-MiniLM-L6-v2 (デバイス: {device})", file=sys.stderr)
            model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device=device)
            _model_cache[key] = model
            print(f"モデルの読み込みが完了しました", file=sys.stderr)
        except Exception as e:
            print(f"エラー: モデルの読み込みに失敗しました", file=sys.stderr)
            print(f"詳細: {e}", file=sys.stderr)
            
            # デバイスエラーの場合、CPUでリトライ
            if device != "cpu" and ("cuda" in str(e).lower() or "gpu" in str(e).lower() or "device" in str(e).lower()):
                print(f"GPUでのモデル読み込みに失敗しました。CPUでリトライします...", file=sys.stderr)
                try:
                    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")
                    _model_cache[key] = model
                    print(f"CPUでのモデル読み込みが完了しました", file=sys.stderr)
                except Exception as cpu_e:
                    print(f"エラー: CPUでのモデル読み込みも失敗しました", file=sys.stderr)
                    print(f"詳細: {cpu_e}", file=sys.stderr)
                    raise RuntimeError(f"モデルの読み込みに失敗しました。GPU/CPU両方でエラーが発生しました。") from cpu_e
            else:
                raise RuntimeError(f"モデルの読み込みに失敗しました: {e}") from e
    return _model_cache[key]


def _batch_iterator(it: Iterable[str], batch_size: int) -> Iterable[List[str]]:
    """イテレータをバッチ単位で切り出す"""
    it = iter(it)
    while True:
        batch = list(itertools.islice(it, batch_size))
        if not batch:
            break
        yield batch


def embed_stream(sentences: Iterable[str], cfg: Config) -> Generator[np.ndarray, None, None]:
    """文ジェネレータを入力し、埋め込みをストリームで返す"""
    device = cfg.runtime.device
    batch_size = cfg.runtime.batch_size

    try:
        model = _get_model(device)
    except Exception as e:
        print(f"エラー: 埋め込みモデルの初期化に失敗しました", file=sys.stderr)
        raise RuntimeError(f"埋め込みモデルの初期化に失敗しました") from e

    batch_count = 0
    for batch in _batch_iterator(sentences, batch_size):
        batch_count += 1
        try:
            with torch.inference_mode():
                vecs = model.encode(batch, device=device, convert_to_numpy=True, normalize_embeddings=True)
            for v in vecs:
                yield v
        except torch.cuda.OutOfMemoryError:
            print(f"エラー: GPU メモリ不足です。バッチサイズを小さくするか、CPUを使用してください", file=sys.stderr)
            raise RuntimeError(f"GPU メモリ不足です。バッチサイズを小さくするか、CPUを使用してください")
        except Exception as e:
            print(f"エラー: バッチ {batch_count} の埋め込み生成に失敗しました", file=sys.stderr)
            print(f"詳細: {e}", file=sys.stderr)
            print(f"バッチ内容: {batch[:3]}..." if len(batch) > 3 else f"バッチ内容: {batch}", file=sys.stderr)
            raise RuntimeError(f"バッチ {batch_count} の埋め込み生成に失敗しました") from e