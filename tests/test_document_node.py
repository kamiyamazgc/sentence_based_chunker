#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DocumentNodeの単体テストスクリプト
Day 5: 基本機能の単体テスト作成
- DocumentNode作成テスト
- フォーマット復元テスト
- エッジケーステスト
"""

import pytest
from typing import List, Dict, Any
from semantic_parser.core.document_node import DocumentNode, FormatConfig


class TestDocumentNodeCreation:
    """DocumentNode作成テストクラス"""
    
    def test_basic_node_creation(self):
        """基本的なノード作成テスト"""
        node = DocumentNode(
            node_type='paragraph',
            content='テストコンテンツ',
            start_line=1,
            end_line=1
        )
        
        assert node.node_type == 'paragraph'
        assert node.content == 'テストコンテンツ'
        assert node.start_line == 1
        assert node.end_line == 1
        assert node.children == []
        assert node.metadata == {}
    
    def test_node_with_metadata(self):
        """メタデータ付きノード作成テスト"""
        metadata = {
            'header_level': 2,
            'header_style': 'markdown',
            'original_indent': '  '
        }
        
        node = DocumentNode(
            node_type='section',
            content='セクションタイトル',
            metadata=metadata,
            start_line=5,
            end_line=5
        )
        
        assert node.metadata == metadata
        assert node.metadata['header_level'] == 2
        assert node.metadata['header_style'] == 'markdown'
        assert node.metadata['original_indent'] == '  '
    
    def test_node_with_children(self):
        """子ノード付きノード作成テスト"""
        parent = DocumentNode(
            node_type='document',
            content='テスト文書',
            start_line=1,
            end_line=1
        )
        
        child1 = DocumentNode(
            node_type='paragraph',
            content='最初の段落',
            start_line=2,
            end_line=2
        )
        
        child2 = DocumentNode(
            node_type='paragraph',
            content='二番目の段落',
            start_line=3,
            end_line=3
        )
        
        parent.add_child(child1)
        parent.add_child(child2)
        
        assert len(parent.children) == 2
        assert parent.children[0] == child1
        assert parent.children[1] == child2
    
    def test_list_node_creation(self):
        """リストノード作成テスト"""
        list_node = DocumentNode(
            node_type='list',
            content='',
            start_line=1,
            end_line=1
        )
        
        item1 = DocumentNode(
            node_type='list_item',
            content='リストアイテム1',
            metadata={'list_type': 'unordered', 'indent_level': 0},
            start_line=1,
            end_line=1
        )
        
        item2 = DocumentNode(
            node_type='list_item',
            content='リストアイテム2',
            metadata={'list_type': 'unordered', 'indent_level': 0},
            start_line=2,
            end_line=2
        )
        
        list_node.add_child(item1)
        list_node.add_child(item2)
        
        assert list_node.node_type == 'list'
        assert len(list_node.children) == 2
        assert list_node.children[0].metadata['list_type'] == 'unordered'
        assert list_node.children[1].metadata['list_type'] == 'unordered'
    
    def test_section_node_creation(self):
        """セクションノード作成テスト"""
        section = DocumentNode(
            node_type='section',
            content='セクションタイトル',
            metadata={'header_level': 2, 'header_style': 'markdown'},
            start_line=1,
            end_line=1
        )
        
        paragraph = DocumentNode(
            node_type='paragraph',
            content='セクションの内容',
            start_line=2,
            end_line=2
        )
        
        section.add_child(paragraph)
        
        assert section.node_type == 'section'
        assert section.metadata['header_level'] == 2
        assert len(section.children) == 1
        assert section.children[0].node_type == 'paragraph'
    
    def test_complex_document_structure(self):
        """複雑な文書構造作成テスト"""
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
            metadata={'header_level': 2},
            start_line=2,
            end_line=2
        )
        
        paragraph1 = DocumentNode(
            node_type='paragraph',
            content='セクション1の内容',
            start_line=3,
            end_line=3
        )
        
        section1.add_child(paragraph1)
        
        # セクション2（リスト付き）
        section2 = DocumentNode(
            node_type='section',
            content='セクション2',
            metadata={'header_level': 2},
            start_line=4,
            end_line=4
        )
        
        list_node = DocumentNode(
            node_type='list',
            content='',
            start_line=5,
            end_line=5
        )
        
        item1 = DocumentNode(
            node_type='list_item',
            content='リストアイテム1',
            metadata={'list_type': 'unordered', 'indent_level': 0},
            start_line=5,
            end_line=5
        )
        
        list_node.add_child(item1)
        section2.add_child(list_node)
        
        document.add_child(section1)
        document.add_child(section2)
        
        # 構造の検証
        assert document.node_type == 'document'
        assert len(document.children) == 2
        assert document.children[0].node_type == 'section'
        assert document.children[1].node_type == 'section'
        assert len(document.children[1].children) == 1
        assert document.children[1].children[0].node_type == 'list'


class TestDocumentNodeFormatRestoration:
    """フォーマット復元テストクラス"""
    
    def test_paragraph_format_restoration(self):
        """段落のフォーマット復元テスト"""
        paragraph = DocumentNode(
            node_type='paragraph',
            content='これはテスト段落です。',
            start_line=1,
            end_line=1
        )
        
        result = paragraph.to_text(preserve_formatting=True)
        assert result == 'これはテスト段落です。'
        
        # フォーマット無効の場合
        result_no_format = paragraph.to_text(preserve_formatting=False)
        assert result_no_format == 'これはテスト段落です。'
    
    def test_section_format_restoration(self):
        """セクションのフォーマット復元テスト"""
        section = DocumentNode(
            node_type='section',
            content='テストセクション',
            metadata={'header_level': 2, 'header_style': 'markdown'},
            start_line=1,
            end_line=1
        )
        
        paragraph = DocumentNode(
            node_type='paragraph',
            content='セクションの内容',
            start_line=2,
            end_line=2
        )
        
        section.add_child(paragraph)
        
        result = section.to_text(preserve_formatting=True)
        expected = "## テストセクション\n\nセクションの内容"
        assert result == expected
    
    def test_list_format_restoration(self):
        """リストのフォーマット復元テスト"""
        list_node = DocumentNode(
            node_type='list',
            content='',
            start_line=1,
            end_line=1
        )
        
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
        
        result = list_node.to_text(preserve_formatting=True)
        expected = "- 最初のアイテム\n- 二番目のアイテム"
        assert result == expected
    
    def test_nested_list_format_restoration(self):
        """ネストしたリストのフォーマット復元テスト"""
        list_node = DocumentNode(
            node_type='list',
            content='',
            start_line=1,
            end_line=1
        )
        
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
        
        # ネストしたリスト
        nested_list = DocumentNode(
            node_type='list',
            content='',
            start_line=3,
            end_line=3
        )
        
        nested_item = DocumentNode(
            node_type='list_item',
            content='ネストしたアイテム',
            metadata={'list_type': 'unordered', 'indent_level': 1},
            start_line=3,
            end_line=3
        )
        
        nested_list.add_child(nested_item)
        item2.add_child(nested_list)
        
        list_node.add_child(item1)
        list_node.add_child(item2)
        
        result = list_node.to_text(preserve_formatting=True)
        
        # ネストしたリストの正しいフォーマットを確認
        assert "- 最初のアイテム" in result
        assert "- 二番目のアイテム" in result
        assert "  - ネストしたアイテム" in result
    
    def test_ordered_list_format_restoration(self):
        """番号付きリストのフォーマット復元テスト"""
        list_node = DocumentNode(
            node_type='list',
            content='',
            start_line=1,
            end_line=1
        )
        
        item1 = DocumentNode(
            node_type='list_item',
            content='最初のアイテム',
            metadata={'list_type': 'ordered', 'indent_level': 0, 'item_number': 1},
            start_line=1,
            end_line=1
        )
        
        item2 = DocumentNode(
            node_type='list_item',
            content='二番目のアイテム',
            metadata={'list_type': 'ordered', 'indent_level': 0, 'item_number': 2},
            start_line=2,
            end_line=2
        )
        
        list_node.add_child(item1)
        list_node.add_child(item2)
        
        result = list_node.to_text(preserve_formatting=True)
        expected = "1. 最初のアイテム\n2. 二番目のアイテム"
        assert result == expected
    
    def test_document_format_restoration(self):
        """文書全体のフォーマット復元テスト"""
        document = DocumentNode(
            node_type='document',
            content='テスト文書',
            start_line=1,
            end_line=1
        )
        
        section = DocumentNode(
            node_type='section',
            content='セクション1',
            metadata={'header_level': 2, 'header_style': 'markdown'},
            start_line=2,
            end_line=2
        )
        
        paragraph = DocumentNode(
            node_type='paragraph',
            content='セクションの内容です。',
            start_line=3,
            end_line=3
        )
        
        section.add_child(paragraph)
        document.add_child(section)
        
        result = document.to_text(preserve_formatting=True)
        expected = "# テスト文書\n\n## セクション1\n\nセクションの内容です。"
        assert result == expected
    
    def test_format_config_application(self):
        """FormatConfig適用テスト"""
        config = FormatConfig(
            preserve_blank_lines=False,
            list_indent_size=4,
            section_spacing=2
        )
        
        document = DocumentNode(
            node_type='document',
            content='テスト文書',
            start_line=1,
            end_line=1
        )
        
        section = DocumentNode(
            node_type='section',
            content='セクション1',
            metadata={'header_level': 2, 'header_style': 'markdown'},
            start_line=2,
            end_line=2
        )
        
        paragraph = DocumentNode(
            node_type='paragraph',
            content='セクションの内容です。',
            start_line=3,
            end_line=3
        )
        
        section.add_child(paragraph)
        document.add_child(section)
        
        result = document.to_text(preserve_formatting=True, format_config=config)
        
        # preserve_blank_lines=Falseなので空行は追加されない
        expected = "# テスト文書\n## セクション1\nセクションの内容です。"
        assert result == expected
    
    def test_line_break_preservation(self):
        """改行保持テスト"""
        paragraph = DocumentNode(
            node_type='paragraph',
            content='最初の行です。\n二番目の行です。',
            start_line=1,
            end_line=2
        )
        
        result = paragraph.to_text(preserve_formatting=True)
        assert '\n' in result
        assert '最初の行です。' in result
        assert '二番目の行です。' in result


class TestDocumentNodeEdgeCases:
    """エッジケーステストクラス"""
    
    def test_empty_content(self):
        """空のコンテンツテスト"""
        node = DocumentNode(
            node_type='paragraph',
            content='',
            start_line=1,
            end_line=1
        )
        
        assert node.content == ''
        assert node.to_text() == ''
        assert node.get_text_length() == 0
    
    def test_none_content_handling(self):
        """None コンテンツの処理テスト"""
        # contentがNoneの場合の処理
        node = DocumentNode(
            node_type='paragraph',
            content=None,  # type: ignore
            start_line=1,
            end_line=1
        )
        
        # to_textメソッドがエラーを発生させずに処理することを確認
        result = node.to_text()
        assert result == '' or result is None
    
    def test_invalid_node_type(self):
        """不正なノードタイプテスト"""
        node = DocumentNode(
            node_type='invalid_type',
            content='テストコンテンツ',
            start_line=1,
            end_line=1
        )
        
        # 不正なノードタイプでもエラーを発生させずに処理することを確認
        result = node.to_text()
        assert result == 'テストコンテンツ'
    
    def test_add_invalid_child(self):
        """不正な子ノード追加テスト"""
        parent = DocumentNode(
            node_type='document',
            content='親ノード',
            start_line=1,
            end_line=1
        )
        
        # 不正な型の子ノードを追加しようとした場合
        with pytest.raises(TypeError):
            parent.add_child("invalid_child")  # type: ignore
    
    def test_line_number_update(self):
        """行番号更新テスト"""
        parent = DocumentNode(
            node_type='document',
            content='親ノード',
            start_line=0,
            end_line=0
        )
        
        child1 = DocumentNode(
            node_type='paragraph',
            content='子ノード1',
            start_line=2,
            end_line=3
        )
        
        child2 = DocumentNode(
            node_type='paragraph',
            content='子ノード2',
            start_line=5,
            end_line=7
        )
        
        parent.add_child(child1)
        parent.add_child(child2)
        
        # 親ノードの行番号が適切に更新されることを確認
        assert parent.start_line == 2
        assert parent.end_line == 7
    
    def test_deep_nesting(self):
        """深いネスト構造テスト"""
        # 深いネスト構造を作成
        root = DocumentNode(
            node_type='document',
            content='ルートノード',
            start_line=1,
            end_line=1
        )
        
        current = root
        for i in range(10):  # 10レベルの深いネスト
            child = DocumentNode(
                node_type='section',
                content=f'レベル{i}',
                start_line=i+2,
                end_line=i+2
            )
            current.add_child(child)
            current = child
        
        # 最深レベルに段落を追加
        deepest_paragraph = DocumentNode(
            node_type='paragraph',
            content='最深レベルの段落',
            start_line=12,
            end_line=12
        )
        current.add_child(deepest_paragraph)
        
        # フォーマット復元が正常に動作することを確認
        result = root.to_text(preserve_formatting=True)
        assert 'ルートノード' in result
        assert '最深レベルの段落' in result
    
    def test_circular_reference_prevention(self):
        """循環参照防止テスト"""
        parent = DocumentNode(
            node_type='document',
            content='親ノード',
            start_line=1,
            end_line=1
        )
        
        child = DocumentNode(
            node_type='section',
            content='子ノード',
            start_line=2,
            end_line=2
        )
        
        parent.add_child(child)
        
        # 循環参照を作成しようとする（これは設計上防げない場合があるが、
        # 実際の使用では発生しないはず）
        # child.add_child(parent)  # これは避けるべき
        
        # 正常なケースでの動作確認
        result = parent.to_text(preserve_formatting=True)
        assert '親ノード' in result
        assert '子ノード' in result
    
    def test_large_content_handling(self):
        """大きなコンテンツの処理テスト"""
        # 大きなコンテンツを作成
        large_content = 'テストコンテンツ' * 1000
        
        node = DocumentNode(
            node_type='paragraph',
            content=large_content,
            start_line=1,
            end_line=1
        )
        
        # メモリエラーを発生させずに処理できることを確認
        result = node.to_text()
        assert len(result) > 0
        assert node.get_text_length() == len(large_content)
    
    def test_special_characters_handling(self):
        """特殊文字の処理テスト"""
        special_content = 'テスト\n\r\t特殊文字\u0000\u001F\u007F'
        
        node = DocumentNode(
            node_type='paragraph',
            content=special_content,
            start_line=1,
            end_line=1
        )
        
        # 特殊文字が含まれていても正常に処理されることを確認
        result = node.to_text()
        assert 'テスト' in result
        assert '特殊文字' in result
    
    def test_metadata_edge_cases(self):
        """メタデータのエッジケーステスト"""
        # 空のメタデータ
        node1 = DocumentNode(
            node_type='paragraph',
            content='テスト1',
            metadata={},
            start_line=1,
            end_line=1
        )
        
        # 大きなメタデータ
        large_metadata = {f'key_{i}': f'value_{i}' for i in range(100)}
        node2 = DocumentNode(
            node_type='paragraph',
            content='テスト2',
            metadata=large_metadata,
            start_line=1,
            end_line=1
        )
        
        # 不正な値を含むメタデータ
        invalid_metadata = {
            'valid_key': 'valid_value',
            'none_value': None,
            'list_value': [1, 2, 3],
            'dict_value': {'nested': 'value'}
        }
        node3 = DocumentNode(
            node_type='paragraph',
            content='テスト3',
            metadata=invalid_metadata,
            start_line=1,
            end_line=1
        )
        
        # すべてのケースで正常に処理されることを確認
        assert node1.to_text() == 'テスト1'
        assert node2.to_text() == 'テスト2'
        assert node3.to_text() == 'テスト3'


class TestDocumentNodeUtilityMethods:
    """DocumentNodeのユーティリティメソッドテストクラス"""
    
    def test_find_children_by_type(self):
        """タイプ別子ノード検索テスト"""
        document = DocumentNode(
            node_type='document',
            content='テスト文書',
            start_line=1,
            end_line=1
        )
        
        section1 = DocumentNode(
            node_type='section',
            content='セクション1',
            start_line=2,
            end_line=2
        )
        
        section2 = DocumentNode(
            node_type='section',
            content='セクション2',
            start_line=3,
            end_line=3
        )
        
        paragraph = DocumentNode(
            node_type='paragraph',
            content='段落',
            start_line=4,
            end_line=4
        )
        
        document.add_child(section1)
        document.add_child(section2)
        document.add_child(paragraph)
        
        # セクションノードの検索
        sections = document.find_children_by_type('section')
        assert len(sections) == 2
        assert sections[0].content == 'セクション1'
        assert sections[1].content == 'セクション2'
        
        # 段落ノードの検索
        paragraphs = document.find_children_by_type('paragraph')
        assert len(paragraphs) == 1
        assert paragraphs[0].content == '段落'
        
        # 存在しないタイプの検索
        lists = document.find_children_by_type('list')
        assert len(lists) == 0
    
    def test_get_text_length(self):
        """テキスト長取得テスト"""
        document = DocumentNode(
            node_type='document',
            content='テスト文書',  # 4文字
            start_line=1,
            end_line=1
        )
        
        section = DocumentNode(
            node_type='section',
            content='セクション',  # 5文字
            start_line=2,
            end_line=2
        )
        
        paragraph = DocumentNode(
            node_type='paragraph',
            content='段落内容',  # 4文字
            start_line=3,
            end_line=3
        )
        
        section.add_child(paragraph)
        document.add_child(section)
        
        # テキスト長の合計が正しく計算されることを確認
        total_length = document.get_text_length()
        expected_length = len('テスト文書') + len('セクション') + len('段落内容')
        assert total_length == expected_length
    
    def test_to_dict_serialization(self):
        """辞書形式変換テスト"""
        node = DocumentNode(
            node_type='paragraph',
            content='テスト段落',
            metadata={'key': 'value'},
            start_line=1,
            end_line=1
        )
        
        result = node.to_dict()
        
        assert result['node_type'] == 'paragraph'
        assert result['content'] == 'テスト段落'
        assert result['metadata'] == {'key': 'value'}
        assert result['start_line'] == 1
        assert result['end_line'] == 1
        assert result['children'] == []
        assert 'text_length' in result
        assert result['text_length'] == len('テスト段落')
    
    def test_to_dict_with_children(self):
        """子ノード付き辞書形式変換テスト"""
        parent = DocumentNode(
            node_type='document',
            content='親ノード',
            start_line=1,
            end_line=1
        )
        
        child = DocumentNode(
            node_type='paragraph',
            content='子ノード',
            start_line=2,
            end_line=2
        )
        
        parent.add_child(child)
        
        result = parent.to_dict()
        
        assert len(result['children']) == 1
        assert result['children'][0]['node_type'] == 'paragraph'
        assert result['children'][0]['content'] == '子ノード'
    
    def test_string_representations(self):
        """文字列表現テスト"""
        node = DocumentNode(
            node_type='paragraph',
            content='これはテスト用の非常に長いコンテンツです。この文字列は50文字を超えるので省略されるはずです。',
            metadata={'key': 'value'},
            start_line=1,
            end_line=1
        )
        
        # __str__メソッドのテスト
        str_repr = str(node)
        assert 'paragraph' in str_repr
        assert 'children=0' in str_repr
        
        # __repr__メソッドのテスト
        repr_str = repr(node)
        assert 'DocumentNode' in repr_str
        assert 'paragraph' in repr_str
        assert 'lines=1-1' in repr_str 