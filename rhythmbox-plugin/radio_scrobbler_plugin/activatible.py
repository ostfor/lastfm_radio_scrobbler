import csv
import datetime
import logging
import yaml
from pathlib import Path
# from lf_scrobbler.lastfm_radio_scrobble import RadioScrobbler
# from lf_scrobbler.config_schema import Config, Radio

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Peas, Gio, Gtk, Gdk
# from gi.repository import RB



class TrackListWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Track List")
        self.set_default_size(350, 400)

        vbox = Gtk.VBox(spacing=10)  # Create a vertical box container

        # Add instruction label
        instruction_label = Gtk.Label()
        instruction_label.set_text("Double click on Srobble emoji (🎵)")
        vbox.pack_start(instruction_label, False, False, 0)

        self.tree_view = Gtk.TreeView()
        self.tree_view.connect('row-activated', self.on_row_activated)
        vbox.pack_start(self.tree_view, True, True, 0)

        # Add the Status column
        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Srobble", renderer_text, text=0)
        self.tree_view.append_column(column_text)

        # Add the Track column
        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn("Track", renderer_text, text=1)
        self.tree_view.append_column(column_text)

        self.add(vbox)

        self.load_tracks(Path('~/tracks.csv').expanduser())

    def load_tracks(self, fname):
        self.list_store = Gtk.ListStore(str, str)

        with open(fname, 'r') as csv_file:
            reader = csv.reader(csv_file)
            sorted_list = sorted(reader, key=lambda row: datetime.datetime.strptime(row[0], '%Y-%m-%d'), reverse=True)
            for row in sorted_list:
                self.list_store.append(["🎵", row[1]])

        self.tree_view.set_model(self.list_store)

    def on_row_activated(self, tree_view, path, column):
        if column.get_title() == 'Status':
            tree_iter = self.list_store.get_iter(path)
            self.list_store.set_value(tree_iter, 0, "✅")
            self.tree_view.set_cursor(path, column, start_editing=False)
            track = self.list_store.get_value(tree_iter, 1)
            self.on_scrobble_button_clicked(track)

    def on_scrobble_button_clicked(self, track):
        logging.error('Click')
        # You can implement your scrobbling logic here

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

    def on_scrobble_button_clicked(self, action, parameter):
        win = TrackListWindow()
        win.connect("delete-event", Gtk.main_quit)
        win.show_all()
        Gtk.main()

    def do_activate(self):
        # Get the main window from the shell
        app = self.object.props.application

        # Add the action to an action group
        app.add_action(self.action)

        item = Gio.MenuItem()
        item.set_label("Scrobble Radio")
        item.set_detailed_action('app.start_scrobbling')
        app.add_plugin_menu_item('tools', 'scrobble-radio', item)




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

if __name__ == "__main__":
    win = TrackListWindow()
    win.connect("delete-event", Gtk.main_quit)
    win.show_all()
    Gtk.main()