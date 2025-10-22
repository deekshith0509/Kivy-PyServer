[app]
title = pyServer
package.name = server
package.domain = com.share
source.main = main.py
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,dm

# Python requirements
requirements = python3==3.10,kivy,qrcode,plyer,kivymd==1.1.1,materialyoucolor,exceptiongroup,asyncgui,asynckivy,Pillow,urllib3,requests,pyjnius,setuptools,libffi

# Display settings
orientation = portrait
presplash.filename = presplash.png  
icon.filename = icon.png
fullscreen = 0

# Android specific settings
android.archs = arm64-v8a
android.release_artifact = apk
android.accept_sdk_license = True
android.api = 33
android.ndk = 25.2.9519653
android.sdk.build_tools = 33.0.2
android.presplash_color = #FFFFFF
android.permissions = MANAGE_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, INTERNET, READ_MEDIA_IMAGES, READ_MEDIA_VIDEO, READ_MEDIA_AUDIO

# Java settings
android.java_version = 17

# Versioning
version = 0.2
debug = 1

# SDK and NDK paths - CRITICAL
android.sdk_path = /home/runner/.buildozer/android/platform/android-sdk
android.ndk_path = /home/runner/.buildozer/android/platform/android-sdk/ndk/25.2.9519653

[buildozer]
log_level = 2
warn_on_root = 1
android.allow_backup = True
android.logcat = True
android.deploy = false
