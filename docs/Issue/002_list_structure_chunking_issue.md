# Issue #002: リスト構造のチャンク化問題

## 概要
チャンク化の際にリスト構造が考慮されず、リストの要素が細切れに分割されたり、複数のチャンクにまたがってしまう問題が発生している。

## 問題の詳細

### 1. 問題の具体例

#### 元のテキスト（sample_1.txt）
```
- v3.0: (improved) Sentence Transformer (Dense Embedding) model training
- v4.0: (improved) Cross Encoder (Reranker) model training
- v5.0: (new) Sparse Embedding model training

Table of Contents
- What are Sparse Embedding models?
- Why Finetune?
- Training Components
- Model
- Dataset
- Loss Function
- Training Arguments
- Evaluator
- Trainer
- Evaluation
- Training Tips
- Vector Database Integration
- Additional Resources
```

#### 生成されたチャンク（sample_1.chunks.jsonl）
```json
{"text": "Training and Finetuning Sparse Embedding Models with Sentence Transformers v5Sentence Transformers is a Python library...- v3.0: (improved) Sentence Transformer (Dense Embedding) model training- v4.0: (improved) Cross Encoder (Reranker) model training", "sentences": ["Training and Finetuning Sparse Embedding Models with Sentence Transformers v5", "Sentence Transformers is a Python library...", "- v3.0: (improved) Sentence Transformer (Dense Embedding) model training", "- v4.0: (improved) Cross Encoder (Reranker) model training"]}

{"text": "- v5.0: (new) Sparse Embedding model trainingIn this blogpost, I'll show you how to use it to finetune...", "sentences": ["- v5.0: (new) Sparse Embedding model training", "In this blogpost, I'll show you how to use it to finetune..."]}

{"text": "Table of Contents", "sentences": ["Table of Contents"]}
{"text": "- What are Sparse Embedding models?", "sentences": ["- What are Sparse Embedding models?"]}
{"text": "- Why Finetune?", "sentences": ["- Why Finetune?"]}
{"text": "- Training Components", "sentences": ["- Training Components"]}
{"text": "- Model", "sentences": ["- Model"]}
{"text": "- Dataset", "sentences": ["- Dataset"]}
{"text": "- Loss Function", "sentences": ["- Loss Function"]}
{"text": "- Training Arguments", "sentences": ["- Training Arguments"]}
{"text": "- Evaluator", "sentences": ["- Evaluator"]}
{"text": "- Trainer", "sentences": ["- Trainer"]}
{"text": "- Evaluation", "sentences": ["- Evaluation"]}
{"text": "- Training Tips", "sentences": ["- Training Tips"]}
{"text": "- Vector Database Integration", "sentences": ["- Vector Database Integration"]}
{"text": "- Additional Resources", "sentences": ["- Additional Resources"]}
```

### 2. 問題の分析

#### A. リスト要素の分散
- **問題**: 連続したリスト要素（v3.0, v4.0, v5.0）が異なるチャンクに分割されている
- **影響**: リストの文脈が失われ、個別の項目として扱われる

#### B. 目次の過度な分割
- **問題**: 目次の各項目が独立したチャンクとして生成されている
- **影響**: 目次としての構造が失われ、単なる短い文の集合になる

#### C. リスト構造の認識不足
- **問題**: システムがリストの開始・終了を認識できていない
- **影響**: リスト全体を一つの論理的な単位として扱えない

### 3. 根本原因の考察

#### 3.1 文分割レベルでの問題
1. **リストマーカーの認識不足**:
   - `- `、`* `、`1. `などのリストマーカーを特別扱いしていない
   - リスト項目を通常の文として処理している

2. **リスト境界の検出不足**:
   - リストの開始（前の段落との空行）を検出していない
   - リストの終了（次の段落との空行）を検出していない

#### 3.2 境界判定レベルでの問題
1. **セマンティック類似性の誤解釈**:
   - リスト項目間の類似性が高いため、境界として検出されない
   - リスト全体が一つのチャンクとして扱われるべきだが、個別に分割される

2. **構造的情報の無視**:
   - リストの階層構造やインデント情報を考慮していない
   - リストの長さや項目数を考慮していない

#### 3.3 チャンク構築レベルでの問題
1. **リスト単位でのチャンク化不足**:
   - リスト全体を一つの論理単位として扱う仕組みがない
   - 個別の文レベルでの境界判定のみに依存している

### 4. 影響範囲

#### 4.1 機能的影響
- **情報の断片化**: リストの文脈が失われる
- **構造の消失**: 文書の論理構造が保持されない
- **可読性の低下**: チャンク間の関係性が不明確

#### 4.2 後続処理への影響
- **翻訳精度の低下**: リスト全体の文脈が失われる
- **要約の不正確性**: リスト項目の関係性が考慮されない
- **検索精度の低下**: リスト全体の意味が分散される

### 5. 解決策の方向性

#### 5.1 前処理の改善
- リストマーカーの検出機能の追加
- リスト境界の自動検出
- リスト階層構造の解析

#### 5.2 境界判定の改善
- リスト単位での境界判定ロジック
- 構造的情報を考慮した類似性計算
- リスト長に基づく適応的なチャンクサイズ調整

#### 5.3 チャンク構築の改善
- リスト全体を一つのチャンクとして扱うオプション
- リスト項目の論理的なグループ化
- 構造保持オプションの追加

## 優先度
高 - 文書構造の保持に重大な影響があり、後続処理の精度に直接影響する

## 関連ファイル
- `samples/sample_1.txt`
- `samples/sample_1.chunks.jsonl`
- 前処理モジュール（リスト構造検出機能の追加が必要）
- 境界判定モジュール（構造考慮ロジックの追加が必要）

## 作成日
2025/07/07 