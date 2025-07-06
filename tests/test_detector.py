import numpy as np

from sentence_based_chunker import detector
from sentence_based_chunker.config import (
    Config,
    RuntimeConfig,
    LLMConfig,
    FailoverConfig,
    DetectorConfig,
)


def _dummy_cfg() -> Config:
    return Config(
        runtime=RuntimeConfig(),
        llm=LLMConfig(),
        failover=FailoverConfig(),
        detector=DetectorConfig(θ_high=0.9, θ_low=0.8, k=2, τ=10, n_vote=3),
    )


def test_detect_boundaries_simple():
    emb = [
        np.array([1.0, 0.0]),
        np.array([1.0, 0.0]),
        np.array([0.0, 1.0]),
    ]
    flags = list(detector.detect_boundaries(emb, _dummy_cfg()))
    assert flags == [False, False, True]