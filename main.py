import os
import socket
import platform
import threading
import datetime
import subprocess
import webbrowser
from io import BytesIO
import qrcode
from PIL import Image as PILImage

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Rectangle
from kivy.graphics.texture import Texture
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import get_color_from_hex, platform
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.filemanager import MDFileManager
from plyer import filechooser
from kivy.core.image import Image as CoreImage

if platform == 'android':
    from android.permissions import request_permissions, Permission, check_permission
    from android.storage import primary_external_storage_path
    from jnius import autoclass, cast

    # Required Android classes
    Build = autoclass('android.os.Build')
    Environment = autoclass('android.os.Environment')
    Intent = autoclass('android.content.Intent')
    Settings = autoclass('android.provider.Settings')
    Uri = autoclass('android.net.Uri')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    PackageManager = autoclass('android.content.pm.PackageManager')
try:

    class WSLCompatiblePermissions:
        def __init__(self):
            self.permissions = [
                'android.permission.ACCEPT_HANDOVER',
                'android.permission.ACCESS_BACKGROUND_LOCATION',
                'android.permission.ACCESS_CHECKIN_PROPERTIES',
                'android.permission.ACCESS_COARSE_LOCATION',
                'android.permission.ACCESS_FINE_LOCATION',
                'android.permission.ACCESS_LOCATION_EXTRA_COMMANDS',
                'android.permission.ACCESS_NETWORK_STATE',
                'android.permission.ACCESS_NOTIFICATION_POLICY',
                'android.permission.ACCESS_WIFI_STATE',
                'android.permission.ACCOUNT_MANAGER',
                'android.permission.ACTIVITY_RECOGNITION',
                'android.permission.ADD_VOICEMAIL',
                'android.permission.ANSWER_PHONE_CALLS',
                'android.permission.BATTERY_STATS',
                'android.permission.BIND_ACCESSIBILITY_SERVICE',
                'android.permission.BIND_APPWIDGET',
                'android.permission.BIND_AUTOFILL_SERVICE',
                'android.permission.BIND_CALL_REDIRECTION_SERVICE',
                'android.permission.BIND_CARRIER_MESSAGING_SERVICE',
                'android.permission.BIND_CARRIER_SERVICES',
                'android.permission.BIND_CHOOSER_TARGET_SERVICE',
                'android.permission.BIND_CONDITION_PROVIDER_SERVICE',
                'android.permission.BIND_DEVICE_ADMIN',
                'android.permission.BIND_DREAM_SERVICE',
                'android.permission.BIND_INCALL_SERVICE',
                'android.permission.BIND_INPUT_METHOD',
                'android.permission.BIND_MIDI_DEVICE_SERVICE',
                'android.permission.BIND_NFC_SERVICE',
                'android.permission.BIND_NOTIFICATION_LISTENER_SERVICE',
                'android.permission.BIND_PRINT_SERVICE',
                'android.permission.BIND_QUICK_ACCESS_WALLET_SERVICE',
                'android.permission.BIND_QUICK_SETTINGS_TILE',
                'android.permission.BIND_REMOTEVIEWS',
                'android.permission.BIND_SCREENING_SERVICE',
                'android.permission.BIND_TELECOM_CONNECTION_SERVICE',
                'android.permission.BIND_TEXT_SERVICE',
                'android.permission.BIND_TV_INPUT',
                'android.permission.BIND_VISUAL_VOICEMAIL_SERVICE',
                'android.permission.BIND_VOICE_INTERACTION',
                'android.permission.BIND_VPN_SERVICE',
                'android.permission.BIND_VR_LISTENER_SERVICE',
                'android.permission.BIND_WALLPAPER',
                'android.permission.BLUETOOTH',
                'android.permission.BLUETOOTH_ADMIN',
                'android.permission.BLUETOOTH_PRIVILEGED',
                'android.permission.BODY_SENSORS',
                'android.permission.BODY_SENSORS_BACKGROUND',
                'android.permission.BROADCAST_PACKAGE_REMOVED',
                'android.permission.BROADCAST_SMS',
                'android.permission.BROADCAST_STICKY',
                'android.permission.BROADCAST_WAP_PUSH',
                'android.permission.CALL_COMPANION_APP',
                'android.permission.CALL_PHONE',
                'android.permission.CALL_PRIVILEGED',
                'android.permission.CAMERA',
                'android.permission.CAPTURE_AUDIO_OUTPUT',
                'android.permission.CAPTURE_SECURE_VIDEO_OUTPUT',
                'android.permission.CAPTURE_VIDEO_OUTPUT',
                'android.permission.CHANGE_COMPONENT_ENABLED_STATE',
                'android.permission.CHANGE_CONFIGURATION',
                'android.permission.CHANGE_NETWORK_STATE',
                'android.permission.CHANGE_WIFI_MULTICAST_STATE',
                'android.permission.CHANGE_WIFI_STATE',
                'android.permission.CLEAR_APP_CACHE',
                'android.permission.CONTROL_LOCATION_UPDATES',
                'android.permission.DELETE_CACHE_FILES',
                'android.permission.DELETE_PACKAGES',
                'android.permission.DIAGNOSTIC',
                'android.permission.DISABLE_KEYGUARD',
                'android.permission.DUMP',
                'android.permission.EXPAND_STATUS_BAR',
                'android.permission.FACTORY_TEST',
                'android.permission.FOREGROUND_SERVICE',
                'android.permission.GET_ACCOUNTS',
                'android.permission.GET_ACCOUNTS_PRIVILEGED',
                'android.permission.GET_PACKAGE_SIZE',
                'android.permission.GET_TASKS',
                'android.permission.GLOBAL_SEARCH',
                'android.permission.INSTALL_LOCATION_PROVIDER',
                'android.permission.INSTALL_PACKAGES',
                'android.permission.INSTALL_SHORTCUT',
                'android.permission.INSTANT_APP_FOREGROUND_SERVICE',
                'android.permission.INTERACT_ACROSS_PROFILES',
                'android.permission.INTERNET',
                'android.permission.KILL_BACKGROUND_PROCESSES',
                'android.permission.LOCATION_HARDWARE',
                'android.permission.MANAGE_DOCUMENTS',
                'android.permission.MANAGE_EXTERNAL_STORAGE',
                'android.permission.MANAGE_OWN_CALLS',
                'android.permission.MASTER_CLEAR',
                'android.permission.MEDIA_CONTENT_CONTROL',
                'android.permission.MODIFY_AUDIO_SETTINGS',
                'android.permission.MODIFY_PHONE_STATE',
                'android.permission.MOUNT_FORMAT_FILESYSTEMS',
                'android.permission.MOUNT_UNMOUNT_FILESYSTEMS',
                'android.permission.NFC',
                'android.permission.PACKAGE_USAGE_STATS',
                'android.permission.PERSISTENT_ACTIVITY',
                'android.permission.PROCESS_OUTGOING_CALLS',
                'android.permission.READ_CALENDAR',
                'android.permission.READ_CALL_LOG',
                'android.permission.READ_CONTACTS',
                'android.permission.READ_EXTERNAL_STORAGE',
                'android.permission.READ_INPUT_STATE',
                'android.permission.READ_LOGS',
                'android.permission.READ_PHONE_NUMBERS',
                'android.permission.READ_PHONE_STATE',
                'android.permission.READ_PRECISE_PHONE_STATE',
                'android.permission.READ_SMS',
                'android.permission.READ_SYNC_SETTINGS',
                'android.permission.READ_SYNC_STATS',
                'android.permission.READ_VOICEMAIL',
                'android.permission.REBOOT',
                'android.permission.RECEIVE_BOOT_COMPLETED',
                'android.permission.RECEIVE_MMS',
                'android.permission.RECEIVE_SMS',
                'android.permission.RECEIVE_WAP_PUSH',
                'android.permission.RECORD_AUDIO',
                'android.permission.REORDER_TASKS',
                'android.permission.REQUEST_COMPANION_PROFILE_SIDECHANNEL',
                'android.permission.REQUEST_COMPANION_RUN_IN_BACKGROUND',
                'android.permission.REQUEST_COMPANION_USE_DATA_IN_BACKGROUND',
                'android.permission.REQUEST_DELETE_PACKAGES',
                'android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS',
                'android.permission.REQUEST_INSTALL_PACKAGES',
                'android.permission.RESTART_PACKAGES',
                'android.permission.SCHEDULE_EXACT_ALARM',
                'android.permission.SEND_RESPOND_VIA_MESSAGE',
                'android.permission.SEND_SMS',
                'android.permission.SET_ALARM',
                'android.permission.SET_ALWAYS_FINISH',
                'android.permission.SET_ANIMATION_SCALE',
                'android.permission.SET_DEBUG_APP',
                'android.permission.SET_PREFERRED_APPLICATIONS',
                'android.permission.SET_PROCESS_LIMIT',
                'android.permission.SET_TIME',
                'android.permission.SET_TIME_ZONE',
                'android.permission.SET_WALLPAPER',
                'android.permission.SET_WALLPAPER_HINTS',
                'android.permission.SIGNAL_PERSISTENT_PROCESSES',
                'android.permission.STATUS_BAR',
                'android.permission.SYSTEM_ALERT_WINDOW',
                'android.permission.TRANSMIT_IR',
                'android.permission.UNINSTALL_SHORTCUT',
                'android.permission.UPDATE_DEVICE_STATS',
                'android.permission.USE_BIOMETRIC',
                'android.permission.USE_FINGERPRINT',
                'android.permission.USE_FULL_SCREEN_INTENT',
                'android.permission.USE_SIP',
                'android.permission.VIBRATE',
                'android.permission.WAKE_LOCK',
                'android.permission.WRITE_APN_SETTINGS',
                'android.permission.WRITE_CALENDAR',
                'android.permission.WRITE_CALL_LOG',
                'android.permission.WRITE_CONTACTS',
                'android.permission.WRITE_EXTERNAL_STORAGE',
                'android.permission.WRITE_GSERVICES',
                'android.permission.WRITE_SECURE_SETTINGS',
                'android.permission.WRITE_SETTINGS',
                'android.permission.WRITE_SYNC_SETTINGS',
                'android.permission.WRITE_VOICEMAIL',
            ]


        def check_and_request_permissions(self):
            if platform == 'android':
                from android.permissions import request_permissions, check_permission, Permission

                permissions_to_request = []
                for permission in self.permissions:
                    if not check_permission(permission):
                        permissions_to_request.append(permission)

                if permissions_to_request:
                    request_permissions(permissions_to_request, self.permission_callback)

        def permission_callback(self, permissions, grant_results):
            if all(grant_results):
                print("All permissions granted")
            else:
                print("Some permissions were denied")

    class DirectoryListingHandler(http.server.SimpleHTTPRequestHandler):

        def list_directory(self, path):
            try:
                file_list = os.listdir(path)
            except os.error:
                self.send_error(404, "No permission to list directory")
                return None

            file_list.sort(key=lambda a: a.lower())
            displaypath = urllib.parse.unquote(self.path)

            try:
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()

                # HTML with modern CSS
                self.wfile.write(b'<!DOCTYPE html>')
                self.wfile.write(b"<html lang='en'><head>")
                self.wfile.write(b"<meta charset='UTF-8'>")
                self.wfile.write(b"<meta name='viewport' content='width=device-width, initial-scale=1.0'>")

                # Insert the custom CSS styles
                self.wfile.write(b"""
                <style>
                    :root {
                        --primary-color: #4299E1;
                        --secondary-color: #2C5282;
                        --background-color: #F7FAFC;
                        --text-color: #2D3748;
                        --border-color: #E2E8F0;
                        --hover-color: #EDF2F7;
                    }

                    * {
                        box-sizing: border-box;
                        margin: 0;
                        padding: 0;
                    }

                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                        background-color: var(--background-color);
                        color: var(--text-color);
                        line-height: 1.5;
                    }

                    .container {
                        max-width: 1200px;
                        margin: 0 auto;
                        padding: 1rem;
                    }

                    h1 {
                        font-size: 2rem;
                        text-align: center;
                        margin-bottom: 1rem;
                    }

                    .breadcrumb {
                        display: flex;
                        flex-wrap: wrap;
                        justify-content: center;
                        padding: 0.5rem;
                        background-color: white;
                        border-radius: 0.5rem;
                        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
                        margin-bottom: 1rem;
                    }

                    .breadcrumb a {
                        color: var(--primary-color);
                        text-decoration: none;
                        padding: 0.25rem 0.5rem;
                    }

                    .breadcrumb a:hover {
                        text-decoration: underline;
                    }

                    .actions {
                        display: flex;
                        flex-wrap: wrap;
                        gap: 1rem;
                        margin-bottom: 1rem;
                    }

                    .action-form {
                        flex: 1;
                        min-width: 200px;
                    }

                    input[type="text"],
                    input[type="file"] {
                        width: 100%;
                        padding: 0.5rem;
                        border: 1px solid var(--border-color);
                        border-radius: 0.25rem;
                        font-size: 1rem;
                    }

                    input[type="submit"] {
                        width: 100%;
                        padding: 0.5rem;
                        background-color: var(--primary-color);
                        color: white;
                        border: none;
                        border-radius: 0.25rem;
                        font-size: 1rem;
                        cursor: pointer;
                        transition: background-color 0.2s ease;
                    }

                    input[type="submit"]:hover {
                        background-color: var(--secondary-color);
                    }

                    .table-container {
                        overflow-x: auto;
                        background-color: white;
                        border-radius: 0.5rem;
                        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
                    }

                    table {
                        width: 100%;
                        border-collapse: separate;
                        border-spacing: 0;
                    }

                    th, td {
                        padding: 0.75rem 1rem;
                        text-align: left;
                        border-bottom: 1px solid var(--border-color);
                    }

                    th {
                        background-color: var(--primary-color);
                        color: white;
                        font-weight: 600;
                        position: sticky;
                        top: 0;
                        z-index: 10;
                    }

                    tr:hover {
                        background-color: var(--hover-color);
                    }

                    .file-icon {
                        font-size: 1.25rem;
                    }

                    .file-name {
                        max-width: 200px;
                        overflow: hidden;
                        text-overflow: ellipsis;
                        white-space: nowrap;
                    }

                    .file-name:hover {
                        overflow: visible;
                        white-space: normal;
                        word-break: break-all;
                    }

                    .action-button {
                        padding: 0.25rem 0.5rem;
                        background-color: var(--primary-color);
                        color: white;
                        border: none;
                        border-radius: 0.25rem;
                        font-size: 0.875rem;
                        cursor: pointer;
                        transition: background-color 0.2s ease;
                        white-space: nowrap;
                    }

                    .action-button:hover {
                        background-color: var(--secondary-color);
                    }

                    @media (max-width: 640px) {
                        .actions {
                            flex-direction: column;
                        }

                        th, td {
                            padding: 0.5rem;
                        }

                        .hide-on-mobile {
                            display: none;
                        }

                        .file-name {
                            max-width: 150px;
                        }

                        table {
                            table-layout: fixed;
                        }

                        th:nth-child(1), td:nth-child(1) { width: 10%; }
                        th:nth-child(2), td:nth-child(2) { width: 60%; }
                        th:nth-child(3), td:nth-child(3) { width: 30%; }
                    }
                </style>
                """)

                self.wfile.write(f"<title>Directory listing for {displaypath}</title>".encode('utf-8'))
                self.wfile.write(b"</head><body>")

                # Container for content
                self.wfile.write(b"<div class='container'>")

                self.wfile.write(f"<h1>Directory listing for {displaypath}</h1>".encode('utf-8'))

                # Breadcrumb Navigation
                self.wfile.write(b'<div class="breadcrumb">')
                self.wfile.write(b'<a href="/">Home</a>')
                parts = displaypath.split('/')
                breadcrumb_path = ""
                for part in parts[:-1]:
                    if part:
                        breadcrumb_path += part + '/'
                        self.wfile.write(f'<span>/</span><a href="{urllib.parse.quote(breadcrumb_path)}">{part}</a>'.encode('utf-8'))
                if parts[-1]:
                    self.wfile.write(f'<span>/</span>{parts[-1]}'.encode('utf-8'))
                self.wfile.write(b'</div>')

                # Actions
                self.wfile.write(b"""
                    <div class="actions">
                        <form method="POST" action="/create_directory" class="action-form">
                            <input type="text" name="dirname" placeholder="New Directory Name" required>
                            <input type="submit" value="Create Directory">
                        </form>
                        <form method="POST" action="/upload" enctype="multipart/form-data" class="action-form">
                            <input type="file" name="file" required>
                            <input type="submit" value="Upload File">
                        </form>
                        <div class="action-form">
                            <input type="text" id="searchBar" onkeyup="filterFiles()" placeholder="Search files..">
                        </div>
                    </div>
                """)

                # File listing in a table
                self.wfile.write(b"<div class='table-container'><table id='fileTable'>")
                self.wfile.write(b"<thead><tr>")
                self.wfile.write(b"<th>Type</th>")
                self.wfile.write(b"<th>Name</th>")
                self.wfile.write(b"<th>Actions</th>")
                self.wfile.write(b"</tr></thead>")
                self.wfile.write(b"<tbody>")

                for name in file_list:
                    fullname = os.path.join(path, name)
                    displayname = linkname = name
                    
                    if os.path.isdir(fullname):
                        icon = "📁"
                        displayname += "/"
                        linkname += "/"
                    else:
                        icon = "📄"

                    self.wfile.write(b"<tr>")
                    self.wfile.write(f"<td><span class='file-icon'>{icon}</span></td>".encode('utf-8'))
                    self.wfile.write(f'<td><div class="file-name"><a href="{urllib.parse.quote(linkname)}" title="{displayname}">{displayname}</a></div></td>'.encode('utf-8'))
                    self.wfile.write(b"<td>")
                    if not os.path.isdir(fullname):
                        self.wfile.write(f'<button class="action-button" onclick="location.href=\'/download?file={urllib.parse.quote(fullname)}\'">Download</button>'.encode('utf-8'))
                    self.wfile.write(b"</td>")
                    self.wfile.write(b"</tr>")

                self.wfile.write(b"</tbody></table></div>")

                # Add JavaScript for search functionality
                self.wfile.write(b"""
                <script>
                function filterFiles() {
                    var input, filter, table, tr, td, i, txtValue;
                    input = document.getElementById("searchBar");
                    filter = input.value.toUpperCase();
                    table = document.getElementById("fileTable");
                    tr = table.getElementsByTagName("tr");
                    for (i = 0; i < tr.length; i++) {
                        td = tr[i].getElementsByTagName("td")[1];
                        if (td) {
                            txtValue = td.textContent || td.innerText;
                            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                                tr[i].style.display = "";
                            } else {
                                tr[i].style.display = "none";
                            }
                        }
                    }
                }
                </script>
                """)

                self.wfile.write(b"</div></body></html>")
            except Exception as e:
                self.send_error(500, "Internal Server Error")
        def do_GET(self):
            """Handle GET requests."""
            if self.path == '/favicon.ico':
                self.send_response(204)  # No content
                self.end_headers()
                return
            elif self.path.startswith('/download'):
                self.handle_download()
            else:
                log_message(f"GET request for: {self.path}")
                super().do_GET()  # Call parent method for other GET requests
        def end_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')  # Allow access from any origin
            super().end_headers()
        def do_POST(self):
            """Handle POST requests."""
            if self.path == '/upload':
                self.handle_upload()
            elif self.path == '/create_directory':
                self.handle_create_directory()  # Assuming you have this method
            else:
                self.send_error(404, "File not found.")

        def handle_upload(self):
            """Handle file upload."""
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            # Assuming the upload uses a multipart/form-data encoding
            boundary = self.headers['Content-Type'].split('=')[1].encode()
            parts = post_data.split(boundary)

            # Find the part that contains the file
            for part in parts:
                if b'Content-Disposition' in part and b'filename=' in part:
                    # Split header and content
                    header, file_content = part.split(b'\r\n\r\n', 1)
                    filename = self.extract_filename(header)
                    if filename:
                        # Remove trailing CRLF from file content
                        file_content = file_content.rstrip(b'\r\n--')

                        # Sanitize filename to prevent directory traversal attacks
                        filename = os.path.basename(filename)

                        # Check if file already exists
                        if os.path.isfile(os.path.join(os.getcwd(), filename)):
                            self.send_error(409, "File already exists.")
                            return

                        # Save the uploaded file
                        try:
                            with open(os.path.join(os.getcwd(), filename), 'wb') as f:
                                f.write(file_content)
                            self.send_response(302)  # Redirect after upload
                            self.send_header('Location', '/')
                            self.end_headers()
                        except OSError as e:
                            self.send_error(500, f"Failed to save file: {e}")
                        return

            self.send_error(400, "No valid file found in upload.")

        def handle_download(self):
            """Handle file download requests."""
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)

            if 'file' in params:
                filename = params['file'][0]
                full_path = os.path.join(os.getcwd(), filename)

                if os.path.isfile(full_path):
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/octet-stream')
                    self.send_header('Content-Disposition', f'attachment; filename="{os.path.basename(full_path)}"')
                    self.send_header('Content-Length', str(os.path.getsize(full_path)))
                    self.end_headers()

                    with open(full_path, 'rb') as file:
                        self.wfile.write(file.read())
                else:
                    self.send_error(404, "File not found")
            else:
                self.send_error(400, "Bad request: No file specified")

        def extract_filename(self, header):
            """Extract the filename from the Content-Disposition header."""
            header = header.decode('utf-8')
            filename = None
            for line in header.splitlines():
                if "filename=" in line:
                    filename = line.split('filename=')[1].strip('"')
                    break
            return filename

        def handle_create_directory(self):
            """Handle directory creation."""
            form = self.parse_multipart_form_data()
            if 'dirname' not in form:
                self.send_error(400, "Directory name not provided.")
                return
            
            dirname = form['dirname'][0]
            os.makedirs(os.path.join(os.getcwd(), dirname), exist_ok=True)
            
            self.send_response(302)  # Redirect after directory creation
            self.send_header('Location', '/')
            self.end_headers()

        def parse_multipart_form_data(self):
            """Parse multipart form data from the request."""
            boundary = self.headers['Content-Type'].split("=")[1].encode()
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)

            parts = body.split(boundary)
            form_data = {}

            for part in parts:
                if not part or part == b'--' or part == b'--\r\n':
                    continue
                
                if b'Content-Disposition' in part:
                    header, data = part.split(b'\r\n\r\n', 1)
                    disposition = header.decode()
                    name = self.get_disposition_value(disposition, 'name')
                    filename = self.get_disposition_value(disposition, 'filename')

                    if filename:
                        form_data['file'] = {
                            'filename': filename,
                            'file': data.rstrip(b'\r\n--')
                        }
                    else:
                        value = data.rstrip(b'\r\n--').decode()
                        form_data[name] = [value]
            
            return form_data

        def get_disposition_value(self, disposition, attribute):
            """Extract a value from a content disposition header."""
            for part in disposition.split(';'):
                if attribute in part:
                    return part.split('=')[1].strip(' "')
            return None

        def format_date_time(self, timestamp):
            """Format timestamp to a readable date-time string."""
            return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

        def sizeof_fmt(self, num, suffix='B'):
            """Human-readable file size."""
            for unit in ['','K','M','G','T']:
                if num < 1024:
                    return f"{num:.1f}{unit}{suffix}"
                num /= 1024
            return f"{num:.1f}Y{suffix}"

    class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
        """Handle requests in a separate thread."""
        pass
    class ReuseAddressHTTPServer(socketserver.TCPServer):
        allow_reuse_address = True

    # Define a global variable for the server
    httpd = None
    server_thread = None

    # Function to log messages
    def log_message(message):
        app = MDApp.get_running_app()
        if app:
            Clock.schedule_once(lambda dt: app.log_output(message))

    # Function to start the HTTP server
    def start_http_server(directory):
        global httpd
        PORT = 8000
        os.chdir(directory)

        try:
            log_message(f"Serving HTTP on port {PORT} from {directory}...")
            httpd = ReuseAddressHTTPServer(("", PORT), DirectoryListingHandler)
            httpd.serve_forever()
        except OSError as e:
            log_message(f"Error starting server: {e}")
            

    class MainScreen(Screen):
        qr_image = ObjectProperty(None)

        def __init__(self, **kwargs):
            super(MainScreen, self).__init__(**kwargs)
            self.server_running = False
            self.file_manager = None
            self.current_ip = None  # Initialize the current IP variable
            self.current_port = 8000  # Set default port
            self.build()

        def build(self):
            layout = BoxLayout(orientation='vertical', padding=[10, 10, 10, 10], spacing=5)

            # Set the background color
            with self.canvas.before:
                self.rect = Rectangle(size=self.size, pos=self.pos)
                self.bind(size=self._update_rect, pos=self._update_rect)

            # Title Label
            self.title_label = MDLabel(
                text="PyServer",
                halign="center",
                theme_text_color="Custom",
                text_color=get_color_from_hex("#333333"),
                font_style="H4",
                size_hint_y=None,
                height=dp(50),
                pos_hint={'center_x': 0.5, 'center_y': -0.4}
                
            )
            layout.add_widget(self.title_label)

            # QR Code Display
            qr_layout = RelativeLayout(size_hint_y=None, height=dp(200))
            self.qr_image = Image(
                size_hint=(None, None),
                size=(dp(100), dp(100)),
                allow_stretch=True,
                keep_ratio=True,
                pos_hint={'center_x': 0.5, 'center_y': 0.5}
            )
            qr_layout.add_widget(self.qr_image)
            layout.add_widget(qr_layout)

            # IP Address and Port Label
            self.ip_label = Label(
                text="IP:Port will appear here",
                halign="center",
                color=get_color_from_hex("#0000FF"),
                size_hint_y=None,
                height=dp(40)
            )
            self.ip_label.bind(on_touch_down=self.open_link)
            layout.add_widget(self.ip_label)

            # Directory Input Layout
            dir_input_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(35))

            # Directory Input Text Field
            self.directory_input = TextInput(
                hint_text="Enter directory path",
                multiline=False,
                size_hint_x=0.7,
                pos_hint={'center_x': 0.5}
            )
            dir_input_layout.add_widget(self.directory_input)

            # Enter Button
            button_enter = MDRaisedButton(
                text="Enter",
                size_hint_x=0.3,
                pos_hint={'center_x': 0.5}
            )
            button_enter.bind(on_press=self.enter_directory)
            dir_input_layout.add_widget(button_enter)

            layout.add_widget(dir_input_layout)

            # Start/Stop Server Button
            self.button_start_stop = MDRaisedButton(
                text="Start Server",
                size_hint_x=0.8,
                height=dp(50),
                pos_hint={'center_x': 0.5},
                md_bg_color=get_color_from_hex("#03DAC6"),
                text_color=get_color_from_hex("#000000")
            )
            self.button_start_stop.bind(on_press=self.toggle_server)
            layout.add_widget(self.button_start_stop)

            # View Logs Button
            button_view_logs = MDRaisedButton(
                text="View Logs",
                size_hint_x=0.8,
                height=dp(50),
                pos_hint={'center_x': 0.5},
                md_bg_color=get_color_from_hex("#BB86FC"),
                text_color=get_color_from_hex("#000000")
            )
            button_view_logs.bind(on_press=self.switch_to_logs)
            layout.add_widget(button_view_logs)

            # Information Label
            info_label = MDLabel(
                text="/storage/sdcard is for internal storage\n/storage/XXXX-XXXX is for external storage",
                halign='center',
                theme_text_color="Custom",
                text_color=get_color_from_hex("#555555"),
                pos_hint={'center_x': 0.5, 'center_y': -0.09},                
                height=dp(20)
            )
            layout.add_widget(info_label)

            # Quit Button
            button_quit = MDRaisedButton(
                text="Quit",
                size_hint_x=0.2,
                size_hint_y=None,
                height=dp(40),
                pos_hint={'x': 0, 'y': 0}  # Positioning the quit button
            )
            button_quit.bind(on_press=self.quit_app)  # Bind the quit button to the quit_app method
            layout.add_widget(button_quit)

            self.add_widget(layout)

        # Add this method to handle the "Enter" button action

        def enter_directory(self, instance):
            """Get the directory input from the user and start the server."""
            directory = self.directory_input.text.strip()  # Get the input from the TextInput
            if directory:  # Check if the directory is not empty
                if os.path.isdir(directory):  # Check if the directory is valid
                    self.start_server(directory)  # Start the server with the entered directory
                    self.directory_input.text = ""  # Clear the input field after submission
                else:
                    self.show_error_dialog("Please enter a valid directory path.")  # Show a message if the directory is invalid
            else:
                self.show_error_dialog("Please enter a directory path.")  # Show a message if the directory is empty

        def show_error_dialog(self, message):
            """Display a modern MDDialog with the provided message."""
            self.dialog = MDDialog(
                text=message,
                buttons=[
                    MDRaisedButton(
                        text="OK",
                        on_release=lambda x: self.dialog.dismiss()
                    )
                ]
            )
            self.dialog.open()

        def _update_rect(self, instance, value):
            self.rect.pos = instance.pos
            self.rect.size = instance.size

        def open_link(self, instance, touch):
            """Open the URL in a web browser when the label is clicked."""
            if instance.collide_point(touch.x, touch.y) and self.server_running:
                if self.current_ip and self.current_port:  # Ensure IP and port are set
                    url = f"http://{self.current_ip}:{self.current_port}"  # Construct URL
                    webbrowser.open(url)  # Open URL in web browser






        def toggle_server(self, instance):
            """Toggle the server on and off."""
            if self.server_running:
                self.stop_server()
            else:
                self.enter_directory(instance)

        def stop_server(self):
            global httpd, server_thread
            if httpd:
                try:
                    log_message("Stopping server...")
                    # Shutdown the server
                    httpd.shutdown()
                    httpd.server_close()
                    
                    # Wait for the server thread to complete
                    if server_thread and server_thread.is_alive():
                        server_thread.join(timeout=5)
                    
                    # Reset server variables
                    httpd = None
                    server_thread = None
                    
                    # Update UI
                    self.server_running = False
                    self.button_start_stop.text = "Start Server"
                    self.qr_image.texture = None
                    self.ip_label.text = "IP:Port will appear here"
                    self.ip_label.bind(on_touch_down=self.open_link)
                    
                    log_message("Server stopped.")
                except Exception as e:
                    log_message(f"Error stopping server: {e}")

        def start_server(self, directory):
            """Start the HTTP server with the selected directory."""
            global httpd, server_thread
            
            # Ensure previous server is fully stopped
            if self.server_running:
                self.stop_server()
                # Add a small delay to ensure socket is fully released
                import time
                time.sleep(1)
            
            # Start new server
            server_thread = threading.Thread(
                target=start_http_server,
                args=(directory,),
                daemon=True
            )
            server_thread.start()
            
            # Update UI
            self.current_ip = self.get_local_ip()
            qr_texture = self.generate_qr_code(f"http://{self.current_ip}:{self.current_port}")
            if qr_texture:
                self.qr_image.texture = qr_texture
                self.qr_image.size = qr_texture.size
                self.qr_image.canvas.ask_update()
            
            self.update_ip_label()
            self.server_running = True
            self.button_start_stop.text = "Stop Server"
        
        

        def select_directory(self, path):
            """Select a directory to serve."""
            if self.server_running:
                self.stop_server()  # Stop the current server if running
            self.start_server(path)  # Start server with the selected path
            self.close_file_manager()  # Close the file manager




        def update_ip_label(self):
            """Update the IP address and port label."""
            self.ip_label.text = f"{self.current_ip}:{self.current_port}"  # Update the label with current IP and port
            self.ip_label.color = get_color_from_hex("#0000FF")  # Reset color to indicate it's clickable
            self.ip_label.bind(on_touch_down=self.open_link)  # Re-bind the click event

        def open_filechooser(self, instance):
            """Open the file chooser for directory selection."""
            self.file_manager = MDFileManager(
                exit_manager=self.close_file_manager,
                select_path=self.select_directory,
            )
            self.file_manager.show('/')  # Show the file manager at the root directory

        def close_file_manager(self, *args):
            """Close the file manager."""
            if self.file_manager:
                self.file_manager.close()

        def get_local_ip(self):
            """Fetch the local IP address."""
            ip = None
            try:
                # Try getting the IP by connecting to an external server
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip = s.getsockname()[0]
                s.close()
            except Exception:
                try:
                    if platform.system() == "Windows":
                        output = subprocess.check_output(['ipconfig'], text=True)
                        for line in output.splitlines():
                            if 'IPv4 Address' in line:
                                ip = line.split(':')[1].strip()
                                break
                    else:
                        output = subprocess.check_output(['ifconfig'], text=True)
                        for line in output.splitlines():
                            if 'inet ' in line and '127.0.0.1' not in line:
                                ip = line.split()[1]
                                break
                        if ip is None:
                            output = subprocess.check_output(['ip', 'addr'], text=True)
                            for line in output.splitlines():
                                if 'inet ' in line and '127.0.0.1' not in line:
                                    ip = line.split()[1].split('/')[0]
                                    break
                except Exception as e:
                    self.log_message(f"Error fetching local IP: {e}")
            
            if ip is None or ip.startswith("127."):
                # As a last resort, try to get the hostname IP
                ip = socket.gethostbyname(socket.gethostname())
            
            return ip



        def quit_app(self, instance):
            """Quit the application."""
            App.get_running_app().stop()  # Terminate the application


        def generate_qr_code(self, url):
            try:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(url)
                qr.make(fit=True)

                img = qr.make_image(fill_color="black", back_color="white")

                # Convert PIL image to bytes
                buf = BytesIO()
                img.save(buf, format='PNG')
                buf.seek(0)

                # Create a Kivy texture
                core_img = CoreImage(buf, ext='png')
                qr_texture = core_img.texture
                if qr_texture:
                    self.qr_image.texture = qr_texture
                    self.qr_image.size = (dp(200), dp(200))  # Set to match the size in build method
                    self.qr_image.canvas.ask_update()
                else:
                    pass
        
                print(f"QR code generated successfully. Texture size: {texture.size}")
                return texture
            except Exception as e:
                return None
            
        def switch_to_logs(self, instance):
            self.manager.current = 'logs'


    class LogScreen(Screen):
        log_output_area = ObjectProperty(None)

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            # Create the layout
            layout = FloatLayout()

            # Create a text input for logs
            self.log_output_area = TextInput(
                size_hint=(1, 0.9),
                readonly=True,
                background_color=(1, 1, 1, 1),
                foreground_color=(0, 0, 0, 1),
                font_size=14,
                hint_text="Logs will appear here...",
                multiline=True,
            )
            layout.add_widget(self.log_output_area)

            # Back to Main Button
            button_back = MDRaisedButton(
                text="Back to Main",
                size_hint=(0.8, None),
                height=50,
                pos_hint={'center_x': 0.5, 'y': 0}
            )
            button_back.bind(on_press=self.switch_to_main)
            layout.add_widget(button_back)

            # Add the layout to the Log screen
            self.add_widget(layout)

        def switch_to_main(self, instance):
            self.manager.current = 'main'

        def log_output(self, message):
            self.log_output_area.text += f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n"
            self.log_output_area.cursor = (0, 0)  # Scroll to the bottom



    class FileShareApp(MDApp):
        def build(self):
            # Rest of your app initialization
            self.sm = ScreenManager()
            self.sm.add_widget(MainScreen(name='main'))
            self.sm.add_widget(LogScreen(name='logs'))
            return self.sm

        def log_output(self, message):
            # Get the current log screen and call its log_output method
            log_screen = self.sm.get_screen('logs')
            log_screen.log_output(message)


        def check_and_request_storage_permissions(self):
            if platform =='linux':
                return
                
            if not Environment.isExternalStorageManager():
                self.show_storage_permission_dialog()
            else:
                print("Already have all files access permission")
            return True

        def show_storage_permission_dialog(self):
            """Show dialog explaining why we need storage permission"""
            dialog = MDDialog(
                title="Storage Permission Required",
                text="This app needs permission to manage files in external storage. Please enable 'Allow all files access' in the next screen.",
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        on_release=lambda x: dialog.dismiss()
                    ),
                    MDFlatButton(
                        text="SETTINGS",
                        on_release=lambda x: self.open_all_files_settings()
                    ),
                ],
            )
            dialog.open()

        def open_all_files_settings(self):
            """Open Android settings for all files access"""
            if platform == 'android':
                activity = PythonActivity.mActivity
                
                # Create intent for "All files access" settings page
                intent = Intent()
                intent.setAction(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
                
                # Set package URI
                uri = Uri.fromParts("package", "com.share.server", None)
                intent.setData(uri)
                
                # Start the settings activity
                activity.startActivity(intent)
                
                # Schedule a check after returning from settings
                Clock.schedule_once(self.check_permission_after_return, 1)

        def check_permission_after_return(self, dt):
            """Check if permission was granted after returning from settings"""
            if platform == 'android':
                if Environment.isExternalStorageManager():
                    print("All files access permission granted!")
                    # Proceed with your file operations
                    self.initialize_storage()
                else:
                    print("All files access permission not granted")
                    # Optionally show another dialog or handle denial

        def on_start(self):
            """Check permissions when app starts"""
            self.check_and_request_storage_permissions()
    if __name__ == '__main__':
        FileShareApp().run()

except:
    pass
