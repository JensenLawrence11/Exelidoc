"""
Office AI Add-in - Desktop Launcher
PyQt5 GUI application to manage the backend server and user settings.
"""

import sys
import os
import json
import subprocess
import threading
import time
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QComboBox, QTextEdit, QTabWidget,
    QProgressBar, QStatusBar, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPixmap
from PyQt5.QtCore import QTimer

# ─── Server Manager Thread ─────────────────────────────────────────────────────

class ServerThread(QThread):
    """Runs the FastAPI backend in a separate thread."""
    server_output = pyqtSignal(str)
    server_started = pyqtSignal(bool)
    
    def __init__(self, backend_path):
        super().__init__()
        self.backend_path = backend_path
        self.process = None
        self.running = False
    
    def run(self):
        """Start the backend server."""
        try:
            # Change to backend directory
            os.chdir(os.path.dirname(self.backend_path))
            
            # Start the server
            self.process = subprocess.Popen(
                [sys.executable, "main_production.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            self.running = True
            self.server_started.emit(True)
            self.server_output.emit("✓ Backend server started on http://localhost:8000\n")
            
            # Stream output
            for line in self.process.stdout:
                if line:
                    self.server_output.emit(line)
                    if "Uvicorn running on" in line or "Application startup complete" in line:
                        self.server_started.emit(True)
        
        except Exception as e:
            self.server_output.emit(f"✗ Error starting server: {str(e)}\n")
            self.server_started.emit(False)
    
    def stop(self):
        """Stop the server."""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except:
                self.process.kill()
            self.running = False
            self.server_started.emit(False)


# ─── Main Application ─────────────────────────────────────────────────────────

class ExelidocLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Office AI Add-in — Control Panel")
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet(self._get_stylesheet())
        
        # State
        self.server_running = False
        self.server_thread = None
        self.backend_path = Path(__file__).parent / "backend" / "main_production.py"
        self.config_path = Path.home() / ".office_ai" / "config.json"
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config = self._load_config()
        
        # UI
        self._setup_ui()
        self._check_server()
    
    def _get_stylesheet(self):
        """Dark theme stylesheet."""
        return """
        QMainWindow {
            background-color: #0f1117;
            color: #e8eaf6;
        }
        QWidget {
            background-color: #0f1117;
            color: #e8eaf6;
        }
        QTabWidget::pane {
            border: 1px solid #2e3350;
        }
        QTabBar::tab {
            background-color: #1a1d27;
            color: #e8eaf6;
            padding: 8px 20px;
            border: 1px solid #2e3350;
            border-bottom: none;
        }
        QTabBar::tab:selected {
            background-color: #22263a;
            color: #6c8ef5;
            border-bottom: 2px solid #6c8ef5;
        }
        QPushButton {
            background-color: #6c8ef5;
            color: #fff;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #7d9cf6;
        }
        QPushButton:pressed {
            background-color: #5a7bd0;
        }
        QPushButton:disabled {
            background-color: #3a4a8a;
            color: #999;
        }
        QLineEdit, QTextEdit {
            background-color: #22263a;
            color: #e8eaf6;
            border: 1px solid #2e3350;
            border-radius: 4px;
            padding: 6px;
        }
        QLineEdit:focus, QTextEdit:focus {
            border: 1px solid #6c8ef5;
        }
        QComboBox {
            background-color: #22263a;
            color: #e8eaf6;
            border: 1px solid #2e3350;
            padding: 6px;
            border-radius: 4px;
        }
        QLabel {
            color: #e8eaf6;
        }
        QStatusBar {
            background-color: #1a1d27;
            color: #e8eaf6;
            border-top: 1px solid #2e3350;
        }
        QProgressBar {
            background-color: #22263a;
            border: 1px solid #2e3350;
            border-radius: 4px;
            text-align: center;
        }
        QProgressBar::chunk {
            background-color: #6c8ef5;
        }
        """
    
    def _setup_ui(self):
        """Build the UI."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # ─── Title ────────────────────────────────────────────────────────
        title = QLabel("Office AI Add-in — Server Control Panel")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        # ─── Status Bar ────────────────────────────────────────────────────
        self.status_label = QLabel("⚪ Server offline")
        self.status_label.setStyleSheet("color: #e8564a; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        # ─── Control Buttons ───────────────────────────────────────────────
        btn_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("▶ Start Server")
        self.start_btn.clicked.connect(self.start_server)
        btn_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("⏹ Stop Server")
        self.stop_btn.clicked.connect(self.stop_server)
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.stop_btn)
        
        layout.addLayout(btn_layout)
        
        # ─── Tabs ──────────────────────────────────────────────────────────
        tabs = QTabWidget()
        tabs.addTab(self._create_settings_tab(), "⚙ Settings")
        tabs.addTab(self._create_server_tab(), "📊 Server")
        tabs.addTab(self._create_help_tab(), "ℹ Help")
        layout.addWidget(tabs)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def _create_settings_tab(self):
        """Settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # ─── API Keys ──────────────────────────────────────────────────────
        layout.addWidget(QLabel("API Keys (for cloud AI):"))
        
        layout.addWidget(QLabel("OpenAI Key:"))
        self.openai_key = QLineEdit()
        self.openai_key.setEchoMode(QLineEdit.Password)
        self.openai_key.setText(self.config.get("openai_key", ""))
        layout.addWidget(self.openai_key)
        
        layout.addWidget(QLabel("Anthropic Key:"))
        self.anthropic_key = QLineEdit()
        self.anthropic_key.setEchoMode(QLineEdit.Password)
        self.anthropic_key.setText(self.config.get("anthropic_key", ""))
        layout.addWidget(self.anthropic_key)
        
        layout.addWidget(QLabel("Gemini Key:"))
        self.gemini_key = QLineEdit()
        self.gemini_key.setEchoMode(QLineEdit.Password)
        self.gemini_key.setText(self.config.get("gemini_key", ""))
        layout.addWidget(self.gemini_key)
        
        # ─── Subscription Tiers ────────────────────────────────────────────
        layout.addWidget(QLabel("\nSubscription Tiers (tokens/month):"))
        
        layout.addWidget(QLabel("Free Tier:"))
        self.free_tier = QLineEdit()
        self.free_tier.setText(str(self.config.get("free_tier", 10000)))
        layout.addWidget(self.free_tier)
        
        layout.addWidget(QLabel("Pro Tier:"))
        self.pro_tier = QLineEdit()
        self.pro_tier.setText(str(self.config.get("pro_tier", 100000)))
        layout.addWidget(self.pro_tier)
        
        layout.addWidget(QLabel("Enterprise Tier:"))
        self.enterprise_tier = QLineEdit()
        self.enterprise_tier.setText(str(self.config.get("enterprise_tier", 1000000)))
        layout.addWidget(self.enterprise_tier)
        
        # ─── Buttons ───────────────────────────────────────────────────────
        save_btn = QPushButton("💾 Save Configuration")
        save_btn.clicked.connect(self.save_config)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        
        return widget
    
    def _create_server_tab(self):
        """Server status tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("Server Output:"))
        self.server_log = QTextEdit()
        self.server_log.setReadOnly(True)
        layout.addWidget(self.server_log)
        
        # ─── Stats ────────────────────────────────────────────────────────
        stats_layout = QHBoxLayout()
        
        self.stats_label = QLabel("Requests: 0 | Tokens Used: 0 | Users: 0")
        self.stats_label.setStyleSheet("color: #6c8ef5; font-weight: bold;")
        stats_layout.addWidget(self.stats_label)
        
        refresh_stats_btn = QPushButton("🔄 Refresh")
        refresh_stats_btn.clicked.connect(self.refresh_stats)
        stats_layout.addWidget(refresh_stats_btn)
        
        layout.addLayout(stats_layout)
        
        # ─── Database ──────────────────────────────────────────────────────
        db_layout = QHBoxLayout()
        db_layout.addWidget(QLabel("Database Location:"))
        self.db_label = QLabel("~/.office_ai/office_ai.db")
        self.db_label.setStyleSheet("color: #7b82a8;")
        db_layout.addWidget(self.db_label)
        
        view_db_btn = QPushButton("📂 View")
        view_db_btn.clicked.connect(self.open_database_folder)
        db_layout.addWidget(view_db_btn)
        
        layout.addLayout(db_layout)
        
        return widget
    
    def _create_help_tab(self):
        """Help tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setText("""
OFFICE AI ADD-IN — SERVER CONTROL PANEL

1. START THE SERVER
   Click "Start Server" to begin. The backend will run on http://localhost:8000

2. CONFIGURE API KEYS
   In Settings tab, enter your API keys for:
   • OpenAI (GPT)
   • Anthropic (Claude)
   • Google Gemini

3. LOAD IN OFFICE
   In Word/Excel/PowerPoint:
   • Insert → Add-ins → Upload My Add-in
   • Select the manifest.xml file
   • The Office AI panel appears on the right

4. USERS SIGN UP
   Users enter their email in the "Account" tab
   They're automatically assigned a Free tier (10,000 tokens/month)

5. CHARGE FOR UPGRADES
   When users hit their token limit, they see an upgrade prompt
   Set your pricing and integrate Stripe/Paddle for billing

LOCAL AI (OLLAMA)
   • Download Ollama from ollama.com
   • Run: ollama pull llama3
   • Run: ollama serve
   • Users can switch to "Local AI" in the add-in

TOKEN TRACKING
   All usage is tracked in SQLite database at:
   ~/.office_ai/office_ai.db
   
   View with: sqlite3 office_ai.db
   SELECT * FROM usage;
   SELECT * FROM logs;

TROUBLESHOOTING
   If the add-in won't load:
   • Make sure server is running (green status)
   • Check that port 8000 is available
   • Hard refresh in Office (Ctrl+F5)

For more info: Check the documentation files included
        """)
        layout.addWidget(help_text)
        
        return widget
    
    def start_server(self):
        """Start the backend server."""
        if self.server_running:
            QMessageBox.warning(self, "Already Running", "Server is already running!")
            return
        
        self.server_log.clear()
        self.server_log.append("Starting server...\n")
        
        self.server_thread = ServerThread(str(self.backend_path))
        self.server_thread.server_output.connect(self.log_output)
        self.server_thread.server_started.connect(self.on_server_started)
        self.server_thread.start()
        
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
    
    def stop_server(self):
        """Stop the backend server."""
        if self.server_thread:
            self.server_thread.stop()
            self.server_log.append("\n✓ Server stopped.\n")
        
        self.server_running = False
        self.status_label.setText("⚪ Server offline")
        self.status_label.setStyleSheet("color: #e8564a; font-weight: bold;")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    
    def on_server_started(self, started):
        """Called when server starts/stops."""
        self.server_running = started
        if started:
            self.status_label.setText("🟢 Server online at http://localhost:8000")
            self.status_label.setStyleSheet("color: #4caf88; font-weight: bold;")
            self.statusBar().showMessage("Server running!")
        else:
            self.status_label.setText("🔴 Server offline")
            self.status_label.setStyleSheet("color: #e8564a; font-weight: bold;")
    
    def log_output(self, text):
        """Log server output."""
        self.server_log.append(text.strip())
        # Auto-scroll to bottom
        self.server_log.verticalScrollBar().setValue(
            self.server_log.verticalScrollBar().maximum()
        )
    
    def save_config(self):
        """Save configuration."""
        self.config.update({
            "openai_key": self.openai_key.text(),
            "anthropic_key": self.anthropic_key.text(),
            "gemini_key": self.gemini_key.text(),
            "free_tier": int(self.free_tier.text() or 10000),
            "pro_tier": int(self.pro_tier.text() or 100000),
            "enterprise_tier": int(self.enterprise_tier.text() or 1000000),
        })
        
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        QMessageBox.information(self, "Saved", "Configuration saved!")
        self.statusBar().showMessage("Configuration saved")
    
    def _load_config(self):
        """Load configuration from file."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {
            "openai_key": "",
            "anthropic_key": "",
            "gemini_key": "",
            "free_tier": 10000,
            "pro_tier": 100000,
            "enterprise_tier": 1000000,
        }
    
    def refresh_stats(self):
        """Refresh stats from database."""
        try:
            import sqlite3
            db_path = Path.home() / ".office_ai" / "office_ai.db"
            
            if db_path.exists():
                conn = sqlite3.connect(db_path)
                c = conn.cursor()
                
                c.execute("SELECT COUNT(*) FROM logs")
                requests = c.fetchone()[0]
                
                c.execute("SELECT SUM(tokens_used) FROM logs")
                tokens = c.fetchone()[0] or 0
                
                c.execute("SELECT COUNT(*) FROM users")
                users = c.fetchone()[0]
                
                conn.close()
                
                self.stats_label.setText(
                    f"Requests: {requests} | Tokens Used: {tokens:,} | Users: {users}"
                )
        except Exception as e:
            self.stats_label.setText(f"Error loading stats: {str(e)}")
    
    def open_database_folder(self):
        """Open database location in file explorer."""
        db_path = Path.home() / ".office_ai"
        db_path.mkdir(parents=True, exist_ok=True)
        
        import platform
        if platform.system() == "Windows":
            os.startfile(db_path)
        elif platform.system() == "Darwin":
            os.system(f"open '{db_path}'")
        else:
            os.system(f"xdg-open '{db_path}'")
    
    def _check_server(self):
        """Periodically check server status."""
        timer = QTimer()
        timer.timeout.connect(self.refresh_stats)
        timer.start(5000)  # Every 5 seconds


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = ExelidocLauncher()
    launcher.show()
    sys.exit(app.exec_())
