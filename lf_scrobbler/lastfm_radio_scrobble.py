import argparse
import re
import time
import datetime
from typing import NamedTuple, Optional
import yaml
import requests

import pylast
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from .config_schema import Config

class Track(NamedTuple):
    """Track description"""
    artist: str
    title: str

    def __str__(self) -> str:
        return f"Artist: {self.artist}, Title: {self.title}"

class RadioScrobbler:
    def __init__(self, config: Config):
        self.config = config
        self.track_old = None

        # Initialize Last.fm network
        self.network = pylast.LastFMNetwork(
            api_key=config.lastfm.api_key,
            api_secret=config.lastfm.shared_secret,
            username=config.lastfm.user_name,
            password_hash=config.lastfm.md5_password
        )

        # Initialize Spotify API client
        self.sp = None
        if self.config.spotify:
            self.sp = spotipy.Spotify(
                auth_manager=SpotifyOAuth(
                scope='user-read-recently-played playlist-modify-private')
            )

    @staticmethod
    def __decode_metadata(metadata: bytes) -> str:
        """Decode the given metadata byte sequence into a string

        Parameters
        ----------
        metadata : bytes
            The byte sequence representing the metadata

        Returns
        -------
        str
            The decoded metadata as a string
        """
        try:
            decoded_metadata = metadata.decode('utf-8')
        except UnicodeDecodeError:
            # Try a different encoding or use the 'ignore' error handling strategy
            decoded_metadata = metadata.decode('latin-1', errors='ignore')
        # TODO: Use other decoders and process possible exceptions
        return decoded_metadata

    def get_artist_track(self):
        response = requests.get(
            self.config.radios[0].stream_url,
            headers={'Icy-MetaData': '1'},
            stream=True
        )
        # Retrieve the Icy-MetaInt header
        icy_metaint_header = response.headers.get('icy-metaint')

        if icy_metaint_header:
            metaint = int(icy_metaint_header)
            for chunk in response.iter_content(chunk_size=metaint + 255):
                # Extract metadata from the chunk
                metadata = self.__decode_metadata(chunk[metaint:])
                track_match = re.search(r'StreamTitle=(?P<track>[^;]+)', metadata)

                if track_match:
                    track_info = track_match.group('track')
                    artist, title = track_info.split(' - ')
                    track = Track(artist=artist, title=title)
                    return track

        return None

    def scrobble(self, artist, title):
        timestamp = datetime.datetime.now()
        self.network.scrobble(artist, title, timestamp)

        if (
            self.sp
            and self.config.spotify
            and self.config.spotify.spotify_username
            and self.config.spotify.spotify_playlist_id
        ):
            track_info = f"{track.artist} - {track.title}"
            # TODO: Add multiple items by one request
            self.sp.playlist_add_items(
                playlist=self.config.spotify.spotify_playlist_id,
                items=[track_info]
            )

    def start_scrobbling(self):
        """Scrobbling tracks continiously"""
        while True:
            track = self.get_artist_track()
            if track and track != self.track_old:
                print(track)
                self.scrobble(track)
                self.track_old = track
            time.sleep(1)

def main():
    # Parse args
    parser = argparse.ArgumentParser(
        description='Scrobble radio playlists to Last.fm and Spotify'
    )
    parser.add_argument('--config', '-c', help='path to YAML configuration file')
    args = parser.parse_args()

    if args.config:
        with open(args.config, 'r') as config_file:
            config_data = yaml.safe_load(config_file)
        config = Config(**config_data)

    # Start scrobbling
    scrobbler = RadioScrobbler(config)
    scrobbler.start_scrobbling()

if __name__ == '__main__':
    main()
