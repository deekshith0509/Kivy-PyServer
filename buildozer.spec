[app]

# (str) Title of your application
title = pyServer

# (str) Package name
package.name = server

# (str) Package domain (needed for android/ios packaging)
package.domain = com.share

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (leave empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas
fullscreen=0 
# (str) Application versioning (method 1)
version = 1.0

# (list) Application requirements
# CRITICAL: Added hostpython3 and fixed order

requirements = python3==3.10.0,hostpython3==3.10.0,kivy,kivymd==1.1.1,pillow,qrcode,plyer,materialyoucolor,exceptiongroup,asyncgui,asynckivy,urllib3,requests,pyjnius,setuptools,android

android.permissions = MANAGE_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INTERNET,READ_MEDIA_IMAGES,READ_MEDIA_VIDEO,READ_MEDIA_AUDIO,POST_NOTIFICATIONS,FOREGROUND_SERVICE,WAKE_LOCK


# (str) Presplash of the application
presplash.filename = presplash.png

# (str) Icon of the application
icon.filename = icon.png

# (list) Supported orientations
orientation = portrait



# CRITICAL FIX: Update to API 34 (was 31, needs 33+)
# (int) Target Android API, should be as high as possible.
android.api = 34

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (int) Android SDK version to use (match api level)
android.sdk = 34

# (str) Android NDK version to use
android.ndk = 25b

# (int) Android NDK API to use. This is the minimum API your app will support
android.ndk_api = 21

# (bool) Use --private to avoid copying dependencies into APK
#android.add_assets = False

# (str) Android entry point, default is ok for Kivy-based app
android.entrypoint = org.kivy.android.PythonActivity

# (str) Full name including package path of the Java class that implements Android Activity
android.activity_class_name = org.kivy.android.PythonActivity

# (list) Android architecture to build for
android.archs = arm64-v8a

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# CRITICAL: Enable AndroidX support (required for appcompat)
android.enable_androidx = True

# (list) Android Gradle dependencies to add
# CRITICAL: Compatible versions for API 34
# (bool) Add SDK Manager available packages and update them
android.accept_sdk_license = True

# CRITICAL: Prevent wakelock issues
#android.wakelock = False
android.wakelock = True
android.foreground = True
android.allow_backup = True
android.keep_alive = True

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (bool) Android logcat only display log for activity's pid
android.logcat_pid_only = False

# (int) overrides automatic versionCode computation (used in manifest)
#android.numeric_version = 1

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning for deprecated flags
warn_on_deprecated_flags = True

# (bool) Display warnings when building with NDK API 21+
warn_on_ndk_api_21 = False

