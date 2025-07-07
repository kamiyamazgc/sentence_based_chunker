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


if __name__ == "__main__":
    test_document_node() 