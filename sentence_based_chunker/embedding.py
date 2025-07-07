"""埋め込みベクトル生成モジュール"""

from __future__ import annotations

import itertools
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
        model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device=device)
        _model_cache[key] = model
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

    model = _get_model(device)

    for batch in _batch_iterator(sentences, batch_size):
        with torch.inference_mode():
            vecs = model.encode(batch, device=device, convert_to_numpy=True, normalize_embeddings=True)
        for v in vecs:
            yield v