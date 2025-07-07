# Issue #001: 見出し判別と改行保持の問題

## 概要
見出し行の後の改行が消失し、次の語と連続してしまう問題が発生している。

## 問題の詳細

### 1. 元のテキスト（sample_1.txt）
```
Training and Finetuning Sparse Embedding Models with Sentence Transformers v5
Sentence Transformers is a Python library for using and training embedding and reranker models...
```

### 2. 生成されたチャンク（sample_1.chunks.jsonl）
```json
{
  "text": "Training and Finetuning Sparse Embedding Models with Sentence Transformers v5Sentence Transformers is a Python library...",
  "sentences": [
    "Training and Finetuning Sparse Embedding Models with Sentence Transformers v5",
    "Sentence Transformers is a Python library..."
  ]
}
```

### 3. 問題点の特定

**見出しの判別に関する問題：**

1. **改行の消失**: 見出し行の後の改行が`text`フィールドで失われている
   - 元: `"v5\nSentence Transformers..."`
   - 結果: `"v5Sentence Transformers..."`

2. **見出しの特徴が活用されていない**:
   - 見出しは通常、短い文で文末に句読点がない
   - 次の文との間に空行があることが多い
   - フォントやスタイルの違い（マークダウンでは`#`など）

3. **境界判定の精度**:
   - 見出しと本文の境界が適切に検出されていない可能性
   - 見出しの後にチャンク境界を設定すべき箇所で設定されていない

### 4. 根本原因の推測

1. **前処理段階**: 文分割時に見出しの特徴を考慮していない
2. **境界判定段階**: 見出し後の境界を適切に検出できていない
3. **チャンク構築段階**: 見出しを独立したチャンクとして扱うべきかどうかの判断が不適切

## 影響
- 見出しと本文が連続して読みにくくなる
- 文書構造の情報が失われる
- 後続の処理（翻訳、要約など）で見出しが適切に処理されない可能性

## 優先度
中程度 - 文書構造の保持に影響するが、基本的なチャンク分割機能には影響しない

## 関連ファイル
- `samples/sample_1.txt`
- `samples/sample_1.chunks.jsonl`
- 前処理モジュール（見出し判別機能の追加が必要）

## 作成日
2025/07/07 