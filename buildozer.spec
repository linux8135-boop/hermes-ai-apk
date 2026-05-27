[app]

# (str) Title of your application
title = Hermes AI

# (str) Package name
package.name = hermes-ai

# (str) Package domain (needs at least 2 dots)
package.domain = com.nous

# (str) Version of your app
version = 1.0.0

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (patterns)
source.include_exts = py,png,jpg,kv,atlas

# (list) List of inclusions (patterns)
source.include_patterns = assets/*

# (list) List of requirements (pip packages)
requirements = python3,kivy,websockets,requests

# (str) Presplash of the application
presplash.filename = assets/icon-48.png

# (str) Icon of the application
icon.filename = assets/icon.png

# (str) Supported orientation
orientation = portrait

# (list) List of service to declare
services = HermesGateway:service.py:foreground

# (bool) Indicate if the application is fullscreen or not
fullscreen = 0

# (list) Android permissions
android.permissions = INTERNET, ACCESS_NETWORK_STATE, POST_NOTIFICATIONS, FOREGROUND_SERVICE, RECEIVE_BOOT_COMPLETED, WAKE_LOCK, VIBRATE

# (int) Target Android API
android.api = 34

# (int) Minimum API
android.minapi = 24

# (str) Android NDK version
android.ndk = 28c

# (bool) Use --private-data-storage for Android 11+
android.private_storage = True

# (bool) Enable AndroidX support
android.enable_androidx = True

# (bool) Accept Android SDK licenses automatically
android.accept_sdk_license = True

# (list) Android archs to build for
android.archs = arm64-v8a

# (str) Specific Android SDK tools version
android.sdk_tools_version = 34.0.0

# (str) Android activity to launch
android.launch_activity = org.kivy.android.PythonActivity

# (bool) Use Gradle
android.gradle = True

# (str) Gradle version
android.gradle_version = 8.7

# (str) Path to custom AndroidManifest.xml
android.manifest = %(source.dir)s/android/AndroidManifest.xml

# (bool) Enable verbose build
android.verbose = True

# (str) Java maximum heap size
android.java_max_heap = 2048M

# (str) Python version
python.version = 3.14

[buildozer]

# (int) Log level (0-2)
log_level = 2

# (str) Build directory
build_dir = ./.buildozer

# (str) Output APK directory
bin_dir = ./bin
