# semantic_parser - セマンティック構造パーサー

## 概要

文書構造を階層的に解析し、意味的な単位でのチャンク分割を実現するモジュールです。

## フェーズ1 Day 1-2 実装状況

### 完了した機能

- [x] DocumentNodeクラスの基本実装
- [x] データクラス定義と型ヒント整備
- [x] 基本的なメソッド実装
  - `to_text()` - フォーマット保持テキスト出力
  - `add_child()` - 子ノード追加
  - `find_children_by_type()` - タイプ別子ノード検索
  - `get_text_length()` - テキスト長取得
  - `to_dict()` - 辞書形式変換
- [x] フォーマット復元機能
  - 段落、セクション、リスト、リストアイテムの適切なフォーマット
  - インデントレベルとリストマーカーの保持
- [x] 基本的な動作テスト

### 実装したファイル

```
semantic_parser/
├── __init__.py
├── core/
│   ├── __init__.py
│   └── document_node.py
├── tests/
│   ├── __init__.py
│   └── test_document_node.py
└── README.md
```

## 使用例

```python
from semantic_parser.core.document_node import DocumentNode

# 基本的な文書構造の作成
document = DocumentNode(node_type='document', content='文書タイトル')
section = DocumentNode(node_type='section', content='# セクション見出し')
paragraph = DocumentNode(node_type='paragraph', content='段落内容')

# 階層構造の構築
document.add_child(section)
section.add_child(paragraph)

# フォーマットされたテキストの出力
print(document.to_text())
# 出力:
# 文書タイトル
# # セクション見出し
# 段落内容
```

## 実装設計

### DocumentNodeクラス

文書の階層構造を表現するコアデータクラスです。

**主要フィールド:**
- `node_type`: ノードタイプ (document, section, paragraph, list, list_item)
- `content`: 実際のテキスト内容
- `children`: 子ノードのリスト
- `metadata`: 構造固有のメタデータ
- `start_line`, `end_line`: 元文書での行番号範囲

**主要メソッド:**
- `to_text(preserve_formatting=True)`: フォーマット保持テキスト出力
- `add_child(child)`: 子ノード追加
- `find_children_by_type(node_type)`: タイプ別子ノード検索
- `get_text_length()`: テキスト長取得
- `to_dict()`: 辞書形式変換

## 次のフェーズ

フェーズ2では、DocumentNodeを活用したSemanticDocumentParserの実装を予定しています。

## テスト

```bash
cd semantic_parser
python3 -c "from core.document_node import DocumentNode; print('Import successful')"
```

## 関連文書

- `docs/implementation_plan_b_semantic_parser.md`: 実装計画詳細
- `docs/implementation_architecture_report.md`: アーキテクチャ設計
- `docs/change_history/change_log.md`: 変更履歴