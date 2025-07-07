#!/usr/bin/env python3
"""LLM動作テストスクリプト"""

import asyncio
from sentence_based_chunker.config import load_config
from sentence_based_chunker import local_llm

def test_llm():
    """LLMの動作をテストする"""
    print("LLMテスト開始...")
    
    # 設定を読み込み
    cfg = load_config("conf/mac_local.yaml")
    print(f"設定読み込み完了: {cfg.llm.provider}")
    
    # テストプロンプト
    test_prompt = "次の2文は異なるトピックか？ yes/no\n-----\nこれは最初の文です。\n-----\nこれは二番目の文です。"
    print(f"テストプロンプト: {test_prompt}")
    
    try:
        # LLMを呼び出し
        print("LLM呼び出し中...")
        response = local_llm.generate(test_prompt, cfg)
        print(f"LLM応答: {response}")
        print("LLMテスト成功！")
        return True
    except Exception as e:
        print(f"LLMテスト失敗: {e}")
        return False

if __name__ == "__main__":
    test_llm() 