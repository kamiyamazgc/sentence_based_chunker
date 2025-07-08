#!/usr/bin/env python3
"""semantic_parserのデバッグテスト"""

import sys
import os
sys.path.append('.')

from semantic_parser.core.semantic_parser import SemanticDocumentParser, DocumentStructureConfig, StructuredSentence
from semantic_parser.core.document_node import DocumentNode


def create_structured_sentences_from_text(text: str) -> list[StructuredSentence]:
    """テキストから構造化された文のリストを作成"""
    lines = text.split('\n')
    structured_sentences = []
    
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            # 空行
            structured_sentences.append(StructuredSentence(
                text="",
                structure_info="blank",
                line_number=i,
                indent_level=0
            ))
        elif line.startswith('#'):
            # 見出し
            structured_sentences.append(StructuredSentence(
                text=line,
                structure_info="header",
                line_number=i,
                indent_level=0
            ))
        elif line.startswith('-') or line.startswith('*') or line.startswith('+'):
            # リストアイテム
            structured_sentences.append(StructuredSentence(
                text=line,
                structure_info="list_item",
                line_number=i,
                indent_level=0
            ))
        else:
            # 段落
            structured_sentences.append(StructuredSentence(
                text=line,
                structure_info="paragraph",
                line_number=i,
                indent_level=0
            ))
    
    return structured_sentences


def main():
    """メイン処理"""
    print("=== semantic_parser デバッグテスト ===")
    
    # 簡単なテストケース
    test_text = """# タイトル
これは段落です。

## セクション1
- リストアイテム1
- リストアイテム2

## セクション2
別の段落です。"""
    
    print("【テストテキスト】")
    print(test_text)
    print("\n" + "="*50 + "\n")
    
    # 構造化された文のリストを作成
    structured_sentences = create_structured_sentences_from_text(test_text)
    
    print("【構造化された文】")
    for i, sentence in enumerate(structured_sentences, 1):
        if sentence.text:
            print(f"{i:2d}. [{sentence.structure_info:10s}] {sentence.text}")
        else:
            print(f"{i:2d}. [blank      ] (空行)")
    print("\n" + "="*50 + "\n")
    
    # セマンティックパーサーで処理
    config = DocumentStructureConfig()
    parser = SemanticDocumentParser(config)
    
    try:
        document_node = parser.parse(structured_sentences)
        
        print("【解析結果】")
        print(f"文書タイトル: '{document_node.content}'")
        print(f"子要素数: {len(document_node.children)}")
        
        for i, child in enumerate(document_node.children):
            print(f"子要素{i+1}: {child.node_type} - '{child.content}'")
            print(f"  子要素の子要素数: {len(child.children)}")
        
        print("\n【復元されたテキスト】")
        restored_text = document_node.to_text(preserve_formatting=True)
        print(restored_text)
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 