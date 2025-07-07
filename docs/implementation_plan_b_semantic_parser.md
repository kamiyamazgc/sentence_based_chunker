# B案実装計画書：セマンティック構造パーサー型アプローチ

## 1. プロジェクト概要

### 1.1 目標
文書構造を完全に認識し、LLM翻訳用に最適化されたチャンク分割システムの構築

### 1.2 主要な解決課題
- **改行消失問題**: `"".join(self.sentences)` による情報損失の根本解決
- **リスト構造分割問題**: 構造を考慮した境界検出の実現
- **LLM翻訳最適化**: トークン数制御とコンテキスト保持

### 1.3 技術的アプローチ
文書を階層構造（DocumentNode）として解析し、セマンティックな単位でチャンク分割を実行

## 2. 4フェーズ実装戦略

### フェーズ1: コアデータ構造開発
**期間**: 2週間  
**目標**: 文書構造表現の基盤構築

### フェーズ2: 構造解析エンジン開発
**期間**: 2週間  
**目標**: 文書の構造認識機能の実装

### フェーズ3: LLM最適化チャンカー開発
**期間**: 2週間  
**目標**: 翻訳用チャンク生成機能の実装

### フェーズ4: システム統合・最適化
**期間**: 2週間  
**目標**: 既存システムとの統合と本番投入準備

## 3. フェーズ1詳細：コアデータ構造開発

### 3.1 実装対象

#### 3.1.1 DocumentNodeクラス
**ファイル**: `sentence_based_chunker/core/document_node.py`

```python
@dataclass
class DocumentNode:
    """文書の階層構造ノード"""
    node_type: str  # 'document', 'section', 'paragraph', 'list', 'list_item'
    content: str
    children: List['DocumentNode'] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_line: int = 0
    end_line: int = 0
    
    def to_text(self, preserve_formatting: bool = True) -> str
    def add_child(self, child: 'DocumentNode') -> None
    def find_children_by_type(self, node_type: str) -> List['DocumentNode']
    def get_text_length(self) -> int
    def to_dict(self) -> Dict[str, Any]
```

#### 3.1.2 基本的なフォーマット復元機能
```python
def _format_list(self, preserve_formatting: bool) -> str
def _format_section(self, preserve_formatting: bool) -> str
def _format_paragraph(self, preserve_formatting: bool) -> str
```

### 3.2 実装タスク

#### Week 1
- [ ] **Day 1-2**: DocumentNodeクラスの基本実装
  - データクラス定義
  - 基本的なメソッド実装
  - 型ヒント整備

- [ ] **Day 3-4**: フォーマット復元機能の実装
  - `to_text()`メソッドの実装
  - 各構造タイプのフォーマット処理
  - 改行・インデント保持ロジック

- [ ] **Day 5**: 基本機能の単体テスト作成
  - DocumentNode作成テスト
  - フォーマット復元テスト
  - エッジケーステスト

#### Week 2
- [ ] **Day 1-2**: ヘルパーメソッドの実装
  - `add_child()`, `find_children_by_type()`
  - `get_text_length()`, `to_dict()`
  - 階層構造操作メソッド

- [ ] **Day 3-4**: 高度なテストケース作成
  - 複雑な階層構造のテスト
  - パフォーマンステスト
  - メモリ使用量テスト

- [ ] **Day 5**: コードレビューと改善
  - 型安全性の向上
  - エラーハンドリングの追加
  - ドキュメント作成

### 3.3 成果物
- `sentence_based_chunker/core/document_node.py`
- `tests/test_document_node.py`
- `docs/api/document_node.md`

### 3.4 成功指標
- [ ] DocumentNodeの基本操作が100%動作
- [ ] フォーマット復元精度: 95%以上
- [ ] 単体テストカバレッジ: 90%以上
- [ ] メモリ使用量: 基準値以内

## 4. フェーズ2詳細：構造解析エンジン開発

### 4.1 実装対象

#### 4.1.1 SemanticDocumentParserクラス
**ファイル**: `sentence_based_chunker/core/semantic_parser.py`

```python
class SemanticDocumentParser:
    def __init__(self, config: DocumentStructureConfig)
    def parse(self, structured_sentences: List[StructuredSentence]) -> DocumentNode
    def _create_section_node(self, sentence: StructuredSentence) -> DocumentNode
    def _create_list_node(self) -> DocumentNode
    def _create_list_item_node(self, sentence: StructuredSentence) -> DocumentNode
    def _create_paragraph_node(self) -> DocumentNode
    def _is_continuous_list(self, current_list: DocumentNode, sentence: StructuredSentence) -> bool
    def _extract_header_level(self, structure_info: str) -> int
    def _extract_list_type(self, structure_info: str) -> str
```

### 4.2 実装タスク

#### Week 1
- [ ] **Day 1-2**: パーサーコアロジック実装
  - `SemanticDocumentParser`クラス初期化
  - 基本的な`parse()`メソッド実装
  - 構造タイプ判定ロジック

- [ ] **Day 3-4**: ノード作成メソッド実装
  - セクション、リスト、段落ノード作成
  - メタデータ抽出ロジック
  - 行番号追跡機能

- [ ] **Day 5**: 基本解析テスト
  - シンプルな文書構造の解析テスト
  - ノード作成精度の検証

#### Week 2
- [ ] **Day 1-2**: 高度な構造認識実装
  - ネストしたリスト構造の処理
  - 複雑な見出し階層の認識
  - 段落結合ロジック

- [ ] **Day 3-4**: エラーハンドリングと最適化
  - 不正な構造への対応
  - パフォーマンス最適化
  - メモリ効率の改善

- [ ] **Day 5**: 包括的テストと統合
  - 複雑な文書での解析テスト
  - 既存の前処理システムとの統合テスト

### 4.3 成果物
- `sentence_based_chunker/core/semantic_parser.py`
- `tests/test_semantic_parser.py`
- `tests/fixtures/complex_documents/`
- `docs/api/semantic_parser.md`

### 4.4 成功指標
- [ ] 構造認識精度: 95%以上
- [ ] 処理速度: 既存比+25%以内
- [ ] 階層構造正確性: 90%以上
- [ ] エラー率: 5%以下

## 5. フェーズ3詳細：LLM最適化チャンカー開発

### 5.1 実装対象

#### 5.1.1 LLMOptimizedSemanticChunkerクラス
**ファイル**: `sentence_based_chunker/core/llm_chunker.py`

```python
class LLMOptimizedSemanticChunker:
    def __init__(self, config: Config)
    def create_chunks(self, document: DocumentNode) -> List[TranslationOptimizedChunk]
    def _chunk_section_for_translation(self, section: DocumentNode) -> List[TranslationOptimizedChunk]
    def _count_tokens(self, text: str) -> int
    def _should_split_for_translation_quality(self, node: DocumentNode, total_tokens: int) -> bool
    def _create_translation_chunk_from_nodes(self, nodes: List[DocumentNode]) -> TranslationOptimizedChunk
    def _optimize_chunks_for_translation(self, chunks: List[TranslationOptimizedChunk]) -> List[TranslationOptimizedChunk]
    def _calculate_structure_complexity(self, nodes: List[DocumentNode]) -> float
```

#### 5.1.2 TranslationOptimizedChunkクラス
**ファイル**: `sentence_based_chunker/core/translation_chunk.py`

```python
@dataclass
class TranslationOptimizedChunk:
    text: str
    sentences: List[str]
    token_count: int
    translation_metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]
    def is_translation_ready(self) -> bool
    def get_context_headers(self) -> List[str]
    def get_structure_complexity(self) -> float
```

### 5.2 実装タスク

#### Week 1
- [ ] **Day 1**: 依存関係のセットアップ
  - `tiktoken`ライブラリの統合
  - トークナイザー設定とテスト

- [ ] **Day 2-3**: TranslationOptimizedChunk実装
  - データクラス定義
  - メタデータ管理機能
  - 翻訳準備状態判定ロジック

- [ ] **Day 4-5**: LLMOptimizedSemanticChunker基本実装
  - 初期化とコンフィグ設定
  - 基本的なチャンク分割ロジック

#### Week 2
- [ ] **Day 1-2**: トークン数制御機能
  - 200-3000トークン範囲での分割
  - 最適サイズ（2000トークン）への調整
  - オーバーサイズチャンクの分割処理

- [ ] **Day 3**: 翻訳品質最適化
  - コンテキスト保持（見出し情報含有）
  - 構造複雑性スコア算出
  - 翻訳適性判定

- [ ] **Day 4-5**: 最適化とテスト
  - チャンク統合/分割の最適化
  - パフォーマンステスト
  - 翻訳品質指標の検証

### 5.3 成果物
- `sentence_based_chunker/core/llm_chunker.py`
- `sentence_based_chunker/core/translation_chunk.py`
- `tests/test_llm_chunker.py`
- `tests/test_translation_chunk.py`
- `requirements.txt`（tiktoken追加）
- `docs/api/llm_chunker.md`

### 5.4 成功指標
- [ ] トークン数適性: 95%以上のチャンクが200-3000トークン範囲
- [ ] 平均トークン数: 1800-2200トークン
- [ ] コンテキスト保持率: 90%以上（見出し情報含有）
- [ ] 構造複雑性: 平均0.5以下
- [ ] 翻訳準備完了率: 98%以上

## 6. フェーズ4詳細：システム統合・最適化

### 6.1 実装対象

#### 6.1.1 TranslationOptimizedChunkingPipelineクラス
**ファイル**: `sentence_based_chunker/pipeline/translation_pipeline.py`

```python
class TranslationOptimizedChunkingPipeline:
    def __init__(self, config: Config)
    async def process(self, input_path: pathlib.Path) -> List[TranslationOptimizedChunk]
    def _validate_translation_chunks(self, chunks: List[TranslationOptimizedChunk]) -> List[TranslationOptimizedChunk]
    def _is_translation_suitable(self, chunk: TranslationOptimizedChunk) -> bool
    def _repair_translation_chunk(self, chunk: TranslationOptimizedChunk) -> List[TranslationOptimizedChunk]
    def _ensure_translation_readiness(self, chunks: List[TranslationOptimizedChunk]) -> List[TranslationOptimizedChunk]
```

#### 6.1.2 API互換性レイヤー
**ファイル**: `sentence_based_chunker/compatibility/legacy_adapter.py`

```python
class LegacyChunkAdapter:
    """既存APIとの互換性を保つアダプター"""
    def __init__(self, new_pipeline: TranslationOptimizedChunkingPipeline)
    def convert_to_legacy_chunk(self, translation_chunk: TranslationOptimizedChunk) -> Chunk
    def process_with_legacy_interface(self, input_path: str) -> List[Chunk]
```

### 6.2 実装タスク

#### Week 1
- [ ] **Day 1-2**: パイプライン統合実装
  - エンドツーエンド処理フローの構築
  - 各コンポーネントの連携実装
  - エラーハンドリング強化

- [ ] **Day 3-4**: API互換性レイヤー実装
  - 既存Chunkクラスとの変換機能
  - レガシーインターフェース保持
  - 移行期間の並行稼働対応

- [ ] **Day 5**: 基本統合テスト
  - エンドツーエンドテストの実行
  - API互換性の検証

#### Week 2
- [ ] **Day 1-2**: パフォーマンス最適化
  - メモリ使用量の最適化
  - 処理速度の改善
  - 並列処理の実装

- [ ] **Day 3**: 包括的テスト実施
  - 大規模文書での処理テスト
  - 各種文書形式での動作確認
  - 性能ベンチマーク実施

- [ ] **Day 4-5**: 本番投入準備
  - ドキュメント整備
  - デプロイメント準備
  - モニタリング設定

### 6.3 成果物
- `sentence_based_chunker/pipeline/translation_pipeline.py`
- `sentence_based_chunker/compatibility/legacy_adapter.py`
- `tests/integration/test_full_pipeline.py`
- `tests/performance/benchmark_tests.py`
- `docs/migration_guide.md`
- `docs/deployment_guide.md`

### 6.4 成功指標
- [ ] 処理速度: 既存比125%以内
- [ ] メモリ使用量: 既存比140%以内
- [ ] API互換性: 100%保持
- [ ] 統合テスト通過率: 100%

## 7. 全体スケジュール

```
Week 1-2:  フェーズ1（コアデータ構造）
Week 3-4:  フェーズ2（構造解析エンジン）
Week 5-6:  フェーズ3（LLM最適化チャンカー）
Week 7-8:  フェーズ4（システム統合・最適化）
```

### 7.1 マイルストーン
- **Week 2**: DocumentNodeによる文書構造表現が可能
- **Week 4**: 複雑な文書構造の正確な解析が可能
- **Week 6**: LLM翻訳用最適チャンクの生成が可能
- **Week 8**: 本番環境投入準備完了

## 8. リスク管理

### 8.1 技術的リスク

#### 8.1.1 パフォーマンス劣化リスク
**リスク**: メモリ使用量・処理速度の大幅な増加
**軽減策**: 
- 各フェーズでのベンチマーク実施
- 早期最適化による性能確保
- フォールバック機能の実装

#### 8.1.2 tiktoken依存リスク
**リスク**: 外部ライブラリの安定性・ライセンス問題
**軽減策**:
- 代替トークナイザーの調査・準備
- ライセンス適合性の事前確認
- 独自トークン計算ロジックの検討

#### 8.1.3 複雑性増加リスク
**リスク**: アーキテクチャの複雑化による保守性低下
**軽減策**:
- 明確な責任分離設計
- 包括的なドキュメント作成
- 段階的なコードレビュー実施

### 8.2 スケジュールリスク

#### 8.2.1 各フェーズ遅延リスク
**軽減策**:
- 週次進捗レビューの実施
- 早期の課題識別と対応
- バッファ期間の確保

#### 8.2.2 統合時問題発生リスク
**軽減策**:
- 各フェーズでの部分統合テスト
- インターフェース設計の事前合意
- ロールバック手順の準備

## 9. 品質保証

### 9.1 テスト戦略

#### 9.1.1 単体テスト
- **カバレッジ目標**: 90%以上
- **フレームワーク**: pytest
- **テスト種別**: 機能テスト、境界値テスト、エラーケーステスト

#### 9.1.2 統合テスト
- **対象**: コンポーネント間の連携
- **テストデータ**: 実際の技術文書セット
- **自動化**: CI/CDパイプライン組み込み

#### 9.1.3 パフォーマンステスト
- **測定項目**: 処理時間、メモリ使用量、トークン数精度
- **ベンチマーク**: 既存システムとの比較
- **継続監視**: 性能回帰の早期発見

### 9.2 コード品質

#### 9.2.1 静的解析
- **ツール**: mypy（型チェック）、flake8（スタイル）、bandit（セキュリティ）
- **実施頻度**: コミット毎
- **品質ゲート**: 解析エラー0件

#### 9.2.2 コードレビュー
- **レビュー観点**: 設計、性能、保守性、テスト
- **レビュー体制**: 2名以上のレビュアー
- **承認条件**: 全レビュアーの承認

## 10. 成功指標とKPI

### 10.1 機能的KPI
- [ ] **改行保持率**: 100%
- [ ] **リスト構造保持率**: 95%以上
- [ ] **構造認識精度**: 95%以上
- [ ] **トークン数適性**: 95%以上のチャンクが200-3000トークン範囲

### 10.2 性能KPI
- [ ] **処理速度**: 既存比125%以内
- [ ] **メモリ使用量**: 既存比140%以内
- [ ] **API応答時間**: 3秒以内（中規模文書）

### 10.3 品質KPI
- [ ] **テストカバレッジ**: 90%以上
- [ ] **バグ密度**: 1件/1000行以下
- [ ] **翻訳準備完了率**: 98%以上

### 10.4 翻訳最適化KPI
- [ ] **平均チャンクトークン数**: 1800-2200トークン
- [ ] **コンテキスト保持率**: 90%以上
- [ ] **構造複雑性**: 平均0.5以下

## 11. 次のアクション

### 11.1 プロジェクト開始前準備（1週間）
- [ ] 開発環境のセットアップ
- [ ] テストデータセットの準備
- [ ] CI/CDパイプラインの構築
- [ ] チーム体制の確立

### 11.2 フェーズ1開始準備（3日）
- [ ] DocumentNode設計の最終レビュー
- [ ] テスト戦略の詳細化
- [ ] 開発ツールチェーンの確認

### 11.3 継続的な活動
- [ ] 週次進捗レビュー
- [ ] リスク評価とエスカレーション
- [ ] ステークホルダー向け報告

---

**作成日**: 2025/01/27  
**バージョン**: 1.0  
**承認者**: TBD  
**関連文書**: 
- `docs/implementation_architecture_report.md`
- `docs/proposal_issue_004_solutions.md`  
**更新履歴**:
- 2025/01/27: 初版作成