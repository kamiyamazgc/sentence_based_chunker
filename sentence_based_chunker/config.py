"""設定ファイルの読み込みとバリデーションを行うモジュール"""

from __future__ import annotations

import pathlib
from typing import Literal, Optional

import yaml
from pydantic import BaseModel, Field


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


class Config(BaseModel):
    runtime: RuntimeConfig
    llm: LLMConfig
    failover: FailoverConfig
    detector: DetectorConfig = DetectorConfig()


# ------------------------------------------------------------
#  public helpers
# ------------------------------------------------------------

def load_config(path: pathlib.Path | str) -> Config:
    """YAML ファイルを読み込み Config オブジェクトを返す"""
    path = pathlib.Path(path)
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return Config.model_validate(data)