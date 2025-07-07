import pathlib
import sys
from typing import Optional

import typer

from .config import load_config, Config
from . import preprocess, embedding as emb_mod, detector as det_mod, builder as builder_mod, writer as writer_mod
from .exceptions import SentenceBasedChunkerError

app = typer.Typer(add_completion=False, help="Sentence-Based Chunker CLI")


@app.command()
def run(
    input_path: pathlib.Path = typer.Argument(..., help="解析対象のテキストファイル"),
    conf: pathlib.Path = typer.Option("conf/mac_local.yaml", help="設定ファイルのパス"),
    force_remote: bool = typer.Option(False, "--force-remote", help="外部 LLM を強制使用する"),
    output: Optional[pathlib.Path] = typer.Option(None, "--output", help="出力ファイルパス。未指定なら <input>.chunks.jsonl"),
):
    """文章ファイルを分割し、チャンク情報を出力します。"""
    try:
        cfg: Config = load_config(conf)
        if force_remote:
            cfg.llm.provider = "remote"

        # 文リスト生成 (ストリームで2回利用するためリスト化)
        sentences = list(preprocess.stream_sentences(input_path))

        # ベクトル生成
        embeddings = emb_mod.embed_stream(sentences, cfg)

        # 境界判定
        boundaries = list(det_mod.detect_boundaries(embeddings, cfg))

        # チャンク構築
        chunks = builder_mod.build_chunks(sentences, boundaries, cfg)

        # 出力
        out_path = output or input_path.with_suffix(".chunks.jsonl")
        writer_mod.write_chunks(out_path, chunks)
        typer.echo(f"書き込み完了: {out_path}")
    except SentenceBasedChunkerError as e:
        typer.echo(f"エラー: {e}", err=True)
        sys.exit(1)
    except Exception as e:  # pylint: disable=broad-except
        # 予期しないエラー
        typer.echo(f"予期しないエラーが発生しました: {e}", err=True)
        sys.exit(1)


@app.command()
def eval(
    gold_dir: pathlib.Path = typer.Argument(..., help="ゴールドセット格納ディレクトリ"),
    pred_dir: pathlib.Path = typer.Argument(..., help="予測結果ディレクトリ"),
):
    """F1 スコアを計算して表示します (簡易版)。"""
    from .evaluation import evaluate

    f1 = evaluate(gold_dir, pred_dir)
    typer.echo(f"Topic-Boundary F1: {f1:.4f}")


def _entry_point():  # pragma: no cover
    app()


if __name__ == "__main__":
    _entry_point()