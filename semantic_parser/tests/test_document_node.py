"""
DocumentNodeクラスの基本機能テスト

フェーズ1 Day 1-2の実装に対応する基本的なテストケースを提供します。
"""

import pytest
from semantic_parser.core.document_node import DocumentNode


class TestDocumentNode:
    """DocumentNodeクラスのテストケース"""

    def test_basic_creation(self):
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
        assert len(node.children) == 0
        assert isinstance(node.metadata, dict)
    
    def test_add_child(self):
        """子ノード追加テスト"""
        parent = DocumentNode(
            node_type='section',
            content='親セクション',
            start_line=1,
            end_line=5
        )
        
        child = DocumentNode(
            node_type='paragraph',
            content='子段落',
            start_line=2,
            end_line=3
        )
        
        parent.add_child(child)
        
        assert len(parent.children) == 1
        assert parent.children[0] == child
        assert parent.start_line == 1  # 既存の開始行が保持される
        assert parent.end_line == 5   # 既存の終了行が保持される
    
    def test_add_child_line_number_update(self):
        """子ノード追加時の行番号更新テスト"""
        parent = DocumentNode(
            node_type='section',
            content='親セクション',
            start_line=0,  # 未設定
            end_line=0     # 未設定
        )
        
        child = DocumentNode(
            node_type='paragraph',
            content='子段落',
            start_line=5,
            end_line=10
        )
        
        parent.add_child(child)
        
        assert parent.start_line == 5
        assert parent.end_line == 10
    
    def test_add_child_invalid_type(self):
        """不正な子ノード追加エラーテスト"""
        parent = DocumentNode(
            node_type='section',
            content='親セクション'
        )
        
        with pytest.raises(TypeError, match="子ノードはDocumentNodeインスタンスである必要があります"):
            parent.add_child("不正なオブジェクト")
    
    def test_find_children_by_type(self):
        """タイプ別子ノード検索テスト"""
        root = DocumentNode(
            node_type='document',
            content='ルート'
        )
        
        section1 = DocumentNode(node_type='section', content='セクション1')
        section2 = DocumentNode(node_type='section', content='セクション2')
        paragraph = DocumentNode(node_type='paragraph', content='段落')
        
        root.add_child(section1)
        root.add_child(section2)
        root.add_child(paragraph)
        
        sections = root.find_children_by_type('section')
        paragraphs = root.find_children_by_type('paragraph')
        
        assert len(sections) == 2
        assert len(paragraphs) == 1
        assert sections[0] == section1
        assert sections[1] == section2
        assert paragraphs[0] == paragraph
    
    def test_find_children_by_type_recursive(self):
        """再帰的な子ノード検索テスト"""
        root = DocumentNode(node_type='document', content='ルート')
        section = DocumentNode(node_type='section', content='セクション')
        paragraph = DocumentNode(node_type='paragraph', content='段落')
        
        root.add_child(section)
        section.add_child(paragraph)
        
        paragraphs = root.find_children_by_type('paragraph')
        
        assert len(paragraphs) == 1
        assert paragraphs[0] == paragraph
    
    def test_get_text_length(self):
        """テキスト長取得テスト"""
        parent = DocumentNode(
            node_type='section',
            content='親コンテンツ'  # 6文字
        )
        
        child = DocumentNode(
            node_type='paragraph',
            content='子コンテンツ'  # 5文字
        )
        
        parent.add_child(child)
        
        assert parent.get_text_length() == 11  # 6 + 5
    
    def test_to_dict(self):
        """辞書変換テスト"""
        parent = DocumentNode(
            node_type='section',
            content='親セクション',
            start_line=1,
            end_line=5
        )
        parent.metadata['header_level'] = 2
        
        child = DocumentNode(
            node_type='paragraph',
            content='子段落',
            start_line=3,
            end_line=4
        )
        
        parent.add_child(child)
        
        dict_result = parent.to_dict()
        
        assert dict_result['node_type'] == 'section'
        assert dict_result['content'] == '親セクション'
        assert dict_result['start_line'] == 1
        assert dict_result['end_line'] == 5
        assert dict_result['metadata']['header_level'] == 2
        assert len(dict_result['children']) == 1
        assert dict_result['children'][0]['node_type'] == 'paragraph'
        assert dict_result['text_length'] == 9  # 親5文字 + 子3文字
    
    def test_to_text_paragraph(self):
        """段落のテキストフォーマットテスト"""
        node = DocumentNode(
            node_type='paragraph',
            content='これは段落です'
        )
        
        assert node.to_text() == 'これは段落です'
        assert node.to_text(preserve_formatting=False) == 'これは段落です'
    
    def test_to_text_list_item(self):
        """リストアイテムのテキストフォーマットテスト"""
        node = DocumentNode(
            node_type='list_item',
            content='リストアイテム'
        )
        node.metadata['indent_level'] = 1
        node.metadata['list_type'] = 'unordered'
        
        expected = '  - リストアイテム'
        assert node.to_text() == expected
    
    def test_to_text_list_item_ordered(self):
        """順序付きリストアイテムのテキストフォーマットテスト"""
        node = DocumentNode(
            node_type='list_item',
            content='順序付きアイテム'
        )
        node.metadata['indent_level'] = 0
        node.metadata['list_type'] = 'ordered'
        
        expected = '1. 順序付きアイテム'
        assert node.to_text() == expected
    
    def test_to_text_list(self):
        """リストのテキストフォーマットテスト"""
        list_node = DocumentNode(
            node_type='list',
            content=''
        )
        
        item1 = DocumentNode(
            node_type='list_item',
            content='アイテム1'
        )
        item1.metadata['indent_level'] = 0
        item1.metadata['list_type'] = 'unordered'
        
        item2 = DocumentNode(
            node_type='list_item',
            content='アイテム2'
        )
        item2.metadata['indent_level'] = 0
        item2.metadata['list_type'] = 'unordered'
        
        list_node.add_child(item1)
        list_node.add_child(item2)
        
        expected = '- アイテム1\n- アイテム2'
        assert list_node.to_text() == expected
    
    def test_to_text_section(self):
        """セクションのテキストフォーマットテスト"""
        section = DocumentNode(
            node_type='section',
            content='# セクション見出し'
        )
        
        paragraph = DocumentNode(
            node_type='paragraph',
            content='段落コンテンツ'
        )
        
        section.add_child(paragraph)
        
        expected = '# セクション見出し\n段落コンテンツ'
        assert section.to_text() == expected
    
    def test_to_text_document(self):
        """文書のテキストフォーマットテスト"""
        document = DocumentNode(
            node_type='document',
            content='文書タイトル'
        )
        
        section = DocumentNode(
            node_type='section',
            content='# セクション'
        )
        
        paragraph = DocumentNode(
            node_type='paragraph',
            content='段落テキスト'
        )
        
        section.add_child(paragraph)
        document.add_child(section)
        
        expected = '文書タイトル\n# セクション\n段落テキスト'
        assert document.to_text() == expected
    
    def test_str_representation(self):
        """文字列表現テスト"""
        node = DocumentNode(
            node_type='paragraph',
            content='とても長いコンテンツテキストですがこれは省略されるでしょう'
        )
        
        str_repr = str(node)
        assert 'DocumentNode' in str_repr
        assert 'paragraph' in str_repr
        assert 'children=0' in str_repr
    
    def test_repr_representation(self):
        """開発者向け文字列表現テスト"""
        node = DocumentNode(
            node_type='section',
            content='セクションコンテンツ',
            start_line=5,
            end_line=10
        )
        node.metadata['level'] = 2
        
        repr_str = repr(node)
        assert 'DocumentNode' in repr_str
        assert 'section' in repr_str
        assert 'lines=5-10' in repr_str
        assert 'level' in repr_str