import argparse
import logging
from pathlib import Path
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
        self.__logger = logging.getLogger(__name__)
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
                    scope='user-read-recently-played playlist-modify-private playlist-modify-public',
                    client_id=self.config.spotify.client_id,
                    client_secret=self.config.spotify.client_secret,
                    redirect_uri=self.config.spotify.redirect_url  # Optional, provide if necessary
                )
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

    def search_spotify_track(self, track: Track) -> Optional[str]:
        # Search for the track
        if not self.sp:
            self.__logger.warning(f'Cannot search track beecause not authorised in spotify')
            return None
        search_query = f'artist:{track.artist} track:{track.title}'
        results = self.sp.search(search_query, type='track', limit=1)
        # Extract the track URI from the search results
        if results['tracks']['items']:
            track_uri = results['tracks']['items'][0]['uri']
            return track_uri
        else:
            self.__logger.warning(f'Track {track} not found in spotify')
            return None

    @staticmethod
    def clean_track(track: Track) -> Track:
        return Track(
            artist=track.artist,
            title=re.sub(r'\[.*?\]', '', track.title)
        )

    def get_artist_track(self) -> Optional[Track]:
        """Get track from radio stream

        Returns
        -------
        Optional[Track]
            Track instance if track metadata found, None otherwise
        """
        # TODO: get stream frome more than one radio
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
                    track = self.clean_track(Track(artist=artist, title=title))
                    return track

        return None


    def scrobble(self, track: Track):
        """Scrobble one track

        Parameters
        ----------
        Ttrack : Track
            Track instance whic should be added
        """
        timestamp = datetime.datetime.now()
        self.network.scrobble(track.artist, track.title, timestamp)

        if self.sp and self.config.spotify:
            track_uri = self.search_spotify_track(track)
            # TODO: Add multiple items by one request
            if track_uri:
                self.sp.playlist_add_items(
                    self.config.spotify.spotify_playlist_id,
                    [track_uri]
                )

    def start_scrobbling(self):
        """Scrobbling tracks continiously"""
        while True:
            track = self.get_artist_track()
            if track and track != self.track_old:
                self.__logger.info(track)
                self.scrobble(track)
                self.track_old = track
            time.sleep(1)


def main():
    logger = logging.getLogger(__name__)
    # Parse args
    parser = argparse.ArgumentParser(
        description='Scrobble radio playlists to Last.fm and Spotify'
    )
    parser.add_argument(
        '--config', '-c',
        help='path to YAML configuration file',
        default=Path('~/.confiig/radio-scrobble/config.yaml')
    )
    args = parser.parse_args()

    if args.config:
        if Path(args.config).exists():
            with open(args.config, 'r') as config_file:
                config_data = yaml.safe_load(config_file)
            config = Config(**config_data)
        else:
            logger.error(f'Config {args.config} not found!')
            exit(1)

    # Start scrobbling
    scrobbler = RadioScrobbler(config)
    scrobbler.start_scrobbling()

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)
    main()