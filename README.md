# ⚡ **Kivy-PyServer — Modern HTTP File Server for Android & Desktop**

> **Turn your Android device or PC into a fully functional, beautifully designed local web file server — powered by Python, Kivy, and KivyMD.**

**Kivy-PyServer** transforms your device into a **portable, private cloud**, enabling you to serve, browse, and download files instantly across your local network.
Compatible with **Android**, **Windows**, **Linux**, and **macOS**, it provides a simple, secure, and elegant file-sharing experience — **no internet or cloud dependency required.**

---

## 🌟 Key Features

* ✅ **Modern Material Design UI** — Built using **KivyMD**, with adaptive layouts and animations.
* ✅ **Full HTTP File Server** — Browse and download files or folders via any web browser.
* ✅ **Instant Folder ZIP Downloads** — Download entire directories as `.zip` archives.
* ✅ **Multi-Threaded Server Engine** — Powered by `ThreadedHTTPServer` for concurrent requests.
* ✅ **Auto IP Resolver** — Smart detection of Wi-Fi / hotspot / USB interfaces.
* ✅ **Real-Time Log Viewer** — Live-updating, filterable, and searchable logs.
* ✅ **QR Code Access** — Share instantly across devices with a scan.
* ✅ **Scoped Storage Safe** — Works seamlessly with Android 11+ file access policies.
* ✅ **Cross-Platform Support** — Fully functional on Android, Linux, macOS, and Windows.
* ✅ **Offline & Private** — No internet connection or third-party servers required.

---

## 🚀 Quick Start Guide

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/deekshith0509/Kivy-PyServer.git
cd Kivy-PyServer
```

### 2️⃣ (Optional) Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

For Android development (manual install):

```bash
pip install kivy kivymd qrcode pillow psutil plyer materialyoucolor asynckivy asyncgui requests urllib3
```

---

## 📱 Build for Android (API 34+)

You can package **Kivy-PyServer** into a native Android APK using **Buildozer**.

### Initialize Buildozer

```bash
buildozer init
```

### Update `buildozer.spec`

Below is the **optimized, API 34–ready configuration** (latest Android build standards):

```ini
[app]
title = pyServer
package.name = server
package.domain = com.share
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
fullscreen = 0
version = 0.1

# Dependencies (CRITICAL ORDER)
requirements = python3==3.10.0,hostpython3==3.10.0,kivy,kivymd==1.1.1,pillow,qrcode,plyer,materialyoucolor,exceptiongroup,asyncgui,asynckivy,urllib3,requests,pyjnius,setuptools,android,psutil

android.permissions = MANAGE_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INTERNET,READ_MEDIA_IMAGES,READ_MEDIA_VIDEO,READ_MEDIA_AUDIO,POST_NOTIFICATIONS,FOREGROUND_SERVICE,WAKE_LOCK

presplash.filename = presplash.png
icon.filename = icon.png
orientation = portrait

android.api = 34
android.minapi = 21
android.sdk = 34
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a
android.copy_libs = 1
android.enable_androidx = True
android.accept_sdk_license = True
android.wakelock = True
android.foreground = True
android.allow_backup = True
android.keep_alive = True
android.logcat_filters = *:S python:D
android.logcat_pid_only = False

[buildozer]
log_level = 2
warn_on_deprecated_flags = True
warn_on_ndk_api_21 = False
```

### Build the APK

```bash
buildozer -v android debug
```

After a successful build, your `.apk` will appear under:

```
bin/
```

Transfer and install it on your Android device — and start your personal HTTP file server instantly.

---

## 💻 Run on Desktop

```bash
python main.py
```

Access from any browser:

```
http://<your-IP>:8000
```

Example:

```
http://192.168.43.102:8000
```

You can specify a serving directory:

```bash
python main.py --dir /path/to/folder
```

---

## 🌐 Connect from Another Device

1. Ensure both devices are on the same Wi-Fi or hotspot.
2. Run **Kivy-PyServer**.
3. Scan the generated **QR code** or enter the IP URL in any browser.

Example:

```
http://192.168.0.104:8000
```

Now browse, view, and download files securely — just like a local cloud drive.

---

## ⚙️ Project Layout

```
Kivy-PyServer/
├── main.py               # Core server + KivyMD UI
├── buildozer.spec        # Android build configuration
├── icon.png              # App icon
├── presplash.png         # Splash screen
├── logs/                 # Generated log files
├── requirements.txt      # Dependencies list
├── LICENSE               # MIT License
└── README.md             # Documentation
```

---

## 🧩 Core Components

| Component               | Description                                                                                                 |
| ----------------------- | ----------------------------------------------------------------------------------------------------------- |
| **EnhancedHTTPHandler** | Extends Python’s `SimpleHTTPRequestHandler` with security headers, ZIP folder downloads, and smart routing. |
| **ThreadedHTTPServer**  | Multi-threaded backend for concurrent client handling.                                                      |
| **ServerManager**       | Manages server lifecycle, start/stop logic, and IP resolution.                                              |
| **Logger**              | Real-time, thread-safe logging system with truncation for performance.                                      |
| **MainScreen (KivyMD)** | Primary UI screen for folder selection, server control, and QR display.                                     |
| **LogScreen**           | Real-time viewer for access logs.                                                                           |
| **PyServerApp**         | KivyMD root application integrating server and UI.                                                          |

---

## 🔒 Android Permissions Explained

| Permission                | Purpose                                      |
| ------------------------- | -------------------------------------------- |
| `INTERNET`                | Enable HTTP file sharing.                    |
| `READ_EXTERNAL_STORAGE`   | Read files from device storage.              |
| `WRITE_EXTERNAL_STORAGE`  | Save logs, ZIPs, and configurations.         |
| `MANAGE_EXTERNAL_STORAGE` | Full access to shared storage (Android 11+). |
| `FOREGROUND_SERVICE`      | Allow background server execution.           |
| `WAKE_LOCK`               | Prevent device sleep during transfers.       |

---

## 🧠 Tech Stack

| Library                        | Role                              |
| ------------------------------ | --------------------------------- |
| **Kivy**                       | Cross-platform UI framework       |
| **KivyMD**                     | Material Design components        |
| **qrcode**                     | Generate connection QR codes      |
| **Pillow**                     | Image processing backend          |
| **asyncgui / asynckivy**       | Asynchronous UI updates           |
| **http.server / socketserver** | Python-native HTTP backend        |
| **psutil**                     | System resource management        |
| **plyer / pyjnius**            | Android system bridge             |
| **materialyoucolor**           | Android 12+ dynamic color palette |

---

## 🧰 Developer Notes

* 🐍 **Python 3.10+** required for Android builds
* 📱 **Android 7.0+ (API 24+)** fully supported
* ⚙️ Optimized for **API 34 (Android 14)**
* 🔄 Thread-safe with **Kivy Clock**
* 💾 Auto-truncates logs (default: 500 lines)
* 🔋 Runs in **foreground service** with wakelock
* 🚫 No internet or external servers required

---

## ⚠️ Roadmap / Upcoming Features

* [ ] File upload support
* [ ] Dark/light theme toggle
* [ ] Custom port configuration
* [ ] Persistent settings (JSON / SQLite)
* [ ] Network interface diagnostics panel

---

## 🤝 Contributing

Pull requests are welcome!

```bash
git checkout -b feature/my-feature
git commit -m "Add my feature"
git push origin feature/my-feature
```

Then open a **PR** on GitHub.

---

## 🪪 License

Licensed under the **MIT License**.
See the [LICENSE](LICENSE) file for full terms.

---

## 💡 Credits

Developed by [**Deekshith B**](https://github.com/deekshith0509)
Built using **Python**, **Kivy**, and **KivyMD**.

> “A simple idea can turn your phone into a private local cloud.”


