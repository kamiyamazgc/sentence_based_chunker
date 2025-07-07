# Issue #005: 文書構造復元機能のテスト結果レポート

## 概要

DocumentNodeの文書構造復元機能をテストした結果、実装と期待値の間に複数の不整合が発見されました。

## テスト実行日時

2025年1月27日

## テスト内容

### テスト対象機能
- DocumentNodeの文書構造復元機能
- 階層的な文書構造の再構築
- Markdown形式での出力

### テストケース
複雑な文書構造（見出し、段落、ネストしたリスト）を含むテストケースを実行

## テスト結果

### 実行されたテスト
```python
def test_document_structure_restoration():
    """文書構造復元機能のテスト"""
    # テスト用の元文書
    original_text = """# テスト文書

## セクション1
これはセクション1の段落です。

## セクション2
セクション2の内容：

- リストアイテム1
- リストアイテム2
  - ネストしたアイテム1
  - ネストしたアイテム2

## セクション3
最後のセクションです。
"""
```

### 期待される結果
```
# テスト文書

## セクション1

これはセクション1の段落です。

## セクション2

セクション2の内容：

- リストアイテム1
- リストアイテム2
  - ネストしたアイテム1
  - ネストしたアイテム2

## セクション3

最後のセクションです。
```

### 実際の結果
```
テスト文書

## セクション1

これはセクション1の段落です。

## セクション2

セクション2の内容：

- リストアイテム1
- リストアイテム2

## セクション3

最後のセクションです。
```

## 発見された問題

### 1. 文書タイトルのMarkdown形式化問題

**問題**: `document`ノードのコンテンツがMarkdown形式で出力されていない

**期待値**: `# テスト文書`
**実際の結果**: `テスト文書`

**原因**: `_format_document`メソッドで文書タイトルがMarkdown形式で処理されていない

### 2. ネストしたリストの処理問題

**問題**: リストアイテム内のネストしたリストが正しく処理されていない

**期待値**: 
```
- リストアイテム2
  - ネストしたアイテム1
  - ネストしたアイテム2
```

**実際の結果**: 
```
- リストアイテム2
```

**原因**: `_format_list_item`メソッドでネストしたリストの処理が不完全

## 技術的詳細

### 実装の問題点

1. **`_format_document`メソッド**:
   - 文書タイトルがMarkdown形式で出力されていない
   - セクションレベルの見出し処理が適用されていない

2. **`_format_list_item`メソッド**:
   - ネストしたリストの子ノードが処理されていない
   - インデントレベルの計算が不正確

3. **階層構造の処理**:
   - リストアイテム内の子ノード（ネストしたリスト）が無視されている

## 影響範囲

### 影響を受ける機能
- 文書構造の復元
- Markdown形式での出力
- ネストしたリストの処理
- 階層的な文書構造の表現

### 影響を受けるファイル
- `semantic_parser/core/document_node.py`
- 関連するテストファイル

## 修正が必要な箇所

### 1. `_format_document`メソッドの修正
```python
def _format_document(self, preserve_formatting: bool, format_config: FormatConfig) -> str:
    # 文書タイトルをMarkdown形式で出力
    if self.content:
        lines = [f"# {self.content}"]  # Markdown形式で出力
    else:
        lines = []
```

### 2. `_format_list_item`メソッドの修正
```python
def _format_list_item(self, preserve_formatting: bool, format_config: FormatConfig) -> str:
    # 既存の処理...
    
    # 子ノード（ネストしたリスト）の処理を追加
    if self.children:
        child_lines = []
        for child in self.children:
            child_text = child.to_text(preserve_formatting, format_config)
            if child_text:
                # 子ノードの各行を適切にインデント
                child_lines.extend(child_text.split('\n'))
        
        if child_lines:
            formatted_lines.extend(child_lines)
```

## 結論

**実装の方が想定とずれています**。テストの期待値は正しく、以下の実装上の問題が確認されました：

1. 文書タイトルのMarkdown形式化が不完全
2. ネストしたリストの処理が不完全
3. 階層構造の子ノード処理が不十分

これらの問題を修正することで、期待される文書構造復元機能が実現できます。

## 次のステップ

1. `_format_document`メソッドの修正
2. `_format_list_item`メソッドの修正
3. 階層構造処理の改善
4. 修正後の再テスト実行

## 関連ファイル

- `tests/test_document_node.py`: テストケース
- `semantic_parser/core/document_node.py`: 実装対象
- `docs/Issue/`: 関連する課題レポート