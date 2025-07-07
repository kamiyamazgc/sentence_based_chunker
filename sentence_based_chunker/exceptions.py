"""Sentence-Based Chunker 共通例外定義モジュール

このモジュールでは本パッケージ全体で使用する共通例外クラスを定義する。
各機能モジュールは必要に応じてこれらの例外を送出し、CLI 層で集中的に捕捉することで
ユーザーに分かりやすいエラーメッセージを提供することを目的とする。
"""

from __future__ import annotations


class SentenceBasedChunkerError(Exception):
    """本ライブラリで発生する例外の基底クラス"""


class FileReadError(SentenceBasedChunkerError):
    """ファイル読み込み失敗"""


class FileWriteError(SentenceBasedChunkerError):
    """ファイル書き込み失敗"""


class ConfigLoadError(SentenceBasedChunkerError):
    """設定ファイル読み込み・パース失敗"""


class ModelLoadError(SentenceBasedChunkerError):
    """埋め込みモデルの読み込み失敗"""


class EmbeddingComputeError(SentenceBasedChunkerError):
    """埋め込み計算時のエラー"""


class LLMCallError(SentenceBasedChunkerError):
    """LLM 呼び出し失敗"""