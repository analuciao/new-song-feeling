# backend/app/main.py
from fastapi import FastAPI
from app.db import init_db, get_tracks, get_any_embedding_vector_size
from app.ingest import seed_all
from app.embeddings import cosine
from dotenv import load_dotenv
load_dotenv()
import numpy as np

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()
    # seed in startup (quick & simple). For production use background workers.
    seed_all()

def pick_daily_gem(user_embedding=None, candidates=None):
    if not candidates:
        candidates = get_tracks(500)
    # If no user embedding provided, use centroid of saved tracks to approximate taste
    if user_embedding is None:
        # centroid of first N tracks
        vecs = [c['embedding'] for c in candidates if c.get('embedding')]
        if not vecs:
            return None
        user_embedding = np.mean(np.array(vecs), axis=0).tolist()

    best = None
    best_score = -999
    for c in candidates:
        emb = c.get('embedding')
        if not emb:
            continue
        sim = cosine(user_embedding, emb)
        novelty = 1.0 - sim
        artist_boost = 0.15 if (c.get('popularity') or 0) < 30 else 0.0
        score = 0.7 * novelty + 0.3 * artist_boost
        if score > best_score:
            best_score = score
            best = c
    return best

@app.get("/daily-gem")
def daily_gem():
    candidates = get_tracks(500)
    gem = pick_daily_gem(None, candidates)
    return {"gem": gem}