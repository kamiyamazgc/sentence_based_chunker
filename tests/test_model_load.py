from sentence_transformers import SentenceTransformer

print("モデル初期化開始")
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")
print("モデル初期化成功") 