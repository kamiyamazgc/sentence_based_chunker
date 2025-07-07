"""
semantic_parser - セマンティック構造パーサー

このモジュールは文書構造を階層的に解析し、
意味的な単位でのチャンク分割を実現します。
"""

from .core import DocumentNode

__version__ = '0.1.0'
__all__ = ['DocumentNode']