# backend/app/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Track(Base):
    __tablename__ = "tracks"
    id = Column(String, primary_key=True, index=True)        # spotify id or custom id
    title = Column(String, nullable=False)
    artist = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    embedding = Column(Text, nullable=True)                 # JSON-serialized list
    popularity = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())