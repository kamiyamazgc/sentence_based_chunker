"""トピック境界検出モジュール (簡易実装版)"""

from __future__ import annotations

from typing import Generator, Iterable, List, TYPE_CHECKING

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from .config import Config

# 遅延評価の型ヒント用途。実行時に未使用のため lint エラーを回避
if TYPE_CHECKING:
    from .provider_router import ProviderRouter


# ------------------------------------------------------------
# A. Embedding スコア基準
# ------------------------------------------------------------

def _stage_a(embeddings: List[np.ndarray], θ_high: float, θ_low: float) -> List[bool]:
    results: List[bool] = []
    for i in range(1, len(embeddings)):
        sim = float(cosine_similarity(embeddings[i - 1 : i], embeddings[i : i + 1])[0][0])
        results.append(bool(sim < θ_low))  # bool 化して型警告を抑制
    results.insert(0, False)  # 先頭は境界無し
    return results


# ------------------------------------------------------------
# B. Window アノマリー
# ------------------------------------------------------------

def _moving_average(data: List[float], k: int) -> List[float]:
    ret = []
    window = []
    for d in data:
        window.append(d)
        if len(window) > k:
            window.pop(0)
        ret.append(float(np.mean(window)))
    return ret


def _stage_b(embeddings: List[np.ndarray], k: int, τ: float) -> List[bool]:
    # 連続コサインで異常スコア
    sims = [float(cosine_similarity(embeddings[i : i + 1], embeddings[i + 1 : i + 2])[0][0]) for i in range(len(embeddings) - 1)]
    sims.insert(0, 1.0)
    avg = _moving_average(sims, k)
    resid = [abs(s - a) for s, a in zip(sims, avg)]
    sigma = np.std(resid)
    results = [bool(r > τ * sigma) for r in resid]
    return results


# ------------------------------------------------------------
# C. LLM 精査 stage
# ------------------------------------------------------------
async def _stage_c(sentences: List[str], prelim: List[bool], router: "ProviderRouter", n_vote: int) -> List[bool]:
    refined = prelim.copy()
    for idx, is_boundary in enumerate(prelim):
        if not is_boundary:
            continue
        prompt = f"次の2文は異なるトピックか？ yes/no\n-----\n{sentences[idx]}\n-----\n{sentences[idx+1] if idx+1 < len(sentences) else ''}"
        votes = 0
        for _ in range(n_vote):
            ans = await router.call(prompt)
            votes += 1 if "yes" in ans.lower() else 0
        refined[idx] = votes > n_vote // 2
    return refined


# ------------------------------------------------------------
# D. Post filter
# ------------------------------------------------------------

def _stage_d(sentences: List[str], boundaries: List[bool]) -> List[bool]:
    """簡易版: 1 文字以下の短文は境界として採用しない"""
    ret = boundaries.copy()
    for idx, flag in enumerate(boundaries):
        if flag and len(sentences[idx].strip()) <= 1:
            ret[idx] = False
    return ret


# ------------------------------------------------------------
# public API
# ------------------------------------------------------------

def detect_boundaries(embeddings: Iterable[np.ndarray], cfg: Config) -> Generator[bool, None, None]:
    """埋め込みストリームを受け取り、境界判定結果をストリームで返す"""
    emb_list: List[np.ndarray] = list(embeddings)

    # Stage A/B (同期)
    a_flags = _stage_a(emb_list, θ_high=cfg.detector.θ_high, θ_low=cfg.detector.θ_low)  # type: ignore[attr-defined]
    b_flags = _stage_b(emb_list, k=cfg.detector.k, τ=cfg.detector.τ)  # type: ignore[attr-defined]

    final_flags = [a or b for a, b in zip(a_flags, b_flags)]

    for f in final_flags:
        yield f