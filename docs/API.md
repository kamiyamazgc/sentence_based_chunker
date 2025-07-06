# Sentence-Based Chunker – API 概要

| モジュール | 役割 | 主要公開関数 / クラス |
| ---------- | ---- | ------------------- |
| `preprocess` | 文分割ジェネレータ | `stream_sentences` |
| `embedding` | SentenceTransformer 埋め込み | `encode_stream` |
| `detector` | 境界検出 Stage A–D | `detect_boundaries` |
| `builder` | Chunk 構築 | `Chunk`, `build_chunks` |
| `writer` | JSONL 出力 | `write_chunks` |
| `provider_router` | LLM ルーティング | `ProviderRouter` |
| `local_llm` | ローカル llama サーバ呼び出し | `generate` |
| `remote_llm` | OpenAI 互換 API 呼び出し | `generate` |
| `cli` | Typer CLI | `run`, `eval` コマンド |

各モジュールには詳細な docstring を付与してあります。エディタから `Go to Definition` を使って参照してください。