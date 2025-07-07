"""
semantic_parser.core - セマンティック構造パーサーのコアモジュール

このモジュールは文書構造を階層的に表現し、
意味的な単位でのチャンク分割を実現するコアクラスを提供します。
"""

from .document_node import DocumentNode

__all__ = ['DocumentNode']