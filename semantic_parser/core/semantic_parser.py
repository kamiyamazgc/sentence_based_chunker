"""
SemanticDocumentParser - 構造化文書のセマンティック解析エンジン

このモジュールは文書を構造化し、DocumentNodeの階層構造を生成します。
フェーズ2: 構造解析エンジン開発
- 文書の構造認識機能
- セマンティックな単位での解析
- 階層構造の自動生成
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional, Union
import re
from dataclasses import dataclass
from .document_node import DocumentNode


@dataclass
class DocumentStructureConfig:
    """文書構造設定クラス
    
    文書構造の解析設定を管理します。
    """
    # 見出し認識設定
    header_patterns: Optional[List[str]] = None
    max_header_level: int = 6
    
    # リスト認識設定
    list_patterns: Optional[Dict[str, str]] = None
    max_list_depth: int = 10
    
    # 段落認識設定
    paragraph_min_length: int = 10
    paragraph_break_patterns: Optional[List[str]] = None
    
    # 構造境界認識設定
    section_boundary_patterns: Optional[List[str]] = None
    
    def __post_init__(self):
        """設定の初期化"""
        if self.header_patterns is None:
            self.header_patterns = [
                r'^#{1,6}\s+',  # Markdown見出し
                r'^\d+\.\s+',   # 番号付き見出し
                r'^[A-Z][^.]*:$'  # 大文字始まりのコロン終了
            ]
        
        if self.list_patterns is None:
            self.list_patterns = {
                'unordered': r'^\s*[-*+]\s+',
                'ordered': r'^\s*\d+\.\s+',
                'nested': r'^\s{2,}[-*+]\s+'
            }
        
        if self.paragraph_break_patterns is None:
            self.paragraph_break_patterns = [
                r'^\s*$',  # 空行
                r'^#{1,6}\s+',  # 見出し
                r'^\s*[-*+]\s+',  # リスト
                r'^\s*\d+\.\s+'  # 番号付きリスト
            ]
        
        if self.section_boundary_patterns is None:
            self.section_boundary_patterns = [
                r'^#{1,6}\s+',  # Markdown見出し
                r'^\d+\.\s+[A-Z]',  # 番号付きセクション
                r'^[A-Z][^.]*:$'  # 大文字始まりのコロン終了
            ]


@dataclass
class StructuredSentence:
    """構造化された文データクラス
    
    前処理済みの文データを表現します。
    """
    text: str
    structure_info: str  # 'header', 'list_item', 'paragraph', 'blank'
    line_number: int
    indent_level: int = 0
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class SemanticDocumentParser:
    """セマンティック文書パーサー
    
    構造化された文のリストを受け取り、DocumentNodeの階層構造を生成します。
    """
    
    def __init__(self, config: Optional[DocumentStructureConfig] = None):
        """初期化
        
        Args:
            config: 文書構造設定
        """
        self.config = config if config is not None else DocumentStructureConfig()
        self._current_section_stack: List[DocumentNode] = []
        self._current_list_stack: List[DocumentNode] = []
        self._line_number = 0
    
    def parse(self, structured_sentences: List[StructuredSentence]) -> DocumentNode:
        """構造化された文リストから文書ノードを生成
        
        Args:
            structured_sentences: 構造化された文のリスト
            
        Returns:
            文書のルートノード
            
        Raises:
            ValueError: 不正な文構造の場合
        """
        if not structured_sentences:
            return DocumentNode(
                node_type='document',
                content='',
                start_line=0,
                end_line=0
            )
        
        # 文書ルートノードを作成
        document_node = DocumentNode(
            node_type='document',
            content=self._extract_document_title(structured_sentences),
            start_line=1,
            end_line=len(structured_sentences)
        )
        
        # 解析状態を初期化
        self._current_section_stack = []
        self._current_list_stack = []
        self._line_number = 0
        
        # 文を順次処理
        current_paragraph_sentences = []
        
        for sentence in structured_sentences:
            self._line_number = sentence.line_number
            
            try:
                if sentence.structure_info == 'header':
                    # 段落を完了してからヘッダーを処理
                    if current_paragraph_sentences:
                        paragraph_node = self._create_paragraph_node(current_paragraph_sentences)
                        self._add_node_to_current_context(paragraph_node)
                        current_paragraph_sentences = []
                    
                    # ヘッダーノードを作成
                    section_node = self._create_section_node(sentence)
                    self._add_section_to_document(document_node, section_node)
                    
                elif sentence.structure_info == 'list_item':
                    # 段落を完了してからリストアイテムを処理
                    if current_paragraph_sentences:
                        paragraph_node = self._create_paragraph_node(current_paragraph_sentences)
                        self._add_node_to_current_context(paragraph_node)
                        current_paragraph_sentences = []
                    
                    # リストアイテムノードを作成
                    list_item_node = self._create_list_item_node(sentence)
                    self._add_list_item_to_context(list_item_node, document_node)
                    
                elif sentence.structure_info == 'paragraph':
                    # 段落文を蓄積
                    current_paragraph_sentences.append(sentence)
                    
                elif sentence.structure_info == 'blank':
                    # 空行は段落の区切りとして処理
                    if current_paragraph_sentences:
                        paragraph_node = self._create_paragraph_node(current_paragraph_sentences)
                        self._add_node_to_current_context(paragraph_node)
                        current_paragraph_sentences = []
                
            except Exception as e:
                # エラーログを記録して処理を続行
                self._log_error(f"文の解析中にエラーが発生: {sentence.text[:50]}... - {e}")
                continue
        
        # 最後の段落を処理
        if current_paragraph_sentences:
            paragraph_node = self._create_paragraph_node(current_paragraph_sentences)
            self._add_node_to_current_context(paragraph_node)
        
        return document_node
    
    def _create_section_node(self, sentence: StructuredSentence) -> DocumentNode:
        """セクションノードを作成
        
        Args:
            sentence: 見出し文
            
        Returns:
            セクションノード
        """
                 header_level = self._extract_header_level(sentence.structure_info)
         header_style = self._extract_header_style(sentence.text)
         
         # 見出しテキストをクリーンアップ
         cleaned_content = self._clean_header_text(sentence.text)
         
         metadata = {
             'header_level': header_level,
             'header_style': header_style,
             'original_text': sentence.text,
             'indent_level': sentence.indent_level
         }
         if sentence.metadata:
             metadata.update(sentence.metadata)
        
        return DocumentNode(
            node_type='section',
            content=cleaned_content,
            metadata=metadata,
            start_line=sentence.line_number,
            end_line=sentence.line_number
        )
    
    def _create_list_node(self, list_type: str = 'unordered') -> DocumentNode:
        """リストノードを作成
        
        Args:
            list_type: リストタイプ ('ordered' or 'unordered')
            
        Returns:
            リストノード
        """
        metadata = {
            'list_type': list_type,
            'created_at_line': self._line_number
        }
        
        return DocumentNode(
            node_type='list',
            content='',
            metadata=metadata,
            start_line=self._line_number,
            end_line=self._line_number
        )
    
    def _create_list_item_node(self, sentence: StructuredSentence) -> DocumentNode:
        """リストアイテムノードを作成
        
        Args:
            sentence: リストアイテム文
            
        Returns:
            リストアイテムノード
        """
                 list_type = self._extract_list_type(sentence.text)
         item_number = self._extract_item_number(sentence.text)
         
         # リストアイテムテキストをクリーンアップ
         cleaned_content = self._clean_list_item_text(sentence.text)
         
         metadata = {
             'list_type': list_type,
             'item_number': item_number,
             'indent_level': sentence.indent_level,
             'original_text': sentence.text,
             'original_indent': self._extract_original_indent(sentence.text)
         }
         if sentence.metadata:
             metadata.update(sentence.metadata)
        
        return DocumentNode(
            node_type='list_item',
            content=cleaned_content,
            metadata=metadata,
            start_line=sentence.line_number,
            end_line=sentence.line_number
        )
    
    def _create_paragraph_node(self, sentences: List[StructuredSentence]) -> DocumentNode:
        """段落ノードを作成
        
        Args:
            sentences: 段落を構成する文のリスト
            
        Returns:
            段落ノード
        """
        if not sentences:
            return DocumentNode(
                node_type='paragraph',
                content='',
                start_line=self._line_number,
                end_line=self._line_number
            )
        
        # 段落テキストを結合
        paragraph_text = self._combine_paragraph_sentences(sentences)
        
        # メタデータを収集
        metadata = {
            'sentence_count': len(sentences),
            'original_line_breaks': self._extract_line_breaks(sentences),
            'indent_level': sentences[0].indent_level if sentences else 0
        }
        
        # 最初の文からメタデータを継承
        if sentences[0].metadata:
            metadata.update(sentences[0].metadata)
        
        return DocumentNode(
            node_type='paragraph',
            content=paragraph_text,
            metadata=metadata,
            start_line=sentences[0].line_number,
            end_line=sentences[-1].line_number
        )
    
    def _is_continuous_list(self, current_list: DocumentNode, sentence: StructuredSentence) -> bool:
        """連続するリストかどうかを判定
        
        Args:
            current_list: 現在のリストノード
            sentence: 判定対象の文
            
        Returns:
            連続するリストかどうか
        """
        if current_list is None:
            return False
        
        current_list_type = current_list.metadata.get('list_type', 'unordered')
        sentence_list_type = self._extract_list_type(sentence.text)
        
        # リストタイプが一致し、インデントレベルが適切な場合
        return (current_list_type == sentence_list_type and 
                sentence.indent_level <= current_list.metadata.get('max_indent_level', 0) + 1)
    
    def _extract_document_title(self, sentences: List[StructuredSentence]) -> str:
        """文書タイトルを抽出
        
        Args:
            sentences: 文のリスト
            
        Returns:
            文書タイトル
        """
        # 最初の見出しを文書タイトルとして使用
        for sentence in sentences:
            if sentence.structure_info == 'header':
                return self._clean_header_text(sentence.text)
        
        # 見出しがない場合は空文字
        return ''
    
    def _extract_header_level(self, structure_info: str) -> int:
        """見出しレベルを抽出
        
        Args:
            structure_info: 構造情報
            
        Returns:
            見出しレベル (1-6)
        """
        # 構造情報から見出しレベルを抽出
        if 'header_level' in structure_info:
            level_match = re.search(r'header_level_(\d+)', structure_info)
            if level_match:
                return min(int(level_match.group(1)), self.config.max_header_level)
        
        return 1  # デフォルトレベル
    
    def _extract_header_style(self, text: str) -> str:
        """見出しスタイルを抽出
        
        Args:
            text: 見出しテキスト
            
        Returns:
            見出しスタイル
        """
        if re.match(r'^#+\s+', text):
            return 'markdown'
        elif re.match(r'^\d+\.\s+', text):
            return 'numbered'
        else:
            return 'plain'
    
    def _extract_list_type(self, text: str) -> str:
        """リストタイプを抽出
        
        Args:
            text: リストアイテムテキスト
            
        Returns:
            リストタイプ ('ordered' or 'unordered')
        """
        # 番号付きリストの判定
        if re.match(r'^\s*\d+\.\s+', text):
            return 'ordered'
        
        # 順序なしリストの判定
        if re.match(r'^\s*[-*+]\s+', text):
            return 'unordered'
        
        return 'unordered'  # デフォルト
    
    def _extract_item_number(self, text: str) -> int:
        """リストアイテム番号を抽出
        
        Args:
            text: リストアイテムテキスト
            
        Returns:
            アイテム番号
        """
        match = re.match(r'^\s*(\d+)\.\s+', text)
        if match:
            return int(match.group(1))
        
        return 1  # デフォルト番号
    
    def _extract_original_indent(self, text: str) -> str:
        """元のインデントを抽出
        
        Args:
            text: テキスト
            
        Returns:
            元のインデント文字列
        """
        match = re.match(r'^(\s*)', text)
        if match:
            return match.group(1)
        
        return ''
    
    def _clean_header_text(self, text: str) -> str:
        """見出しテキストをクリーンアップ
        
        Args:
            text: 見出しテキスト
            
        Returns:
            クリーンアップされたテキスト
        """
        # Markdown記号を除去
        text = re.sub(r'^#+\s*', '', text)
        # 番号を除去
        text = re.sub(r'^\d+\.\s*', '', text)
        # 前後の空白を除去
        text = text.strip()
        
        return text
    
    def _clean_list_item_text(self, text: str) -> str:
        """リストアイテムテキストをクリーンアップ
        
        Args:
            text: リストアイテムテキスト
            
        Returns:
            クリーンアップされたテキスト
        """
        # リストマーカーを除去
        text = re.sub(r'^\s*[-*+]\s*', '', text)
        text = re.sub(r'^\s*\d+\.\s*', '', text)
        # 前後の空白を除去
        text = text.strip()
        
        return text
    
    def _combine_paragraph_sentences(self, sentences: List[StructuredSentence]) -> str:
        """段落文を結合
        
        Args:
            sentences: 段落を構成する文のリスト
            
        Returns:
            結合された段落テキスト
        """
        if not sentences:
            return ''
        
        # 文を結合し、改行を保持
        combined_text = []
        for sentence in sentences:
            combined_text.append(sentence.text.strip())
        
        return '\n'.join(combined_text)
    
    def _extract_line_breaks(self, sentences: List[StructuredSentence]) -> List[int]:
        """改行位置を抽出
        
        Args:
            sentences: 文のリスト
            
        Returns:
            改行位置のリスト
        """
        line_breaks = []
        for sentence in sentences:
            if '\n' in sentence.text:
                line_breaks.append(sentence.line_number)
        
        return line_breaks
    
    def _add_section_to_document(self, document_node: DocumentNode, section_node: DocumentNode):
        """セクションを文書に追加
        
        Args:
            document_node: 文書ノード
            section_node: セクションノード
        """
        header_level = section_node.metadata.get('header_level', 1)
        
        # セクションスタックを調整
        self._adjust_section_stack(header_level)
        
        # 適切な親ノードに追加
        if self._current_section_stack:
            parent_section = self._current_section_stack[-1]
            parent_section.add_child(section_node)
        else:
            document_node.add_child(section_node)
        
        # セクションスタックに追加
        self._current_section_stack.append(section_node)
    
    def _add_list_item_to_context(self, list_item_node: DocumentNode, document_node: DocumentNode):
        """リストアイテムを適切なコンテキストに追加
        
        Args:
            list_item_node: リストアイテムノード
            document_node: 文書ノード
        """
        list_type = list_item_node.metadata.get('list_type', 'unordered')
        indent_level = list_item_node.metadata.get('indent_level', 0)
        
        # 適切なリストノードを検索または作成
        current_list = self._find_or_create_list_node(list_type, indent_level)
        
        # リストアイテムを追加
        current_list.add_child(list_item_node)
        
        # 現在のコンテキストにリストを追加（初回のみ）
        if current_list not in self._get_current_context_children():
            self._add_node_to_current_context(current_list)
    
    def _add_node_to_current_context(self, node: DocumentNode):
        """ノードを現在のコンテキストに追加
        
        Args:
            node: 追加するノード
        """
        if self._current_section_stack:
            # 現在のセクションに追加
            current_section = self._current_section_stack[-1]
            current_section.add_child(node)
        else:
            # 文書直下に追加 - 適切な親ノードを見つける必要がある
            # この場合、呼び出し元で適切に処理する必要がある
            pass
    
    def _adjust_section_stack(self, new_header_level: int):
        """セクションスタックを新しい見出しレベルに調整
        
        Args:
            new_header_level: 新しい見出しレベル
        """
        # 新しいレベル以上のセクションをスタックから削除
        while (self._current_section_stack and 
               self._current_section_stack[-1].metadata.get('header_level', 1) >= new_header_level):
            self._current_section_stack.pop()
        
        # リストスタックもクリア（新しいセクションではリストは継続しない）
        self._current_list_stack = []
    
    def _find_or_create_list_node(self, list_type: str, indent_level: int) -> DocumentNode:
        """適切なリストノードを検索または作成
        
        Args:
            list_type: リストタイプ
            indent_level: インデントレベル
            
        Returns:
            リストノード
        """
        # 現在のリストスタックから適切なリストを検索
        for list_node in reversed(self._current_list_stack):
            if (list_node.metadata.get('list_type') == list_type and 
                list_node.metadata.get('indent_level', 0) == indent_level):
                return list_node
        
        # 適切なリストが見つからない場合は新しく作成
        new_list = self._create_list_node(list_type)
        new_list.metadata['indent_level'] = indent_level
        
        # リストスタックに追加
        self._current_list_stack.append(new_list)
        
        return new_list
    
    def _get_current_context_children(self) -> List[DocumentNode]:
        """現在のコンテキストの子ノードを取得
        
        Returns:
            現在のコンテキストの子ノードリスト
        """
        if self._current_section_stack:
            return self._current_section_stack[-1].children
        else:
            return []  # 文書レベルの場合は別途処理が必要
    
    def _log_error(self, message: str) -> None:
        """エラーログの出力
        
        Args:
            message: エラーメッセージ
        """
        # 実際の実装では適切なロガーを使用
        print(f"SemanticParser ERROR: {message}")
    
    def _log_warning(self, message: str) -> None:
        """警告ログの出力
        
        Args:
            message: 警告メッセージ
        """
        # 実際の実装では適切なロガーを使用
        print(f"SemanticParser WARNING: {message}")