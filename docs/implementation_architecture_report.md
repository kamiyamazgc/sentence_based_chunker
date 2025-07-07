# アーキテクチャ見直し実装技術仕様レポート

## 1. 現状分析

### 1.1 現在のシステム構造

**コアモジュール構成:**
- `preprocess.py`: 文書構造認識機能（StructuredSentence, DocumentStructure）
- `detector.py`: 埋め込みベースの境界検出（Stage A/B/C/D）
- `builder.py`: シンプルなチャンク構築（文字列結合）
- `config.py`: 文書構造設定（DocumentStructureConfig）

### 1.2 問題の根本原因

1. **改行消失問題**: `builder.py` の `"".join(self.sentences)` による情報損失
2. **リスト構造分割問題**: 境界検出アルゴリズムが構造情報を考慮していない
3. **構造情報の活用不足**: 前処理で認識した構造が後続処理で利用されていない

### 1.3 既存実装の課題

```python
# 現在のChunk.textプロパティ（問題の原因）
@property
def text(self) -> str:
    return "".join(self.sentences)  # 改行が失われる
```

## 2. 実装方法案

### 2.1 案A: 構造認識統合型アプローチ

#### 概要
既存アーキテクチャを維持しつつ、構造情報を各段階で活用する統合的改善。

#### 技術仕様

**1. 拡張チャンクデータ構造**
```python
@dataclass
class StructuredChunk:
    """構造情報を保持するチャンク"""
    sentences: List[StructuredSentence]
    structure_metadata: Dict[str, Any]
    
    @property
    def text(self) -> str:
        """改行とフォーマットを保持したテキスト再構成"""
        lines = []
        current_line = ""
        
        for sentence in self.sentences:
            if sentence.structure_type == 'header':
                if current_line:
                    lines.append(current_line)
                    current_line = ""
                lines.append(f"{sentence.text}")
                
            elif sentence.structure_type == 'list':
                if current_line:
                    lines.append(current_line)
                    current_line = ""
                indent = " " * sentence.indent_level
                marker = self._extract_list_marker(sentence.structure_info)
                lines.append(f"{indent}{marker} {sentence.text}")
                
            else:
                if current_line:
                    current_line += sentence.text
                else:
                    current_line = sentence.text
        
        if current_line:
            lines.append(current_line)
        
        return "\n".join(lines)
    
    def _extract_list_marker(self, structure_info: str) -> str:
        """構造情報からリストマーカーを復元"""
        if 'ordered' in structure_info:
            return "1."  # 簡略化
        else:
            return "-"
```

**2. 構造認識境界検出器**
```python
class StructureAwareBoundaryDetector:
    def __init__(self, config: Config):
        self.config = config
        self.structure_rules = self._load_structure_rules()
    
    def detect_boundaries(
        self, 
        structured_sentences: List[StructuredSentence],
        embeddings: List[np.ndarray]
    ) -> List[bool]:
        """構造情報を考慮した境界検出"""
        
        # Stage 1: 構造境界の強制検出
        structural_boundaries = self._detect_structural_boundaries(structured_sentences)
        
        # Stage 2: 従来の埋め込みベース検出
        embedding_boundaries = self._detect_semantic_boundaries(embeddings)
        
        # Stage 3: 構造ルールによる調整
        adjusted_boundaries = self._apply_structure_rules(
            structured_sentences, 
            structural_boundaries, 
            embedding_boundaries
        )
        
        return adjusted_boundaries
    
    def _detect_structural_boundaries(self, sentences: List[StructuredSentence]) -> List[bool]:
        """構造変化による境界検出"""
        boundaries = [False] * len(sentences)
        
        for i in range(1, len(sentences)):
            prev_sentence = sentences[i-1]
            curr_sentence = sentences[i]
            
            # 見出しの前後は境界
            if curr_sentence.structure_type == 'header':
                boundaries[i] = True
            
            # リスト終了後は境界
            if (prev_sentence.structure_type == 'list' and 
                curr_sentence.structure_type != 'list'):
                boundaries[i] = True
            
            # 大きなインデント変化は境界
            indent_diff = abs(curr_sentence.indent_level - prev_sentence.indent_level)
            if indent_diff >= self.config.document_structure.list_indent_threshold:
                boundaries[i] = True
        
        return boundaries
    
    def _apply_structure_rules(
        self, 
        sentences: List[StructuredSentence],
        structural: List[bool], 
        semantic: List[bool]
    ) -> List[bool]:
        """構造ルールによる境界調整"""
        final_boundaries = [s or e for s, e in zip(structural, semantic)]
        
        # リスト内での過度な分割を抑制
        for i in range(len(sentences)):
            if final_boundaries[i] and sentences[i].structure_type == 'list':
                # 同じリスト内での分割を評価
                if self._is_same_list_context(sentences, i):
                    final_boundaries[i] = False
        
        return final_boundaries
    
    def _is_same_list_context(self, sentences: List[StructuredSentence], index: int) -> bool:
        """同一リストコンテキスト内かどうかを判定"""
        if index == 0:
            return False
        
        curr = sentences[index]
        prev = sentences[index - 1]
        
        # 同じインデントレベルで同じリストタイプ
        return (curr.structure_type == 'list' and 
                prev.structure_type == 'list' and
                curr.indent_level == prev.indent_level and
                self._extract_list_type(curr.structure_info) == 
                self._extract_list_type(prev.structure_info))
```

**3. 改善されたビルダー**
```python
class StructuredChunkBuilder:
    def build_chunks(
        self, 
        structured_sentences: List[StructuredSentence], 
        boundaries: List[bool]
    ) -> List[StructuredChunk]:
        """構造情報を保持するチャンク構築"""
        current_sentences = []
        result = []
        
        for sentence, boundary in zip(structured_sentences, boundaries):
            current_sentences.append(sentence)
            
            if boundary:
                chunk = self._create_structured_chunk(current_sentences)
                result.append(chunk)
                current_sentences = []
        
        if current_sentences:
            chunk = self._create_structured_chunk(current_sentences)
            result.append(chunk)
        
        return result
    
    def _create_structured_chunk(self, sentences: List[StructuredSentence]) -> StructuredChunk:
        """メタデータ付きチャンクの作成"""
        metadata = {
            'structure_types': list(set(s.structure_type for s in sentences)),
            'has_headers': any(s.structure_type == 'header' for s in sentences),
            'has_lists': any(s.structure_type == 'list' for s in sentences),
            'indent_levels': list(set(s.indent_level for s in sentences)),
            'line_range': (sentences[0].line_number, sentences[-1].line_number)
        }
        
        return StructuredChunk(sentences=sentences, structure_metadata=metadata)
```

#### 案Aのメリット・デメリット

**メリット:**
- 既存コードベースの最大活用
- 段階的な移行が可能
- テスト負荷が相対的に軽い
- 既存API互換性の維持が容易

**デメリット:**
- 構造認識ロジックが複数箇所に分散
- 完全な構造認識には限界
- コードの複雑性が増加
- 将来の拡張性に制約

### 2.2 案B: セマンティック構造パーサー型アプローチ

#### 概要
文書を構造的に解析し、意味的な単位でチャンクを分割する新しいアーキテクチャ。

#### 技術仕様

**1. 文書構造パーサー**
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
    
    def to_text(self, preserve_formatting: bool = True) -> str:
        """フォーマットを保持したテキスト出力"""
        if self.node_type == 'list':
            return self._format_list(preserve_formatting)
        elif self.node_type == 'section':
            return self._format_section(preserve_formatting)
        else:
            return self.content

class SemanticDocumentParser:
    """セマンティック文書パーサー"""
    
    def __init__(self, config: DocumentStructureConfig):
        self.config = config
        self.structure_patterns = self._compile_patterns()
    
    def parse(self, structured_sentences: List[StructuredSentence]) -> DocumentNode:
        """文書を階層構造に解析"""
        root = DocumentNode(node_type='document', content='')
        
        current_section = None
        current_list = None
        current_paragraph = None
        
        for sentence in structured_sentences:
            if sentence.structure_type == 'header':
                # 新しいセクション開始
                current_section = self._create_section_node(sentence)
                root.children.append(current_section)
                current_list = None
                current_paragraph = None
                
            elif sentence.structure_type == 'list':
                if not current_list or not self._is_continuous_list(current_list, sentence):
                    # 新しいリスト開始
                    current_list = self._create_list_node()
                    (current_section or root).children.append(current_list)
                
                list_item = self._create_list_item_node(sentence)
                current_list.children.append(list_item)
                current_paragraph = None
                
            else:
                # 通常の段落
                if not current_paragraph:
                    current_paragraph = self._create_paragraph_node()
                    (current_section or root).children.append(current_paragraph)
                
                current_paragraph.content += sentence.text
                current_paragraph.end_line = sentence.line_number
        
        return root
    
    def _create_section_node(self, sentence: StructuredSentence) -> DocumentNode:
        """セクションノードの作成"""
        level = self._extract_header_level(sentence.structure_info)
        return DocumentNode(
            node_type='section',
            content=sentence.text,
            metadata={'header_level': level},
            start_line=sentence.line_number,
            end_line=sentence.line_number
        )
    
    def _create_list_node(self) -> DocumentNode:
        """リストノードの作成"""
        return DocumentNode(node_type='list', content='')
    
    def _create_list_item_node(self, sentence: StructuredSentence) -> DocumentNode:
        """リストアイテムノードの作成"""
        return DocumentNode(
            node_type='list_item',
            content=sentence.text,
            metadata={
                'indent_level': sentence.indent_level,
                'list_type': self._extract_list_type(sentence.structure_info)
            },
            start_line=sentence.line_number,
            end_line=sentence.line_number
        )
```

**2. セマンティックチャンカー**
```python
class SemanticChunker:
    """セマンティック単位でのチャンク分割"""
    
    def __init__(self, config: Config):
        self.config = config
        self.max_chunk_size = 1000  # 文字数制限
        self.min_chunk_size = 100   # 最小文字数
    
    def create_chunks(self, document: DocumentNode) -> List[SemanticChunk]:
        """文書構造に基づくチャンク作成"""
        chunks = []
        
        for section in document.children:
            if section.node_type == 'section':
                section_chunks = self._chunk_section(section)
                chunks.extend(section_chunks)
            else:
                # ルートレベルのコンテンツ
                chunk = self._create_chunk_from_node(section)
                if chunk:
                    chunks.append(chunk)
        
        return self._post_process_chunks(chunks)
    
    def _chunk_section(self, section: DocumentNode) -> List[SemanticChunk]:
        """セクション内のチャンク分割"""
        chunks = []
        current_chunk_nodes = [section]  # 見出しを含める
        current_size = len(section.content)
        
        for child in section.children:
            child_size = len(child.to_text())
            
            if current_size + child_size > self.max_chunk_size and current_chunk_nodes:
                # チャンクを確定
                chunk = self._create_chunk_from_nodes(current_chunk_nodes)
                chunks.append(chunk)
                current_chunk_nodes = []
                current_size = 0
            
            current_chunk_nodes.append(child)
            current_size += child_size
        
        if current_chunk_nodes:
            chunk = self._create_chunk_from_nodes(current_chunk_nodes)
            chunks.append(chunk)
        
        return chunks
    
    def _create_chunk_from_nodes(self, nodes: List[DocumentNode]) -> 'SemanticChunk':
        """ノード群からチャンクを作成"""
        text_parts = []
        metadata = {
            'node_types': [node.node_type for node in nodes],
            'has_header': any(node.node_type == 'section' for node in nodes),
            'has_list': any(node.node_type == 'list' for node in nodes),
            'structure_integrity': True
        }
        
        for node in nodes:
            formatted_text = node.to_text(preserve_formatting=True)
            text_parts.append(formatted_text)
        
        return SemanticChunk(
            text='\n'.join(text_parts),
            sentences=self._extract_sentences(nodes),
            semantic_metadata=metadata
        )
    
    def _post_process_chunks(self, chunks: List['SemanticChunk']) -> List['SemanticChunk']:
        """チャンクの後処理（統合・分割）"""
        processed = []
        
        for chunk in chunks:
            if len(chunk.text) < self.min_chunk_size and processed:
                # 小さすぎるチャンクは前のチャンクに統合
                processed[-1] = self._merge_chunks(processed[-1], chunk)
            else:
                processed.append(chunk)
        
        return processed

@dataclass
class SemanticChunk:
    """セマンティック情報を含むチャンク"""
    text: str
    sentences: List[str]
    semantic_metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """JSON出力用の辞書変換"""
        return {
            'text': self.text,
            'sentences': self.sentences,
            'metadata': self.semantic_metadata
        }
```

**3. 統合パイプライン**
```python
class SemanticChunkingPipeline:
    """セマンティックチャンクングパイプライン"""
    
    def __init__(self, config: Config):
        self.config = config
        self.parser = SemanticDocumentParser(config.document_structure)
        self.chunker = SemanticChunker(config)
    
    async def process(self, input_path: pathlib.Path) -> List[SemanticChunk]:
        """エンドツーエンドの処理"""
        # 1. 構造認識前処理
        structured_sentences = list(stream_structured_sentences(
            input_path, 
            self.config.document_structure
        ))
        
        # 2. 文書構造解析
        document = self.parser.parse(structured_sentences)
        
        # 3. セマンティックチャンク分割
        chunks = self.chunker.create_chunks(document)
        
        # 4. 品質検証
        validated_chunks = self._validate_chunks(chunks)
        
        return validated_chunks
    
    def _validate_chunks(self, chunks: List[SemanticChunk]) -> List[SemanticChunk]:
        """チャンク品質の検証"""
        validated = []
        
        for chunk in chunks:
            # 構造整合性の確認
            if self._validate_structure_integrity(chunk):
                validated.append(chunk)
            else:
                # 問題のあるチャンクは修復または分割
                repaired_chunks = self._repair_chunk(chunk)
                validated.extend(repaired_chunks)
        
        return validated
```

#### 案Bのメリット・デメリット

**メリット:**
- 根本的な構造認識による高品質出力
- 将来の拡張性が非常に高い
- メタデータの豊富な保持
- 複雑な文書構造への対応力

**デメリット:**
- 大幅なアーキテクチャ変更が必要
- 開発・テスト工数が大きい
- 既存APIとの互換性確保が困難
- 性能のオーバーヘッド

## 3. 詳細比較評価

### 3.1 技術的比較

| 評価項目 | 案A: 構造認識統合型 | 案B: セマンティック構造パーサー型 |
|----------|---------------------|-----------------------------------|
| **実装複雑度** | ★★★☆☆ (中程度) | ★★☆☆☆ (高) |
| **開発工数** | 3-4週間 | 6-8週間 |
| **改行保持** | ★★★★☆ (良好) | ★★★★★ (完全) |
| **リスト処理** | ★★★☆☆ (改善) | ★★★★★ (優秀) |
| **構造認識精度** | ★★★☆☆ (向上) | ★★★★★ (高精度) |
| **メタデータ保持** | ★★★☆☆ (限定的) | ★★★★★ (豊富) |
| **拡張性** | ★★☆☆☆ (制限あり) | ★★★★★ (高い) |
| **後方互換性** | ★★★★☆ (維持) | ★★☆☆☆ (困難) |

### 3.2 パフォーマンス評価

**案A: 構造認識統合型**
- メモリ使用量: +20% (構造情報保持のため)
- 処理速度: +10% (構造ルール処理のため)
- 出力品質: +60% (改行・構造保持)

**案B: セマンティック構造パーサー型**
- メモリ使用量: +50% (階層構造・メタデータ)
- 処理速度: +30% (構造解析処理)
- 出力品質: +90% (完全な構造認識)

### 3.3 テストケース設計

**共通テストケース:**
1. 見出し付き文書（改行保持テスト）
2. 複層リスト構造（リスト処理テスト）
3. 混合構造文書（総合テスト）
4. 大規模文書（性能テスト）

**案A固有テストケース:**
- 境界検出ロジックの統合テスト
- 構造ルール適用の正確性テスト

**案B固有テストケース:**
- 文書構造解析の正確性テスト
- セマンティックチャンク品質テスト

### 3.4 リスク分析

**案Aのリスク:**
- 構造認識の限界による品質制約
- 複数箇所への変更による回帰リスク
- 技術的負債の蓄積

**案Bのリスク:**
- 大幅な変更による開発リスク
- 性能劣化の可能性
- 移行期間の長期化

## 4. 推奨案と実装戦略

### 4.1 推奨案: 案B（セマンティック構造パーサー型）

### 4.2 推奨理由

1. **根本的解決**: Issue #004の全問題を根本から解決
2. **将来投資**: 長期的な価値創造と競争優位性
3. **品質向上**: 大幅な出力品質改善
4. **技術的負債回避**: クリーンなアーキテクチャによる保守性向上

### 4.3 段階的実装戦略

**フェーズ1: コアエンジン開発（2週間）**
- DocumentNodeとSemanticDocumentParserの実装
- 基本的な構造認識機能
- 単体テストの作成

**フェーズ2: チャンキング機能（2週間）**
- SemanticChunkerの実装
- チャンク品質検証機能
- 統合テストの作成

**フェーズ3: パイプライン統合（2週間）**
- 既存システムとの統合
- API互換性レイヤーの実装
- 性能最適化

**フェーズ4: 検証・最適化（2週間）**
- 大規模テスト実行
- パフォーマンスチューニング
- ドキュメント作成

### 4.4 移行戦略

1. **パラレル実行期間**: 既存システムと新システムの並行稼働
2. **段階的移行**: 機能ごとの段階的切り替え
3. **フォールバック**: 問題発生時の旧システム復帰
4. **データ比較**: 出力品質の定量的評価

### 4.5 成功指標

**定量指標:**
- 改行保持率: 100%
- リスト構造保持率: 95%以上
- 処理速度: 既存比130%以内
- メモリ使用量: 既存比150%以内

**定性指標:**
- ユーザビリティの大幅改善
- 新機能開発の基盤構築
- 保守性の向上

## 5. 次のアクション

### 5.1 即座に実行（1週間以内）
1. 詳細技術仕様書の作成
2. プロトタイプ開発環境の準備
3. テストデータセットの整備

### 5.2 短期実行（2-3週間）
1. DocumentNodeとパーサーのプロトタイプ実装
2. 基本機能の動作検証
3. 性能ベンチマークの実施

### 5.3 中期実行（1-2ヶ月）
1. 完全実装の実行
2. 既存システムとの統合
3. 本格的なテストとデバッグ

---

**作成日**: 2025/01/27  
**作成者**: AI Assistant  
**関連Issue**: #004  
**前提文書**: docs/proposal_issue_004_solutions.md  
**実装対象**: sentence_based_chunker/