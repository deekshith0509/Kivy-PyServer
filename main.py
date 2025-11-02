import os
import sys
import socket
import threading
import datetime
import subprocess
import webbrowser
import urllib.parse
from io import BytesIO
from pathlib import Path
from typing import Optional, Callable
import asyncio
from concurrent.futures import ThreadPoolExecutor

# HTTP Server imports
import http.server
import socketserver

# Image processing
import qrcode
from PIL import Image as PILImage

# Kivy imports
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.graphics.texture import Texture
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import get_color_from_hex, platform as kivy_platform
from kivy.metrics import dp, sp
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.core.image import Image as CoreImage

# KivyMD imports
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.label import MDLabel
try:
    from kivymd.uix.label import MDIcon  # KivyMD 1.1.1+
except ImportError:
    # Fallback for older versions
    MDIcon = MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.textfield import MDTextField

# Android-specific imports
if kivy_platform == 'android':
    from android.permissions import request_permissions, check_permission
    from android.storage import primary_external_storage_path
    from jnius import autoclass, cast

    Build = autoclass('android.os.Build')
    Environment = autoclass('android.os.Environment')
    Intent = autoclass('android.content.Intent')
    Settings = autoclass('android.provider.Settings')
    Uri = autoclass('android.net.Uri')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Context = autoclass('android.content.Context')
    WifiManager = autoclass('android.net.wifi.WifiManager')
    ConnectivityManager = autoclass('android.net.ConnectivityManager')
    NetworkCapabilities = autoclass('android.net.NetworkCapabilities')


# ============================================================================
# CONSTANTS
# ============================================================================

DEFAULT_PORT = 8000
BUFFER_SIZE = 8192
LOG_MAX_LINES = 1000

# Color scheme
COLORS = {
    'primary': '#6200EE',
    'primary_dark': '#3700B3',
    'secondary': '#03DAC6',
    'background': '#F5F5F5',
    'surface': '#FFFFFF',
    'error': '#B00020',
    'success': '#4CAF50',
    'text_primary': '#000000',
    'text_secondary': '#757575',
}


# ============================================================================
# LOGGING SYSTEM
# ============================================================================

class Logger:
    """Thread-safe logging system"""
    
    def __init__(self, max_lines: int = LOG_MAX_LINES):
        self.max_lines = max_lines
        self.logs = []
        self.callbacks = []
        self._lock = threading.Lock()
    
    def log(self, message: str, level: str = "INFO"):
        """Add a log message"""
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        with self._lock:
            self.logs.append(log_entry)
            if len(self.logs) > self.max_lines:
                self.logs.pop(0)
            
            # Notify callbacks
            for callback in self.callbacks:
                try:
                    Clock.schedule_once(lambda dt: callback(log_entry), 0)
                except Exception as e:
                    print(f"Error in log callback: {e}")
    
    def add_callback(self, callback: Callable):
        """Register a callback for new log messages"""
        self.callbacks.append(callback)
    
    def get_all_logs(self) -> str:
        """Get all logs as a single string"""
        with self._lock:
            return "\n".join(self.logs)
    
    def clear(self):
        """Clear all logs"""
        with self._lock:
            self.logs.clear()


# Global logger instance
logger = Logger()


# ============================================================================
# HTTP SERVER
# ============================================================================

class EnhancedHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """Enhanced HTTP request handler with modern UI and better error handling"""
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        message = f"{self.address_string()} - {format % args}"
        logger.log(message, "INFO")
    
    def log_error(self, format, *args):
        """Override error logging"""
        message = f"{self.address_string()} - {format % args}"
        logger.log(message, "ERROR")
    
    def end_headers(self):
        """Add CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()
    
    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self.end_headers()
    
    def list_directory(self, path):
        """Enhanced directory listing with modern UI"""
        try:
            file_list = os.listdir(path)
        except OSError:
            self.send_error(404, "Cannot read directory")
            return None
        
        file_list.sort(key=lambda a: a.lower())
        displaypath = urllib.parse.unquote(self.path, errors='surrogatepass')
        
        try:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            
            # Modern HTML/CSS template
            html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyServer - {displaypath}</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Roboto', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2em;
            font-weight: 300;
            margin-bottom: 10px;
        }}
        
        .breadcrumb {{
            background: #f8f9fa;
            padding: 15px 30px;
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: 8px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .breadcrumb a {{
            color: #667eea;
            text-decoration: none;
            transition: all 0.3s;
        }}
        
        .breadcrumb a:hover {{
            color: #764ba2;
            text-decoration: underline;
        }}
        
        .actions {{
            padding: 30px;
            background: #f8f9fa;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        .action-card {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }}
        
        .action-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.15);
        }}
        
        .action-card h3 {{
            margin-bottom: 15px;
            color: #333;
            font-size: 1.1em;
            font-weight: 500;
        }}
        
        input[type="text"],
        input[type="file"] {{
            width: 100%;
            padding: 12px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
            margin-bottom: 10px;
        }}
        
        input[type="text"]:focus,
        input[type="file"]:focus {{
            outline: none;
            border-color: #667eea;
        }}
        
        button, input[type="submit"] {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s;
            width: 100%;
        }}
        
        button:hover, input[type="submit"]:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }}
        
        .file-list {{
            padding: 30px;
        }}
        
        .file-item {{
            display: flex;
            align-items: center;
            padding: 15px;
            border-bottom: 1px solid #e9ecef;
            transition: background 0.2s;
        }}
        
        .file-item:hover {{
            background: #f8f9fa;
        }}
        
        .file-icon {{
            font-size: 32px;
            margin-right: 15px;
            color: #667eea;
        }}
        
        .file-info {{
            flex: 1;
        }}
        
        .file-name {{
            color: #333;
            text-decoration: none;
            font-weight: 500;
            display: block;
            margin-bottom: 5px;
        }}
        
        .file-name:hover {{
            color: #667eea;
        }}
        
        .file-meta {{
            color: #6c757d;
            font-size: 0.85em;
        }}
        
        .file-actions {{
            display: flex;
            gap: 10px;
        }}
        
        .btn-download {{
            background: #28a745;
            padding: 8px 16px;
            font-size: 12px;
        }}
        
        .search-box {{
            margin-bottom: 20px;
        }}
        
        .material-icons {{
            vertical-align: middle;
        }}
        
        @media (max-width: 768px) {{
            .actions {{
                grid-template-columns: 1fr;
            }}
            
            .file-item {{
                flex-direction: column;
                align-items: flex-start;
            }}
            
            .file-actions {{
                margin-top: 10px;
                width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><span class="material-icons">folder</span> PyServer</h1>
            <p>{displaypath}</p>
        </div>
        
        <div class="breadcrumb">
            <a href="/"><span class="material-icons">home</span> Home</a>
            {self._generate_breadcrumb(displaypath)}
        </div>
        
        <div class="actions">
            <div class="action-card">
                <h3><span class="material-icons">create_new_folder</span> Create Directory</h3>
                <form method="POST" action="/create_directory">
                    <input type="text" name="dirname" placeholder="New directory name" required>
                    <input type="submit" value="Create">
                </form>
            </div>
            
            <div class="action-card">
                <h3><span class="material-icons">upload_file</span> Upload File</h3>
                <form method="POST" action="/upload" enctype="multipart/form-data">
                    <input type="file" name="file" required>
                    <input type="submit" value="Upload">
                </form>
            </div>
            
            <div class="action-card search-box">
                <h3><span class="material-icons">search</span> Search Files</h3>
                <input type="text" id="searchInput" placeholder="Type to search..." onkeyup="filterFiles()">
            </div>
        </div>
        
        <div class="file-list" id="fileList">
            {self._generate_file_list(path, file_list)}
        </div>
    </div>
    
    <script>
        function filterFiles() {{
            const input = document.getElementById('searchInput');
            const filter = input.value.toUpperCase();
            const fileItems = document.getElementsByClassName('file-item');
            
            for (let item of fileItems) {{
                const fileName = item.querySelector('.file-name').textContent;
                if (fileName.toUpperCase().indexOf(filter) > -1) {{
                    item.style.display = '';
                }} else {{
                    item.style.display = 'none';
                }}
            }}
        }}
    </script>
</body>
</html>
"""
            self.wfile.write(html.encode('utf-8', errors='surrogatepass'))
        except Exception as e:
            logger.log(f"Error generating directory listing: {e}", "ERROR")
            self.send_error(500, "Internal server error")
    
    def _generate_breadcrumb(self, path):
        """Generate breadcrumb navigation"""
        parts = [p for p in path.split('/') if p]
        breadcrumb = ""
        current_path = ""
        
        for part in parts:
            current_path += f"/{part}"
            breadcrumb += f' <span>/</span> <a href="{urllib.parse.quote(current_path)}">{part}</a>'
        
        return breadcrumb
    
    def _generate_file_list(self, path, file_list):
        """Generate HTML for file listing"""
        html = ""
        
        for name in file_list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            
            try:
                stat = os.stat(fullname)
                size = stat.st_size
                mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                
                if os.path.isdir(fullname):
                    icon = "folder"
                    displayname += "/"
                    linkname += "/"
                    size_str = "-"
                else:
                    icon = self._get_file_icon(name)
                    size_str = self._format_size(size)
    
                # ✅ safer: construct the button separately
                if not os.path.isdir(fullname):
                    download_url = f"/download?file={urllib.parse.quote(fullname)}"
                    download_button = f'<button class="btn-download" onclick="location.href=\'{download_url}\'">Download</button>'
                else:
                    download_button = ""
    
                # ✅ build the HTML safely
                html += f"""
                <div class="file-item">
                    <span class="material-icons file-icon">{icon}</span>
                    <div class="file-info">
                        <a href="{urllib.parse.quote(linkname)}" class="file-name">{displayname}</a>
                        <div class="file-meta">{size_str} • {mtime}</div>
                    </div>
                    <div class="file-actions">
                        {download_button}
                    </div>
                </div>
                """
            except OSError:
                continue
        
        return html

    
    def _get_file_icon(self, filename):
        """Get appropriate Material icon for file type"""
        ext = os.path.splitext(filename)[1].lower()
        
        icon_map = {
            '.txt': 'description',
            '.pdf': 'picture_as_pdf',
            '.doc': 'description',
            '.docx': 'description',
            '.jpg': 'image',
            '.jpeg': 'image',
            '.png': 'image',
            '.gif': 'image',
            '.mp3': 'audio_file',
            '.mp4': 'video_file',
            '.zip': 'folder_zip',
            '.rar': 'folder_zip',
            '.py': 'code',
            '.js': 'code',
            '.html': 'code',
            '.css': 'code',
        }
        
        return icon_map.get(ext, 'insert_drive_file')
    
    def _format_size(self, size):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/upload':
            self.handle_upload()
        elif self.path == '/create_directory':
            self.handle_create_directory()
        else:
            self.send_error(404, "Not found")
    
    def handle_upload(self):
        """Handle file uploads"""
        try:
            content_type = self.headers['Content-Type']
            if 'multipart/form-data' not in content_type:
                self.send_error(400, "Invalid content type")
                return
            
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            boundary = content_type.split('=')[1].encode()
            parts = post_data.split(boundary)
            
            for part in parts:
                if b'Content-Disposition' in part and b'filename=' in part:
                    header, file_content = part.split(b'\r\n\r\n', 1)
                    filename = self._extract_filename(header)
                    
                    if filename:
                        file_content = file_content.rstrip(b'\r\n--')
                        filename = os.path.basename(filename)
                        
                        filepath = os.path.join(os.getcwd(), filename)
                        
                        with open(filepath, 'wb') as f:
                            f.write(file_content)
                        
                        logger.log(f"File uploaded: {filename}", "INFO")
                        
                        self.send_response(302)
                        self.send_header('Location', '/')
                        self.end_headers()
                        return
            
            self.send_error(400, "No file in upload")
        except Exception as e:
            logger.log(f"Upload error: {e}", "ERROR")
            self.send_error(500, f"Upload failed: {str(e)}")
    
    def handle_create_directory(self):
        """Handle directory creation"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            params = urllib.parse.parse_qs(post_data)
            dirname = params.get('dirname', [''])[0]
            
            if not dirname:
                self.send_error(400, "Directory name required")
                return
            
            dirname = os.path.basename(dirname)
            dirpath = os.path.join(os.getcwd(), dirname)
            
            os.makedirs(dirpath, exist_ok=True)
            logger.log(f"Directory created: {dirname}", "INFO")
            
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
        except Exception as e:
            logger.log(f"Directory creation error: {e}", "ERROR")
            self.send_error(500, f"Failed to create directory: {str(e)}")
    
    def _extract_filename(self, header):
        """Extract filename from Content-Disposition header"""
        header = header.decode('utf-8')
        for line in header.splitlines():
            if 'filename=' in line:
                return line.split('filename=')[1].strip('"')
        return None
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/favicon.ico':
            self.send_response(204)
            self.end_headers()
        elif self.path.startswith('/download'):
            self.handle_download()
        else:
            super().do_GET()
    
    def handle_download(self):
        """Handle file downloads"""
        try:
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            
            if 'file' not in params:
                self.send_error(400, "File parameter missing")
                return
            
            filepath = params['file'][0]
            
            if not os.path.isfile(filepath):
                self.send_error(404, "File not found")
                return
            
            filename = os.path.basename(filepath)
            filesize = os.path.getsize(filepath)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/octet-stream')
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
            self.send_header('Content-Length', str(filesize))
            self.end_headers()
            
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(BUFFER_SIZE)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
            
            logger.log(f"File downloaded: {filename}", "INFO")
        except Exception as e:
            logger.log(f"Download error: {e}", "ERROR")
            self.send_error(500, f"Download failed: {str(e)}")


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """Threaded HTTP server for handling multiple connections"""
    allow_reuse_address = True
    daemon_threads = True


# ============================================================================
# SERVER MANAGER
# ============================================================================
class ServerManager:
    """Manages the HTTP server lifecycle with proper cleanup"""
    
    def __init__(self):
        self.server = None
        self.server_thread = None
        self.is_running = False
        self.port = DEFAULT_PORT
        self.directory = None
        self._shutdown_lock = threading.Lock()  # ADD THIS
    
    def start(self, directory: str, port: int = DEFAULT_PORT) -> bool:
        """Start the HTTP server"""
        with self._shutdown_lock:  # ADD THIS
            if self.is_running:
                logger.log("Server already running", "WARNING")
                return False
            
            try:
                # Validate directory
                if not os.path.isdir(directory):
                    logger.log(f"Invalid directory: {directory}", "ERROR")
                    return False
                
                self.directory = directory
                self.port = port
                
                # Change to target directory
                os.chdir(directory)
                
                # Create server
                self.server = ThreadedHTTPServer(("", port), EnhancedHTTPHandler)
                self.server.daemon_threads = True  # ADD THIS
                self.server.allow_reuse_address = True  # ADD THIS
                
                # Start server in separate thread
                self.server_thread = threading.Thread(
                    target=self.server.serve_forever,
                    daemon=True
                )
                self.server_thread.start()
                
                self.is_running = True
                logger.log(f"Server started on port {port} serving {directory}", "INFO")
                return True
                
            except OSError as e:
                logger.log(f"Failed to start server: {e}", "ERROR")
                return False
            except Exception as e:
                logger.log(f"Unexpected error starting server: {e}", "ERROR")
                return False
    
    def stop(self) -> bool:
        """Stop the HTTP server with proper cleanup"""
        with self._shutdown_lock:  # ADD THIS
            if not self.is_running:
                logger.log("Server not running", "WARNING")
                return False
            
            try:
                if self.server:
                    logger.log("Stopping server...", "INFO")
                    
                    # Mark as not running first
                    self.is_running = False
                    
                    # Shutdown server
                    try:
                        self.server.shutdown()
                    except Exception as e:
                        logger.log(f"Server shutdown warning: {e}", "WARNING")
                    
                    # Close server socket
                    try:
                        self.server.server_close()
                    except Exception as e:
                        logger.log(f"Server close warning: {e}", "WARNING")
                    
                    # Wait for thread with timeout
                    if self.server_thread and self.server_thread.is_alive():
                        self.server_thread.join(timeout=2)
                    
                    self.server = None
                    self.server_thread = None
                    
                    logger.log("Server stopped", "INFO")
                    return True
            except Exception as e:
                logger.log(f"Error stopping server: {e}", "ERROR")
                self.is_running = False
                return False
    
    def get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            # Try to connect to external server to get IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            try:
                # Fallback to hostname
                return socket.gethostbyname(socket.gethostname())
            except Exception:
                return "127.0.0.1"


# ============================================================================
# UI COMPONENTS
# ============================================================================

class StatusCard(MDCard):
    """Reusable status card widget with enhanced design"""
    
    def __init__(self, title: str = "", icon: str = "", **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(20)
        self.spacing = dp(15)
        self.elevation = 3
        self.radius = [dp(20)]
        self.md_bg_color = get_color_from_hex(COLORS['surface'])
        self.ripple_behavior = True  # Add touch feedback
        
        # Header with icon
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            spacing=dp(10)
        )
        
        if icon:
            icon_widget = MDIcon(
                icon=icon,
                theme_text_color="Custom",
                text_color=get_color_from_hex(COLORS['primary']),
                font_size=sp(24)
            )
            header.add_widget(icon_widget)
        
        self.title_label = MDLabel(
            text=title,
            font_style="H6",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(40)
        )
        header.add_widget(self.title_label)
        self.add_widget(header)
        
        # Content section
        content_box = BoxLayout(
            orientation='vertical',
            padding=[0, dp(10)],
            spacing=dp(5)
        )
        
        self.content_label = MDLabel(
            text="",
            theme_text_color="Secondary",
            halign="center",
            font_style="Body1"
        )
        content_box.add_widget(self.content_label)
        
        # Status indicator
        self.status_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(30),
            spacing=dp(5),
            padding=[dp(10), 0],
            opacity=0
        )
        
        self.status_icon = MDIcon(
            icon="circle",
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['success']),
            size_hint_x=None,
            width=dp(24)
        )
        self.status_box.add_widget(self.status_icon)
        
        self.status_label = MDLabel(
            text="",
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['success']),
            font_style="Caption"
        )
        self.status_box.add_widget(self.status_label)
        content_box.add_widget(self.status_box)
        
        self.add_widget(content_box)
    
    def set_content(self, text: str, status: str = None):
        """Update card content and status"""
        self.content_label.text = text
        
        if status:
            self.status_box.opacity = 1
            self.status_label.text = status
            
            if status.lower() == "running":
                color = COLORS['success']
                self.status_icon.icon = "check-circle"
            elif status.lower() == "stopped":
                color = COLORS['error']
                self.status_icon.icon = "stop-circle"
            else:
                color = COLORS['primary']
                self.status_icon.icon = "information"
            
            self.status_icon.text_color = get_color_from_hex(color)
            self.status_label.text_color = get_color_from_hex(color)
        else:
            self.status_box.opacity = 0


# ============================================================================
# SCREENS
# ============================================================================

class MainScreen(Screen):
    """Main application screen with fixed canvas management"""
    
    def __init__(self, server_manager: ServerManager, **kwargs):
        super().__init__(**kwargs)
        self.server_manager = server_manager
        self.qr_texture = None
        self._toolbar_rect = None  # ADD THIS
        self.build_ui()
    
    def build_ui(self):
        """Build the main UI with safe canvas operations"""
        layout = BoxLayout(orientation='vertical', spacing=dp(10))
        
        # Top App Bar with gradient - FIXED
        toolbar_box = BoxLayout(size_hint_y=None, height=dp(64))
        
        # Safely add canvas instruction
        with toolbar_box.canvas.before:
            Color(rgba=get_color_from_hex(COLORS['primary']))
            self._toolbar_rect = Rectangle(pos=toolbar_box.pos, size=toolbar_box.size)
        
        # Bind updates safely
        toolbar_box.bind(
            pos=lambda instance, value: self._safe_update_rect(instance),
            size=lambda instance, value: self._safe_update_rect(instance)
        )
        
        toolbar = MDTopAppBar(
            title="PyServer",
            md_bg_color=(0, 0, 0, 0),
            specific_text_color=get_color_from_hex('#FFFFFF'),
            elevation=0
        )
        toolbar_box.add_widget(toolbar)
        layout.add_widget(toolbar_box)
        
        
        # Main content in ScrollView
        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(
            orientation='vertical',
            padding=[dp(20), dp(10), dp(20), dp(20)],
            spacing=dp(20),
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter('height'))
        
        # Hero section with server status
        hero_card = MDCard(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(10),
            size_hint_y=None,
            height=dp(180),
            elevation=3,
            md_bg_color=get_color_from_hex(COLORS['surface'])
        )
        
        status_icon = MDIcon(
            icon="server",
            font_size=sp(48),
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['primary']),
            halign="center"
        )
        hero_card.add_widget(status_icon)
        
        self.status_text = MDLabel(
            text="Server Status",
            font_style="H5",
            halign="center",
            theme_text_color="Primary"
        )
        hero_card.add_widget(self.status_text)
        
        self.status_subtext = MDLabel(
            text="Server is stopped",
            theme_text_color="Secondary",
            halign="center"
        )
        hero_card.add_widget(self.status_subtext)
        
        content.add_widget(hero_card)
        
        # Directory selection card
        dir_card = MDCard(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(15),
            size_hint_y=None,
            height=dp(200),
            elevation=2,
            md_bg_color=get_color_from_hex(COLORS['surface'])
        )
        
        dir_header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(30),
            spacing=dp(10)
        )
        
        dir_icon = MDIcon(
            icon="folder",
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['primary'])
        )
        dir_header.add_widget(dir_icon)
        
        dir_title = MDLabel(
            text="Select Directory",
            font_style="H6",
            theme_text_color="Primary"
        )
        dir_header.add_widget(dir_title)
        dir_card.add_widget(dir_header)
        
        self.directory_input = MDTextField(
            hint_text="Enter directory path",
            helper_text="Example: /home/user/files",
            helper_text_mode="persistent",
            mode="rectangle",
            size_hint_y=None,
            height=dp(48)
        )
        dir_card.add_widget(self.directory_input)
        
        if kivy_platform == 'android':
            hint_box = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(30),
                spacing=dp(5)
            )
            hint_icon = MDIcon(
                icon="lightbulb-outline",
                theme_text_color="Hint",
                size_hint_x=None,
                width=dp(24)
            )
            hint_box.add_widget(hint_icon)
            
            hint_label = MDLabel(
                text="Internal Storage: /storage/emulated/0",
                theme_text_color="Hint",
                font_style="Caption"
            )
            hint_box.add_widget(hint_label)
            dir_card.add_widget(hint_box)
        
        content.add_widget(dir_card)
        
        # QR Code section
        qr_card = MDCard(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(15),
            size_hint_y=None,
            height=dp(300),
            elevation=2,
            md_bg_color=get_color_from_hex(COLORS['surface'])
        )
        
        qr_header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(30),
            spacing=dp(10)
        )
        
        qr_icon = MDIcon(
            icon="qrcode",
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['primary'])
        )
        qr_header.add_widget(qr_icon)
        
        qr_title = MDLabel(
            text="Scan to Connect",
            font_style="H6",
            theme_text_color="Primary"
        )
        qr_header.add_widget(qr_title)
        qr_card.add_widget(qr_header)
        
        qr_box = RelativeLayout(
            size_hint_y=None,
            height=dp(200)
        )
        
        self.qr_image = Image(
            size_hint=(None, None),
            size=(dp(200), dp(200)),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        qr_box.add_widget(self.qr_image)
        qr_card.add_widget(qr_box)
        
        content.add_widget(qr_card)
        
        # Action buttons
        actions_layout = GridLayout(
            cols=1,
            spacing=dp(10),
            padding=[0, dp(10)],
            size_hint_y=None,
            height=dp(200)
        )
        
        self.btn_toggle = MDRaisedButton(
            text="START SERVER",
            icon="play",
            font_size=sp(18),
            size_hint=(1, None),
            height=dp(56),
            elevation=3,
            md_bg_color=get_color_from_hex(COLORS['success']),
            _radius=dp(28),
            pos_hint={'center_x': 0.5}
        )
        self.btn_toggle.bind(on_press=self.toggle_server)
        actions_layout.add_widget(self.btn_toggle)
        
        button_row = BoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(48)
        )
        
        btn_logs = MDRaisedButton(
            text="VIEW LOGS",
            icon="text-box-search",
            size_hint_x=0.5,
            height=dp(48),
            elevation=2,
            md_bg_color=get_color_from_hex(COLORS['primary']),
            _radius=dp(24)
        )
        btn_logs.bind(on_press=self.goto_logs)
        button_row.add_widget(btn_logs)
        
        self.btn_open = MDRaisedButton(
            text="OPEN IN BROWSER",
            icon="open-in-new",
            size_hint_x=0.5,
            height=dp(48),
            elevation=2,
            md_bg_color=get_color_from_hex(COLORS['secondary']),
            _radius=dp(24),
            disabled=True
        )
        self.btn_open.bind(on_press=self.open_browser)
        button_row.add_widget(self.btn_open)
        
        actions_layout.add_widget(button_row)
        content.add_widget(actions_layout)
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        
        self.add_widget(layout)

    def _safe_update_rect(self, instance):
        """Safely update rectangle"""
        try:
            if self._toolbar_rect and instance:
                self._toolbar_rect.pos = instance.pos
                self._toolbar_rect.size = instance.size
        except Exception as e:
            logger.log(f"Canvas update error: {e}", "ERROR")
    
    def on_pre_leave(self, *args):
        """Clean up when leaving screen"""
        try:
            # Clear any canvas instructions safely
            pass
        except Exception:
            pass
        return super().on_pre_leave(*args)

    
    def _update_rect(self, instance, value):
        """Update toolbar rectangle position and size"""
        self.toolbar_rect.pos = instance.pos
        self.toolbar_rect.size = instance.size
    
    def toggle_server(self, instance):
        """Toggle server on/off"""
        if self.server_manager.is_running:
            self.stop_server()
        else:
            self.start_server()
    
    def start_server(self):
        """Start the server"""
        directory = self.directory_input.text.strip()
        
        if not directory:
            self.show_snackbar("Please enter a directory path", error=True)
            return
        
        if not os.path.isdir(directory):
            self.show_snackbar("Invalid directory path", error=True)
            return
        
        # Start server
        success = self.server_manager.start(directory, DEFAULT_PORT)
        
        if success:
            # Update UI
            self.btn_toggle.text = "STOP SERVER"
            self.btn_toggle.icon = "stop"
            self.btn_toggle.md_bg_color = get_color_from_hex(COLORS['error'])
            self.btn_open.disabled = False
            
            # Update status
            ip = self.server_manager.get_local_ip()
            port = self.server_manager.port
            url = f"http://{ip}:{port}"
            
            self.status_text.text = "Server Running"
            self.status_subtext.text = f"Available at {url}"
            
            # Generate QR code
            self.generate_qr_code(url)
            
            self.show_snackbar("Server started successfully", error=False)
        else:
            self.show_snackbar("Failed to start server", error=True)
    
    def stop_server(self):
        """Stop the server"""
        success = self.server_manager.stop()
        
        if success:
            # Update UI
            self.btn_toggle.text = "START SERVER"
            self.btn_toggle.icon = "play"
            self.btn_toggle.md_bg_color = get_color_from_hex(COLORS['success'])
            self.btn_open.disabled = True
            
            # Clear status
            self.status_text.text = "Server Status"
            self.status_subtext.text = "Server is stopped"
            self.qr_image.texture = None
            
            self.show_snackbar("Server stopped", error=False)
        else:
            self.show_snackbar("Failed to stop server", error=True)
    
    def generate_qr_code(self, url: str):
        """Generate QR code for the URL"""
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
            
            # Convert to Kivy texture
            buf = BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)
            
            core_img = CoreImage(buf, ext='png')
            self.qr_image.texture = core_img.texture
            
        except Exception as e:
            logger.log(f"QR code generation error: {e}", "ERROR")
    
    def open_browser(self, instance):
        """Open server URL in browser"""
        if self.server_manager.is_running:
            ip = self.server_manager.get_local_ip()
            port = self.server_manager.port
            url = f"http://{ip}:{port}"
            
            try:
                webbrowser.open(url)
            except Exception as e:
                logger.log(f"Failed to open browser: {e}", "ERROR")
                self.show_snackbar("Failed to open browser", error=True)
    
    def goto_logs(self, instance):
        """Switch to logs screen"""
        self.manager.current = 'logs'
    
    def show_snackbar(self, message: str, error: bool = False):
        """Show a modern snackbar message"""
        snackbar = Snackbar(
            duration=2.5,
            padding=[dp(15), dp(10)]
        )
        snackbar.snackbar_x = "10dp"
        snackbar.snackbar_y = "10dp"
        snackbar.size_hint_x = (Window.width - dp(20)) / Window.width
        
        # Create a horizontal layout for icon and text
        box = BoxLayout(spacing=dp(10), size_hint_x=0.9)
        
        # Add icon based on message type
        icon = MDIcon(
            icon="check-circle" if not error else "alert-circle",
            theme_text_color="Custom",
            text_color=get_color_from_hex('#FFFFFF'),
            size_hint_x=None,
            width=dp(24)
        )
        box.add_widget(icon)
        
        # Add message text
        label = MDLabel(
            text=message,
            theme_text_color="Custom",
            text_color=get_color_from_hex('#FFFFFF')
        )
        box.add_widget(label)
        
        # Set snackbar properties
        snackbar.bg_color = get_color_from_hex(COLORS['error'] if error else COLORS['success'])
        snackbar.add_widget(box)
        snackbar.open()


class LogScreen(Screen):
    """Logs screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        
        # Register log callback
        logger.add_callback(self.on_new_log)
    
    def build_ui(self):
        """Build logs UI"""
        layout = BoxLayout(orientation='vertical', spacing=dp(5))
        
        # Top App Bar with gradient
        toolbar_box = BoxLayout(size_hint_y=None, height=dp(64))
        with toolbar_box.canvas.before:
            Color(rgba=get_color_from_hex(COLORS['primary']))
            self.toolbar_rect = Rectangle(pos=toolbar_box.pos, size=toolbar_box.size)
        
        toolbar_box.bind(pos=self._update_rect, size=self._update_rect)
        
        toolbar = MDTopAppBar(
            title="[b]Server Logs[/b]",
            md_bg_color=(0, 0, 0, 0),  # Transparent background
            specific_text_color=get_color_from_hex('#FFFFFF'),
            elevation=0,
            left_action_items=[["arrow-left", lambda x: self.goto_main()]],
            right_action_items=[["content-copy", lambda x: self.copy_logs()]]
        )
        toolbar_box.add_widget(toolbar)
        layout.add_widget(toolbar_box)
        
        # Log content card
        log_card = MDCard(
            orientation='vertical',
            padding=dp(10),
            spacing=dp(10),
            elevation=2,
            md_bg_color=get_color_from_hex(COLORS['surface'])
        )
        
        # Log header
        log_header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40),
            padding=[dp(10), 0],
            spacing=dp(10)
        )
        
        log_icon = MDIcon(
            icon="text-box-search",
            theme_text_color="Custom",
            text_color=get_color_from_hex(COLORS['primary'])
        )
        log_header.add_widget(log_icon)
        
        log_title = MDLabel(
            text="Real-time Server Logs",
            theme_text_color="Primary",
            font_style="H6"
        )
        log_header.add_widget(log_title)
        log_card.add_widget(log_header)
        
        # Search box
        search_box = MDTextField(
            icon_left="magnify",
            hint_text="Search logs...",
            helper_text="Type to filter logs",
            helper_text_mode="persistent",
            mode="rectangle",
            size_hint_y=None,
            height=dp(48),
            padding=[dp(10), 0, dp(10), 0]
        )
        search_box.bind(text=self.filter_logs)
        log_card.add_widget(search_box)
        
        # Log display
        log_scroll = ScrollView()
        self.log_text = TextInput(
            text=logger.get_all_logs(),
            readonly=True,
            size_hint_y=None,
            font_name='RobotoMono-Regular',
            font_size=sp(14),
            background_color=get_color_from_hex('#1E1E1E'),
            foreground_color=get_color_from_hex('#FFFFFF'),
            padding=[dp(15), dp(15)]
        )
        self.log_text.bind(minimum_height=self.log_text.setter('height'))
        log_scroll.add_widget(self.log_text)
        log_card.add_widget(log_scroll)
        
        layout.add_widget(log_card)
        
        # Action buttons in a card
        action_card = MDCard(
            orientation='horizontal',
            padding=dp(10),
            spacing=dp(10),
            size_hint_y=None,
            height=dp(80),
            elevation=2,
            md_bg_color=get_color_from_hex(COLORS['surface'])
        )
        
        btn_clear = MDRaisedButton(
            text="CLEAR LOGS",
            icon="delete-sweep",
            size_hint_x=0.5,
            height=dp(50),
            md_bg_color=get_color_from_hex(COLORS['error']),
            _radius=dp(25)
        )
        btn_clear.bind(on_press=self.clear_logs)
        action_card.add_widget(btn_clear)
        
        btn_back = MDRaisedButton(
            text="BACK TO SERVER",
            icon="arrow-left",
            size_hint_x=0.5,
            height=dp(50),
            md_bg_color=get_color_from_hex(COLORS['primary']),
            _radius=dp(25)
        )
        btn_back.bind(on_press=lambda x: self.goto_main())
        action_card.add_widget(btn_back)
        
        layout.add_widget(action_card)
        
        self.add_widget(layout)
    
    def _update_rect(self, instance, value):
        """Update toolbar rectangle position and size"""
        self.toolbar_rect.pos = instance.pos
        self.toolbar_rect.size = instance.size
    
    def copy_logs(self):
        """Copy logs to clipboard"""
        from kivy.core.clipboard import Clipboard
        Clipboard.copy(self.log_text.text)
        Snackbar(text="Logs copied to clipboard").open()
    
    def filter_logs(self, instance, value):
        """Filter logs based on search text"""
        if not value:
            self.log_text.text = logger.get_all_logs()
            return
        
        filtered_logs = []
        for log in logger.logs:
            if value.lower() in log.lower():
                filtered_logs.append(log)
        
        self.log_text.text = "\n".join(filtered_logs)
    
    def on_new_log(self, log_entry: str):
        """Handle new log entries"""
        self.log_text.text += f"\n{log_entry}"
        # Auto-scroll to bottom
        self.log_text.cursor = (0, len(self.log_text.text))
    
    def clear_logs(self, instance):
        """Clear all logs"""
        logger.clear()
        self.log_text.text = ""
    
    def goto_main(self):
        """Switch to main screen"""
        self.manager.current = 'main'


# ============================================================================
# MAIN APPLICATION
# ============================================================================

class PyServerApp(MDApp):
    """Main application class with proper lifecycle management"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.server_manager = ServerManager()
        self._is_stopping = False  # ADD THIS
        
        # Configure theme
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.accent_palette = "Teal"
        self.theme_cls.theme_style = "Light"
        
        # Configure window
        if kivy_platform != 'android':
            Window.size = (400, 700)
        Window.clearcolor = get_color_from_hex(COLORS['background'])
    
    def build(self):
        """Build the application"""
        if kivy_platform == 'android':
            self.check_permissions()
        
        sm = ScreenManager()
        sm.add_widget(MainScreen(self.server_manager, name='main'))
        sm.add_widget(LogScreen(name='logs'))
        
        return sm
    
    def check_permissions(self):
        """Check and request Android permissions"""
        try:
            # Check if we have all files access
            if Build.VERSION.SDK_INT >= 30:  # Android 11+
                if not Environment.isExternalStorageManager():
                    self.request_all_files_access()
                else:
                    logger.log("Storage permissions granted", "INFO")
            else:
                # Request traditional storage permissions
                permissions = [
                    'android.permission.READ_EXTERNAL_STORAGE',
                    'android.permission.WRITE_EXTERNAL_STORAGE',
                    'android.permission.INTERNET'
                ]
                
                for perm in permissions:
                    if not check_permission(perm):
                        request_permissions([perm])
        except Exception as e:
            logger.log(f"Permission check error: {e}", "ERROR")
    
    def request_all_files_access(self):
        """Request all files access permission (Android 11+)"""
        try:
            dialog = MDDialog(
                title="Storage Permission Required",
                text="This app needs access to manage files. Please grant 'All files access' permission in the next screen.",
                buttons=[
                    MDFlatButton(
                        text="CANCEL",
                        on_release=lambda x: dialog.dismiss()
                    ),
                    MDRaisedButton(
                        text="GRANT",
                        on_release=lambda x: self.open_settings()
                    ),
                ],
            )
            dialog.open()
        except Exception as e:
            logger.log(f"Permission dialog error: {e}", "ERROR")
    
    def open_settings(self):
        """Open Android settings for all files access"""
        try:
            activity = PythonActivity.mActivity
            intent = Intent()
            intent.setAction(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
            uri = Uri.fromParts("package", activity.getPackageName(), None)
            intent.setData(uri)
            activity.startActivity(intent)
        except Exception as e:
            logger.log(f"Failed to open settings: {e}", "ERROR")
    
    def on_pause(self):
        """Handle app pause (Android)"""
        logger.log("App paused", "INFO")
        return True  # Return True to allow pause
    
    def on_resume(self):
        """Handle app resume (Android)"""
        logger.log("App resumed", "INFO")
    
    def on_stop(self):
        """Clean up when app closes - CRITICAL FIX"""
        if self._is_stopping:
            return
        
        self._is_stopping = True
        logger.log("Application stopping...", "INFO")
        
        try:
            # Stop server with timeout
            if self.server_manager.is_running:
                # Use thread to prevent blocking
                stop_thread = threading.Thread(
                    target=self.server_manager.stop,
                    daemon=True
                )
                stop_thread.start()
                stop_thread.join(timeout=3)
        except Exception as e:
            logger.log(f"Error during shutdown: {e}", "ERROR")
        
        logger.log("Application stopped", "INFO")
        return True


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == '__main__':
    try:
        PyServerApp().run()
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
