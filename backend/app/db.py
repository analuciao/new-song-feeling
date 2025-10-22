# backend/app/db.py
import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, Track
from typing import List

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_db():
    Base.metadata.create_all(bind=engine)

def save_track(t: dict):
    """
    t should contain: id, title, artist, source_url, thumbnail_url, embedding (list or json)
    """
    db = SessionLocal()
    try:
        existing = db.query(Track).filter(Track.id == t["id"]).first()
        if existing:
            return existing
        emb = t.get("embedding")
        if emb is not None and not isinstance(emb, str):
            emb = json.dumps(emb)
        track = Track(
            id=t["id"],
            title=t.get("title") or "",
            artist=t.get("artist"),
            source_url=t.get("source_url"),
            thumbnail_url=t.get("thumbnail_url"),
            embedding=emb,
            popularity=t.get("popularity")
        )
        db.add(track)
        db.commit()
        db.refresh(track)
        return track
    finally:
        db.close()

def get_tracks(limit: int = 500) -> List[dict]:
    db = SessionLocal()
    try:
        rows = db.query(Track).limit(limit).all()
        out = []
        for r in rows:
            emb = json.loads(r.embedding) if r.embedding else None
            out.append({
                "id": r.id, "title": r.title, "artist": r.artist,
                "source_url": r.source_url, "thumbnail_url": r.thumbnail_url,
                "embedding": emb, "popularity": r.popularity
            })
        return out
    finally:
        db.close()

def get_any_embedding_vector_size():
    # returns embedding size if any track exists, else 384 as default
    t = get_tracks(1)
    if t and t[0].get("embedding"):
        return len(t[0]["embedding"])
    return 384