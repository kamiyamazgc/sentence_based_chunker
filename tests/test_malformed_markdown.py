#!/usr/bin/env python3
"""中途半端なマークダウンの処理テスト"""

import pytest
from semantic_parser.core.document_node import DocumentNode, FormatConfig


class TestMalformedMarkdownHandling:
    """中途半端なマークダウンの処理テストクラス"""
    
    def test_incomplete_header_processing(self):
        """不完全な見出し記法の処理テスト"""
        # ==== のような不完全な見出し記法
        node = DocumentNode(
            node_type='paragraph',
            content='====',
            start_line=1,
            end_line=1
        )
        
        result = node.to_text(preserve_formatting=True)
        assert result == '===='
        
        # 警告なしで処理されることを確認
        assert '====' in result
    
    def test_mixed_list_and_paragraph(self):
        """リストと段落が混在する場合の処理テスト"""
        # リストアイテムの後に段落が続く場合
        list_item = DocumentNode(
            node_type='list_item',
            content='リストアイテム2',
            metadata={'list_type': 'unordered', 'indent_level': 0},
            start_line=1,
            end_line=1
        )
        
        # リストアイテムに段落を追加（実際には不正だが、システムが処理できることを確認）
        paragraph = DocumentNode(
            node_type='paragraph',
            content='ここに解説。',
            start_line=2,
            end_line=2
        )
        
        list_item.add_child(paragraph)
        
        result = list_item.to_text(preserve_formatting=True)
        assert 'リストアイテム2' in result
        assert 'ここに解説。' in result
    
    def test_invalid_markdown_syntax(self):
        """不正なマークダウン記法の処理テスト"""
        # 不正なノードタイプ
        invalid_node = DocumentNode(
            node_type='invalid_type',
            content='不正な記法',
            start_line=1,
            end_line=1
        )
        
        # エラーを発生させずに処理されることを確認
        result = invalid_node.to_text(preserve_formatting=True)
        assert result == '不正な記法'
    
    def test_missing_header_content(self):
        """見出し内容が空の場合の処理テスト"""
        empty_header = DocumentNode(
            node_type='section',
            content='',
            metadata={'header_level': 2, 'header_style': 'markdown'},
            start_line=1,
            end_line=1
        )
        
        result = empty_header.to_text(preserve_formatting=True)
        # 空の見出しでもエラーを発生させない
        assert result == ''
    
    def test_malformed_list_structure(self):
        """不正なリスト構造の処理テスト"""
        # リストアイテムに不正なメタデータ
        malformed_item = DocumentNode(
            node_type='list_item',
            content='不正なリストアイテム',
            metadata={'list_type': 'invalid_type', 'indent_level': -1},
            start_line=1,
            end_line=1
        )
        
        result = malformed_item.to_text(preserve_formatting=True)
        # 不正なメタデータでも処理されることを確認
        assert '不正なリストアイテム' in result
    
    def test_graceful_error_handling(self):
        """エラーハンドリングのテスト"""
        # フォーマット処理でエラーが発生する可能性のあるケース
        problematic_node = DocumentNode(
            node_type='paragraph',
            content='問題のあるコンテンツ',
            start_line=1,
            end_line=1
        )
        
        # メタデータに不正な値を設定
        problematic_node.metadata = {
            'original_indent': None,
            'invalid_key': [1, 2, 3]  # 不正な値
        }
        
        # エラーを発生させずに処理されることを確認
        result = problematic_node.to_text(preserve_formatting=True)
        assert '問題のあるコンテンツ' in result
    
    def test_special_characters_in_malformed_content(self):
        """特殊文字を含む不正なコンテンツの処理テスト"""
        special_content = '====\n\nテスト文書\n\n## セクション1\nこれは段落です。\n\n## セクション2\n- リストアイテム1\n- リストアイテム2\nここに解説。'
        
        node = DocumentNode(
            node_type='paragraph',
            content=special_content,
            start_line=1,
            end_line=1
        )
        
        result = node.to_text(preserve_formatting=True)
        # 特殊文字が含まれていても処理されることを確認
        assert '====' in result
        assert 'テスト文書' in result
        assert 'セクション1' in result
        assert 'リストアイテム1' in result


if __name__ == "__main__":
    # テスト実行
    pytest.main([__file__, "-v"]) 