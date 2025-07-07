import pathlib

from sentence_based_chunker import preprocess
from sentence_based_chunker.config import DocumentStructureConfig


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


def test_stream_structured_sentences_basic(tmp_path):
    """基本的な構造認識機能のテスト"""
    sample = tmp_path / "sample.txt"
    sample.write_text("これは最初の文です。\n\nこれは二番目の文です。")
    
    structured_sentences = list(preprocess.stream_structured_sentences(sample))
    assert len(structured_sentences) >= 2
    
    # 最初の文を確認
    first_sentence = structured_sentences[0]
    assert first_sentence.text == "これは最初の文です。"
    assert first_sentence.line_number == 1
    assert first_sentence.structure_type == "paragraph"


def test_stream_structured_sentences_markdown(tmp_path):
    """マークダウン記法の構造認識テスト"""
    sample = tmp_path / "sample.md"
    sample.write_text("# 見出し1\n\n- リスト項目1\n- リスト項目2\n\n通常の段落です。")
    
    structured_sentences = list(preprocess.stream_structured_sentences(sample))
    
    # 見出しの確認
    header_sentences = [s for s in structured_sentences if s.structure_type == "header"]
    assert len(header_sentences) == 1
    assert header_sentences[0].text == "見出し1"
    assert header_sentences[0].structure_info == "level_1"
    
    # リストの確認
    list_sentences = [s for s in structured_sentences if s.structure_type == "list"]
    assert len(list_sentences) == 2
    assert list_sentences[0].text == "リスト項目1"
    assert list_sentences[1].text == "リスト項目2"


def test_stream_structured_sentences_html(tmp_path):
    """HTML構造の認識テスト"""
    sample = tmp_path / "sample.html"
    sample.write_text("<h1>見出し</h1>\n<p>段落テキスト</p>")
    
    structured_sentences = list(preprocess.stream_structured_sentences(sample))
    
    # HTML要素の確認
    html_sentences = [s for s in structured_sentences if s.structure_type == "html"]
    assert len(html_sentences) == 2


def test_stream_structured_sentences_indentation(tmp_path):
    """インデント構造の認識テスト"""
    sample = tmp_path / "sample.txt"
    sample.write_text("通常の文\n    インデントされた文\n        さらにインデントされた文")
    
    structured_sentences = list(preprocess.stream_structured_sentences(sample))
    
    # インデントレベルの確認
    assert structured_sentences[0].indent_level == 0
    assert structured_sentences[1].indent_level == 4
    assert structured_sentences[2].indent_level == 8


def test_stream_structured_sentences_code_block(tmp_path):
    """コードブロックの認識テスト"""
    sample = tmp_path / "sample.md"
    sample.write_text("通常の文\n```python\nprint('hello')\n```\n別の文")
    
    structured_sentences = list(preprocess.stream_structured_sentences(sample))
    
    # コードブロックの確認
    code_sentences = [s for s in structured_sentences if s.structure_type == "code_block"]
    assert len(code_sentences) >= 2  # 開始・終了デリミタと内容


def test_stream_structured_sentences_table(tmp_path):
    """テーブル構造の認識テスト"""
    sample = tmp_path / "sample.md"
    sample.write_text("| 列1 | 列2 |\n|-----|-----|\n| 値1 | 値2 |")
    
    structured_sentences = list(preprocess.stream_structured_sentences(sample))
    
    # テーブル行の確認
    table_sentences = [s for s in structured_sentences if s.structure_type == "table"]
    assert len(table_sentences) == 3


def test_stream_sentences_with_config_disabled(tmp_path):
    """構造認識を無効にした場合のテスト"""
    sample = tmp_path / "sample.md"
    sample.write_text("# 見出し\n\n通常の文です。")
    
    # 構造認識を無効にする設定
    config = DocumentStructureConfig(preserve_structure=False)
    
    sentences = list(preprocess.stream_sentences_with_config(sample, config))
    
    # 従来の処理と同じ結果になることを確認
    traditional_sentences = list(preprocess.stream_sentences(sample))
    assert sentences == traditional_sentences


def test_stream_sentences_with_config_enabled(tmp_path):
    """構造認識を有効にした場合のテスト"""
    sample = tmp_path / "sample.md"
    sample.write_text("# 見出し\n\n通常の文です。")
    
    # 構造認識を有効にする設定
    config = DocumentStructureConfig(preserve_structure=True)
    
    sentences = list(preprocess.stream_sentences_with_config(sample, config))
    
    # 構造認識された結果を確認
    assert len(sentences) >= 2
    assert "見出し" in sentences[0]
    assert "通常の文です。" in sentences


def test_document_structure_config_defaults():
    """DocumentStructureConfigのデフォルト値テスト"""
    config = DocumentStructureConfig()
    
    assert config.preserve_structure == True
    assert config.detect_markdown == True
    assert config.detect_html == True
    assert config.detect_indentation == True
    assert config.preserve_headers == True
    assert config.preserve_lists == True
    assert config.preserve_tables == True
    assert config.preserve_code_blocks == True
    assert config.min_header_level == 1
    assert config.max_header_level == 6
    assert config.list_indent_threshold == 2
    assert config.preserve_whitespace == True