import os, json, numpy as np, onnxruntime as ort
from transformers import AutoTokenizer
from tqdm import tqdm
import requests
from huggingface_hub import hf_hub_download

# --------------------------------------------------
# Configuration
# --------------------------------------------------
MODEL_REPO = "Xenova/all-MiniLM-L6-v2"
MODEL_FILE = "model.onnx"
DOCS_DIR = "requirements_docs"
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --------------------------------------------------
# Step 1: Ensure ONNX model exists locally
# --------------------------------------------------
def ensure_model_downloaded():
    local_path = os.path.join("/tmp/onnx", MODEL_FILE)
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    if not os.path.exists(local_path):
        print("⬇️  Downloading ONNX model via huggingface-hub …")
        model_path = hf_hub_download(repo_id=MODEL_REPO, filename=MODEL_FILE, local_dir="/tmp/onnx")
        print(f"✅  Model saved at {model_path}")
        return model_path
    print(f"✅  Model already exists → {local_path}")
    return local_path

# --------------------------------------------------
# Step 2: Load documents from requirements_docs/
# --------------------------------------------------
def load_documents():
    docs, names = [], []
    for file in os.listdir(DOCS_DIR):
        path = os.path.join(DOCS_DIR, file)
        if not os.path.isfile(path):
            continue
        if file.endswith((".txt", ".md")):
            with open(path, "r", encoding="utf-8") as f:
                docs.append(f.read())
        elif file.endswith(".json"):
            with open(path, "r", encoding="utf-8") as f:
                docs.append(json.dumps(json.load(f), indent=2))
        elif file.endswith(".docx"):
            from docx import Document
            doc = Document(path)
            docs.append("\n".join(p.text for p in doc.paragraphs))
        names.append(file)
    print(f"✅ Loaded {len(docs)} document(s).")
    return docs, names

# --------------------------------------------------
# Step 3: Load tokenizer + ONNX session
# --------------------------------------------------
def load_model(model_path):
    tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
    return tokenizer, session

# --------------------------------------------------
# Step 4: Compute embeddings
# --------------------------------------------------
def embed_texts(tokenizer, session, texts):
    embeddings = []
    for text in tqdm(texts, desc="🔹 Embedding"):
        inputs = tokenizer(text, return_tensors="np", truncation=True, padding="max_length", max_length=256)
        ort_inputs = {k: v for k, v in inputs.items()}
        ort_outs = session.run(None, ort_inputs)
        emb = ort_outs[0].mean(axis=1)  # mean pooling
        norm = np.linalg.norm(emb)
        emb = emb / norm if norm != 0 else emb
        embeddings.append(emb[0])
    return np.vstack(embeddings)

# --------------------------------------------------
# Step 5: Save embeddings index
# --------------------------------------------------
def save_index(embeddings, names):
    np.savez(os.path.join(OUTPUT_DIR, "index.npz"), embeddings=embeddings, names=np.array(names))
    print(f"✅ Saved embeddings index → {OUTPUT_DIR}/index.npz")

# --------------------------------------------------
# Main
# --------------------------------------------------
if __name__ == "__main__":
    model_path = ensure_model_downloaded()
    tokenizer, session = load_model(model_path)
    docs, names = load_documents()
    embeddings = embed_texts(tokenizer, session, docs)
    save_index(embeddings, names)
