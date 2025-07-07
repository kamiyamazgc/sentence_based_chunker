#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DocumentNodeのテストスクリプト
実際の文章を処理して結果を表示します
"""

from semantic_parser.core.document_node import DocumentNode


def test_document_node():
    """DocumentNodeの基本機能をテスト"""
    
    # テスト用の文書構造を作成
    print("=== DocumentNode テスト ===")
    
    # 1. シンプルな段落のテスト
    print("\n1. シンプルな段落のテスト")
    paragraph = DocumentNode(
        node_type='paragraph',
        content='これはテスト用の段落です。',
        start_line=1,
        end_line=1
    )
    print(f"段落: {paragraph.to_text()}")
    
    # 2. 見出し付きセクションのテスト
    print("\n2. 見出し付きセクションのテスト")
    section = DocumentNode(
        node_type='section',
        content='テストセクション',
        start_line=1,
        end_line=1
    )
    
    # セクションに段落を追加
    section.add_child(DocumentNode(
        node_type='paragraph',
        content='このセクションには段落が含まれています。',
        start_line=2,
        end_line=2
    ))
    
    print(f"セクション: {section.to_text()}")
    
    # 3. リストのテスト
    print("\n3. リストのテスト")
    list_node = DocumentNode(
        node_type='list',
        content='',
        start_line=1,
        end_line=1
    )
    
    # リストアイテムを追加
    item1 = DocumentNode(
        node_type='list_item',
        content='最初のアイテム',
        metadata={'list_type': 'unordered', 'indent_level': 0},
        start_line=1,
        end_line=1
    )
    
    item2 = DocumentNode(
        node_type='list_item',
        content='二番目のアイテム',
        metadata={'list_type': 'unordered', 'indent_level': 0},
        start_line=2,
        end_line=2
    )
    
    list_node.add_child(item1)
    list_node.add_child(item2)
    
    print(f"リスト: {list_node.to_text()}")
    
    # 4. 複雑な文書構造のテスト
    print("\n4. 複雑な文書構造のテスト")
    document = DocumentNode(
        node_type='document',
        content='テスト文書',
        start_line=1,
        end_line=1
    )
    
    # セクション1を追加
    section1 = DocumentNode(
        node_type='section',
        content='セクション1',
        start_line=2,
        end_line=2
    )
    section1.add_child(DocumentNode(
        node_type='paragraph',
        content='セクション1の内容です。',
        start_line=3,
        end_line=3
    ))
    
    # セクション2を追加
    section2 = DocumentNode(
        node_type='section',
        content='セクション2',
        start_line=4,
        end_line=4
    )
    
    # セクション2にリストを追加
    list_in_section = DocumentNode(
        node_type='list',
        content='',
        start_line=5,
        end_line=5
    )
    
    list_in_section.add_child(DocumentNode(
        node_type='list_item',
        content='セクション2のリストアイテム1',
        metadata={'list_type': 'unordered', 'indent_level': 0},
        start_line=5,
        end_line=5
    ))
    
    list_in_section.add_child(DocumentNode(
        node_type='list_item',
        content='セクション2のリストアイテム2',
        metadata={'list_type': 'unordered', 'indent_level': 0},
        start_line=6,
        end_line=6
    ))
    
    section2.add_child(list_in_section)
    
    document.add_child(section1)
    document.add_child(section2)
    
    print("複雑な文書構造:")
    print(document.to_text())
    
    # 5. JSON形式での出力テスト
    print("\n5. JSON形式での出力テスト")
    print("段落の辞書形式:")
    print(paragraph.to_dict())
    
    # 6. メタデータのテスト
    print("\n6. メタデータのテスト")
    ordered_list = DocumentNode(
        node_type='list',
        content='',
        metadata={'list_style': 'ordered'},
        start_line=1,
        end_line=1
    )
    
    ordered_list.add_child(DocumentNode(
        node_type='list_item',
        content='番号付きアイテム1',
        metadata={'list_type': 'ordered', 'indent_level': 0},
        start_line=1,
        end_line=1
    ))
    
    ordered_list.add_child(DocumentNode(
        node_type='list_item',
        content='番号付きアイテム2',
        metadata={'list_type': 'ordered', 'indent_level': 0},
        start_line=2,
        end_line=2
    ))
    
    print(f"番号付きリスト: {ordered_list.to_text()}")


def test_document_structure_restoration():
    """文書構造復元機能のテスト"""
    print("\n=== 文書構造復元テスト ===")
    
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
    
    print("元文書:")
    print(original_text)
    
    # 文書構造を再構築
    document = DocumentNode(
        node_type='document',
        content='テスト文書',
        start_line=1,
        end_line=1
    )
    
    # セクション1
    section1 = DocumentNode(
        node_type='section',
        content='セクション1',
        metadata={'header_level': 2, 'header_style': 'markdown'},
        start_line=3,
        end_line=3
    )
    section1.add_child(DocumentNode(
        node_type='paragraph',
        content='これはセクション1の段落です。',
        start_line=4,
        end_line=4
    ))
    
    # セクション2
    section2 = DocumentNode(
        node_type='section',
        content='セクション2',
        metadata={'header_level': 2, 'header_style': 'markdown'},
        start_line=6,
        end_line=6
    )
    section2.add_child(DocumentNode(
        node_type='paragraph',
        content='セクション2の内容：',
        start_line=7,
        end_line=7
    ))
    
    # セクション2のリスト
    list_node = DocumentNode(
        node_type='list',
        content='',
        start_line=9,
        end_line=9
    )
    
    # リストアイテム1
    item1 = DocumentNode(
        node_type='list_item',
        content='リストアイテム1',
        metadata={'list_type': 'unordered', 'indent_level': 0},
        start_line=9,
        end_line=9
    )
    
    # リストアイテム2（ネスト付き）
    item2 = DocumentNode(
        node_type='list_item',
        content='リストアイテム2',
        metadata={'list_type': 'unordered', 'indent_level': 0},
        start_line=10,
        end_line=10
    )
    
    # ネストしたリスト
    nested_list = DocumentNode(
        node_type='list',
        content='',
        start_line=11,
        end_line=11
    )
    
    nested_item1 = DocumentNode(
        node_type='list_item',
        content='ネストしたアイテム1',
        metadata={'list_type': 'unordered', 'indent_level': 1},
        start_line=11,
        end_line=11
    )
    
    nested_item2 = DocumentNode(
        node_type='list_item',
        content='ネストしたアイテム2',
        metadata={'list_type': 'unordered', 'indent_level': 1},
        start_line=12,
        end_line=12
    )
    
    nested_list.add_child(nested_item1)
    nested_list.add_child(nested_item2)
    item2.add_child(nested_list)
    
    list_node.add_child(item1)
    list_node.add_child(item2)
    section2.add_child(list_node)
    
    # セクション3
    section3 = DocumentNode(
        node_type='section',
        content='セクション3',
        metadata={'header_level': 2, 'header_style': 'markdown'},
        start_line=14,
        end_line=14
    )
    section3.add_child(DocumentNode(
        node_type='paragraph',
        content='最後のセクションです。',
        start_line=15,
        end_line=15
    ))
    
    document.add_child(section1)
    document.add_child(section2)
    document.add_child(section3)
    
    # 復元された文書を出力
    restored_text = document.to_text(preserve_formatting=True)
    print("\n復元された文書:")
    print(restored_text)
    
    # 期待される結果との比較
    expected_text = """# テスト文書

## セクション1

これはセクション1の段落です。

## セクション2

セクション2の内容：

- リストアイテム1
- リストアイテム2
  - ネストしたアイテム1
  - ネストしたアイテム2

## セクション3

最後のセクションです。"""
    
    print("\n期待される結果:")
    print(expected_text)
    
    # 比較結果
    print("\n=== 比較結果 ===")
    if restored_text == expected_text:
        print("✅ 復元成功: 実装は期待通りに動作しています")
    else:
        print("❌ 復元失敗: 実装と期待値が異なります")
        print("\n差分:")
        print("復元されたテキスト:")
        print(repr(restored_text))
        print("\n期待されるテキスト:")
        print(repr(expected_text))


if __name__ == "__main__":
    test_document_node()
    test_document_structure_restoration() 