# 🎵 Radio Scrobbler

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/release/python-380/)
[![Code Style](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/charliermarsh/ruff)

A Python application that scrobbles songs played on internet radio stations to Last.fm and Spotify.

## 🚀 Features

- [x] Scrobbles songs played on internet radio stations to Last.fm and Spotify
- [x] Supports configuration via YAML file
- [ ] [Coming Soon] GUI version

## 📦 Installation

```bash
pip install .
```

## 📖 Usage

### Run CLI

```bash
radio-scrobble config.yaml
```

## ⚙️ Configuration

The project requires a configuration file in YAML format (`config.yaml`). The structure of the configuration file should be as follows:

```yaml
lastfm:
  api_key: key
  shared_secret: secret
  user_name: user
  md5_password: hash

spotify:
  spotify_username: username
  spotify_playlist_id: playlist_id

radios:
  - name: Radio 1
    stream_url: "http://us2.internet-radio.com:8443"
```

### Last.fm Configuration

- 🔑 `api_key`: The API key obtained from Last.fm.
- 🔒 `shared_secret`: The shared secret obtained from Last.fm.
- 👤 `user_name`: The Last.fm username.
- 🔐 `md5_password`: The MD5 hash of the Last.fm password.

You need an API account. It can be created [here](https://www.last.fm/api/account/create).

### Spotify Configuration

The spotify section is optional and allows you to configure scrobbling to Spotify. It should have the following properties:

- 🎵 `spotify_username`: Your Spotify username.
- 🎶 `spotify_playlist_id`: The ID of the playlist where scrobbled songs will be added.
You can copy Share Link to playlist and copy id which follows `playlist/`. (Example: `https://open.spotify.com/playlist/<playlist id>?...`)

### Radio Configuration

The `radios` section allows you to specify multiple radio stations. Each radio station should have the following properties:

- 📻 `name`: The name of the radio station.
- 🔊 `stream_url`: The URL of the radio station's audio stream.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.md](https://github.com/ostfor/lastfm_radio_scrobbler/blob/master/LICENSE.md) file for details.

🎶 Enjoy scrobbling your favorite tunes to Last.fm and Spotify! 🎧
