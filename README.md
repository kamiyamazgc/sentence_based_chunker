# Sentence-Based High-Accuracy Chunker

日本語文書を高精度にトピック単位へ分割する CLI / Python ライブラリです。docs/仕様書.md の設計 v1.0 を基に実装しています。

## インストール
```bash
pip install -r requirements.txt
```

## 使い方
```bash
# ローカル LLM モード
python -m sentence_based_chunker.cli run article.txt --conf conf/mac_local.yaml

# 外部 LLM を強制
python -m sentence_based_chunker.cli run article.txt --force-remote
```

## 構成図
```
TXT → PreProcess → Embedding → Detector → Builder → Writer
                         │
                         └─ ProviderRouter (local / remote)
```

## ライセンス
MIT

## テストの実行
`pytest` を使ったユニットテストを同梱しています。

```bash
pytest -q
```