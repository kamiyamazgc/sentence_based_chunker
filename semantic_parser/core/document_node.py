"""
DocumentNode - 文書の階層構造を表現するコアデータクラス

このモジュールは文書構造を階層的に表現し、
フォーマット復元機能を提供します。
Day 3-4: フォーマット復元機能の実装
- 改行・インデント保持ロジックの強化
- 各構造タイプのフォーマット処理の充実
- to_text()メソッドの改良
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import re


@dataclass
class FormatConfig:
    """フォーマット設定クラス
    
    フォーマット復元時の詳細な設定を管理します。
    """
    preserve_blank_lines: bool = True
    preserve_original_indentation: bool = True
    list_indent_size: int = 2
    section_spacing: int = 1
    preserve_line_breaks: bool = True
    normalize_whitespace: bool = False


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
    
    def to_text(self, preserve_formatting: bool = True, format_config: Optional[FormatConfig] = None) -> str:
        """フォーマットを保持したテキスト出力
        
        Args:
            preserve_formatting: フォーマット保持の有無
            format_config: 詳細なフォーマット設定
            
        Returns:
            フォーマットされたテキスト
            
        Raises:
            ValueError: 不正なノードタイプの場合
        """
        if format_config is None:
            format_config = FormatConfig()
        
        try:
            if self.node_type == 'list':
                return self._format_list(preserve_formatting, format_config)
            elif self.node_type == 'section':
                return self._format_section(preserve_formatting, format_config)
            elif self.node_type == 'paragraph':
                return self._format_paragraph(preserve_formatting, format_config)
            elif self.node_type == 'document':
                return self._format_document(preserve_formatting, format_config)
            elif self.node_type == 'list_item':
                return self._format_list_item(preserve_formatting, format_config)
            else:
                # 不明なノードタイプの場合は警告してから基本的なフォーマット
                self._log_warning(f"不明なノードタイプ: {self.node_type}")
                return self._format_unknown_node(preserve_formatting, format_config)
        except Exception as e:
            # フォーマット処理中のエラーをキャッチしてフォールバック
            self._log_error(f"フォーマット処理エラー: {e}")
            return self.content if self.content else ""
    
    def add_child(self, child: DocumentNode) -> None:
        """子ノードを追加
        
        Args:
            child: 追加する子ノード
            
        Raises:
            TypeError: 不正な型の子ノードの場合
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
    
    def _format_list(self, preserve_formatting: bool, format_config: FormatConfig) -> str:
        """リストのフォーマット処理
        
        Args:
            preserve_formatting: フォーマット保持の有無
            format_config: フォーマット設定
            
        Returns:
            フォーマットされたリストテキスト
        """
        if not preserve_formatting:
            return self.content
        
        lines = []
        
        # リストアイテムをフォーマット
        for i, child in enumerate(self.children):
            if child.node_type == 'list_item':
                formatted_item = child._format_list_item(preserve_formatting, format_config)
                lines.append(formatted_item)
                
                # リストアイテム間の空行処理
                if (i < len(self.children) - 1 and 
                    format_config.preserve_blank_lines and 
                    self._should_add_blank_line_after_item(child)):
                    lines.append("")
        
        return '\n'.join(lines)
    
    def _format_section(self, preserve_formatting: bool, format_config: FormatConfig) -> str:
        """セクションのフォーマット処理
        
        Args:
            preserve_formatting: フォーマット保持の有無
            format_config: フォーマット設定
            
        Returns:
            フォーマットされたセクションテキスト
        """
        if not preserve_formatting:
            return self.content
        
        lines = []
        
        # セクションヘッダーを追加
        if self.content:
            header_text = self._format_section_header(format_config)
            lines.append(header_text)
            
            # セクション見出し後の空行
            if format_config.preserve_blank_lines and format_config.section_spacing > 0:
                lines.extend([""] * format_config.section_spacing)
        
        # 子ノードをフォーマット
        for i, child in enumerate(self.children):
            child_text = child.to_text(preserve_formatting, format_config)
            if child_text:
                lines.append(child_text)
                
                # 子ノード間の空行処理
                if (i < len(self.children) - 1 and 
                    format_config.preserve_blank_lines and 
                    self._should_add_blank_line_after_child(child, self.children[i + 1])):
                    lines.append("")
        
        return '\n'.join(lines)
    
    def _format_paragraph(self, preserve_formatting: bool, format_config: FormatConfig) -> str:
        """段落のフォーマット処理
        
        Args:
            preserve_formatting: フォーマット保持の有無
            format_config: フォーマット設定
            
        Returns:
            フォーマットされた段落テキスト
        """
        if not preserve_formatting:
            return self.content
        
        content = self.content
        
        # 元の改行パターンを保持
        if format_config.preserve_line_breaks:
            # 元のコンテンツの改行を保持
            content = self._preserve_original_line_breaks(content)
        
        # ホワイトスペースの正規化
        if format_config.normalize_whitespace:
            content = self._normalize_whitespace(content)
        
        # インデント保持
        if format_config.preserve_original_indentation:
            content = self._preserve_paragraph_indentation(content)
        
        return content
    
    def _format_document(self, preserve_formatting: bool, format_config: FormatConfig) -> str:
        """文書のフォーマット処理
        
        Args:
            preserve_formatting: フォーマット保持の有無
            format_config: フォーマット設定
            
        Returns:
            フォーマットされた文書テキスト
        """
        if not preserve_formatting:
            return self.content
        
        lines = []
        
        # ドキュメントレベルのコンテンツがある場合は追加
        if self.content:
            lines.append(self.content)
            
            # 文書タイトル後の空行
            if format_config.preserve_blank_lines and self.children:
                lines.extend([""] * format_config.section_spacing)
        
        # 子ノードをフォーマット
        for i, child in enumerate(self.children):
            child_text = child.to_text(preserve_formatting, format_config)
            if child_text:
                lines.append(child_text)
                
                # セクション間の空行処理
                if (i < len(self.children) - 1 and 
                    format_config.preserve_blank_lines and 
                    child.node_type == 'section'):
                    lines.extend([""] * format_config.section_spacing)
        
        return '\n'.join(lines)
    
    def _format_list_item(self, preserve_formatting: bool, format_config: FormatConfig) -> str:
        """リストアイテムのフォーマット処理
        
        Args:
            preserve_formatting: フォーマット保持の有無
            format_config: フォーマット設定
            
        Returns:
            フォーマットされたリストアイテムテキスト
        """
        if not preserve_formatting:
            return self.content
        
        # インデントレベルを取得
        indent_level = self.metadata.get('indent_level', 0)
        list_type = self.metadata.get('list_type', 'unordered')
        item_number = self.metadata.get('item_number', 1)
        
        # インデントを作成
        if format_config.preserve_original_indentation:
            original_indent = self.metadata.get('original_indent', '')
            if original_indent:
                indent = original_indent
            else:
                indent = " " * (indent_level * format_config.list_indent_size)
        else:
            indent = " " * (indent_level * format_config.list_indent_size)
        
        # リストマーカーを決定
        marker = self._get_list_marker(list_type, item_number, indent_level)
        
        # コンテンツの複数行処理
        content_lines = self.content.split('\n')
        formatted_lines = []
        
        for i, line in enumerate(content_lines):
            if i == 0:
                # 最初の行はマーカー付き
                formatted_lines.append(f"{indent}{marker} {line}")
            else:
                # 続行行は適切にインデント
                continuation_indent = " " * (len(indent) + len(marker) + 1)
                formatted_lines.append(f"{continuation_indent}{line}")
        
        return '\n'.join(formatted_lines)
    
    def _format_section_header(self, format_config: FormatConfig) -> str:
        """セクションヘッダーのフォーマット処理
        
        Args:
            format_config: フォーマット設定
            
        Returns:
            フォーマットされたセクションヘッダー
        """
        header_level = self.metadata.get('header_level', 1)
        header_style = self.metadata.get('header_style', 'markdown')
        
        content = self.content
        
        # Markdownスタイルのヘッダー調整
        if header_style == 'markdown':
            # 既存の#を削除してから正しいレベルで追加
            content = re.sub(r'^#+\s*', '', content)
            content = f"{'#' * header_level} {content}"
        
        return content
    
    def _get_list_marker(self, list_type: str, item_number: int, indent_level: int) -> str:
        """リストマーカーを取得
        
        Args:
            list_type: リストタイプ ('ordered', 'unordered')
            item_number: アイテム番号
            indent_level: インデントレベル
            
        Returns:
            適切なリストマーカー
        """
        if list_type == 'ordered':
            return f"{item_number}."
        else:
            # インデントレベルによってマーカーを変更
            markers = ['-', '*', '+']
            return markers[indent_level % len(markers)]
    
    def _preserve_original_line_breaks(self, content: str) -> str:
        """元の改行パターンを保持
        
        Args:
            content: 処理対象コンテンツ
            
        Returns:
            改行が保持されたコンテンツ
        """
        # メタデータに元の改行情報があれば使用
        original_breaks = self.metadata.get('original_line_breaks', [])
        if original_breaks:
            # 元の改行位置を復元
            lines = content.split('\n')
            return '\n'.join(lines)
        
        return content
    
    def _normalize_whitespace(self, content: str) -> str:
        """ホワイトスペースを正規化
        
        Args:
            content: 処理対象コンテンツ
            
        Returns:
            正規化されたコンテンツ
        """
        # 複数のスペースを単一スペースに
        content = re.sub(r' +', ' ', content)
        # 行末のスペースを削除
        content = re.sub(r' +$', '', content, flags=re.MULTILINE)
        return content
    
    def _preserve_paragraph_indentation(self, content: str) -> str:
        """段落のインデントを保持
        
        Args:
            content: 処理対象コンテンツ
            
        Returns:
            インデントが保持されたコンテンツ
        """
        original_indent = self.metadata.get('original_indent', '')
        if original_indent:
            lines = content.split('\n')
            indented_lines = [f"{original_indent}{line}" if line.strip() else line 
                             for line in lines]
            return '\n'.join(indented_lines)
        
        return content
    
    def _should_add_blank_line_after_item(self, item: DocumentNode) -> bool:
        """リストアイテム後に空行を追加すべきかを判定
        
        Args:
            item: 判定対象のアイテム
            
        Returns:
            空行追加の可否
        """
        # メタデータに空行情報があれば使用
        return item.metadata.get('followed_by_blank_line', False)
    
    def _should_add_blank_line_after_child(self, current: DocumentNode, next_child: DocumentNode) -> bool:
        """子ノード後に空行を追加すべきかを判定
        
        Args:
            current: 現在のノード
            next_child: 次のノード
            
        Returns:
            空行追加の可否
        """
        # 異なるタイプのノード間では空行を追加
        if current.node_type != next_child.node_type:
            return True
        
        # セクション間では空行を追加
        if current.node_type == 'section':
            return True
        
        # メタデータに明示的な指定があれば従う
        return current.metadata.get('followed_by_blank_line', False)
    
    def _format_unknown_node(self, preserve_formatting: bool, format_config: FormatConfig) -> str:
        """不明なノードタイプのフォーマット処理
        
        Args:
            preserve_formatting: フォーマット保持の有無
            format_config: フォーマット設定
            
        Returns:
            基本的なフォーマットが適用されたテキスト
        """
        if not preserve_formatting:
            return self.content
        
        # 基本的なフォーマットのみ適用
        content = self.content
        
        if format_config.normalize_whitespace:
            content = self._normalize_whitespace(content)
        
        return content
    
    def _log_warning(self, message: str) -> None:
        """警告ログの出力
        
        Args:
            message: 警告メッセージ
        """
        # 実際の実装では適切なロガーを使用
        print(f"WARNING: {message}")
    
    def _log_error(self, message: str) -> None:
        """エラーログの出力
        
        Args:
            message: エラーメッセージ
        """
        # 実際の実装では適切なロガーを使用
        print(f"ERROR: {message}")
    
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