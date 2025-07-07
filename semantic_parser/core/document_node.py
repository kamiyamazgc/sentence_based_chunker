"""
DocumentNode - 文書の階層構造を表現するコアデータクラス

このモジュールは文書構造を階層的に表現し、
フォーマット復元機能を提供します。
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass
class DocumentNode:
    """文書の階層構造ノード
    
    文書構造を階層的に表現し、各ノードが以下の情報を保持します：
    - ノードタイプ (document, section, paragraph, list, list_item)
    - コンテンツ (実際のテキスト内容)
    - 子ノード (階層構造)
    - メタデータ (構造固有の情報)
    - 行番号範囲 (元文書での位置)
    """
    
    node_type: str  # 'document', 'section', 'paragraph', 'list', 'list_item'
    content: str
    children: List[DocumentNode] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_line: int = 0
    end_line: int = 0
    
    def to_text(self, preserve_formatting: bool = True) -> str:
        """フォーマットを保持したテキスト出力
        
        Args:
            preserve_formatting: フォーマット保持の有無
            
        Returns:
            フォーマットされたテキスト
        """
        if self.node_type == 'list':
            return self._format_list(preserve_formatting)
        elif self.node_type == 'section':
            return self._format_section(preserve_formatting)
        elif self.node_type == 'paragraph':
            return self._format_paragraph(preserve_formatting)
        elif self.node_type == 'document':
            return self._format_document(preserve_formatting)
        elif self.node_type == 'list_item':
            return self._format_list_item(preserve_formatting)
        else:
            # 不明なノードタイプの場合は基本的なフォーマット
            return self.content
    
    def add_child(self, child: DocumentNode) -> None:
        """子ノードを追加
        
        Args:
            child: 追加する子ノード
        """
        if not isinstance(child, DocumentNode):
            raise TypeError("子ノードはDocumentNodeインスタンスである必要があります")
        
        self.children.append(child)
        
        # 行番号範囲を更新
        if child.start_line > 0:
            if self.start_line == 0 or child.start_line < self.start_line:
                self.start_line = child.start_line
        if child.end_line > 0:
            if self.end_line == 0 or child.end_line > self.end_line:
                self.end_line = child.end_line
    
    def find_children_by_type(self, node_type: str) -> List[DocumentNode]:
        """指定されたタイプの子ノードを検索
        
        Args:
            node_type: 検索するノードタイプ
            
        Returns:
            マッチする子ノードのリスト
        """
        result = []
        
        # 直接の子ノードをチェック
        for child in self.children:
            if child.node_type == node_type:
                result.append(child)
        
        # 再帰的に検索
        for child in self.children:
            result.extend(child.find_children_by_type(node_type))
        
        return result
    
    def get_text_length(self) -> int:
        """ノードのテキスト長を取得
        
        Returns:
            テキスト長（文字数）
        """
        total_length = len(self.content)
        
        # 子ノードのテキスト長を加算
        for child in self.children:
            total_length += child.get_text_length()
        
        return total_length
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換（JSON出力用）
        
        Returns:
            辞書形式の表現
        """
        return {
            'node_type': self.node_type,
            'content': self.content,
            'children': [child.to_dict() for child in self.children],
            'metadata': self.metadata,
            'start_line': self.start_line,
            'end_line': self.end_line,
            'text_length': self.get_text_length()
        }
    
    def _format_list(self, preserve_formatting: bool) -> str:
        """リストのフォーマット処理
        
        Args:
            preserve_formatting: フォーマット保持の有無
            
        Returns:
            フォーマットされたリストテキスト
        """
        if not preserve_formatting:
            return self.content
        
        lines = []
        
        # リストアイテムをフォーマット
        for child in self.children:
            if child.node_type == 'list_item':
                formatted_item = child._format_list_item(preserve_formatting)
                lines.append(formatted_item)
        
        return '\n'.join(lines)
    
    def _format_section(self, preserve_formatting: bool) -> str:
        """セクションのフォーマット処理
        
        Args:
            preserve_formatting: フォーマット保持の有無
            
        Returns:
            フォーマットされたセクションテキスト
        """
        if not preserve_formatting:
            return self.content
        
        lines = []
        
        # セクションヘッダーを追加
        if self.content:
            lines.append(self.content)
        
        # 子ノードをフォーマット
        for child in self.children:
            child_text = child.to_text(preserve_formatting)
            if child_text:
                lines.append(child_text)
        
        return '\n'.join(lines)
    
    def _format_paragraph(self, preserve_formatting: bool) -> str:
        """段落のフォーマット処理
        
        Args:
            preserve_formatting: フォーマット保持の有無
            
        Returns:
            フォーマットされた段落テキスト
        """
        if not preserve_formatting:
            return self.content
        
        # 段落は基本的にコンテンツをそのまま返す
        return self.content
    
    def _format_document(self, preserve_formatting: bool) -> str:
        """文書のフォーマット処理
        
        Args:
            preserve_formatting: フォーマット保持の有無
            
        Returns:
            フォーマットされた文書テキスト
        """
        if not preserve_formatting:
            return self.content
        
        lines = []
        
        # ドキュメントレベルのコンテンツがある場合は追加
        if self.content:
            lines.append(self.content)
        
        # 子ノードをフォーマット
        for child in self.children:
            child_text = child.to_text(preserve_formatting)
            if child_text:
                lines.append(child_text)
        
        return '\n'.join(lines)
    
    def _format_list_item(self, preserve_formatting: bool) -> str:
        """リストアイテムのフォーマット処理
        
        Args:
            preserve_formatting: フォーマット保持の有無
            
        Returns:
            フォーマットされたリストアイテムテキスト
        """
        if not preserve_formatting:
            return self.content
        
        # インデントレベルを取得
        indent_level = self.metadata.get('indent_level', 0)
        list_type = self.metadata.get('list_type', 'unordered')
        
        # インデントを作成
        indent = "  " * indent_level
        
        # リストマーカーを決定
        if list_type == 'ordered':
            marker = "1."  # 簡略化（実際の番号は将来的に改良）
        else:
            marker = "-"
        
        return f"{indent}{marker} {self.content}"
    
    def __str__(self) -> str:
        """文字列表現
        
        Returns:
            読みやすい文字列表現
        """
        return f"DocumentNode(type={self.node_type}, content='{self.content[:50]}...', children={len(self.children)})"
    
    def __repr__(self) -> str:
        """開発者向け文字列表現
        
        Returns:
            詳細な文字列表現
        """
        return (f"DocumentNode(node_type='{self.node_type}', "
                f"content='{self.content[:30]}...', "
                f"children_count={len(self.children)}, "
                f"metadata={self.metadata}, "
                f"lines={self.start_line}-{self.end_line})")