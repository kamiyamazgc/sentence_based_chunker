## ワークフロー

1. 実装する機能の仕様を決定
2. 実装を行う
3. 動作テスト
4. sentence_based_chunker/docs/change_history に変更内容を記載。形式は以下の通り：

2025/06/30 20:30: 機能A, アルゴリズムの概要（50〜100文字）

## 守って欲しいこと

1. コメントは日本語で表記する
2. 出力は原則として日本語
3. 実装する機能ごとに作業フォルダを分ける
4. 実装したい機能については[仕様書](./docs/仕様書.md)を参照。同フォルダ内には、実装機能に関する文書が保存されているので、適宜参照すること
5. 更新履歴は docs/change_history/ を参照
    5.1. semantic_parserの更新履歴は docs/change_history/semantic_parser_change_log.md に記載してください