# backend/app/ingest.py
import os
from app.db import save_track, get_tracks
from app.embeddings import embed_text

def seed_from_spotify(limit=50):
    """Attempt to fetch from Spotify using spotipy if env vars are present."""
    try:
        import spotipy
        from spotipy.oauth2 import SpotifyClientCredentials
    except Exception:
        print("spotipy not installed or available; skipping Spotify seeding.")
        return

    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    if not client_id or not client_secret:
        print("No Spotify creds found in env; skipping Spotify seeding.")
        return

    auth = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=auth)
    results = sp.search(q="tag:new OR year:2024 OR genre:indie", type="track", limit=limit)
    for item in results['tracks']['items']:
        t = {
            "id": item['id'],
            "title": item['name'],
            "artist": item['artists'][0]['name'],
            "source_url": item['external_urls']['spotify'],
            "thumbnail_url": item['album']['images'][0]['url'] if item['album']['images'] else None
        }
        txt = f"{t['title']} — {t['artist']}"
        t['embedding'] = embed_text(txt)
        save_track(t)
    print("Spotify seed complete.")

def seed_manual():
    """A few explicit tracks so you can test without API keys."""
    examples = [
        {"id":"seed:1","title":"Warm Glow","artist":"Indie Friend","source_url":"https://example.com/1"},
        {"id":"seed:2","title":"Late Night Drive","artist":"Bedroom Producer","source_url":"https://example.com/2"},
        {"id":"seed:3","title":"Sunset Loop","artist":"Lo-Fi Beats","source_url":"https://example.com/3"},
    ]
    for t in examples:
        txt = f"{t['title']} — {t['artist']}"
        t['embedding'] = embed_text(txt)
        save_track(t)
    print("Manual seed complete.")

def seed_all():
    # run spotify if possible, then fallback manual if DB is empty
    seed_from_spotify()
    from app.db import get_tracks
    if len(get_tracks(1)) == 0:
        seed_manual()