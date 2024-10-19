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

# (bool) Use --debug to enable debug mode
debug = 1

# (str) Android NDK version
# (str) Android NDK version
#android.ndk = 25b  # Use the version you prefer


# (str) Android SDK path (commented out to let Buildozer install it)
# android.sdk_path = ~/.buildozer/android/platform/android-sdk

# (str) Android NDK path (commented out to let Buildozer install it)
# android.ndk_path = ~/.buildozer/android/platform/android-ndk-r25b

# Uncomment this line only if you have a specific source directory for p4a
# p4a.source_dir =
