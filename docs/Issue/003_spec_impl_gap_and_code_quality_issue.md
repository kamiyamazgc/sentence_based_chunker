# Issue #003: 設計仕様と実装の乖離およびコード品質改善レポート

## 概要
AGENTS.md・docs/change_history/・docs/仕様書.md を確認し、リポジトリ全体の実装をレビューしたところ、仕様未達成の機能や保守性・性能面での課題が複数検出された。本レポートでは、優先度と共に改善・修正すべきポイントを列挙する。

## チェックリスト
- [x] AGENTS.md のワークフロー遵守状況
- [x] change_history の記録一貫性
- [x] docs/仕様書.md と実装の差分
- [x] コードベースの静的解析・テストカバレッジ
- [x] CLI・設定ファイルの実行パス

---

## 1. 仕様と実装のギャップ

| # | 項目 | 状況 | 優先度 |
|---|------|------|--------|
| 1 | Detector Stage **C (LLM 精査)** / **D (Post Filter)** | 関数は存在するが `detect_boundaries()` が呼び出しておらず無効 | ★★★ 高 |
| 2 | `provider_router` の **auto** モード & `failover.f1_drop_threshold` ロジック | 未実装。外部 LLM 切替が手動 `--force-remote` のみ | ★★★ 高 |
| 3 | `runtime.llm_concurrency` パラメータ | 未使用。LLM 呼び出しが逐次実行 | ★★☆ 中 |
| 4 | Builder の **`max_chars` / `min_chars`** 制限 | 仕様書に記載があるが未実装 | ★★☆ 中 |
| 5 | Preprocess での **見出し / リスト構造** 保持 | Issue #001 / #002 で既知。根本改善まだ | ★★☆ 中 |
| 6 | Post-run の **F1 自動評価 & Slack 通知** | evaluation モジュールはあるが自動実行箇所無し | ★★☆ 中 |
| 7 | Embedding モジュールの **`torch.mps.empty_cache()`** 呼び出し | 仕様書 2.2 参照。未実装 | ★★☆ 中 |
| 8 | LocalLLM 設定の **model_path 未利用** | server 側に依存しており参照されていない | ★☆☆ 低 |
| 9 | Config 内 **FailoverConfig** 未使用 | 設定後段で参照されていない | ★☆☆ 低 |

---

## 2. コード品質・保守性の課題

1. **Unicode 変数名 (θ, τ など)**: IDE 互換性や検索性を下げるため ASCII へ置換推奨。
2. **型ヒント不足 / Any の使用**: `local_llm.py`, `remote_llm.py` の JSON 型が Any となっている。
3. **エラーハンドリング**: LLM サーバー障害時にリトライやタイムアウト後のフォールバックが無い。
4. **テストカバレッジ**: CLI (`typer`) エントリポイントと ProviderRouter の単体テストが欠如。
5. **ドキュメント**: 関数 docstring が英語混在・不統一。AGENTS.md の「コメントは日本語」方針と乖離。
6. **依存管理**: requirements.txt に `scikit-learn` のみで `typer`, `aiohttp`, `pydantic`, `sentence_transformers`, `torch` が漏れている。
7. **性能最適化**: Embedding キャッシュは存在するがメモリ解放が無い、LLM 同時接続が 1 固定。

---

## 3. 推奨修正プラン

### 3.1 機能実装
1. `detect_boundaries()` に Stage C/D を統合。
   - `asyncio.gather` で並列呼び出しし、`n_vote` 融合ロジックを適用。
2. ProviderRouter
   - `auto` モード時に F1 評価結果を監視し、しきい値超過で remote へスイッチ。
   - `llm_concurrency` を `asyncio.Semaphore` で管理。
3. Builder
   - `max_chars` / `min_chars` を考慮しオーバーフロー時に新チャンク開始。

### 3.2 コードリファクタ
- 変数名を ASCII (`theta_high`, `theta_low`, `tau`) へ変更。
- 共通例外 `LLMCallError` を定義しリトライロジック追加。
- `requirements.txt` を最新版に更新し、`pip-tools` / `poetry` 導入を検討。

### 3.3 テスト & CI
- `pytest -m "not slow"` と `-m slow` タグ分類。LLM 絡みは slow。
- GitHub Actions で M1 ランナーが無いため、CPU モードでの smoke test を実行。
- `ruff` / `mypy` を CI に統合。

---

## 4. 優先度付きロードマップ (7 月)
| 週 | 作業 | 担当 | 完了基準 |
|----|------|------|---------|
| W2 | Stage C/D 実装 & 単体テスト | Taro | F1 +2pt, test pass |
| W2 | requirements.txt 整備 | Hana | CI で `pip install -r` 通過 |
| W3 | ProviderRouter auto/failover | Ken | drop ≥3pt でリモート切替確認 |
| W3 | エラーハンドリング・リトライ | Ken | LLM サーバーダウン時に retry 成功 |
| W4 | Builder max_chars 実装 | Yuki | 長文 (>4k) が分割される |
| W4 | ドキュメント・変数名統一 | All | ruff/mypy パス |

---

## 5. 参考コミット
- `docs/change_history/2025-07-06_14-00_init.txt`
- `docs/change_history/2025-07-07_10-30_update.txt`


## 作成日
2025/07/07