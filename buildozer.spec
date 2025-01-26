[app]
title = pyServer
package.name = server
package.domain = com.share
source.main = main.py
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,dm
requirements = python3,kivy,qrcode,plyer,kivymd==2.0.0,materialyoucolor,exceptiongroup,asyncgui,asynckivy,Pillow,urllib3,requests,pyjnius,setuptools,libffi
orientation = portrait
presplash.filename = presplash.png  
icon.filename = icon.png
fullscreen = 0
android.archs = arm64-v8a
android.release_artifact = apk
android.accept_sdk_license = True
android.api = 33
android.ndk = 27c
android.minapi=23
android.presplash_color = #FFFFFF
android.permissions = MANAGE_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET, READ_MEDIA_IMAGES, READ_MEDIA_VIDEO, READ_MEDIA_AUDIO
# Versioning
version = 0.2

# Debug mode
debug = 1

[buildozer]
log_level = 2
warn_on_root = 1

android.allow_backup = True
android.logcat = True