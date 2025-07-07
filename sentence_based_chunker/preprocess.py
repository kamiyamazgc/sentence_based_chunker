"""前処理モジュール: 入力テキストを文単位のストリームに変換する"""

from __future__ import annotations

import pathlib
import re
from typing import Generator, List, Optional, NamedTuple
from dataclasses import dataclass

from .exceptions import FileReadError
from .config import DocumentStructureConfig

_SENT_SPLIT_REGEX = re.compile(r"(?<=[。．！？!?])")


class StructuredSentence(NamedTuple):
    """構造情報を含む文のデータ構造"""
    text: str
    line_number: int
    indent_level: int
    structure_type: str  # 'paragraph', 'header', 'list', 'table', 'code_block', 'html'
    structure_info: Optional[str] = None  # 追加の構造情報（マークダウン記法等）


@dataclass
class DocumentStructure:
    """文書構造の検出・処理クラス"""
    config: DocumentStructureConfig
    
    # 正規表現パターン
    _MARKDOWN_HEADER_PATTERN = re.compile(r'^(#{1,6})\s+(.+)$')
    _MARKDOWN_LIST_PATTERN = re.compile(r'^(\s*)([-*+]|\d+\.)\s+(.+)$')
    _MARKDOWN_TABLE_PATTERN = re.compile(r'^\s*\|.*\|\s*$')
    _MARKDOWN_CODE_BLOCK_PATTERN = re.compile(r'^```.*$')
    _HTML_TAG_PATTERN = re.compile(r'<[^>]+>')
    _INDENTATION_PATTERN = re.compile(r'^(\s*)')
    
    def __post_init__(self):
        self._in_code_block = False
        self._in_html_block = False
        self._current_table_lines = []
        
    def detect_structure_type(self, line: str, line_number: int) -> tuple[str, Optional[str]]:
        """行の構造タイプを検出する"""
        stripped_line = line.strip()
        
        # 空行の処理
        if not stripped_line:
            return 'empty', None
            
        # コードブロックの処理
        if self.config.preserve_code_blocks and self._MARKDOWN_CODE_BLOCK_PATTERN.match(stripped_line):
            self._in_code_block = not self._in_code_block
            return 'code_block', 'delimiter'
        
        if self._in_code_block:
            return 'code_block', 'content'
        
        # マークダウン記法の検出
        if self.config.detect_markdown:
            # 見出しの検出
            if self.config.preserve_headers:
                header_match = self._MARKDOWN_HEADER_PATTERN.match(stripped_line)
                if header_match:
                    level = len(header_match.group(1))
                    if self.config.min_header_level <= level <= self.config.max_header_level:
                        return 'header', f'level_{level}'
            
            # リストの検出
            if self.config.preserve_lists:
                list_match = self._MARKDOWN_LIST_PATTERN.match(line)
                if list_match:
                    indent = len(list_match.group(1))
                    marker = list_match.group(2)
                    list_type = 'ordered' if marker[0].isdigit() else 'unordered'
                    return 'list', f'{list_type}_indent_{indent}'
            
            # テーブルの検出
            if self.config.preserve_tables and self._MARKDOWN_TABLE_PATTERN.match(line):
                return 'table', 'row'
        
        # HTMLタグの検出
        if self.config.detect_html:
            html_tags = self._HTML_TAG_PATTERN.findall(stripped_line)
            if html_tags:
                return 'html', f'tags_{len(html_tags)}'
        
        # インデント構造の検出
        if self.config.detect_indentation:
            indent_match = self._INDENTATION_PATTERN.match(line)
            if indent_match:
                indent_level = len(indent_match.group(1))
                if indent_level >= self.config.list_indent_threshold:
                    return 'indented', f'level_{indent_level}'
        
        return 'paragraph', None
    
    def get_indent_level(self, line: str) -> int:
        """行のインデントレベルを取得"""
        indent_match = self._INDENTATION_PATTERN.match(line)
        return len(indent_match.group(1)) if indent_match else 0
    
    def should_preserve_as_block(self, structure_type: str) -> bool:
        """構造タイプに基づいて、ブロックとして保持すべきか判定"""
        if not self.config.preserve_structure:
            return False
        
        preserve_rules = {
            'header': self.config.preserve_headers,
            'list': self.config.preserve_lists,
            'table': self.config.preserve_tables,
            'code_block': self.config.preserve_code_blocks,
            'html': self.config.detect_html,
            'indented': self.config.detect_indentation
        }
        
        return preserve_rules.get(structure_type, False)


def _split_sentences(text: str) -> List[str]:
    """日本語用の簡易文分割"""
    sentences = [s.strip() for s in _SENT_SPLIT_REGEX.split(text) if s.strip()]
    return sentences


def _split_sentences_with_structure(text: str, structure_type: str, structure_info: Optional[str] = None) -> List[str]:
    """構造を考慮した文分割"""
    # 見出しやリストアイテムは分割しない
    if structure_type in ['header', 'list', 'table', 'code_block']:
        processed_text = text.strip()
        
        # 見出しの場合、マークダウン記法を除去
        if structure_type == 'header':
            header_match = re.match(r'^(#{1,6})\s+(.+)$', processed_text)
            if header_match:
                processed_text = header_match.group(2)
        
        # リストの場合、リストマーカーを除去
        elif structure_type == 'list':
            list_match = re.match(r'^(\s*)([-*+]|\d+\.)\s+(.+)$', processed_text)
            if list_match:
                processed_text = list_match.group(3)
        
        return [processed_text] if processed_text else []
    
    # 通常の段落は従来通り分割
    return _split_sentences(text)


def stream_sentences(path: pathlib.Path | str) -> Generator[str, None, None]:
    """ファイルを読み込み、文を逐次 yield する。

    ファイルが見つからない、または読み込みに失敗した場合は ``FileReadError`` を送出する。
    """
    path = pathlib.Path(path)
    try:
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                for sent in _split_sentences(line):
                    yield sent
    except FileNotFoundError as e:
        raise FileReadError(f"入力ファイルが見つかりません: {path}") from e
    except Exception as e:  # pylint: disable=broad-except
        raise FileReadError(f"入力ファイルの読み取り中にエラーが発生しました: {e}") from e


def stream_structured_sentences(
    path: pathlib.Path | str,
    structure_config: Optional[DocumentStructureConfig] = None
) -> Generator[StructuredSentence, None, None]:
    """文書構造を認識して、構造情報付きの文を逐次 yield する"""
    path = pathlib.Path(path)
    
    # デフォルト設定を使用
    if structure_config is None:
        structure_config = DocumentStructureConfig()
    
    document_structure = DocumentStructure(structure_config)
    
    try:
        with path.open("r", encoding="utf-8") as f:
            for line_number, line in enumerate(f, 1):
                # 構造タイプの検出
                structure_type, structure_info = document_structure.detect_structure_type(line, line_number)
                indent_level = document_structure.get_indent_level(line)
                
                # 構造を考慮した文分割
                sentences = _split_sentences_with_structure(line, structure_type, structure_info)
                
                for sentence in sentences:
                    if sentence:  # 空文字列は除外
                        yield StructuredSentence(
                            text=sentence,
                            line_number=line_number,
                            indent_level=indent_level,
                            structure_type=structure_type,
                            structure_info=structure_info
                        )
                
                # 構造的な空行も保持する場合
                if structure_config.preserve_whitespace and structure_type == 'empty':
                    yield StructuredSentence(
                        text="",
                        line_number=line_number,
                        indent_level=0,
                        structure_type='empty',
                        structure_info=None
                    )
    
    except FileNotFoundError as e:
        raise FileReadError(f"入力ファイルが見つかりません: {path}") from e
    except Exception as e:  # pylint: disable=broad-except
        raise FileReadError(f"入力ファイルの読み取り中にエラーが発生しました: {e}") from e


def stream_sentences_with_config(
    path: pathlib.Path | str,
    structure_config: Optional[DocumentStructureConfig] = None
) -> Generator[str, None, None]:
    """設定に基づいて文を逐次 yield する（従来APIとの互換性を保持）"""
    if structure_config is None or not structure_config.preserve_structure:
        # 構造認識を無効にする場合は従来の処理
        yield from stream_sentences(path)
    else:
        # 構造認識を有効にする場合
        for structured_sentence in stream_structured_sentences(path, structure_config):
            yield structured_sentence.text