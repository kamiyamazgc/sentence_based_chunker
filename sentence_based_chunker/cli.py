import pathlib
import sys
from typing import Optional

import typer

from .config import load_config, Config
from . import preprocess, embedding as emb_mod, detector as det_mod, builder as builder_mod, writer as writer_mod

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
        # 設定ファイル読み込み
        try:
            cfg: Config = load_config(conf)
        except FileNotFoundError:
            print(f"エラー: 設定ファイルが見つかりません: {conf}", file=sys.stderr)
            print(f"設定ファイルが存在することを確認してください。", file=sys.stderr)
            raise typer.Exit(1)
        except Exception as e:
            print(f"エラー: 設定ファイルの読み込みに失敗しました: {conf}", file=sys.stderr)
            print(f"詳細: {e}", file=sys.stderr)
            raise typer.Exit(1)
        
        if force_remote:
            cfg.llm.provider = "remote"
        
        print(f"処理開始: {input_path}", file=sys.stderr)
        
        # 文リスト生成 (ストリームで2回利用するためリスト化)
        try:
            print(f"テキストファイルを読み込み中...", file=sys.stderr)
            sentences = list(preprocess.stream_sentences(input_path))
            print(f"文数: {len(sentences)}", file=sys.stderr)
            
            if len(sentences) == 0:
                print(f"警告: 入力ファイルから文が検出されませんでした", file=sys.stderr)
                print(f"ファイルの内容とフォーマットを確認してください", file=sys.stderr)
                
        except Exception as e:
            print(f"エラー: テキストファイルの読み込みに失敗しました", file=sys.stderr)
            raise typer.Exit(1)

        # ベクトル生成
        try:
            print(f"埋め込みベクトルを生成中...", file=sys.stderr)
            embeddings = emb_mod.embed_stream(sentences, cfg)
            embeddings = list(embeddings)  # ストリームをリスト化
            print(f"埋め込みベクトル生成完了: {len(embeddings)} 個", file=sys.stderr)
            
        except Exception as e:
            print(f"エラー: 埋め込みベクトルの生成に失敗しました", file=sys.stderr)
            raise typer.Exit(1)

        # 境界判定
        try:
            print(f"境界検出を実行中...", file=sys.stderr)
            boundaries = list(det_mod.detect_boundaries(embeddings, cfg))
            boundary_count = sum(boundaries)
            print(f"境界検出完了: {boundary_count} 個の境界を検出", file=sys.stderr)
            
        except Exception as e:
            print(f"エラー: 境界検出処理に失敗しました", file=sys.stderr)
            print(f"詳細: {e}", file=sys.stderr)
            raise typer.Exit(1)

        # チャンク構築
        try:
            print(f"チャンクを構築中...", file=sys.stderr)
            chunks = builder_mod.build_chunks(sentences, boundaries, cfg)
            chunk_count = len(list(chunks)) if hasattr(chunks, '__iter__') else 0
            print(f"チャンク構築完了: {chunk_count} 個のチャンク", file=sys.stderr)
            
        except Exception as e:
            print(f"エラー: チャンク構築処理に失敗しました", file=sys.stderr)
            print(f"詳細: {e}", file=sys.stderr)
            raise typer.Exit(1)

        # 出力
        try:
            out_path = output or input_path.with_suffix(".chunks.jsonl")
            print(f"結果を出力中: {out_path}", file=sys.stderr)
            writer_mod.write_chunks(out_path, chunks)
            print(f"書き込み完了: {out_path}")
            
        except PermissionError:
            print(f"エラー: 出力ファイルへの書き込み権限がありません: {out_path}", file=sys.stderr)
            raise typer.Exit(1)
        except Exception as e:
            print(f"エラー: 出力ファイルの書き込みに失敗しました", file=sys.stderr)
            print(f"詳細: {e}", file=sys.stderr)
            raise typer.Exit(1)
            
    except typer.Exit:
        # typer.Exitは再発生させる
        raise
    except KeyboardInterrupt:
        print(f"\n処理が中断されました", file=sys.stderr)
        raise typer.Exit(1)
    except Exception as e:
        print(f"エラー: 予期しないエラーが発生しました", file=sys.stderr)
        print(f"詳細: {e}", file=sys.stderr)
        print(f"この問題が継続する場合は、設定ファイルと入力ファイルを確認してください", file=sys.stderr)
        raise typer.Exit(1)


@app.command()
def eval(
    gold_dir: pathlib.Path = typer.Argument(..., help="ゴールドセット格納ディレクトリ"),
    pred_dir: pathlib.Path = typer.Argument(..., help="予測結果ディレクトリ"),
):
    """F1 スコアを計算して表示します (簡易版)。"""
    try:
        from .evaluation import evaluate
        
        # ディレクトリ存在チェック
        if not gold_dir.exists():
            print(f"エラー: ゴールドセットディレクトリが見つかりません: {gold_dir}", file=sys.stderr)
            raise typer.Exit(1)
        if not pred_dir.exists():
            print(f"エラー: 予測結果ディレクトリが見つかりません: {pred_dir}", file=sys.stderr)
            raise typer.Exit(1)
            
        print(f"評価を実行中...", file=sys.stderr)
        f1 = evaluate(gold_dir, pred_dir)
        typer.echo(f"Topic-Boundary F1: {f1:.4f}")
        
    except ImportError as e:
        print(f"エラー: 評価モジュールのインポートに失敗しました", file=sys.stderr)
        print(f"詳細: {e}", file=sys.stderr)
        raise typer.Exit(1)
    except Exception as e:
        print(f"エラー: 評価処理に失敗しました", file=sys.stderr)
        print(f"詳細: {e}", file=sys.stderr)
        raise typer.Exit(1)


def _entry_point():  # pragma: no cover
    try:
        app()
    except Exception as e:
        print(f"エラー: アプリケーションの実行に失敗しました", file=sys.stderr)
        print(f"詳細: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    _entry_point()