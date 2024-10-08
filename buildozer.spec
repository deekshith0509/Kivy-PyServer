[app]
title = pyServer
package.name = server
android.archs = arm64-v8a
package.domain = com.share
source.main = main.py
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
orientation = portrait
requirements = python3,kivy==2.1.0,qrcode,plyer,kivymd,materialyoucolor,exceptiongroup,asyncgui,asynckivy,Pillow,webbrowser,socketserver,http-server,urllib3,requests,pyjnius,setuptools,os,socket,platform,subprocess,threading,http,datetime,io,six,openssl
fullscreen = 0
version = 0.1
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.release_artifact = apk
android.presplash_color = #FFFFFF
p4a.source_dir = /mnt/c/Users/deeks/desktop/tools/softwares/python-for-android

# (bool) Use --debug to enable debug mode
debug = 1

# (str) Android NDK version
android.ndk = r25b

# (str) Android SDK path
android.sdk_path = ~/.buildozer/android/platform/android-sdk

# (str) Android NDK path
android.ndk_path = ~/.buildozer/android/platform/android-ndk-r25b
