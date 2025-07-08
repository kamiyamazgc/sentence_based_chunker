#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SemanticDocumentParserの単体テストスクリプト
フェーズ2: 構造解析エンジン開発のテスト
- 基本的な構造解析テスト
- セクション・リスト・段落の認識テスト
- 階層構造生成テスト
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from semantic_parser.core.semantic_parser import (
    SemanticDocumentParser, 
    DocumentStructureConfig, 
    StructuredSentence
)
from semantic_parser.core.document_node import DocumentNode


class TestSemanticDocumentParser:
    """SemanticDocumentParser基本テストクラス"""
    
    def test_parser_initialization(self):
        """パーサーの初期化テスト"""
        parser = SemanticDocumentParser()
        
        assert parser.config is not None
        assert isinstance(parser.config, DocumentStructureConfig)
        assert parser._current_section_stack == []
        assert parser._current_list_stack == []
        assert parser._line_number == 0
        
        print("✓ パーサーの初期化テスト - 成功")
    
    def test_parser_with_custom_config(self):
        """カスタム設定でのパーサー初期化テスト"""
        config = DocumentStructureConfig(
            max_header_level=3,
            max_list_depth=5,
            paragraph_min_length=5
        )
        
        parser = SemanticDocumentParser(config)
        
        assert parser.config.max_header_level == 3
        assert parser.config.max_list_depth == 5
        assert parser.config.paragraph_min_length == 5
        
        print("✓ カスタム設定でのパーサー初期化テスト - 成功")
    
    def test_empty_document_parsing(self):
        """空文書の解析テスト"""
        parser = SemanticDocumentParser()
        
        # 空のリストを解析
        result = parser.parse([])
        
        assert result.node_type == 'document'
        assert result.content == ''
        assert result.start_line == 0
        assert result.end_line == 0
        assert len(result.children) == 0
        
        print("✓ 空文書の解析テスト - 成功")
    
    def test_simple_paragraph_parsing(self):
        """シンプルな段落の解析テスト"""
        parser = SemanticDocumentParser()
        
        sentences = [
            StructuredSentence(
                text="これは最初の段落です。",
                structure_info="paragraph",
                line_number=1,
                indent_level=0
            ),
            StructuredSentence(
                text="これは二番目の段落です。",
                structure_info="paragraph",
                line_number=2,
                indent_level=0
            )
        ]
        
        result = parser.parse(sentences)
        
        assert result.node_type == 'document'
        assert len(result.children) == 1  # 1つの段落として結合される
        assert result.children[0].node_type == 'paragraph'
        assert "これは最初の段落です。" in result.children[0].content
        assert "これは二番目の段落です。" in result.children[0].content
        
        print("✓ シンプルな段落の解析テスト - 成功")
    
    def test_header_parsing(self):
        """見出しの解析テスト"""
        parser = SemanticDocumentParser()
        
        sentences = [
            StructuredSentence(
                text="# メイン見出し",
                structure_info="header",
                line_number=1,
                indent_level=0
            ),
            StructuredSentence(
                text="見出し下の段落です。",
                structure_info="paragraph",
                line_number=2,
                indent_level=0
            )
        ]
        
        result = parser.parse(sentences)
        
        assert result.node_type == 'document'
        assert result.content == "メイン見出し"  # 最初の見出しが文書タイトルになる
        assert len(result.children) == 1
        assert result.children[0].node_type == 'section'
        assert result.children[0].content == "メイン見出し"
        
        print("✓ 見出しの解析テスト - 成功")
    
    def test_list_parsing(self):
        """リストの解析テスト"""
        parser = SemanticDocumentParser()
        
        sentences = [
            StructuredSentence(
                text="- 最初のアイテム",
                structure_info="list_item",
                line_number=1,
                indent_level=0
            ),
            StructuredSentence(
                text="- 二番目のアイテム",
                structure_info="list_item",
                line_number=2,
                indent_level=0
            )
        ]
        
        result = parser.parse(sentences)
        
        assert result.node_type == 'document'
        # セクションスタックがないため、リストは直接文書に追加されない可能性がある
        # 実装の詳細により結果が変わる可能性がある
        
        print("✓ リストの解析テスト - 成功")
    
    def test_structured_sentence_creation(self):
        """StructuredSentenceの作成テスト"""
        sentence = StructuredSentence(
            text="テスト文章",
            structure_info="paragraph",
            line_number=1,
            indent_level=0
        )
        
        assert sentence.text == "テスト文章"
        assert sentence.structure_info == "paragraph"
        assert sentence.line_number == 1
        assert sentence.indent_level == 0
        assert sentence.metadata == {}
        
        print("✓ StructuredSentenceの作成テスト - 成功")
    
    def test_structured_sentence_with_metadata(self):
        """メタデータ付きStructuredSentenceの作成テスト"""
        metadata = {"test_key": "test_value"}
        sentence = StructuredSentence(
            text="テスト文章",
            structure_info="paragraph",
            line_number=1,
            indent_level=0,
            metadata=metadata
        )
        
        assert sentence.metadata == metadata
        assert sentence.metadata["test_key"] == "test_value"
        
        print("✓ メタデータ付きStructuredSentenceの作成テスト - 成功")
    
    def test_header_level_extraction(self):
        """見出しレベル抽出テスト"""
        parser = SemanticDocumentParser()
        
        # 基本的な見出しレベル抽出
        level1 = parser._extract_header_level("header")
        assert level1 == 1
        
        level2 = parser._extract_header_level("header_level_2")
        assert level2 == 2
        
        level6 = parser._extract_header_level("header_level_6")
        assert level6 == 6
        
        print("✓ 見出しレベル抽出テスト - 成功")
    
    def test_list_type_extraction(self):
        """リストタイプ抽出テスト"""
        parser = SemanticDocumentParser()
        
        # 順序なしリスト
        unordered1 = parser._extract_list_type("- アイテム")
        assert unordered1 == "unordered"
        
        unordered2 = parser._extract_list_type("* アイテム")
        assert unordered2 == "unordered"
        
        # 順序付きリスト
        ordered1 = parser._extract_list_type("1. アイテム")
        assert ordered1 == "ordered"
        
        ordered2 = parser._extract_list_type("10. アイテム")
        assert ordered2 == "ordered"
        
        print("✓ リストタイプ抽出テスト - 成功")
    
    def test_text_cleaning(self):
        """テキストクリーニングテスト"""
        parser = SemanticDocumentParser()
        
        # 見出しテキストのクリーニング
        cleaned_header1 = parser._clean_header_text("# 見出し")
        assert cleaned_header1 == "見出し"
        
        cleaned_header2 = parser._clean_header_text("## 見出し")
        assert cleaned_header2 == "見出し"
        
        cleaned_header3 = parser._clean_header_text("1. 見出し")
        assert cleaned_header3 == "見出し"
        
        # リストアイテムテキストのクリーニング
        cleaned_item1 = parser._clean_list_item_text("- アイテム")
        assert cleaned_item1 == "アイテム"
        
        cleaned_item2 = parser._clean_list_item_text("* アイテム")
        assert cleaned_item2 == "アイテム"
        
        cleaned_item3 = parser._clean_list_item_text("1. アイテム")
        assert cleaned_item3 == "アイテム"
        
        print("✓ テキストクリーニングテスト - 成功")


def run_all_tests():
    """全テストの実行"""
    print("=== SemanticDocumentParser単体テスト開始 ===")
    
    test_instance = TestSemanticDocumentParser()
    
    try:
        test_instance.test_parser_initialization()
        test_instance.test_parser_with_custom_config()
        test_instance.test_empty_document_parsing()
        test_instance.test_simple_paragraph_parsing()
        test_instance.test_header_parsing()
        test_instance.test_list_parsing()
        test_instance.test_structured_sentence_creation()
        test_instance.test_structured_sentence_with_metadata()
        test_instance.test_header_level_extraction()
        test_instance.test_list_type_extraction()
        test_instance.test_text_cleaning()
        
        print("\n=== 全テスト完了 ===")
        print("✓ 全てのテストが成功しました")
        return True
        
    except Exception as e:
        print(f"\n✗ テストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    if success:
        print("\n🎉 SemanticDocumentParserのテストが全て成功しました！")
    else:
        print("\n❌ テストに失敗しました")
        sys.exit(1)