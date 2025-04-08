from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.properties import ObjectProperty, NumericProperty, StringProperty
from kivy.storage.jsonstore import JsonStore
from kivy.utils import platform
from kivy.metrics import dp  # Use dp for dynamic sizing
import os
import json
from kivy.metrics import dp, sp


# Native Audio implementation with proper platform handling
class AndroidAudio:
    def __init__(self, sound_path):
        self.sound_path = sound_path
        self.player = None
        self.volume = 0.7
        self.loop = False
        self.is_prepared = False
        self.sound = None

        if platform == 'android':
            self._init_android_player()
        else:
            # Fallback to Kivy SoundLoader for non-Android platforms
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
                    # Reset position to beginning
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



class SoundTile(BoxLayout):
    volume = NumericProperty(0.7)
    sound_name = StringProperty("")

    def __init__(self, sound_path, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(5)
        self.spacing = dp(5)
        self.size_hint_y = None
        self.height = dp(120)  # Use dp for height

        self.sound_path = sound_path
        self.sound = None
        self.is_playing = False
        self.is_loading = False

        # Get the sound name from the filename
        self.sound_name = os.path.basename(sound_path)
        self.sound_name = self.sound_name.replace(".ogg", "").replace("-", " ").title()

        # Create the toggle button with sound name
        self.btn = ToggleButton(text=self.sound_name, size_hint_y=0.6, font_size='14sp')
        self.btn.bind(on_press=self.toggle_sound)
        self.add_widget(self.btn)

        # Create the volume slider with responsive layout
        slider_layout = BoxLayout(size_hint_y=0.4, spacing=dp(5))
        vol_label = Label(text="Volume:", size_hint_x=0.3, font_size='12sp')
        slider_layout.add_widget(vol_label)

        self.slider = Slider(min=0, max=1, value=self.volume, size_hint_x=0.7)
        self.slider.bind(value=self.on_volume_change)
        slider_layout.add_widget(self.slider)
        self.add_widget(slider_layout)

        # Load the sound immediately
        self.load_sound()

    def load_sound(self):
        """Load the sound file and prepare it for playback"""
        if self.sound is not None:
            return  # Already loaded

        self.is_loading = True
        try:
            self.sound = AndroidAudio(self.sound_path)
            if self.sound:
                self.sound.set_loop(True)
                self.sound.set_volume(self.volume)
                self.is_loading = False
        except Exception as e:
            print(f"Error loading sound {self.sound_path}: {e}")
            self.is_loading = False
            # Try loading again after a short delay
            Clock.schedule_once(lambda dt: self.load_sound(), 1.0)

    def toggle_sound(self, instance):
        """Toggle sound playback when button is pressed"""
        if self.is_loading:
            return  # Don't respond while loading

        if self.btn.state == 'down':
            self.play()
        else:
            self.stop()

    def on_volume_change(self, instance, value):
        """Handle volume slider changes"""
        self.volume = value
        if self.sound:
            self.sound.set_volume(value)

    def play(self):
        """Play the sound"""
        if self.is_loading:
            return  # Don't attempt to play while loading

        try:
            if not self.sound:
                # Immediately load and play
                self.load_sound()

            if self.sound:
                self.sound.set_loop(True)
                self.sound.set_volume(self.volume)
                self.sound.play()
                self.is_playing = True
                self.btn.state = 'down'  # Ensure button stays down
        except Exception as e:
            print(f"Error playing sound {self.sound_path}: {e}")
            # Try to recover by reloading
            self.sound = None
            Clock.schedule_once(lambda dt: self.load_sound(), 0.5)
            Clock.schedule_once(lambda dt: self.retry_play(), 1.0)

    def retry_play(self):
        """Retry playing sound after error recovery"""
        if self.btn.state == 'down' and not self.is_playing:
            self.play()

    def stop(self):
        """Stop the sound"""
        if self.sound and self.is_playing:
            self.sound.stop()
            self.is_playing = False
            self.btn.state = 'normal'  # Ensure button is up

    def on_pause(self):
        """Handle app pause"""
        # Store state when app is paused
        return self.is_playing

    def on_resume(self):
        """Handle app resume"""
        # Resume playback if it was playing before
        if self.is_playing and self.sound:
            self.play()  # Restart sound

    def get_state(self):
        """Return the current state for saving"""
        return {
            'sound_name': self.sound_name,
            'is_playing': self.is_playing,
            'volume': self.volume
        }

    def set_state(self, state):
        """Apply a saved state to this sound tile"""
        # First set volume as it affects playback
        if 'volume' in state:
            self.volume = state['volume']
            self.slider.value = state['volume']
            if self.sound:
                self.sound.set_volume(state['volume'])

        # Handle playback state
        should_play = state.get('is_playing', False)

        if should_play:
            # Force-load the sound if needed
            if not self.sound:
                self.load_sound()

            # Schedule playing after a small delay to allow loading
            Clock.schedule_once(lambda dt: self.force_play(), 0.1)
        else:
            self.btn.state = 'normal'
            self.stop()

    def force_play(self):
        """Force play even if already playing - used when loading states"""
        self.btn.state = 'down'
        self.is_playing = False  # Reset so play() works properly
        self.play()

    def release_resources(self):
        """Release resources properly"""
        if self.sound:
            self.stop()
            self.sound.release()
            self.sound = None




class SavedMix(BoxLayout):
    def __init__(self, name, app, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(50)
        self.app = app
        self.name = name

        # Create load button
        self.load_btn = Button(text=name, size_hint_x=0.7, font_size='14sp')
        self.load_btn.bind(on_press=self.load_mix)
        self.add_widget(self.load_btn)

        # Create delete button
        self.delete_btn = Button(text="X", size_hint_x=0.3, font_size='14sp')
        self.delete_btn.bind(on_press=self.delete_mix)
        self.add_widget(self.delete_btn)

    def load_mix(self, instance):
        self.app.load_mix(self.name)

    def delete_mix(self, instance):
        self.app.delete_mix(self.name)
        self.parent.remove_widget(self)

class BlanketApp(App):
    def build(self):
        # Create main layout with dynamic spacing
        self.root = BoxLayout(orientation='vertical', padding=dp(5), spacing=dp(5))

        # Create control panel
        control_panel = BoxLayout(size_hint_y=0.1, height=dp(60), padding=dp(5), spacing=dp(5))
        self.mix_name = Label(text="Current Mix", size_hint_x=0.4, font_size='16sp')
        control_panel.add_widget(self.mix_name)


        self.root.add_widget(control_panel)

        # Create content area (sounds + mixes)
        content = BoxLayout(orientation='horizontal', spacing=dp(5), padding=dp(5))

        # Left side - Sound Tiles
        sound_panel = BoxLayout(orientation='vertical', size_hint_x=0.7)
        scroll_view = ScrollView()
        self.layout = GridLayout(cols=2, padding=dp(10), spacing=dp(10), size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        scroll_view.add_widget(self.layout)
        sound_panel.add_widget(scroll_view)
        content.add_widget(sound_panel)

        # Right side - Saved Mixes
        mix_panel = BoxLayout(orientation='vertical', size_hint_x=0.3, padding=dp(5), spacing=dp(5))
        mix_label = Label(text="Saved Mixes", size_hint_y=0.1, font_size='16sp')
        mix_panel.add_widget(mix_label)

        mix_scroll = ScrollView()
        self.mix_layout = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.mix_layout.bind(minimum_height=self.mix_layout.setter('height'))
        mix_scroll.add_widget(self.mix_layout)
        mix_panel.add_widget(mix_scroll)
        content.add_widget(mix_panel)

        self.root.add_widget(content)
        # Bottom Controls
        bottom_controls = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(5), padding=dp(5))
        bottom_save_btn = Button(text="Save Mix", font_size=sp(14))
        bottom_save_btn.bind(on_press=self.save_current_mix)
        bottom_controls.add_widget(bottom_save_btn)

        bottom_stop_btn = Button(text="Stop All", font_size=sp(14))
        bottom_stop_btn.bind(on_press=self.stop_all_sounds)
        bottom_controls.add_widget(bottom_stop_btn)

        self.root.add_widget(bottom_controls)

        # Initialize storage
        self.setup_storage()

        # Setup sounds
        Clock.schedule_once(lambda dt: self.setup_sounds(), 0.5)

        # Load saved mixes
        self.load_saved_mixes()

        # Enable background audio
        self.setup_background_audio()

        return self.root

    def setup_storage(self):
        """Set up storage for saving and loading sound mixes"""
        if platform == 'android':
            from android.storage import app_storage_path
            app_folder = os.path.join(app_storage_path(), "app")
        else:
            app_folder = os.getcwd()

        # Create data directory if it doesn't exist
        data_dir = os.path.join(app_folder, 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        # Create store for saved mixes
        self.store = JsonStore(os.path.join(data_dir, 'mixes.json'))

    def setup_sounds(self):
        """Set up sound tiles"""
        # Determine sounds directory
        if platform == 'android':
            from android.storage import app_storage_path
            from android.permissions import request_permissions, Permission

            # Request necessary permissions
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ])

            app_folder = app_storage_path()
            sound_dir = os.path.join(app_folder, "app", "sounds")

            # Create sounds directory if it doesn't exist
            if not os.path.exists(sound_dir):
                os.makedirs(sound_dir)
                # Here you would copy default sounds to the directory
        else:
            sound_dir = os.path.join(os.getcwd(), "sounds")

        # Load sounds
        self.sound_tiles = []
        try:
            if os.path.exists(sound_dir):
                for filename in sorted(os.listdir(sound_dir)):
                    if filename.endswith((".ogg", ".wav", ".mp3")):
                        full_path = os.path.join(sound_dir, filename)
                        tile = SoundTile(sound_path=full_path)
                        self.layout.add_widget(tile)
                        self.sound_tiles.append(tile)
            else:
                print(f"Sound directory not found: {sound_dir}")
        except Exception as e:
            print(f"Error loading sounds: {e}")

    def load_saved_mixes(self):
        """Load saved mixes from storage"""
        try:
            for mix_name in self.store.keys():
                mix_widget = SavedMix(name=mix_name, app=self)
                self.mix_layout.add_widget(mix_widget)
        except Exception as e:
            print(f"Error loading saved mixes: {e}")

    def save_current_mix(self, instance):
        """Save the current mix of sounds and volumes"""
        from kivy.uix.popup import Popup
        from kivy.uix.textinput import TextInput

        # Create popup for mix name
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        text_input = TextInput(text="My Mix", multiline=False, font_size='14sp')
        content.add_widget(Label(text="Enter Mix Name:", font_size='14sp'))
        content.add_widget(text_input)

        save_button = Button(text="Save", font_size='14sp')
        content.add_widget(save_button)

        popup = Popup(title='Save Mix', content=content, size_hint=(0.8, 0.4))

        def do_save(instance):
            mix_name = text_input.text.strip()
            if mix_name:
                self.do_save_mix(mix_name)
                popup.dismiss()

        save_button.bind(on_press=do_save)
        popup.open()

    def do_save_mix(self, mix_name):
        """Actually save the mix with the given name"""
        # Collect current states of all sound tiles
        mix_data = {
            'sounds': [tile.get_state() for tile in self.sound_tiles]
        }

        # Save to storage
        self.store.put(mix_name, **mix_data)

        # Add to UI if not already there
        existing_mixes = [child.name for child in self.mix_layout.children if isinstance(child, SavedMix)]
        if mix_name not in existing_mixes:
            mix_widget = SavedMix(name=mix_name, app=self)
            self.mix_layout.add_widget(mix_widget)

        # Update current mix name
        self.mix_name.text = mix_name



    def load_mix(self, mix_name):
        """Load a saved mix and apply it to the current sound tiles"""
        try:
            if self.store.exists(mix_name):
                # First stop all sounds
                self.stop_all_sounds(None)

                # Get the saved mix data
                mix_data = self.store.get(mix_name)
                saved_sounds = mix_data.get('sounds', [])

                # Process each saved sound
                for saved_sound in saved_sounds:
                    saved_name = saved_sound.get('sound_name', '').lower()

                    # Find matching tile
                    for tile in self.sound_tiles:
                        if tile.sound_name.lower() == saved_name:
                            # Apply the saved state to this tile
                            # Use Clock.schedule_once to prevent UI freezing
                            Clock.schedule_once(
                                lambda dt, t=tile, s=saved_sound: t.set_state(s),
                                0.1
                            )
                            break

                # Update the mix name display
                self.mix_name.text = mix_name
        except Exception as e:
            print(f"Error loading mix '{mix_name}': {e}")



    def delete_mix(self, mix_name):
        """Delete a saved mix"""
        try:
            if self.store.exists(mix_name):
                self.store.delete(mix_name)
                print(f"Deleted mix: {mix_name}")
        except Exception as e:
            print(f"Error deleting mix '{mix_name}': {e}")

    def stop_all_sounds(self, instance):
        """Stop all currently playing sounds"""
        for tile in self.sound_tiles:
            if tile.is_playing:
                tile.btn.state = 'normal'
                tile.stop()

    def setup_background_audio(self):
        """Set up background audio service for Android"""
        if platform == 'android':
            try:
                from jnius import autoclass
                # Prevent screen from sleeping
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                activity = PythonActivity.mActivity

                # Keep screen on
                activity.getWindow().addFlags(128)  # FLAG_KEEP_SCREEN_ON

                # Set up foreground service for background audio
                self.start_foreground_service()

            except Exception as e:
                print(f"Error setting up Android background audio: {e}")

    def start_foreground_service(self):
        """Start a foreground service to keep audio playing in background"""
        if platform == 'android':
            try:
                from jnius import autoclass

                # Get the service and start it
                PythonService = autoclass('org.kivy.android.PythonService')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')

                # Create notification
                Context = PythonActivity.mActivity.getApplicationContext()
                NotificationBuilder = autoclass('android.app.Notification$Builder')
                Notification = autoclass('android.app.Notification')
                NotificationChannel = autoclass('android.app.NotificationChannel')
                NotificationManager = autoclass('android.app.NotificationManager')

                # Create channel
                channel_id = "sound_blanket_channel"
                channel_name = "Sound Blanket"
                channel = NotificationChannel(
                    channel_id,
                    channel_name,
                    NotificationManager.IMPORTANCE_LOW
                )

                # Get notification service
                notification_manager = Context.getSystemService(Context.NOTIFICATION_SERVICE)
                notification_manager.createNotificationChannel(channel)

                # Build notification
                notification_builder = NotificationBuilder(Context, channel_id)
                notification_builder.setContentTitle("Sound Blanket")
                notification_builder.setContentText("Playing ambient sounds")
                notification_builder.setOngoing(True)
                notification_builder.setSmallIcon(Context.getApplicationInfo().icon)

                # Create notification
                notification = notification_builder.build()

                # Start service
                service_args = ""
                PythonService.start(Context, "Sound Blanket Service", service_args)
                PythonService.mService.startForeground(101, notification)

                print("Foreground service started successfully")
            except Exception as e:
                print(f"Error starting foreground service: {e}")

    def on_pause(self):
        """Handle when app is sent to background"""
        print("App paused - saving state")
        # Auto-save current mix as 'last_session'
        mix_data = {
            'sounds': [tile.get_state() for tile in self.sound_tiles]
        }
        self.store.put('last_session', **mix_data)
        return True

    def on_resume(self):
        """Handle when app resumes from background"""
        print("App resumed - restoring audio streams")
        # Resume all playing sounds
        for tile in self.sound_tiles:
            if tile.is_playing:
                tile.on_resume()

    def on_stop(self):
        """Clean up resources when app is closed"""
        # Release all sound resources
        for tile in self.sound_tiles:
            tile.release_resources()

if __name__ == '__main__':
    BlanketApp().run()

