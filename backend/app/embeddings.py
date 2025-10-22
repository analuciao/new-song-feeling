# backend/app/embeddings.py
from sentence_transformers import SentenceTransformer
import numpy as np

# load once
_model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_text(text: str):
    """Return a plain Python list (JSON serializable)."""
    vec = _model.encode(text)
    return vec.tolist()

def cosine(a, b):
    a = np.array(a); b = np.array(b)
    denom = (np.linalg.norm(a) * np.linalg.norm(b)) + 1e-9
    return float(np.dot(a, b) / denom)