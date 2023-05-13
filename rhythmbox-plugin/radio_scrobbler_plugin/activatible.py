import logging
import gi
import yaml

from gi.repository import GObject, Peas, RB, Gio
from pathlib import Path

from lf_scrobbler.lastfm_radio_scrobble import RadioScrobbler
from lf_scrobbler.config_schema import Config, Radio


from gi.repository import RB
gi.require_version('Gtk', '3.0')

class RadioScrobblerActivatable(GObject.Object, Peas.Activatable):
    __gtype_name__ = 'RadioScrobblerActivatable'
    plugin_id = 'radio_scrobbler'
    plugin_name = 'Radio Scrobbler'
    object = GObject.property(type=GObject.Object)

    def __init__(self, *args, **kwargs):
        super(RadioScrobblerActivatable, self).__init__(*args, **kwargs)
        self.config_dialog = None

        # Create an action for the button
        self.action = Gio.SimpleAction.new("start_scrobbling", None)

        # Connect the action to a method
        self.action.connect("activate", self.on_scrobble_button_clicked)


    def do_activate(self):
        # Get the main window from the shell
        app = self.object.props.application

        # # Connect the button to the action
        # Add the action to an action group
        app.add_action(self.action)

        item = Gio.MenuItem()
        item.set_label("Scrobble Radio")
        item.set_detailed_action('app.start_scrobbling')
        app.add_plugin_menu_item('tools', 'scrobble-radio', item)

    def on_scrobble_button_clicked(self, action, parameter):

        PROP = [
            RB.RhythmDBPropType.ENTRY_ID, RB.RhythmDBPropType.TITLE, RB.RhythmDBPropType.GENRE, RB.RhythmDBPropType.ARTIST, RB.RhythmDBPropType.ALBUM, RB.RhythmDBPropType.TRACK_NUMBER, RB.RhythmDBPropType.DISC_NUMBER, RB.RhythmDBPropType.DURATION, RB.RhythmDBPropType.FILE_SIZE, RB.RhythmDBPropType.LOCATION, RB.RhythmDBPropType.MOUNTPOINT, RB.RhythmDBPropType.MTIME, RB.RhythmDBPropType.FIRST_SEEN, RB.RhythmDBPropType.LAST_SEEN, RB.RhythmDBPropType.RATING, RB.RhythmDBPropType.PLAY_COUNT, RB.RhythmDBPropType.LAST_PLAYED, RB.RhythmDBPropType.BITRATE, RB.RhythmDBPropType.DATE, RB.RhythmDBPropType.REPLAYGAIN_TRACK_GAIN, RB.RhythmDBPropType.REPLAYGAIN_TRACK_PEAK, RB.RhythmDBPropType.REPLAYGAIN_ALBUM_GAIN, RB.RhythmDBPropType.REPLAYGAIN_ALBUM_PEAK, RB.RhythmDBPropType.MEDIA_TYPE, RB.RhythmDBPropType.TITLE_SORT_KEY, RB.RhythmDBPropType.GENRE_SORT_KEY, RB.RhythmDBPropType.ARTIST_SORT_KEY, RB.RhythmDBPropType.ALBUM_SORT_KEY, RB.RhythmDBPropType.TITLE_FOLDED, RB.RhythmDBPropType.GENRE_FOLDED, RB.RhythmDBPropType.ARTIST_FOLDED, RB.RhythmDBPropType.ALBUM_FOLDED, RB.RhythmDBPropType.LAST_PLAYED_STR, RB.RhythmDBPropType.HIDDEN, RB.RhythmDBPropType.PLAYBACK_ERROR, RB.RhythmDBPropType.FIRST_SEEN_STR, RB.RhythmDBPropType.LAST_SEEN_STR, RB.RhythmDBPropType.SEARCH_MATCH, RB.RhythmDBPropType.YEAR, RB.RhythmDBPropType.KEYWORD, RB.RhythmDBPropType.STATUS, RB.RhythmDBPropType.DESCRIPTION, RB.RhythmDBPropType.SUBTITLE, RB.RhythmDBPropType.SUMMARY, RB.RhythmDBPropType.LANG, RB.RhythmDBPropType.COPYRIGHT, RB.RhythmDBPropType.IMAGE, RB.RhythmDBPropType.POST_TIME, RB.RhythmDBPropType.MB_TRACKID, RB.RhythmDBPropType.MB_ARTISTID, RB.RhythmDBPropType.MB_ALBUMID, RB.RhythmDBPropType.MB_ALBUMARTISTID, RB.RhythmDBPropType.MB_ARTISTSORTNAME, RB.RhythmDBPropType.ALBUM_SORTNAME, RB.RhythmDBPropType.ARTIST_SORTNAME_SORT_KEY, RB.RhythmDBPropType.ARTIST_SORTNAME_FOLDED, RB.RhythmDBPropType.ALBUM_SORTNAME_SORT_KEY, RB.RhythmDBPropType.ALBUM_SORTNAME_FOLDED, RB.RhythmDBPropType.COMMENT, RB.RhythmDBPropType.ALBUM_ARTIST, RB.RhythmDBPropType.ALBUM_ARTIST_SORT_KEY, RB.RhythmDBPropType.ALBUM_ARTIST_FOLDED, RB.RhythmDBPropType.ALBUM_ARTIST_SORTNAME, RB.RhythmDBPropType.ALBUM_ARTIST_SORTNAME_SORT_KEY, RB.RhythmDBPropType.ALBUM_ARTIST_SORTNAME_FOLDED, RB.RhythmDBPropType.BEATS_PER_MINUTE
            ]
        logging.info('Start scrobbling')
        # Get the Rhythmbox player object
        player = self.object.props.shell_player

        # Get the currently playing entry
        entry = player.get_playing_entry()

        # Check if an entry is currently playing
        if entry is not None:
            # Get the URL of the currently playing entry
            config: Config = self.load_config()
            for prop in PROP:
                try:
                    logging.error(entry.get_string(prop))
                except:
                    pass
            radio_url = entry.get_string(RB.RhythmDBPropType.URL)
            config.radios.insert(0, Radio('Playing now', radio_url))
            logging.error(config.json())
            # Call the RadioScrobbler listen method with the radio URL
            RadioScrobbler(config=self.plugin.config).start_scrobbling()
        else:
            # No radio currently playing
            print("No radio currently playing")


    def do_deactivate(self):
        self.shell.props.application.remove_action("start_scrobbling")

        if self.config_dialog:
            self.config_dialog.close()
            self.config_dialog = None

    def load_config(self):
        config_path = self.get_config_path()

        if config_path.exists():
            with open(config_path, 'r') as config_file:
                config_data = yaml.safe_load(config_file)
            return Config(**config_data)
        else:
            raise FileNotFoundError('Config not found')

    def get_config_path(self):
        config_dir = self.plugin_info.get_module_dir()
        return Path(config_dir) / 'scrobbler.yaml'
