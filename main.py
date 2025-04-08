import os, json
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ObjectProperty
from kivy.uix.scrollview import ScrollView
from kivy.storage.jsonstore import JsonStore
from kivy.utils import platform

# Import KivyMD modules
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDIconButton, MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.tab import MDTabsBase, MDTabs
from kivymd.uix.list import OneLineAvatarIconListItem, IconLeftWidget

# -----------------------------------------------------------------------------
# Native Audio Implementation (Compatible with Android and Other Platforms)
# -----------------------------------------------------------------------------
class AndroidAudio:
    def __init__(self, sound_path):
        self.sound_path = sound_path
        self.volume = 0.7
        self.loop = False
        self.is_prepared = False
        self.sound = None
        self.player = None

        if platform == 'android':
            self._init_android_player()
        else:
            from kivy.core.audio import SoundLoader
            self.sound = SoundLoader.load(sound_path)
            if self.sound:
                self.sound.volume = self.volume
                self.sound.loop = self.loop

    def _init_android_player(self):
        try:
            from jnius import autoclass
            MediaPlayer = autoclass('android.media.MediaPlayer')
            File = autoclass('java.io.File')
            Uri = autoclass('android.net.Uri')
            Context = autoclass('org.kivy.android.PythonActivity').mActivity

            self.player = MediaPlayer()
            file = File(self.sound_path)
            uri = Uri.fromFile(file)
            self.player.setDataSource(Context, uri)
            self.player.setLooping(self.loop)
            self.player.setVolume(self.volume, self.volume)
            self.player.prepare()
            self.is_prepared = True
        except Exception as e:
            print(f"Error initializing Android player: {e}")

    def play(self):
        if platform == 'android':
            if self.player and self.is_prepared:
                try:
                    self.player.start()
                except Exception as e:
                    print(f"Error playing Android audio: {e}")
        else:
            if self.sound:
                self.sound.play()

    def stop(self):
        if platform == 'android':
            if self.player:
                try:
                    self.player.pause()
                    self.player.seekTo(0)
                except Exception as e:
                    print(f"Error stopping Android audio: {e}")
        else:
            if self.sound:
                self.sound.stop()

    def set_volume(self, volume):
        self.volume = volume
        if platform == 'android':
            if self.player:
                try:
                    self.player.setVolume(volume, volume)
                except Exception as e:
                    print(f"Error setting Android volume: {e}")
        else:
            if self.sound:
                self.sound.volume = volume

    def set_loop(self, loop):
        self.loop = loop
        if platform == 'android':
            if self.player:
                try:
                    self.player.setLooping(loop)
                except Exception as e:
                    print(f"Error setting Android loop: {e}")
        else:
            if self.sound:
                self.sound.loop = loop

    def release(self):
        if platform == 'android':
            if self.player:
                try:
                    self.player.release()
                    self.player = None
                    self.is_prepared = False
                except Exception as e:
                    print(f"Error releasing Android player: {e}")
        else:
            if self.sound:
                self.sound.unload()
                self.sound = None

# -----------------------------------------------------------------------------
# SoundTile – Represents an individual audio clip as a modern card widget.
# -----------------------------------------------------------------------------
class SoundTile(MDCard):
    volume = NumericProperty(0.7)
    sound_name = StringProperty("")
    is_playing = BooleanProperty(False)
    sound = ObjectProperty(None, allownone=True)
    sound_path = StringProperty("")

    def __init__(self, sound_path, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint = (None, None)
        self.size = (dp(150), dp(200))
        self.elevation = 8
        self.radius = [10,]
        self.padding = dp(10)
        self.spacing = dp(10)
        self.sound_path = sound_path

        # Format sound name from filename.
        basename = os.path.basename(sound_path)
        self.sound_name = os.path.splitext(basename)[0].replace("-", " ").title()

        # Header: Sound title.
        self.title_label = MDLabel(text=self.sound_name, halign="center", theme_text_color="Primary")
        self.add_widget(self.title_label)

        # Central play/pause button.
        # Replace the invalid property "user_font_size" with the valid "icon_size"
        self.play_btn = MDIconButton(icon="play-circle-outline", icon_size=sp(48), pos_hint={"center_x": 0.5})
        self.play_btn.bind(on_release=self.toggle_sound)
        self.add_widget(self.play_btn)

        # Volume slider with label.
        vol_layout = MDBoxLayout(orientation="vertical", size_hint_y=None, height=dp(60))
        self.vol_label = MDLabel(text="Volume", halign="center", font_style="Caption")
        vol_layout.add_widget(self.vol_label)
        from kivymd.uix.slider import MDSlider
        self.slider = MDSlider(min=0, max=1, value=self.volume)
        self.slider.bind(value=self.on_volume_change)
        vol_layout.add_widget(self.slider)
        self.add_widget(vol_layout)

        Clock.schedule_once(lambda dt: self.load_sound(), 0.1)

    def load_sound(self):
        if self.sound is not None:
            return
        try:
            self.sound = AndroidAudio(self.sound_path)
            if self.sound:
                self.sound.set_loop(True)
                self.sound.set_volume(self.volume)
        except Exception as e:
            print(f"Error loading sound {self.sound_path}: {e}")
            Clock.schedule_once(lambda dt: self.load_sound(), 1.0)

    def toggle_sound(self, instance):
        if self.is_playing:
            self.stop()
        else:
            self.play()

    def on_volume_change(self, instance, value):
        self.volume = value
        if self.sound:
            self.sound.set_volume(value)

    def play(self):
        if not self.sound:
            self.load_sound()
        if self.sound:
            self.sound.set_loop(True)
            self.sound.set_volume(self.volume)
            self.sound.play()
            self.is_playing = True
            self.play_btn.icon = "pause-circle-outline"

    def stop(self):
        if self.sound and self.is_playing:
            self.sound.stop()
            self.is_playing = False
            self.play_btn.icon = "play-circle-outline"

    def get_state(self):
        return {
            "sound_name": self.sound_name,
            "is_playing": self.is_playing,
            "volume": self.volume,
        }

    def set_state(self, state):
        if "volume" in state:
            self.volume = state["volume"]
            self.slider.value = state["volume"]
            if self.sound:
                self.sound.set_volume(state["volume"])
        if state.get("is_playing", False):
            if not self.sound:
                self.load_sound()
            Clock.schedule_once(lambda dt: self.play(), 0.2)
        else:
            self.stop()

    def release_resources(self):
        if self.sound:
            self.stop()
            self.sound.release()
            self.sound = None

# -----------------------------------------------------------------------------
# SavedMixItem – A list item representing a saved mix in the Mixes tab.
# -----------------------------------------------------------------------------
class SavedMixItem(OneLineAvatarIconListItem):
    mix_name = StringProperty("")

    def __init__(self, mix_name, app, **kwargs):
        super().__init__(**kwargs)
        self.mix_name = mix_name
        self.app = app
        self.text = mix_name

        load_icon = IconLeftWidget(icon="playlist-music")
        self.add_widget(load_icon)

        delete_btn = MDIconButton(icon="delete", theme_text_color="Error")
        delete_btn.bind(on_release=self.delete_mix)
        self.add_widget(delete_btn)

    def on_release(self):
        self.app.load_mix(self.mix_name)

    def delete_mix(self, instance):
        self.app.delete_mix(self.mix_name)
        if self.parent:
            self.parent.remove_widget(self)

# -----------------------------------------------------------------------------
# Custom Tab Widgets (for Sounds and Mixes)
#
# Each custom tab includes a "title" property so that MDTabs displays a valid label.
# -----------------------------------------------------------------------------
class SoundsTab(MDBoxLayout, MDTabsBase):
    title = StringProperty("")  # Used by MDTabs for the tab label

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = dp(10)
        scroll = ScrollView()
        from kivy.uix.gridlayout import GridLayout
        self.grid = GridLayout(cols=2, padding=dp(10), spacing=dp(10), size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter("height"))
        scroll.add_widget(self.grid)
        self.add_widget(scroll)

    def add_sound_tile(self, tile):
        self.grid.add_widget(tile)

class MixesTab(MDBoxLayout, MDTabsBase):
    title = StringProperty("")  # Used by MDTabs for the tab label

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.spacing = dp(10)
        scroll = ScrollView()
        from kivy.uix.boxlayout import BoxLayout
        self.mix_list = BoxLayout(orientation="vertical", spacing=dp(5), size_hint_y=None)
        self.mix_list.bind(minimum_height=self.mix_list.setter("height"))
        scroll.add_widget(self.mix_list)
        self.add_widget(scroll)

    def add_mix_item(self, mix_item):
        self.mix_list.add_widget(mix_item)

# -----------------------------------------------------------------------------
# Main App Class – SoundBlanketApp
# -----------------------------------------------------------------------------
class SoundBlanketApp(MDApp):
    def build(self):
        self.title = "Sound Blanket"
        self.theme_cls.primary_palette = "DeepPurple"
        self.store = None
        self.sound_tiles = []
        self.dialog = None

        self.setup_storage()

        screen = MDScreen()

        # Top App Bar with action icons.
        from kivymd.uix.toolbar import MDTopAppBar
        self.top_bar = MDTopAppBar(
            title="Sound Blanket",
            pos_hint={"top": 1},
            elevation=10,
            left_action_items=[["menu", lambda x: None]],
            right_action_items=[
                ["stop-circle", lambda x: self.stop_all_sounds()],
                ["content-save", lambda x: self.show_save_mix_dialog()],
            ],
        )
        screen.add_widget(self.top_bar)

        # Create tabs for Sounds and Mixes.
        self.tabs = MDTabs(
            pos_hint={"top": 0.9},
            size_hint=(1, 0.9),
        )
        screen.add_widget(self.tabs)

        # Instantiate the Sounds tab and assign a title.
        self.sounds_tab = SoundsTab()
        self.sounds_tab.title = "Sounds"
        self.tabs.add_widget(self.sounds_tab)

        # Instantiate the Mixes tab and assign a title.
        self.mixes_tab = MixesTab()
        self.mixes_tab.title = "Mixes"
        self.tabs.add_widget(self.mixes_tab)

        Clock.schedule_once(lambda dt: self.setup_sounds(), 0.3)
        Clock.schedule_once(lambda dt: self.load_saved_mixes(), 0.5)
        self.setup_background_audio()

        return screen

    def setup_storage(self):
        if platform == "android":
            from android.storage import app_storage_path
            app_folder = os.path.join(app_storage_path(), "app")
        else:
            app_folder = os.getcwd()
        data_dir = os.path.join(app_folder, "data")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        self.store = JsonStore(os.path.join(data_dir, "mixes.json"))

    def setup_sounds(self):
        if platform == "android":
            from android.storage import app_storage_path
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
            app_folder = os.path.join(app_storage_path(), "app")
            sound_dir = os.path.join(app_folder, "sounds")
            if not os.path.exists(sound_dir):
                os.makedirs(sound_dir)
        else:
            sound_dir = os.path.join(os.getcwd(), "sounds")
        if os.path.exists(sound_dir):
            for filename in sorted(os.listdir(sound_dir)):
                if filename.lower().endswith((".ogg", ".wav", ".mp3")):
                    full_path = os.path.join(sound_dir, filename)
                    tile = SoundTile(sound_path=full_path)
                    self.sounds_tab.add_sound_tile(tile)
                    self.sound_tiles.append(tile)
        else:
            print(f"Sound directory not found: {sound_dir}")

    def load_saved_mixes(self):
        self.mixes_tab.mix_list.clear_widgets()
        try:
            for mix_name in self.store.keys():
                if mix_name == "last_session":
                    continue
                mix_item = SavedMixItem(mix_name=mix_name, app=self)
                self.mixes_tab.add_mix_item(mix_item)
        except Exception as e:
            print(f"Error loading saved mixes: {e}")

    def show_save_mix_dialog(self):
        if not self.dialog:
            from kivymd.uix.textfield import MDTextField
            self.mix_name_field = MDTextField(
                hint_text="Enter mix name", text="My Mix", pos_hint={"center_x": 0.5}, size_hint_x=0.8
            )
            self.dialog = MDDialog(
                title="Save Mix",
                type="custom",
                content_cls=self.mix_name_field,
                buttons=[
                    MDFlatButton(text="CANCEL", on_release=self.close_dialog),
                    MDRaisedButton(text="SAVE", on_release=self.do_save_mix),
                ],
            )
        self.dialog.open()

    def close_dialog(self, *args):
        if self.dialog:
            self.dialog.dismiss()

    def do_save_mix(self, *args):
        mix_name = self.mix_name_field.text.strip()
        if mix_name:
            mix_data = {"sounds": [tile.get_state() for tile in self.sound_tiles]}
            self.store.put(mix_name, **mix_data)
            self.top_bar.title = mix_name
            self.load_saved_mixes()
            self.close_dialog()

    def load_mix(self, mix_name):
        if self.store.exists(mix_name):
            self.stop_all_sounds()
            mix_data = self.store.get(mix_name)
            saved_sounds = mix_data.get("sounds", [])
            for saved_sound in saved_sounds:
                saved_name = saved_sound.get("sound_name", "").lower()
                for tile in self.sound_tiles:
                    if tile.sound_name.lower() == saved_name:
                        Clock.schedule_once(lambda dt, t=tile, s=saved_sound: t.set_state(s), 0.1)
                        break
            self.top_bar.title = mix_name

    def delete_mix(self, mix_name):
        if self.store.exists(mix_name):
            self.store.delete(mix_name)
            print(f"Deleted mix: {mix_name}")

    def stop_all_sounds(self):
        for tile in self.sound_tiles:
            if tile.is_playing:
                tile.stop()

    def setup_background_audio(self):
        if platform == "android":
            try:
                from jnius import autoclass
                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                activity = PythonActivity.mActivity
                activity.getWindow().addFlags(128)  # FLAG_KEEP_SCREEN_ON
                self.start_foreground_service()
            except Exception as e:
                print(f"Error setting up Android background audio: {e}")

    def start_foreground_service(self):
        if platform == "android":
            try:
                from jnius import autoclass
                PythonService = autoclass("org.kivy.android.PythonService")
                PythonActivity = autoclass("org.kivy.android.PythonActivity")
                Context = PythonActivity.mActivity.getApplicationContext()
                NotificationBuilder = autoclass("android.app.Notification$Builder")
                NotificationChannel = autoclass("android.app.NotificationChannel")
                NotificationManager = autoclass("android.app.NotificationManager")
                channel_id = "sound_blanket_channel"
                channel_name = "Sound Blanket"
                channel = NotificationChannel(channel_id, channel_name, NotificationManager.IMPORTANCE_LOW)
                notification_manager = Context.getSystemService(Context.NOTIFICATION_SERVICE)
                notification_manager.createNotificationChannel(channel)
                notification_builder = NotificationBuilder(Context, channel_id)
                notification_builder.setContentTitle("Sound Blanket")
                notification_builder.setContentText("Playing ambient sounds")
                notification_builder.setOngoing(True)
                notification_builder.setSmallIcon(Context.getApplicationInfo().icon)
                notification = notification_builder.build()
                service_args = ""
                PythonService.start(Context, "Sound Blanket Service", service_args)
                PythonService.mService.startForeground(101, notification)
                print("Foreground service started successfully")
            except Exception as e:
                print(f"Error starting foreground service: {e}")

    def on_pause(self):
        mix_data = {"sounds": [tile.get_state() for tile in self.sound_tiles]}
        self.store.put("last_session", **mix_data)
        return True

    def on_resume(self):
        for tile in self.sound_tiles:
            if tile.is_playing:
                tile.play()

    def on_stop(self):
        for tile in self.sound_tiles:
            tile.release_resources()

if __name__ == "__main__":
    SoundBlanketApp().run()
