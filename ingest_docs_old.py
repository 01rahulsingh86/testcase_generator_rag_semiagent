import os
import numpy as np
import requests
from transformers import AutoTokenizer
import onnxruntime as ort
from tqdm import tqdm
import json

# -------------------------------
# Config
# -------------------------------
MODEL_NAME = "Xenova/paraphrase-MiniLM-L6-v2"
MODEL_ONNX_PATH = "/tmp/paraphrase-MiniLM-L6-v2.onnx"
DOCS_DIR = "docs"
OUT_DIR = "outputs"
INDEX_PATH = os.path.join(OUT_DIR, "index.npz")

os.makedirs(OUT_DIR, exist_ok=True)

# -------------------------------
# Download ONNX Model
# -------------------------------
# -------------------------------
# Download ONNX Model (stable method)
# -------------------------------
from huggingface_hub import hf_hub_download

def ensure_model_downloaded():
    if os.path.exists(MODEL_ONNX_PATH):
        print(f"✅ Using cached ONNX model at {MODEL_ONNX_PATH}")
        return MODEL_ONNX_PATH

    print("⬇️  Downloading ONNX model via huggingface-hub …")
    try:
        model_path = hf_hub_download(
            repo_id="sentence-transformers/all-MiniLM-L6-v2",
            filename="onnx/model.onnx",
            local_dir="/tmp",
            local_dir_use_symlinks=False,
        )
        print(f"✅  Model saved at {model_path}")
        return model_path
    except Exception as e:
        raise RuntimeError(f"❌ Could not download model: {e}")

# -------------------------------
# Load and tokenize documents
# -------------------------------
def load_documents():
    if not os.path.exists(DOCS_DIR):
        raise FileNotFoundError(f"❌ Folder not found: {DOCS_DIR}")
    docs = []
    for file in os.listdir(DOCS_DIR):
        path = os.path.join(DOCS_DIR, file)
        if os.path.isfile(path) and file.endswith((".txt", ".md")):
            with open(path, "r", encoding="utf-8") as f:
                text = f.read().strip()
                if text:
                    docs.append(text)
    print(f"✅ Loaded {len(docs)} document(s).")
    return docs

# -------------------------------
# Embed documents using ONNX model
# -------------------------------
def embed_texts(texts, model_path):
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])

    embeddings = []
    for text in tqdm(texts, desc="🔹 Embedding"):
        inputs = tokenizer(text, padding=True, truncation=True, return_tensors="np", max_length=256)
        outputs = session.run(None, dict(inputs))
        emb = np.mean(outputs[0], axis=1).squeeze()
        emb = emb / (np.linalg.norm(emb) + 1e-10)
        embeddings.append(emb)

    # normalize dimensions
    max_len = max(len(e) for e in embeddings)
    embeddings = np.array([
        np.pad(e, (0, max_len - len(e))) if len(e) < max_len else e
        for e in embeddings
    ])
    return embeddings

# -------------------------------
# Save vector index
# -------------------------------
def save_index(embeddings, docs):
    np.savez(INDEX_PATH, embeddings=embeddings, docs=np.array(docs))
    print(f"✅ Saved embeddings index → {INDEX_PATH}")

# -------------------------------
# Main
# -------------------------------
if __name__ == "__main__":
    model_path = ensure_model_downloaded()
    print("🔹 Loading tokenizer & ONNX model …")
    docs = load_documents()
    if not docs:
        raise SystemExit("❌ No documents found in /docs.")
    print("🔹 Computing embeddings …")
    embs = embed_texts(docs, model_path)
    save_index(embs, docs)
