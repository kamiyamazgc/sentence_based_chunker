from sentence_transformers import SentenceTransformer

print("モデル初期化開始")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")
print("モデル初期化成功")

sentences = ["これはテスト文です。", "もう一つの文です。"]
print(f"エンコード対象: {sentences}")

print("エンコード開始")
embeddings = model.encode(sentences, device="cpu", convert_to_numpy=True, normalize_embeddings=True)
print(f"エンコード成功: shape={embeddings.shape}")
print(embeddings) 