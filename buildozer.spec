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

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*,images/*.png

# (list) Source files to exclude (leave empty to not exclude anything)
#source.exclude_exts = spec

# (list) List of directory to exclude (leave empty to not exclude anything)
#source.exclude_dirs = tests, bin, venv

# (list) List of exclusions using pattern matching
# Do not prefix with './'
#source.exclude_patterns = license,images/*/*.jpg

# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3==3.10,kivy,qrcode,plyer,kivymd==1.1.1,materialyoucolor,exceptiongroup,asyncgui,asynckivy,Pillow,urllib3,requests,pyjnius,setuptools

# (str) Custom Source folders to find application addons
# Sets custom source folders, bases on working dir.
#source.include_exts = py,png,jpg,kv,atlas

# (list) List of directories to exclude from packaging
#source.exclude_dirs = tests, bin, venv

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (list) Supported orientations
# Valid options are: landscape, portrait, portrait-reverse or sensor (default)
orientation = portrait

# (list) OS specific permissions
# Android permissions can be found here: https://developer.android.com/reference/android/Manifest.permission
#android.permissions = INTERNET

# (list) features (adds uses-feature -tags to manifest)
#android.features = 

# (int) Target Android API, should be as high as possible.
#android.api = 31

# (int) Minimum API your APK / AAB will support.
#android.minapi = 21

# (int) Android SDK version to use
#android.sdk = 20

# (str) Android NDK version to use
#android.ndk = 25b

# (int) Android NDK API to use. This is the minimum API your app will support, it should usually match android.minapi.
#android.ndk_api = 21

# (bool) Use --private to avoid copying dependencies into APK
#android.add_assets = False

# (str) Android entry point, default is ok for Kivy-based app
#android.entrypoint = org.kivy.android.PythonActivity

# (str) Full name including package path of the Java class that implements Android Activity
#android.activity_class_name = org.kivy.android.PythonActivity

# (str) Android service Python class to use, defaults to python3
#android.service_class_name = org.kivy.android.PythonService

# (list) Android logcat filters to use
#android.logcat_filters = *:S python:D

# (bool) Android logcat only display log for activity's pid
#android.logcat_pid_only = False

# (str) Android additional adb arguments
#android.adb_args = -H host.docker.internal

# (bool) Copy library instead of making a libpymodules.so
#android.copy_libs = False

# (list) Android AAR archives to add
#android.add_aars =

# (list) Android Gradle dependencies to add
#android.gradle_dependencies = 

# (bool) Enable AndroidX support. Enable when 'android.gradle_dependencies' contains
# an 'androidx' package, or any package from Kotlin source.
#android.enable_androidx = False

# (list) Android gradle dependencies to add
#android.gradle_dependencies = 

# (bool) add --enable-auto-macos-autoloading flag
#macos.autoloading = False

# (list) Permissions
# (See https://python-for-android.readthedocs.io/en/latest/buildoptions/#build-options-1 for all the available Permissions)
#android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INTERNET

# (list) Android architecture to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
#android.archs = arm64-v8a, armeabi-v7a

# (int) overrides automatic versionCode computation (used in manifest)
#android.numeric_version = 1

# (bool) enables Android Debug Bridge (adb) tunneling over USB for access to device (or emulator) from CI
#android.tunnel_ssh = False

# (str) APK manifest.xml to use (generated if empty)
#android.manifest_manifest = 

# (str) Full path to android manifest.xml file to use (override android.manifest_manifest)
#android.manifest_path = 

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning for deprecated flags
#warn_on_deprecated_flags = True

# (bool) Display warnings when building with NDK API 21+
#warn_on_ndk_api_21 = False

# (str) Path to .gradle directory (default ~/.gradle)
#gradle_path = /path/to/.gradle

# (bool) Enable android maven repository
#android.enable_maven = True

# (str) Maven repository repository (e.g. https://repo1.maven.org/maven2)
#android.maven_repo = https://repo1.maven.org/maven2

# (bool) ADD SDK Manager available packages and update them
android.accept_sdk_license = True

# (int) Rebuild the compiler toolchain if version changed
#android.p4a_branch = master

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
#android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
#android.sdk_path =

# (str) ANT directory (if empty, it will be automatically downloaded.)
#ant_path =

# (bool) If True, then skip trying to update the Android sdk
#android.skip_update = False

# (bool) If True, then automatically accept sdk license agreements
#android.accept_sdk_license = False

# (str) Android entry point, default is ok for Kivy-based app
#android.entrypoint = org.kivy.android.PythonActivity

# (str) Full name including package path of the Java class that implements Android Activity
#android.activity_class_name = org.kivy.android.PythonActivity

# (str) Android service Python class to use, defaults to python3
#android.service_class_name = org.kivy.android.PythonService

# (list) Android logcat filters to use
#android.logcat_filters = *:S python:D

# (bool) Android logcat only display log for activity's pid
#android.logcat_pid_only = False

# (str) path to a custom whitelist file
#android.whitelist =

# (str) path to a custom blacklist file
#android.blacklist =

# (str) path to a custom whitelist file
#android.whitelist_src =

# (str) path to a custom blacklist file
#android.blacklist_src =

# (list) List of Java .jar files to add to the libs so that pyjnius can access their classes
#android.add_jars = foo.jar,bar.jar

# (list) List of Java files to add to the android project (can be java or a directory containing the files)
#android.add_src =

# (list) Android AAR archives to add (https://developer.android.com/studio/projects/add-aar)
#android.add_aars =

# (list) Gradle dependencies to add (https://developer.android.com/studio/build/dependencies)
#android.gradle_dependencies =

# (bool) add --enable-auto-macos-autoloading flag
#macos.autoloading = False

# (list) Files to include in the APK as assets, separated by ':'
#android.add_assets =

# (bool) Auto-generate gradle.properties if missing
#android.generate_gradle_properties = True

# (bool) Enable proguard to shrink the final apk
#android.proguard.enable = False

# (bool) Enable multidex
#android.enable_multidex = True

# (list) Android TV showable launchers
#android.tv_launchers = 

# (list) Android TV activities
#android.tv_activities = 

# (bool) Enable AndroidX support. Enable when 'android.gradle_dependencies' contains
# an 'androidx' package, or any package from Kotlin source.
#android.enable_androidx = False

[android]

# (str) Android logcat filters to use
logcat_filters = *:S python:D

# (str) Android entry point, default is ok for Kivy-based app
entrypoint = org.kivy.android.PythonActivity

# (str) Android APK directory
apk_dir = ./bin

# (list) Android architecture to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
archs = arm64-v8a

# (int) Target Android API, should be as high as possible.
api = 33

# (int) Minimum API your APK / AAB will support.
minapi = 21

# (int) Android SDK version to use
sdk = 33

# (str) Android NDK version to use
ndk = 25b

# (bool) Use --private to avoid copying dependencies into APK
copy_libs = 1

# (list) Android permissions
permissions = INTERNET

# (list) Android features (adds uses-feature -tags to manifest)
features = 

# (int) overrides automatic versionCode computation (used in manifest)
# numeric_version = 1

# (bool) enable AndroidX support. Enable when 'android.gradle_dependencies'
# contains an 'androidx' package, or any package from Kotlin source.
enable_androidx = False

# (str) Android manifest XML file to use (if empty, it will be generated by python-for-android)
manifest = 

# (str) Full path to android manifest.xml file to use (override android.manifest)
# manifest_path = 


