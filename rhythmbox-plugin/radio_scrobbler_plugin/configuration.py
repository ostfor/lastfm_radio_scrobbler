import gi
import yaml

from gi.repository import Gtk, GObject, PeasGtk
from pathlib import Path
from lf_scrobbler.config_schema import Config

gi.require_version('Gtk', '3.0')

CONFIG_TEMPLATE = """
# Example YAML config template:
lastfm:
  api_key: YOUR_API_KEY
  shared_secret: YOUR_SHARED_SECRET
  user_name: YOUR_USER_NAME
  md5_password: YOUR_MD5_PASSWORD
radios:
  - name: Radio 1
    stream_url: http://radio1.com/stream
spotify:
  spotify_playlist_id: ID
  client_id: YOUR_CLIENT_ID
  client_secret: YOUR_CLIENT_SECRET
  redirect_url: URL
"""

class RadioScrobblerConfigurable(GObject.Object, PeasGtk.Configurable):
    __gtype_name__ = 'RadioScrobblerConfigurable'

    def __init__(self):
        GObject.Object.__init__(self)
        self.config_widget = None
        self.config_textview = None
        self.config = None
        self.plugin_info = None

    def do_create_configure_widget(self):
        if self.config_widget is None:
            self.config_widget = self.build_config_widget()
        return self.config_widget

    def build_config_widget(self):
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        label = Gtk.Label(label="Configuration:")
        vbox.pack_start(label, False, False, 0)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_hexpand(True)
        scrolled_window.set_vexpand(True)

        self.config_textview = Gtk.TextView()
        self.config_textview.set_wrap_mode(Gtk.WrapMode.WORD)
        scrolled_window.add(self.config_textview)

        vbox.pack_start(scrolled_window, True, True, 0)

        # Creating a save button for writing back the changes to the YAML file
        save_button = Gtk.Button(label='Save')
        save_button.connect('clicked', self.apply_config)
        vbox.pack_start(save_button, False, False, 0)

        self.load_config()

        return vbox

    def load_config(self):
        config_path = self.get_config_path()

        if config_path.exists():
            with open(config_path, 'r') as config_file:
                config_text = config_file.read()
                buffer = self.config_textview.get_buffer()
                buffer.set_text(config_text)
        else:
            buffer = self.config_textview.get_buffer()
            buffer.set_text(CONFIG_TEMPLATE)

    def validate_config(self, config_text):
        try:
            data = yaml.safe_load(config_text)
            self.config = Config(**data)
        except Exception as err:
            raise ValueError(f'Config is not valid.\nDetails: {err}')

        if not self.config:
            raise ValueError('Config is not valid or empty')
    def apply_config(self, widget):
        buffer = self.config_textview.get_buffer()
        start_iter, end_iter = buffer.get_bounds()
        config_text = buffer.get_text(start_iter, end_iter, True)

        self.validate_config(config_text)

        with open(self.get_config_path(), 'w') as config_file:
            config_file.write(config_text)

    # def apply_config(self):
    #     buffer = self.config_textview.get_buffer()
    #     start_iter, end_iter = buffer.get_bounds()
    #     config_text = buffer.get_text(start_iter, end_iter, True)

    #     self.validate_config(config_text)

    #     with open(self.get_config_path(), 'w') as config_file:
    #         config_file.write(config_text)

    def get_config_path(self):
        config_dir = self.plugin_info.get_module_dir()
        return Path(config_dir) / 'scrobbler.yaml'
