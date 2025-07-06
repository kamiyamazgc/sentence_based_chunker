from sentence_based_chunker import builder


def test_build_chunks():
    sentences = ["A。", "B。", "C。"]
    boundaries = [False, True, False]

    chunks = builder.build_chunks(sentences, boundaries, cfg=None)

    assert len(chunks) == 2
    assert chunks[0].sentences == sentences[:2]
    assert chunks[1].sentences == [sentences[2]]