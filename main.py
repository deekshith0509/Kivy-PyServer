"""
PyServer - Complete HTTP File Server for Android
A fully-featured, production-ready file server with modern UI
"""

import os
import sys
import socket
import threading
import datetime
import webbrowser
import urllib.parse
from io import BytesIO
from pathlib import Path
from typing import Optional, Callable
import time

# HTTP Server imports
import http.server
import socketserver

# Image processing
try:
    import qrcode
    from PIL import Image as PILImage
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False
    print("Warning: QR code generation not available")

# Kivy imports
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.utils import get_color_from_hex, platform as kivy_platform
from kivy.metrics import dp, sp
from kivy.core.image import Image as CoreImage
from kivy.animation import Animation

# KivyMD imports
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.textfield import MDTextField
from kivymd.uix.spinner import MDSpinner
from kivy.utils import platform as kivy_platform
from kivymd.uix.list import MDList, OneLineListItem
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton

# Try to import MDIcon
try:
    from kivymd.uix.label import MDIcon
except ImportError:
    MDIcon = MDLabel

# Android-specific imports
if kivy_platform == 'android':
    try:
        from android.permissions import request_permissions, check_permission
        from android.storage import primary_external_storage_path
        from jnius import autoclass, cast

        Build = autoclass('android.os.Build')
        Environment = autoclass('android.os.Environment')
        Intent = autoclass('android.content.Intent')
        PendingIntent = autoclass('android.app.PendingIntent')
        Settings = autoclass('android.provider.Settings')
        Uri = autoclass('android.net.Uri')
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Context = autoclass('android.content.Context')
        
        # Notification components
        NotificationChannel = autoclass('android.app.NotificationChannel')
        NotificationManager = autoclass('android.app.NotificationManager')
        NotificationCompat = autoclass('androidx.core.app.NotificationCompat')
        AndroidColor = autoclass('android.graphics.Color')
        AndroidString = autoclass('java.lang.String')
        
        ANDROID_IMPORTS_OK = True
    except Exception as e:
        print(f"Android imports failed: {e}")
        ANDROID_IMPORTS_OK = False
else:
    ANDROID_IMPORTS_OK = False


# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================

VERSION = "1.0.0"
DEFAULT_PORT = 8000
BUFFER_SIZE = 8192
LOG_MAX_LINES = 1000
DEFAULT_ANDROID_PATH = "/storage/emulated/0/"

# Modern color scheme
COLORS = {
    'primary': '#6366F1',
    'primary_dark': '#4F46E5',
    'secondary': '#10B981',
    'accent': '#F59E0B',
    'background': '#F9FAFB',
    'surface': '#FFFFFF',
    'error': '#EF4444',
    'success': '#10B981',
    'warning': '#F59E0B',
    'text_primary': '#111827',
    'text_secondary': '#6B7280',
    'border': '#E5E7EB',
}


# ============================================================================
# THREAD-SAFE LOGGER
# ============================================================================

class Logger:
    """Thread-safe logging system with callbacks"""
    
    def __init__(self, max_lines: int = LOG_MAX_LINES):
        self.max_lines = max_lines
        self.logs = []
        self.callbacks = []
        self._lock = threading.Lock()
    
    def log(self, message: str, level: str = "INFO"):
        """Add a log message"""
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        with self._lock:
            self.logs.append(log_entry)
            if len(self.logs) > self.max_lines:
                self.logs.pop(0)
            
            # Notify all callbacks on main thread
            for callback in self.callbacks:
                try:
                    Clock.schedule_once(lambda dt, entry=log_entry: callback(entry), 0)
                except Exception as e:
                    print(f"Log callback error: {e}")
        
        print(log_entry)  # Also print to console
    
    def add_callback(self, callback: Callable):
        """Register a callback for new log messages"""
        with self._lock:
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
# ENHANCED HTTP REQUEST HANDLER
# ============================================================================

import zipfile
import tempfile
import shutil

class EnhancedHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler with modern UI, file management, and download functionality"""
    
    server_version = f"PyServer/{VERSION}"
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        message = f"{self.address_string()} - {format % args}"
        logger.log(message, "INFO")
    
    def log_error(self, format, *args):
        """Override error logging"""
        message = f"{self.address_string()} - {format % args}"
        logger.log(message, "ERROR")
    
    def end_headers(self):
        """Add CORS and security headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('X-Content-Type-Options', 'nosniff')
        super().end_headers()
    
    def do_OPTIONS(self):
        """Handle preflight requests"""
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests including download endpoints"""
        # Check if this is a download request
        if self.path.startswith('/download/'):
            self.handle_download()
        else:
            super().do_GET()
    

    def handle_download(self):
        """Handle file/folder download requests"""
        try:
            # Extract the path from /download/url/path
            download_path = self.path[10:]  # Remove '/download/' prefix
            download_path = urllib.parse.unquote(download_path)
            
            # Security check: ensure the path is relative and doesn't try to escape the base directory
            if download_path.startswith('/') or '..' in download_path:
                self.send_error(403, "Access denied")
                return
            
            # Construct the full path
            full_path = os.path.abspath(os.path.join(os.getcwd(), download_path))
            base_dir = os.path.abspath(os.getcwd())
            
            # Additional security: ensure the resolved path is within base directory
            if not full_path.startswith(base_dir):
                self.send_error(403, "Access denied")
                return
            
            if not os.path.exists(full_path):
                self.send_error(404, f"File or folder not found: {download_path}")
                return
            
            if os.path.isfile(full_path):
                # Download single file
                self.download_file(full_path)
            elif os.path.isdir(full_path):
                # Download folder as zip
                self.download_folder_as_zip(full_path)
            else:
                self.send_error(400, "Invalid download target")
                
        except Exception as e:
            logger.log(f"Download error: {e}", "ERROR")
            self.send_error(500, f"Download failed: {str(e)}")


    
    def download_file(self, file_path):
        """Serve a file for download"""
        try:
            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/octet-stream')
            self.send_header('Content-Disposition', f'attachment; filename="{file_name}"')
            self.send_header('Content-Length', str(file_size))
            self.end_headers()
            
            with open(file_path, 'rb') as f:
                shutil.copyfileobj(f, self.wfile)
                
            logger.log(f"File downloaded: {file_name}", "INFO")
            
        except Exception as e:
            logger.log(f"File download error: {e}", "ERROR")
            self.send_error(500, "File download failed")
    
    def download_folder_as_zip(self, folder_path):
        """Compress and download a folder as zip"""
        try:
            folder_name = os.path.basename(folder_path)
            zip_filename = f"{folder_name}.zip"
            
            # Create temporary zip file
            temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
            temp_zip.close()
            
            # Create zip file
            with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Create relative path for zip
                        arcname = os.path.relpath(file_path, os.path.dirname(folder_path))
                        zipf.write(file_path, arcname)
            
            # Get zip file size
            zip_size = os.path.getsize(temp_zip.name)
            
            # Send zip file
            self.send_response(200)
            self.send_header('Content-Type', 'application/zip')
            self.send_header('Content-Disposition', f'attachment; filename="{zip_filename}"')
            self.send_header('Content-Length', str(zip_size))
            self.end_headers()
            
            with open(temp_zip.name, 'rb') as f:
                shutil.copyfileobj(f, self.wfile)
            
            # Clean up temporary file
            os.unlink(temp_zip.name)
            
            logger.log(f"Folder downloaded as zip: {folder_name}", "INFO")
            
        except Exception as e:
            logger.log(f"Folder zip download error: {e}", "ERROR")
            # Clean up temporary file if it exists
            if 'temp_zip' in locals():
                try:
                    os.unlink(temp_zip.name)
                except:
                    pass
            self.send_error(500, "Folder download failed")
    
    def list_directory(self, path):
        """Generate modern directory listing with download buttons"""
        try:
            file_list = os.listdir(path)
        except OSError:
            self.send_error(404, "Cannot read directory")
            return None
        
        file_list.sort(key=lambda a: (not os.path.isdir(os.path.join(path, a)), a.lower()))
        displaypath = urllib.parse.unquote(self.path, errors='surrogatepass')
        
        try:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            
            html = self._generate_html(path, file_list, displaypath)
            self.wfile.write(html.encode('utf-8', errors='surrogatepass'))
        except Exception as e:
            logger.log(f"Directory listing error: {e}", "ERROR")
            self.send_error(500, "Internal server error")
    
    def _generate_html(self, path, file_list, displaypath):
        """Generate modern HTML interface with download buttons"""
        breadcrumb = self._generate_breadcrumb(displaypath)
        file_items = self._generate_file_list(path, file_list)
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyServer - {displaypath}</title>
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
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
        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
        color: white;
        padding: 30px;
        text-align: center;
    }}
    .header h1 {{ font-size: 2em; font-weight: 600; }}
    .breadcrumb {{
        background: #F9FAFB;
        padding: 15px 30px;
        border-bottom: 1px solid #E5E7EB;
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        word-break: break-word;
    }}
    .breadcrumb a {{
        color: #6366F1;
        text-decoration: none;
        margin: 0 5px;
    }}
    .breadcrumb a:hover {{ text-decoration: underline; }}
    .file-list {{ padding: 20px; }}

    .file-item {{
        display: flex;
        align-items: flex-start; /* ✅ align top to match multi-line names */
        justify-content: space-between;
        gap: 10px;
        padding: 15px;
        border-bottom: 1px solid #E5E7EB;
        transition: background 0.2s;
        flex-wrap: nowrap; /* ✅ keeps buttons to right */
        word-break: break-word;
    }}
    .file-item:hover {{ background: #F9FAFB; }}
    .file-icon {{
        font-size: 28px;
        margin-right: 10px;
        min-width: 28px;
        margin-top: 2px;
    }}
    .file-info {{
        flex: 1 1 auto;
        min-width: 0;
        overflow: hidden;
    }}
    .file-name {{
        color: #111827;
        text-decoration: none;
        font-weight: 500;
        display: block;
        word-wrap: anywhere;
        white-space: normal; /* ✅ allows wrapping text naturally */
    }}
    .file-name:hover {{ color: #6366F1; }}
    .file-meta {{
        color: #6B7280;
        font-size: 0.85em;
        margin-top: 5px;
    }}
    .file-actions {{
        flex-shrink: 0;
        display: flex;
        align-items: flex-start;
        justify-content: flex-end;
        gap: 8px;
        min-width: 120px;
    }}
    .download-btn {{
        background: #10B981;
        color: white;
        border: none;
        padding: 8px 14px;
        border-radius: 6px;
        cursor: pointer;
        text-decoration: none;
        font-size: 0.85em;
        white-space: nowrap;
        transition: background 0.2s;
    }}
    .download-btn:hover {{ background: #059669; }}
    .download-btn.zip {{
        background: #F59E0B;
    }}
    .download-btn.zip:hover {{
        background: #D97706;
    }}
    .search-box {{
        padding: 20px 30px;
        background: #F9FAFB;
        border-bottom: 1px solid #E5E7EB;
    }}
    .search-box input {{
        width: 100%;
        padding: 12px 20px;
        border: 2px solid #E5E7EB;
        border-radius: 8px;
        font-size: 14px;
    }}
    .search-box input:focus {{
        outline: none;
        border-color: #6366F1;
    }}

    /* ✅ RESPONSIVE: preserve side alignment without wrapping */
    @media (max-width: 768px) {{
        body {{ padding: 0; }}
        .container {{ border-radius: 0; }}
        .file-item {{
            flex-direction: row;
            align-items: flex-start;
            padding: 12px;
        }}
        .file-info {{
            flex: 1 1 auto;
            overflow-wrap: anywhere;
        }}
        .file-actions {{
            gap: 6px;
            min-width: auto;
        }}
        .download-btn {{
            padding: 7px 10px;
            font-size: 0.8em;
        }}
    }}

    @media (max-width: 480px) {{
        .header h1 {{ font-size: 1.6em; }}
        .file-meta {{ font-size: 0.8em; }}
        .download-btn {{
            padding: 6px 8px;
            font-size: 0.78em;
        }}
    }}
</style>


</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📁 PyServer</h1>
            <p>{displaypath}</p>
        </div>
        <div class="breadcrumb">
            <a href="/">🏠 Home</a>
            {breadcrumb}
        </div>
        <div class="search-box">
            <input type="text" id="search" placeholder="🔍 Search files..." onkeyup="filterFiles()">
        </div>
        <div class="file-list" id="fileList">
            {file_items}
        </div>
    </div>
    <script>
        function filterFiles() {{
            const input = document.getElementById('search');
            const filter = input.value.toUpperCase();
            const items = document.querySelectorAll('.file-item');
            
            items.forEach(item => {{
                const name = item.querySelector('.file-name').textContent;
                item.style.display = name.toUpperCase().indexOf(filter) > -1 ? '' : 'none';
            }});
        }}
    </script>
</body>
</html>"""
    
    def _generate_breadcrumb(self, path):
        """Generate breadcrumb navigation"""
        parts = [p for p in path.split('/') if p]
        breadcrumb = ""
        current = ""
        
        for part in parts:
            current += f"/{part}"
            breadcrumb += f' <span>/</span> <a href="{urllib.parse.quote(current)}">{part}</a>'
        
        return breadcrumb
    
    def _generate_file_list(self, path, file_list):
        """Generate file list HTML with download buttons"""
        html = ""
        
        for name in file_list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            
            try:
                is_dir = os.path.isdir(fullname)
                stat = os.stat(fullname)
                size = stat.st_size
                mtime = datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                
                # Get the relative path from the current directory
                current_dir = os.getcwd()
                relative_path = os.path.relpath(fullname, current_dir)
                
                if is_dir:
                    icon = "📁"
                    displayname += "/"
                    linkname += "/"
                    size_str = "-"
                    download_btn = f'<a href="/download/{urllib.parse.quote(relative_path)}" class="download-btn zip" title="Download as ZIP">📦 ZIP</a>'
                else:
                    icon = self._get_file_icon(name)
                    size_str = self._format_size(size)
                    download_btn = f'<a href="/download/{urllib.parse.quote(relative_path)}" class="download-btn" title="Download file">⬇️ Download</a>'
                
                html += f"""
                <div class="file-item">
                    <div class="file-icon">{icon}</div>
                    <div class="file-info">
                        <a href="{urllib.parse.quote(linkname)}" class="file-name">{displayname}</a>
                        <div class="file-meta">{size_str} • {mtime}</div>
                    </div>
                    <div class="file-actions">
                        {download_btn}
                    </div>
                </div>
                """
            except OSError:
                continue
        
        return html if html else '<p style="text-align:center;padding:40px;color:#6B7280;">No files found</p>'
        
    def _get_file_icon(self, filename):
        """Get emoji icon for file type"""
        ext = os.path.splitext(filename)[1].lower()
        
        icons = {
            '.txt': '📄', '.pdf': '📕', '.doc': '📘', '.docx': '📘',
            '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️', '.gif': '🖼️',
            '.mp3': '🎵', '.mp4': '🎬', '.avi': '🎬',
            '.zip': '📦', '.rar': '📦', '.7z': '📦',
            '.py': '🐍', '.js': '📜', '.html': '🌐', '.css': '🎨',
        }
        
        return icons.get(ext, '📄')
    
    def _format_size(self, size):
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """Threaded HTTP server for handling multiple connections"""
    allow_reuse_address = True
    daemon_threads = True


# ============================================================================
# ANDROID FOREGROUND SERVICE
# ============================================================================

class AndroidForegroundService:
    """Manages Android foreground service for background operation"""
    
    def __init__(self):
        self.service_started = False
        self.notification_id = 1001
        self.channel_id = "pyserver_channel"
    
    def create_notification_channel(self):
        """Create notification channel (Android 8.0+)"""
        if not ANDROID_IMPORTS_OK:
            return
        
        try:
            activity = PythonActivity.mActivity
            nm = activity.getSystemService(Context.NOTIFICATION_SERVICE)
            
            if Build.VERSION.SDK_INT >= 26:
                channel = NotificationChannel(
                    self.channel_id,
                    AndroidString("PyServer Service"),
                    NotificationManager.IMPORTANCE_LOW
                )
                channel.setDescription(AndroidString("Keeps server running"))
                channel.enableLights(True)
                channel.setLightColor(AndroidColor.BLUE)
                nm.createNotificationChannel(channel)
                logger.log("Notification channel created", "INFO")
        except Exception as e:
            logger.log(f"Channel creation error: {e}", "ERROR")
    
    def start_service(self, ip: str, port: int):
        """Start foreground service with notification"""
        if not ANDROID_IMPORTS_OK:
            return False
        
        try:
            activity = PythonActivity.mActivity
            self.create_notification_channel()
            
            # Create intent
            intent = Intent(activity, PythonActivity)
            intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK)
            
            flags = PendingIntent.FLAG_IMMUTABLE | PendingIntent.FLAG_UPDATE_CURRENT
            pending_intent = PendingIntent.getActivity(activity, 0, intent, flags)
            
            # Build notification
            builder = NotificationCompat.Builder(activity, self.channel_id)
            builder.setContentTitle(AndroidString("PyServer Running"))
            builder.setContentText(AndroidString(f"http://{ip}:{port}"))
            builder.setSmallIcon(activity.getApplicationInfo().icon)
            builder.setPriority(NotificationCompat.PRIORITY_LOW)
            builder.setContentIntent(pending_intent)
            builder.setOngoing(True)
            builder.setAutoCancel(False)
            
            notification = builder.build()
            
            # Show notification
            nm = activity.getSystemService(Context.NOTIFICATION_SERVICE)
            nm.notify(self.notification_id, notification)
            
            self.service_started = True
            logger.log("Foreground service started", "INFO")
            return True
            
        except Exception as e:
            logger.log(f"Service start error: {e}", "ERROR")
            return False
    
    def stop_service(self):
        """Stop foreground service"""
        if not ANDROID_IMPORTS_OK or not self.service_started:
            return
        
        try:
            activity = PythonActivity.mActivity
            nm = activity.getSystemService(Context.NOTIFICATION_SERVICE)
            nm.cancel(self.notification_id)
            
            self.service_started = False
            logger.log("Foreground service stopped", "INFO")
        except Exception as e:
            logger.log(f"Service stop error: {e}", "ERROR")


# ============================================================================
# SERVER MANAGER
# ============================================================================

class ServerManager:
    """Manages HTTP server lifecycle with thread safety"""
    
    def __init__(self):
        self.server = None
        self.server_thread = None
        self.is_running = False
        self.port = DEFAULT_PORT
        self.directory = None
        self._lock = threading.Lock()
        self.foreground_service = AndroidForegroundService()
        self._stop_event = threading.Event()
    
    def start(self, directory: str, port: int = DEFAULT_PORT) -> tuple[bool, str]:
        """Start the HTTP server. Returns (success, message)"""
        with self._lock:
            if self.is_running:
                return False, "Server already running"
            
            try:
                # Validate directory
                if not directory or not os.path.isdir(directory):
                    return False, f"Invalid directory: {directory}"
                
                # Check if directory is accessible
                try:
                    test_file = os.path.join(directory, '.pyserver_test')
                    with open(test_file, 'w') as f:
                        f.write('test')
                    os.remove(test_file)
                except Exception as e:
                    return False, f"No write access to directory: {e}"
                
                self.directory = directory
                self.port = port
                
                # Change to target directory
                os.chdir(directory)
                
                # Create and start server
                self.server = ThreadedHTTPServer(("", port), EnhancedHTTPHandler)
                self.server.daemon_threads = True
                self.server.allow_reuse_address = True
                
                self._stop_event.clear()
                self.server_thread = threading.Thread(
                    target=self._run_server,
                    daemon=True
                )
                self.server_thread.start()
                
                # Wait a moment to ensure server started
                time.sleep(0.5)
                
                if not self.server_thread.is_alive():
                    return False, "Server thread failed to start"
                
                self.is_running = True
                
                # Start foreground service on Android
                if kivy_platform == 'android':
                    ip = self.get_local_ip()
                    self.foreground_service.start_service(ip, port)
                
                logger.log(f"Server started on port {port}", "INFO")
                return True, f"Server started successfully on port {port}"
                
            except OSError as e:
                error_msg = f"Failed to start server: {e}"
                if "Address already in use" in str(e):
                    error_msg = f"Port {port} is already in use"
                logger.log(error_msg, "ERROR")
                return False, error_msg
            except Exception as e:
                error_msg = f"Unexpected error: {e}"
                logger.log(error_msg, "ERROR")
                return False, error_msg
    
    def _run_server(self):
        """Run server in thread"""
        try:
            self.server.serve_forever()
        except Exception as e:
            if not self._stop_event.is_set():
                logger.log(f"Server error: {e}", "ERROR")
    
    def stop(self) -> tuple[bool, str]:
        """Stop the HTTP server. Returns (success, message)"""
        with self._lock:
            if not self.is_running:
                return False, "Server not running"
            
            try:
                self._stop_event.set()
                
                # Stop foreground service
                if kivy_platform == 'android':
                    self.foreground_service.stop_service()
                
                # Shutdown server
                if self.server:
                    try:
                        self.server.shutdown()
                    except:
                        pass
                    
                    try:
                        self.server.server_close()
                    except:
                        pass
                    
                    self.server = None
                
                # Wait for thread
                if self.server_thread and self.server_thread.is_alive():
                    self.server_thread.join(timeout=3)
                
                self.server_thread = None
                self.is_running = False
                
                logger.log("Server stopped", "INFO")
                return True, "Server stopped successfully"
                
            except Exception as e:
                error_msg = f"Error stopping server: {e}"
                logger.log(error_msg, "ERROR")
                self.is_running = False
                return False, error_msg
    
    def get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(2)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            try:
                return socket.gethostbyname(socket.gethostname())
            except:
                return "127.0.0.1"


# ============================================================================
# MODERN UI COMPONENTS
# ============================================================================

class StatusCard(MDCard):
    """Animated status card"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(20)
        self.spacing = dp(15)
        self.elevation = 4
        self.radius = [dp(16)]
        self.md_bg_color = get_color_from_hex(COLORS['surface'])
        
        # Status indicator
        self.indicator = BoxLayout(
            size_hint_y=None,
            height=dp(8),
            size_hint_x=0.3,
            pos_hint={'center_x': 0.5}
        )
        with self.indicator.canvas.before:
            self.indicator_color = Color(rgba=get_color_from_hex(COLORS['error']))
            self.indicator_rect = RoundedRectangle(
                pos=self.indicator.pos,
                size=self.indicator.size,
                radius=[dp(4)]
            )
        self.indicator.bind(pos=self._update_indicator, size=self._update_indicator)
        self.add_widget(self.indicator)
        
        # Status text
        self.status_label = MDLabel(
            text="Server Stopped",
            font_style="H5",
            halign="center",
            theme_text_color="Primary"
        )
        self.add_widget(self.status_label)
        
        # URL label
        self.url_label = MDLabel(
            text="Ready to start",
            theme_text_color="Secondary",
            halign="center",
            font_style="Body1"
        )
        self.add_widget(self.url_label)
    
    def _update_indicator(self, *args):
        """Update indicator graphics"""
        self.indicator_rect.pos = self.indicator.pos
        self.indicator_rect.size = self.indicator.size
    
    def set_running(self, url: str):
        """Set running state"""
        self.status_label.text = "Server Running"
        self.url_label.text = url
        self.indicator_color.rgba = get_color_from_hex(COLORS['success'])
        
        # Pulse animation
        anim = Animation(size_hint_x=0.4, duration=0.3) + Animation(size_hint_x=0.3, duration=0.3)
        anim.repeat = True
        anim.start(self.indicator)
    
    def set_stopped(self):
        """Set stopped state"""
        self.status_label.text = "Server Stopped"
        self.url_label.text = "Ready to start"
        self.indicator_color.rgba = get_color_from_hex(COLORS['error'])
        Animation.cancel_all(self.indicator)
        self.indicator.size_hint_x = 0.3


# ============================================================================
# MAIN SCREEN
# ============================================================================

class MainScreen(Screen):
    """Main application screen with modern UI"""
    
    def __init__(self, server_manager: ServerManager, **kwargs):
        super().__init__(**kwargs)
        self.server_manager = server_manager
        self.qr_texture = None
        self.build_ui()
    
    def build_ui(self):
        """Build modern UI"""
        layout = BoxLayout(orientation='vertical')
        
        # Modern gradient toolbar
        toolbar = MDTopAppBar(
            title="PyServer",
            md_bg_color=get_color_from_hex(COLORS['primary']),
            specific_text_color=get_color_from_hex('#FFFFFF'),
            elevation=0,
            right_action_items=[
                ["information-outline", lambda x: self.show_about()],
                ["cog-outline", lambda x: self.show_settings()]
            ]
        )
        layout.add_widget(toolbar)
        
        # Scrollable content
        scroll = ScrollView(do_scroll_x=False)
        content = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(20),
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter('height'))
        
        # Status card with animation
        self.status_card = StatusCard(size_hint_y=None, height=dp(180))
        content.add_widget(self.status_card)
        
        # Directory card
        dir_card = MDCard(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(15),
            size_hint_y=None,
            height=dp(200),
            elevation=3,
            radius=[dp(16)]
        )
        
        dir_label = MDLabel(
            text="📁 Server Directory",
            font_style="H6",
            theme_text_color="Primary"
        )
        dir_card.add_widget(dir_label)
        
        # Pre-fill directory
        default_path = DEFAULT_ANDROID_PATH if kivy_platform == 'android' else os.path.expanduser("~")
        
        self.directory_input = MDTextField(
            text=default_path,
            hint_text="Enter directory path",
            helper_text="This directory will be served over HTTP",
            helper_text_mode="persistent",
            mode="rectangle",
            size_hint_y=None,
            height=dp(56)
        )
        dir_card.add_widget(self.directory_input)
        from kivy.uix.widget import Widget
        dir_card.add_widget(Widget(size_hint_y=None, height=dp(3)))
        # Browse button
        browse_btn = MDRaisedButton(
            text="Browse Common Folders",
            md_bg_color=(0, 0.8, 0.4, 1),  # Green
            text_color=(1, 1, 1, 1),       # White text
            on_release=self.show_folder_picker,
            size_hint_y=None,
            height=dp(48)
        )
        dir_card.add_widget(browse_btn)
        
        content.add_widget(dir_card)
        
        # QR Code card

        
        qr_card = MDCard(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(10),
            size_hint_y=None,
            height=dp(320),
            elevation=3,
            radius=[dp(16)]
        )

        # --- Container inside card ---
        qr_container = BoxLayout(
            orientation='vertical',
            padding=[0, dp(10), 0, dp(10)],  # top/bottom padding
            spacing=dp(10)
        )

        # --- Label (top) ---
        qr_label = MDLabel(
            text="📱 Scan to Connect",
            font_style="H6",
            theme_text_color="Primary",
            halign="center",
            size_hint_y=None,
            height=dp(30)
        )

        # --- QR Image (middle) ---
        self.qr_image = Image(
            size_hint=(None, None),
            size=(dp(180), dp(180)),
            pos_hint={'center_x': 0.5}
        )

        # --- Hint Label (bottom) ---
        self.qr_hint = MDLabel(
            text="QR code will appear when server starts",
            theme_text_color="Hint",
            halign="center",
            font_style="Caption",
            size_hint_y=None,
            height=dp(20)
        )

        # --- Add in correct order ---
        qr_container.add_widget(qr_label)
        qr_container.add_widget(self.qr_image)
        qr_container.add_widget(self.qr_hint)

        qr_card.add_widget(qr_container)
        content.add_widget(qr_card)
        # Action buttons
        actions_card = MDCard(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(15),
            size_hint_y=None,
            height=dp(180),
            elevation=3,
            radius=[dp(16)]
        )
        
        # Main toggle button with icon
        self.btn_toggle = MDRaisedButton(
            text="START SERVER",
            icon="play-circle",
            font_size=sp(18),
            size_hint=(1, None),
            height=dp(56),
            elevation=4,
            md_bg_color=get_color_from_hex(COLORS['success']),
            pos_hint={'center_x': 0.5}
        )
        self.btn_toggle.bind(on_press=self.toggle_server)
        actions_card.add_widget(self.btn_toggle)
        
        # Secondary action buttons
        btn_row = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(48))
        
        btn_logs = MDRaisedButton(
            text="VIEW LOGS",
            icon="file-document-outline",
            size_hint_x=0.5,
            elevation=2,
            md_bg_color=get_color_from_hex(COLORS['primary'])
        )
        btn_logs.bind(on_press=lambda x: setattr(self.manager, 'current', 'logs'))
        btn_row.add_widget(btn_logs)
        
        self.btn_browser = MDRaisedButton(
            text="OPEN BROWSER",
            icon="web",
            size_hint_x=0.5,
            elevation=2,
            md_bg_color=get_color_from_hex(COLORS['secondary']),
            disabled=True
        )
        self.btn_browser.bind(on_press=self.open_browser)
        btn_row.add_widget(self.btn_browser)
        
        actions_card.add_widget(btn_row)
        content.add_widget(actions_card)
        
        # Add some bottom padding
        content.add_widget(BoxLayout(size_hint_y=None, height=dp(20)))
        
        scroll.add_widget(content)
        layout.add_widget(scroll)
        self.add_widget(layout)
    


    def show_folder_picker(self, instance):
        """Show a clean, scrollable folder picker dialog"""
        if kivy_platform == 'android':
            base = "/storage/emulated/0/"
            common_folders = [
                ("Internal Storage", base),
                ("Download", base + "Download"),
                ("Documents", base + "Documents"),
                ("Pictures", base + "Pictures"),
                ("Music", base + "Music"),
                ("Movies", base + "Movies"),
                ("DCIM", base + "DCIM"),
            ]
        else:
            home = os.path.expanduser("~")
            common_folders = [
                ("Home", home),
                ("Downloads", os.path.join(home, "Downloads")),
                ("Documents", os.path.join(home, "Documents")),
                ("Desktop", os.path.join(home, "Desktop")),
            ]

        # Create scrollable content
        folder_list = MDList()
        for name, path in common_folders:
            if os.path.exists(path):
                item = OneLineListItem(
                    text=f"📁 {name}",
                    on_release=lambda x, p=path: self.select_folder_from_dialog(p)
                )
                folder_list.add_widget(item)

        scroll = MDScrollView(size_hint_y=None, height="300dp")
        scroll.add_widget(folder_list)

        # Create the dialog
        self.folder_dialog = MDDialog(
            title="Select Folder",
            type="custom",
            content_cls=scroll,
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.folder_dialog.dismiss()
                ),
            ],
        )

        self.folder_dialog.open()


    def select_folder_from_dialog(self, path):
        """Handle folder selection"""
        self.folder_dialog.dismiss()
        self.select_folder(path)

    
    def select_folder(self, path):
        """Set selected folder"""
        self.directory_input.text = path
        self.folder_dialog.dismiss()
        self.show_snackbar(f"Selected: {os.path.basename(path)}")
    
    def toggle_server(self, instance):
        """Toggle server on/off"""
        if self.server_manager.is_running:
            self.stop_server()
        else:
            self.start_server()
    
    def start_server(self):
        """Start the server with permission validation"""
        # Check Android permissions first
        if kivy_platform == 'android' and ANDROID_IMPORTS_OK:
            try:
                if Build.VERSION.SDK_INT >= 30:
                    if not Environment.isExternalStorageManager():
                        self.show_permission_error()
                        return
            except Exception as e:
                logger.log(f"Permission check error: {e}", "ERROR")
                self.show_permission_error()
                return

        directory = self.directory_input.text.strip()
        
        if not directory:
            self.show_error_dialog("Invalid Input", "Please enter a directory path")
            return
        
        if not os.path.isdir(directory):
            self.show_error_dialog("Directory Not Found", f"The directory '{directory}' does not exist or is not accessible.")
            return
        
        # Show loading
        self.show_loading("Starting server...")
        
        # Start server in background
        def start_thread():
            success, message = self.server_manager.start(directory, DEFAULT_PORT)
            Clock.schedule_once(lambda dt: self.on_server_started(success, message), 0)
        
        threading.Thread(target=start_thread, daemon=False).start()

    def on_server_started(self, success, message):
        """Handle server start result"""
        self.dismiss_loading()
        
        if success:
            # Update UI
            self.btn_toggle.text = "STOP SERVER"
            self.btn_toggle.icon = "stop-circle"
            self.btn_toggle.md_bg_color = get_color_from_hex(COLORS['error'])
            self.btn_browser.disabled = False
            
            # Update status card
            ip = self.server_manager.get_local_ip()
            port = self.server_manager.port
            url = f"http://{ip}:{port}"
            
            self.status_card.set_running(url)
            
            # Generate QR code
            self.generate_qr_code(url)
            
            self.show_snackbar("✅ Server started successfully!", success=True)
        else:
            self.show_error_dialog("Server Error", message)
    
    def stop_server(self):
        """Stop the server"""
        self.show_loading("Stopping server...")
        
        def stop_thread():
            success, message = self.server_manager.stop()
            Clock.schedule_once(lambda dt: self.on_server_stopped(success, message), 0)
        
        threading.Thread(target=stop_thread, daemon=False).start()
    
    def on_server_stopped(self, success, message):
        """Handle server stop result"""
        self.dismiss_loading()
        
        if success:
            # Update UI
            self.btn_toggle.text = "START SERVER"
            self.btn_toggle.icon = "play-circle"
            self.btn_toggle.md_bg_color = get_color_from_hex(COLORS['success'])
            self.btn_browser.disabled = True
            
            # Update status card
            self.status_card.set_stopped()
            
            # Clear QR code
            self.qr_image.texture = None
            self.qr_hint.text = "QR code will appear when server starts"
            
            self.show_snackbar("Server stopped", success=True)
        else:
            self.show_snackbar(message, success=False)
    
    def generate_qr_code(self, url: str):
        """Generate QR code for URL"""
        if not QR_AVAILABLE:
            self.qr_hint.text = "QR code unavailable (install qrcode package)"
            return
        
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color=COLORS['primary'], back_color="white")
            
            buf = BytesIO()
            img.save(buf, format='PNG')
            buf.seek(0)
            
            core_img = CoreImage(buf, ext='png')
            self.qr_image.texture = core_img.texture
            self.qr_hint.text = f"Scan to open {url}"
            
        except Exception as e:
            logger.log(f"QR generation error: {e}", "ERROR")
            self.qr_hint.text = "QR code generation failed"
    
    def open_browser(self, instance):
        """Open server URL in browser"""
        if self.server_manager.is_running:
            ip = self.server_manager.get_local_ip()
            port = self.server_manager.port
            url = f"http://{ip}:{port}"
            
            try:
                webbrowser.open(url)
                self.show_snackbar("Opening browser...")
            except Exception as e:
                logger.log(f"Browser open error: {e}", "ERROR")
                self.show_snackbar("Failed to open browser", success=False)
    
    def show_loading(self, message: str):
        """Show loading dialog"""
        self.loading_dialog = MDDialog(
            title="Please Wait",
            text=message,
            auto_dismiss=False
        )
        self.loading_dialog.open()
    def show_permission_error(self):
        """Show permission error dialog"""
        dialog = MDDialog(
            title="⚠️ Permission Required",
            text=(
                "All Files Access permission is required to start the HTTP server.\n\n"
                "This permission allows the server to access and serve files from your device over the local network."
            ),
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="GRANT PERMISSION",
                    md_bg_color=get_color_from_hex(COLORS['primary']),
                    on_release=lambda x: self.open_permission_settings(dialog)
                )
            ]
        )
        dialog.open()

    def open_permission_settings(self, dialog):
        """Open permission settings"""
        dialog.dismiss()
        app = App.get_running_app()
        if hasattr(app, 'open_all_files_settings'):
            app.open_all_files_settings()
    
    def dismiss_loading(self):
        """Dismiss loading dialog"""
        if hasattr(self, 'loading_dialog'):
            self.loading_dialog.dismiss()
    
    def show_error_dialog(self, title: str, message: str):
        """Show error dialog"""
        dialog = MDDialog(
            title=title,
            text=message,
            buttons=[
                MDRaisedButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
    
    def show_snackbar(self, message: str, success: bool = True):
        """Show modern snackbar - FIXED VERSION"""
        try:
            # Create a custom snackbar implementation to avoid property conflicts
            snackbar_content = BoxLayout(
                orientation='horizontal',
                padding=dp(15),
                spacing=dp(15),
                size_hint_y=None,
                height=dp(50)
            )
            
            # Add message label
            message_label = MDLabel(
                text=message,
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),
                size_hint_x=0.9
            )
            snackbar_content.add_widget(message_label)
            
            # Create the actual snackbar
            snackbar = Snackbar(
                snackbar_x="10dp",
                snackbar_y="10dp",
                size_hint_x=(Window.width - dp(20)) / Window.width,
                bg_color=get_color_from_hex(COLORS['success'] if success else COLORS['error']),
                duration=2.5
            )
            
            # Add our custom content
            snackbar.add_widget(snackbar_content)
            snackbar.open()
            
        except Exception as e:
            # Fallback to simple snackbar if the above fails
            try:
                snackbar = Snackbar(
                    snackbar_x="10dp",
                    snackbar_y="10dp",
                    size_hint_x=(Window.width - dp(20)) / Window.width,
                    bg_color=get_color_from_hex(COLORS['success'] if success else COLORS['error']),
                    duration=2.5
                )
                
                # Try different property names
                if hasattr(snackbar, 'text'):
                    snackbar.text = message
                elif hasattr(snackbar, 'label'):
                    snackbar.label = message
                    
                snackbar.open()
            except Exception as e2:
                print(f"Snackbar error: {e2}")
    
    def show_about(self):
        """Show about dialog"""
        dialog = MDDialog(
            title="About PyServer",
            text=f"Version {VERSION}\n\nA modern HTTP file server for Android.\n\nServe files from your device over your local network.",
            buttons=[
                MDRaisedButton(text="OK", on_release=lambda x: dialog.dismiss())
            ]
        )
        dialog.open()
    
    def show_settings(self):
        """Show settings dialog"""
        dialog = MDDialog(
            title="Settings",
            text=f"Port: {DEFAULT_PORT}\nBuffer Size: {BUFFER_SIZE} bytes",
            buttons=[
                MDRaisedButton(text="OK", on_release=lambda x: dialog.dismiss())
            ]
        )
        dialog.open()


# ============================================================================
# LOGS SCREEN
# ============================================================================

class LogScreen(Screen):
    """Modern logs screen with search and filters"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        logger.add_callback(self.on_new_log)
    
    def build_ui(self):
        """Build logs UI"""
        layout = BoxLayout(orientation='vertical')
        
        # Toolbar
        toolbar = MDTopAppBar(
            title="Server Logs",
            md_bg_color=get_color_from_hex(COLORS['primary']),
            specific_text_color=get_color_from_hex('#FFFFFF'),
            elevation=0,
            left_action_items=[["arrow-left", lambda x: self.go_back()]],
            right_action_items=[
                ["delete-sweep", lambda x: self.clear_logs()],
                ["content-copy", lambda x: self.copy_logs()]
            ]
        )
        layout.add_widget(toolbar)
        
        # Search box
        search_box = BoxLayout(
            orientation='horizontal',
            padding=dp(15),
            spacing=dp(10),
            size_hint_y=None,
            height=dp(70)
        )
        
        self.search_input = MDTextField(
            hint_text="Search logs...",
            mode="rectangle",
            icon_left="magnify"
        )
        self.search_input.bind(text=self.filter_logs)
        search_box.add_widget(self.search_input)
        
        layout.add_widget(search_box)
        
        # Log display
        scroll = ScrollView()
        self.log_text = TextInput(
            text=logger.get_all_logs(),
            readonly=True,
            size_hint_y=None,
            font_name='RobotoMono-Regular',
            font_size=sp(12),
            background_color=get_color_from_hex('#1E293B'),
            foreground_color=get_color_from_hex('#F1F5F9'),
            padding=[dp(15), dp(15)],
            cursor_color=(0, 0, 0, 0)
        )
        self.log_text.bind(minimum_height=self.log_text.setter('height'))
        scroll.add_widget(self.log_text)
        layout.add_widget(scroll)
        
        # Bottom buttons
        buttons = BoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            padding=dp(15),
            size_hint_y=None,
            height=dp(80)
        )
        
        btn_clear = MDRaisedButton(
            text="CLEAR",
            icon="delete",
            size_hint_x=0.33,
            md_bg_color=get_color_from_hex(COLORS['error'])
        )
        btn_clear.bind(on_press=lambda x: self.clear_logs())
        buttons.add_widget(btn_clear)
        
        btn_export = MDRaisedButton(
            text="EXPORT",
            icon="export",
            size_hint_x=0.33,
            md_bg_color=get_color_from_hex(COLORS['accent'])
        )
        btn_export.bind(on_press=lambda x: self.export_logs())
        buttons.add_widget(btn_export)
        
        btn_back = MDRaisedButton(
            text="BACK",
            icon="arrow-left",
            size_hint_x=0.34,
            md_bg_color=get_color_from_hex(COLORS['primary'])
        )
        btn_back.bind(on_press=lambda x: self.go_back())
        buttons.add_widget(btn_back)
        
        layout.add_widget(buttons)
        self.add_widget(layout)
    
    def filter_logs(self, instance, value):
        """Filter logs by search term"""
        if not value:
            self.log_text.text = logger.get_all_logs()
            return
        
        filtered = []
        for log in logger.logs:
            if value.lower() in log.lower():
                filtered.append(log)
        
        self.log_text.text = "\n".join(filtered) if filtered else "No matching logs found"
    
    def on_new_log(self, log_entry: str):
        """Handle new log entry"""
        if not self.search_input.text:
            self.log_text.text += f"\n{log_entry}"
            # Auto-scroll to bottom
            self.log_text.cursor = (0, len(self.log_text.text))
    
    def clear_logs(self):
        """Clear all logs with confirmation"""
        dialog = MDDialog(
            title="Clear Logs?",
            text="This will delete all log entries. Continue?",
            buttons=[
                MDFlatButton(text="CANCEL", on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(
                    text="CLEAR",
                    md_bg_color=get_color_from_hex(COLORS['error']),
                    on_release=lambda x: self.confirm_clear(dialog)
                )
            ]
        )
        dialog.open()
    
    def confirm_clear(self, dialog):
        """Confirm and clear logs"""
        logger.clear()
        self.log_text.text = ""
        dialog.dismiss()
        self.show_snackbar("Logs cleared")
    
    def copy_logs(self):
        """Copy logs to clipboard"""
        try:
            from kivy.core.clipboard import Clipboard
            Clipboard.copy(self.log_text.text)
            self.show_snackbar("Logs copied to clipboard")
        except Exception as e:
            logger.log(f"Copy error: {e}", "ERROR")
            self.show_snackbar("Failed to copy logs")
    
    def export_logs(self):
        """Export logs to file"""
        try:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"pyserver_logs_{timestamp}.txt"
            
            if kivy_platform == 'android':
                path = os.path.join("/storage/emulated/0/Download", filename)
            else:
                path = os.path.join(os.path.expanduser("~"), filename)
            
            with open(path, 'w') as f:
                f.write(self.log_text.text)
            
            self.show_snackbar(f"Logs exported to {filename}")
            logger.log(f"Logs exported to {path}", "INFO")
        except Exception as e:
            logger.log(f"Export error: {e}", "ERROR")
            self.show_snackbar("Failed to export logs")
    
    def show_snackbar(self, message: str):
        """Show snackbar for log screen"""
        try:
            snackbar = Snackbar(
                snackbar_x="10dp",
                snackbar_y="10dp",
                size_hint_x=(Window.width - dp(20)) / Window.width,
                bg_color=get_color_from_hex(COLORS['primary']),
                duration=2
            )
            
            # Try different property names
            if hasattr(snackbar, 'text'):
                snackbar.text = message
            elif hasattr(snackbar, 'label'):
                snackbar.label = message
                
            snackbar.open()
        except Exception as e:
            print(f"Log screen snackbar error: {e}")
    
    def go_back(self):
        """Return to main screen"""
        self.manager.current = 'main'


# ============================================================================
# MAIN APPLICATION
# ============================================================================

class PyServerApp(MDApp):
    """Main PyServer application with full lifecycle management"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.server_manager = ServerManager()
        self._is_stopping = False
        self._permissions_requested = False
        self._permission_checked = False

        # Configure theme
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.accent_palette = "Green"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.material_style = "M3"

        # Configure window
        if kivy_platform != 'android':
            Window.size = (400, 700)
        Window.clearcolor = get_color_from_hex(COLORS['background'])

        logger.log(f"PyServer v{VERSION} initialized", "INFO")

    def build(self):
        """Build the application"""
        sm = ScreenManager()
        sm.add_widget(MainScreen(self.server_manager, name='main'))
        sm.add_widget(LogScreen(name='logs'))
        
        # Check permissions immediately
        if kivy_platform == 'android':
            Clock.schedule_once(lambda dt: self.check_and_request_permissions(), 0.5)
        
        return sm
    # ----------------------------------------------------------------------
    # PERMISSION HANDLING
    # ----------------------------------------------------------------------
    def request_permissions(self):
        """Request all necessary permissions"""
        if self._permissions_requested or not ANDROID_IMPORTS_OK:
            return

        self._permissions_requested = True
        logger.log("Requesting permissions...", "INFO")

        try:
            # Notification permission (Android 13+)
            if Build.VERSION.SDK_INT >= 33:
                if not check_permission('android.permission.POST_NOTIFICATIONS'):
                    request_permissions(['android.permission.POST_NOTIFICATIONS'])

            # Android 11+ (API 30 and above)
            if Build.VERSION.SDK_INT >= 30:
                if not Environment.isExternalStorageManager():
                    Clock.schedule_once(lambda dt: self.show_storage_permission_dialog(), 0.5)
                else:
                    logger.log("Storage permission granted", "INFO")
            else:
                # Android 10 and below
                perms = [
                    'android.permission.READ_EXTERNAL_STORAGE',
                    'android.permission.WRITE_EXTERNAL_STORAGE'
                ]
                needed = [p for p in perms if not check_permission(p)]
                if needed:
                    request_permissions(needed)
                else:
                    logger.log("Storage permissions granted", "INFO")

        except Exception as e:
            logger.log(f"Permission request error: {e}", "ERROR")

    def show_storage_permission_dialog(self):
        """Show dialog explaining why 'All Files Access' is required"""
        dialog = MDDialog(
            title="📁 Storage Permission Required",
            text=(
                "PyServer needs access to your files to serve them over the network.\n\n"
                "Please grant 'All Files Access' permission on the next screen."
            ),
            buttons=[
                MDFlatButton(
                    text="LATER",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRaisedButton(
                    text="GRANT PERMISSION",
                    md_bg_color=get_color_from_hex(COLORS['primary']),
                    on_release=lambda x: self.open_all_files_settings(dialog)
                )
            ]
        )
        dialog.open()

    def open_all_files_settings(self, dialog=None):
        """Open Android 'All Files Access' settings page"""
        if dialog:
            dialog.dismiss()

        try:
            activity = PythonActivity.mActivity
            intent = Intent()
            intent.setAction(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
            uri = Uri.fromParts("package", activity.getPackageName(), None)
            intent.setData(uri)
            activity.startActivity(intent)
            logger.log("Opened All Files Access settings", "INFO")

            # Check permission after returning from settings
            Clock.schedule_once(self.check_permission_after_return, 2)
        except Exception as e:
            logger.log(f"Settings open error: {e}", "ERROR")
            try:
                intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)
                uri = Uri.fromParts("package", activity.getPackageName(), None)
                intent.setData(uri)
                activity.startActivity(intent)
            except:
                pass

    def check_permission_after_return(self, dt):
        """Check if 'All Files Access' permission was granted"""
        try:
            if Environment.isExternalStorageManager():
                logger.log("✅ All Files Access permission granted", "INFO")
            else:
                logger.log("⚠️ All Files Access not granted", "WARNING")
                Clock.schedule_once(lambda dt: self.show_storage_permission_dialog(), 0.5)
        except Exception as e:
            logger.log(f"Permission check error: {e}", "ERROR")

    # ----------------------------------------------------------------------
    # LIFECYCLE
    # ----------------------------------------------------------------------
    def on_pause(self):
        """Handle app pause - server continues running"""
        logger.log("App paused - Server continues in background", "INFO")
        return True

    def on_resume(self):
        """Handle app resume"""
        logger.log("App resumed", "INFO")
        if self.server_manager.is_running:
            logger.log("Server still running in background", "INFO")

    def on_stop(self):
        """Clean up when app stops"""
        if self._is_stopping:
            return True

        self._is_stopping = True
        logger.log("Application stopping...", "INFO")

        try:
            # Stop server gracefully
            if self.server_manager.is_running:
                def stop_server():
                    self.server_manager.stop()

                stop_thread = threading.Thread(target=stop_server, daemon=True)
                stop_thread.start()
                stop_thread.join(timeout=3)
        except Exception as e:
            logger.log(f"Shutdown error: {e}", "ERROR")

        logger.log("Application stopped", "INFO")
        return True
    def check_and_request_permissions(self):
        """Check and request all necessary permissions on app start"""
        if self._permission_checked or not ANDROID_IMPORTS_OK:
            return

        self._permission_checked = True
        logger.log("Checking permissions on app start...", "INFO")

        try:
            # Check if we have All Files Access permission (Android 11+)
            if Build.VERSION.SDK_INT >= 30:
                if not Environment.isExternalStorageManager():
                    logger.log("All Files Access permission not granted", "WARNING")
                    self.show_required_permission_dialog()
                    return
                else:
                    logger.log("All Files Access permission granted", "INFO")
            
            # For Android 10 and below, check storage permissions
            elif Build.VERSION.SDK_INT < 30:
                perms = [
                    'android.permission.READ_EXTERNAL_STORAGE',
                    'android.permission.WRITE_EXTERNAL_STORAGE'
                ]
                needed = [p for p in perms if not check_permission(p)]
                if needed:
                    logger.log("Storage permissions not granted", "WARNING")
                    request_permissions(needed)
                else:
                    logger.log("Storage permissions granted", "INFO")
            
            # Request notification permission for Android 13+
            if Build.VERSION.SDK_INT >= 33:
                if not check_permission('android.permission.POST_NOTIFICATIONS'):
                    request_permissions(['android.permission.POST_NOTIFICATIONS'])

        except Exception as e:
            logger.log(f"Permission check error: {e}", "ERROR")

    def show_required_permission_dialog(self):
        """Show mandatory permission dialog explaining why All Files Access is required"""
        dialog = MDDialog(
            title="🔐 Permission Required for HTTP Server",
            text=(
                "PyServer requires 'All Files Access' permission to function properly.\n\n"
                "This permission is needed to:\n"
                "• Serve files over your local network\n"
                "• Access all directories for file sharing\n"
                "• Stream files to connected devices\n\n"
                "Without this permission, the HTTP server cannot access files on your device."
            ),
            buttons=[
                MDRaisedButton(
                    text="GRANT PERMISSION NOW",
                    md_bg_color=get_color_from_hex(COLORS['primary']),
                    on_release=lambda x: self.open_all_files_settings(dialog)
                )
            ]
        )
        dialog.open()

    def open_all_files_settings(self, dialog=None):
        """Open Android 'All Files Access' settings page"""
        if dialog:
            dialog.dismiss()

        try:
            activity = PythonActivity.mActivity
            intent = Intent()
            intent.setAction(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
            uri = Uri.fromParts("package", activity.getPackageName(), None)
            intent.setData(uri)
            activity.startActivity(intent)
            logger.log("Opened All Files Access settings", "INFO")

            # Check permission after user returns from settings
            Clock.schedule_once(self.verify_permission_after_settings, 3)
            
        except Exception as e:
            logger.log(f"Settings open error: {e}", "ERROR")
            # Fallback to app details settings
            try:
                intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)
                uri = Uri.fromParts("package", activity.getPackageName(), None)
                intent.setData(uri)
                activity.startActivity(intent)
            except Exception as e2:
                logger.log(f"Fallback settings error: {e2}", "ERROR")

    def verify_permission_after_settings(self, dt):
        """Verify if permission was granted after user returns from settings"""
        try:
            if Build.VERSION.SDK_INT >= 30:
                if Environment.isExternalStorageManager():
                    logger.log("✅ All Files Access permission granted!", "INFO")
                    self.show_success_snackbar("Permission granted! Server can now access files.")
                else:
                    logger.log("⚠️ All Files Access still not granted", "WARNING")
                    self.show_required_permission_dialog()
        except Exception as e:
            logger.log(f"Permission verification error: {e}", "ERROR")

    def show_success_snackbar(self, message):
        """Show success message"""
        try:
            snackbar = Snackbar(
                text=message,
                snackbar_x="10dp",
                snackbar_y="10dp",
                size_hint_x=(Window.width - dp(20)) / Window.width
            )
            snackbar.bg_color = get_color_from_hex(COLORS['success'])
            snackbar.open()
        except:
            pass

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================
if __name__ == '__main__':
    try:
        logger.log("Starting PyServer...", "INFO")
        PyServerApp().run()
    except Exception as e:
        logger.log(f"Fatal error: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        raise