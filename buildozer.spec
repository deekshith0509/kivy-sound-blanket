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


android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE,READ_MEDIA_IMAGES,READ_MEDIA_VIDEO,READ_MEDIA_AUDIO
android.archs = arm64-v8a
android.ndk = 25b
android.api = 33
android.release_artifact = apk
debug = 0

android.allow_backup = True
android.logcat = True
log_level = 2
