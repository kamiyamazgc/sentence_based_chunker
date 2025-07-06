import json

from sentence_based_chunker import writer
from sentence_based_chunker.builder import Chunk


def test_write_chunks(tmp_path):
    out_file = tmp_path / "out.jsonl"
    chunks = [
        Chunk(sentences=["A。", "B。"]),
        Chunk(sentences=["C。"]),
    ]

    writer.write_chunks(out_file, chunks)

    lines = out_file.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2

    data = [json.loads(l) for l in lines]
    assert data[0]["sentences"] == ["A。", "B。"]
    assert data[1]["text"] == "C。"