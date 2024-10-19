[app]
title = pyServer
package.name = server
android.archs = arm64-v8a
package.domain = com.share
source.main = main.py
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,dm
orientation = portrait
requirements = python3,kivy,qrcode,plyer,kivymd,materialyoucolor,exceptiongroup,asyncgui,asynckivy,Pillow,urllib3,requests,pyjnius,setuptools,libffi
fullscreen = 0
version = 0.1
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.release_artifact = apk
android.presplash_color = #FFFFFF
debug = 1
android.allow_backup = True
android.manifest.exclude = extractNativeLibs
android.logcat = True
#android.add_activities = org.kivy.android.PythonActivity

# Uncomment these lines if you need to specify paths
# android.sdk_path = /path/to/android-sdk
# android.ndk_path = /path/to/android-ndk-r25b

# Specify NDK version if needed
android.ndk = 25b

# Increase log level for more details
log_level = 2
