# Sound Blanket 🎧🌧️

A **KivyMD-based ambient sound mixer** for Android and desktop — inspired by the amazing [Blanket](https://github.com/rafaelmardojai/blanket) app for GNOME.

Create relaxing, focused environments using layered ambient sounds like rain, wind, birds, and more.

---

## ✨ Features

- 🎵 **Sound Mixer** – Combine multiple ambient sounds with volume sliders.
- 💾 **Save & Load Mixes** – Store your favorite soundscapes.
- 🔁 **Loop Playback** – All sounds loop seamlessly.
- 🪄 **Beautiful UI** – Powered by [KivyMD](https://github.com/kivymd/KivyMD) using Material Design.
- 📱 **Android-Ready** – Foreground service support and native `MediaPlayer` integration.
- 🌐 **Cross-platform** – Runs on Android, Windows, Linux, and macOS (via Kivy).

---

## 📦 Installation

### Clone and run:
```bash
git clone https://github.com/deekshith0509/kivy-sound-blanket.git
cd kivy-sound-blanket
pip install -r requirements.txt
python main.py
```
Or build an APK using Buildozer to run on Android.

## 📁 Folder Structure
```
kivy-sound-blanket/
│
├── main.py               # App entry point
├── sounds/               # Ambient audio files
├── data/mixes.json       # User-saved sound mixes
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

## 🛠️ Tech Stack
- Kivy
- KivyMD
- Pyjnius
- Android SDK (for native builds)

## 🙏 Acknowledgements

This project is deeply inspired by:
    [Blanket](https://github.com/rafaelmardojai/blanket) by [@rafaelmardojai](https://github.com/rafaelmardojai) — A beautiful GTK-based ambient app for GNOME.

Huge thanks to the entire Blanket team and contributors for the concept, UI inspiration, and motivation behind this project.

### If you use GNOME, definitely check out the original Blanket on Flathub!

