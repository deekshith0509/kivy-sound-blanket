[app]
title = Ambient Sounds
package.name = ambientsounds
package.domain = org.deekshith
source.dir = .
source.include_exts = py,ogg,png
include_dirs = sounds
version = 1.0
requirements = python3,kivy,pyjnius,plyer,kivymd


orientation = portrait
fullscreen = 0

presplash.filename = splash.png
icon.filename = icon.png


android.permissions = INTERNET
android.archs = arm64-v8a
android.ndk = 25b
android.api = 33
android.release_artifact = apk
debug = 1

android.allow_backup = True
android.logcat = True
log_level = 2
