#!/usr/bin/env python3
"""選択されたテキストをsemantic_parserで処理するテスト（最終版）"""

import sys
import os
sys.path.append('.')

from semantic_parser.core.semantic_parser import SemanticDocumentParser, DocumentStructureConfig, StructuredSentence
from semantic_parser.core.document_node import DocumentNode


def create_structured_sentences_from_text(text: str) -> list[StructuredSentence]:
    """テキストから構造化された文のリストを作成（改善版）"""
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
            # Markdown見出し
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
        elif line.isupper() and len(line) < 50 and not line.endswith('.'):
            # 大文字の短い行で句点で終わらないものは見出しとして扱う
            structured_sentences.append(StructuredSentence(
                text=f"# {line}",  # Markdown形式に変換
                structure_info="header",
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


def print_document_structure(node: DocumentNode, level: int = 0):
    """文書構造を表示"""
    indent = "  " * level
    content_preview = node.content[:50] + "..." if len(node.content) > 50 else node.content
    print(f"{indent}├── {node.node_type}: {content_preview}")
    
    for child in node.children:
        print_document_structure(child, level + 1)


def main():
    """メイン処理"""
    print("=== 選択されたテキストの処理（最終版）===")
    
    # テキストを読み込み
    with open('test_sample_2.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    
    print("【入力テキスト】")
    print(text)
    print("\n" + "="*50 + "\n")
    
    # 構造化された文のリストを作成
    structured_sentences = create_structured_sentences_from_text(text)
    
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
        
        print("【解析結果 - 階層構造】")
        print_document_structure(document_node)
        print("\n" + "="*50 + "\n")
        
        print("【復元されたテキスト】")
        restored_text = document_node.to_text(preserve_formatting=True)
        print(restored_text)
        print("\n" + "="*50 + "\n")
        
        print("【JSON形式での出力】")
        import json
        document_dict = document_node.to_dict()
        print(json.dumps(document_dict, indent=2, ensure_ascii=False))
        
        print("\n" + "="*50 + "\n")
        print("【統計情報】")
        print(f"文書タイトル: '{document_node.content}'")
        print(f"文書の子要素数: {len(document_node.children)}")
        
        # 各セクションの詳細
        for i, child in enumerate(document_node.children):
            print(f"セクション{i+1}: {child.node_type} - '{child.content}'")
            print(f"  子要素数: {len(child.children)}")
            for j, grandchild in enumerate(child.children):
                print(f"    子要素{j+1}: {grandchild.node_type} - '{grandchild.content[:30]}...'")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 