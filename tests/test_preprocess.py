import pathlib

from sentence_based_chunker import preprocess


def test_stream_sentences(tmp_path):
    text = "こんにちは。お元気ですか？今日は晴れです。"
    sample = tmp_path / "sample.txt"
    sample.write_text(text, encoding="utf-8")

    sentences = list(preprocess.stream_sentences(sample))

    assert sentences == [
        "こんにちは。",
        "お元気ですか？",
        "今日は晴れです。",
    ]