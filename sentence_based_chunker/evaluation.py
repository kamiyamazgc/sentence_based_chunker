"""簡易 F1 評価モジュール (ゴールド比較)"""

from __future__ import annotations

import json
import pathlib
from typing import List, Set

from sklearn.metrics import f1_score


def _load_boundaries(path: pathlib.Path) -> Set[int]:
    """chunks jsonl から boundary インデックス集合を抽出"""
    indices: Set[int] = set()
    idx = 0
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            sent_len = len(rec["sentences"])
            idx += sent_len
            indices.add(idx)
    return indices


def evaluate(gold_dir: pathlib.Path, pred_dir: pathlib.Path) -> float:
    gold_files = sorted(gold_dir.glob("*.jsonl"))
    preds_files = [pred_dir / p.name for p in gold_files]

    gold_labels: List[int] = []
    pred_labels: List[int] = []

    for g, p in zip(gold_files, preds_files):
        g_set = _load_boundaries(g)
        p_set = _load_boundaries(p)
        all_idx = g_set.union(p_set)
        for i in all_idx:
            gold_labels.append(1 if i in g_set else 0)
            pred_labels.append(1 if i in p_set else 0)

    return f1_score(gold_labels, pred_labels)