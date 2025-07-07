"""設定ファイルの読み込みとバリデーションを行うモジュール"""

from __future__ import annotations

import pathlib
from typing import Literal, Optional

import yaml
from pydantic import BaseModel, Field
from .exceptions import ConfigLoadError


class RuntimeConfig(BaseModel):
    device: str = Field("cpu", description="mps / cpu / cuda")
    batch_size: int = 32
    llm_concurrency: int = 1


class LocalLLMConfig(BaseModel):
    model_path: str
    server_url: str = "http://127.0.0.1:8000"


class RemoteLLMConfig(BaseModel):
    endpoint: str
    model: str


class LLMConfig(BaseModel):
    provider: Literal["local", "remote", "auto"] = "local"
    local: Optional[LocalLLMConfig] = None
    remote: Optional[RemoteLLMConfig] = None


class FailoverConfig(BaseModel):
    f1_drop_threshold: float = 0.03


class DetectorConfig(BaseModel):
    θ_high: float = 0.85
    θ_low: float = 0.55
    k: int = 5
    τ: float = 3.5
    n_vote: int = 3
    use_llm_review: bool = False  # Stage C（LLM精査）を使用するかどうか


class DocumentStructureConfig(BaseModel):
    """文書構造の処理設定"""
    preserve_structure: bool = True
    detect_markdown: bool = True
    detect_html: bool = True
    detect_indentation: bool = True
    preserve_headers: bool = True
    preserve_lists: bool = True
    preserve_tables: bool = True
    preserve_code_blocks: bool = True
    min_header_level: int = 1
    max_header_level: int = 6
    list_indent_threshold: int = 2  # インデントリスト検出の閾値（スペース数）
    preserve_whitespace: bool = True  # 構造的な空白の保持


class Config(BaseModel):
    runtime: RuntimeConfig
    llm: LLMConfig
    failover: FailoverConfig
    detector: DetectorConfig = DetectorConfig()
    document_structure: DocumentStructureConfig = DocumentStructureConfig()


# ------------------------------------------------------------
#  public helpers
# ------------------------------------------------------------

def load_config(path: pathlib.Path | str) -> Config:
    """YAML ファイルを読み込み Config オブジェクトを返す。

    何らかの理由で読み込みに失敗した場合は ``ConfigLoadError`` を送出する。
    """
    path = pathlib.Path(path)
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError as e:
        raise ConfigLoadError(f"設定ファイルが見つかりません: {path}") from e
    except yaml.YAMLError as e:
        raise ConfigLoadError(f"YAML の解析に失敗しました: {e}") from e
    except Exception as e:  # pylint: disable=broad-except
        raise ConfigLoadError(f"設定ファイルの読み込み中に予期せぬエラーが発生しました: {e}") from e

    # バリデーション
    try:
        return Config.model_validate(data)
    except Exception as e:  # pylint: disable=broad-except
        raise ConfigLoadError(f"設定値のバリデーションに失敗しました: {e}") from e