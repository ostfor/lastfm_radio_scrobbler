import argparse
import re
import time
import datetime
import urllib.request
import yaml

import pylast
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from .config_schema import Config

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

    def get_artist_track(self):
        d = dict()
        request = urllib.request.Request(self.config.lastfm.stream_url)
        request.add_header('Icy-MetaData', 1)
        response = urllib.request.urlopen(request)
        icy_metaint_header = response.headers.get('icy-metaint')

        if icy_metaint_header is not None:
            metaint = int(icy_metaint_header)
            read_buffer = metaint + 255
            content = response.read(read_buffer)
            data = str(content[metaint:])
            p = re.compile(r'StreamTitle=(?P<track>[^;]+)')
            s = re.search(p, data)
            if s:
                d = s.groupdict()
            else:
                d = None
        return d

    def scrobble(self, artist, title):
        timestamp = datetime.datetime.now()
        self.network.scrobble(artist, title, timestamp)

        if (
            self.sp
            and self.config.spotify.spotify_username
            and self.config.spotify.spotify_playlist_id
        ):
            track_info = f"{artist} - {title}"
            self.sp.playlist_add_items(self.config.spotify.spotify_playlist_id[track_info])

    def start_scrobbling(self):
        while True:
            track = self.get_artist_track()
            if track and track != self.track_old:
                tr = str(track["track"])
                tr = tr.replace("'", "")
                tr_info = tr.split(" - ")
                if len(tr_info) < 2:
                    tr_info = ["Unknown", tr]

                print(tr_info)
                self.scrobble(tr_info[0], tr_info[1])
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
