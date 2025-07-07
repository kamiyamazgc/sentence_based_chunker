#!/usr/bin/env python3
"""埋め込み生成テストスクリプト"""

from sentence_based_chunker.config import load_config
from sentence_based_chunker import embedding

def test_embedding():
    """埋め込み生成をテストする"""
    print("埋め込み生成テスト開始...")
    
    # 設定を読み込み
    cfg = load_config("conf/mac_local.yaml")
    print(f"設定読み込み完了: device={cfg.runtime.device}")
    
    # テスト文（1文のみ）
    test_sentences = ["これは最初の文です。"]
    print(f"テスト文: {test_sentences}")
    
    try:
        # 埋め込み生成
        print("埋め込み生成中...")
        embeddings = list(embedding.embed_stream(test_sentences, cfg))
        print(f"埋め込み生成完了: {len(embeddings)}個のベクトル")
        
        # ベクトルの形状を確認
        for i, emb in enumerate(embeddings):
            print(f"ベクトル{i+1}: 形状={emb.shape}, 型={emb.dtype}")
        
        print("埋め込み生成テスト成功！")
        return True
    except Exception as e:
        print(f"埋め込み生成テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_embedding() 