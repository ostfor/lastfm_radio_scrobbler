from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class Radio(BaseModel):
    name: str
    stream_url: HttpUrl


class LastFMConfig(BaseModel):
    api_key: str
    shared_secret: str
    user_name: str
    md5_password: str = Field(description="md5 hash for your password")


class SpotifyConfig(BaseModel):
    client_id: str
    client_secret: str
    redirect_url: str
    spotify_playlist_id: str


class Config(BaseModel):
    lastfm: LastFMConfig
    radios: List[Radio]
    spotify: Optional[SpotifyConfig]
