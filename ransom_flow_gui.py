import sys
# import base64
import os
# import time
import shutil
import smtplib
# import hashlib
import math
from email.mime.text import MIMEText
from email.utils import formataddr
from PyQt5 import QtCore, QtWidgets, QtGui
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from cryptography.fernet import Fernet, InvalidToken
from datetime import datetime


# === CONFIGURATION - CHANGE THESE PATHS AS NEEDED === #
EMAIL_SENDER = "" # gmail of sender
EMAIL_PASSWORD = ""  # App password if 2FA is enabled app passcode
EMAIL_RECEIVER = ""# reciver
# ===================================================== #

class RansomwareHandler(FileSystemEventHandler):
    def __init__(self, window, key=None):
        self.window = window
        self.key = key
        self.suspicious_exts = ['.locked', '.encrypted', '.crypt', '.enc']
        self.ignored_extensions = ['.log', '.dll', '.sys', '.tmp', '.pyc']
        self.known_ransom_filenames = ['readme.txt', 'decrypt_instructions.txt', 'how_to_decrypt.html']
        self.recent_alerts = set()  # Track alerted filenames to avoid duplicates

    def on_created(self, event):
        if event.is_directory:
            return
        self._check_file(event.src_path, created=True)

    def on_modified(self, event):
        if event.is_directory:
            return
        self._check_file(event.src_path, created=False)

    def _check_file(self, filepath, created=False):
        filename = os.path.basename(filepath).lower()
        ext = os.path.splitext(filename)[1].lower()

        if ext in self.ignored_extensions:
            return  # Ignore irrelevant files

        # Only alert once per file regardless of created/modified
        if filename in self.recent_alerts:
            return

        # 1. Detect by suspicious extension (highest priority)
        if any(s_ext in filename for s_ext in self.suspicious_exts):
            self._trigger_alert(
                f"[ALERT - {self._now()}] Suspicious encrypted extension: {filename}",
                "Ransomware Alert - File Extension",
                filename
            )
            return

        # 2. Detect ransom note by name and content
        if filename in self.known_ransom_filenames or filename.endswith((".txt", ".html")):
            if self._contains_ransom_note(filepath):
                self._trigger_alert(
                    f"[ALERT - {self._now()}] Possible ransom note: {filename}",
                    "Ransomware Alert - Ransom Note",
                    filename
                )
                return

        # 3. Detect encrypted content (entropy + unreadable + optional Fernet)
        if self._looks_encrypted(filepath):
            action = "created" if created else "modified"
            self._trigger_alert(
                f"[ALERT - {self._now()}] Encrypted file {action}: {filename}",
                "Ransomware Alert - Encrypted Content",
                filename
            )

    def _looks_encrypted(self, filepath):
        try:
            with open(filepath, "rb") as f:
                data = f.read(2048)
                entropy = self._calculate_entropy(data)

            if entropy > 7.5:
                return True  # Likely encrypted or compressed

            try:
                decoded = data.decode('utf-8')
                if any(ord(c) > 127 for c in decoded):  # Contains non-ASCII
                    return True
            except UnicodeDecodeError:
                return True

            if self.key:
                try:
                    fernet = Fernet(self.key)
                    fernet.decrypt(data)
                    return False
                except InvalidToken:
                    return True

        except Exception as e:
            print(f"[ERROR] Could not check encryption for {filepath}: {e}")
        return False

    def _contains_ransom_note(self, filepath):
        try:
            with open(filepath, 'r', errors='ignore') as f:
                content = f.read().lower()
            keywords = ['your files', 'ransom', 'bitcoin', 'decrypt', 'pay', 'key', 'victim', 'restore']
            return any(k in content for k in keywords)
        except PermissionError:
            print(f"[PERMISSION DENIED] Cannot read file: {filepath}")
        except Exception as e:
            print(f"[ERROR] Failed to read ransom note from {filepath}: {e}")
        return False

    def _calculate_entropy(self, data):
        if not data:
            return 0
        byte_count = [0] * 256
        for byte in data:
            byte_count[byte] += 1
        entropy = 0
        for count in byte_count:
            if count:
                p = count / len(data)
                entropy -= p * math.log2(p)
        return entropy

    def _trigger_alert(self, message, subject, filename):
        if filename in self.recent_alerts:
            return  # Already alerted for this file
        self.recent_alerts.add(filename)

        print(message)
        self.window.show_alert(message)
        self.window.send_email(subject, message)
        self.window.backup_all()

    def _now(self):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')




class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ransom Flow - Ransomware Defense")
        self.resize(1000, 650)
        self.setStyleSheet("""
            QWidget {
                background-color: #0d1117;
                color: #c9d1d9;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 14px;
            }
            QPushButton {
                background-color: #238636;
                border: none;
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
                color: white;
            }
            QPushButton:hover {
                background-color: #2ea043;
            }
            QTextEdit, QListWidget {
                background-color: #161b22;
                color: #f0f6fc;
                border: 1px solid #30363d;
                border-radius: 6px;
            }
        """)

        self.folders_to_monitor = []
        self.backup_folders = []
        self.local_backup_path = None
        self.cloud_backup_path = None
        self.observer = None

        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()

        title = QtWidgets.QLabel("🛡 Ransom Flow - Ransomware Defense System")
        title.setAlignment(QtCore.Qt.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #58a6ff; margin-bottom: 15px;")
        layout.addWidget(title)

        btn_layout = QtWidgets.QHBoxLayout()

        btn_monitor = QtWidgets.QPushButton("Add Folder/Disk to Monitor")
        btn_monitor.clicked.connect(self.add_monitor_folder)
        btn_layout.addWidget(btn_monitor)

        btn_start = QtWidgets.QPushButton("Start Monitoring")
        btn_start.clicked.connect(self.start_monitoring)
        btn_layout.addWidget(btn_start)

        btn_stop = QtWidgets.QPushButton("Stop Monitoring")
        btn_stop.clicked.connect(self.stop_monitoring)
        btn_layout.addWidget(btn_stop)

        layout.addLayout(btn_layout)

        btn_add_backup = QtWidgets.QPushButton("Add Folder to Be Backed Up")
        btn_add_backup.clicked.connect(self.add_backup_folder)
        layout.addWidget(btn_add_backup)

        btn_local = QtWidgets.QPushButton("Set Local Backup Directory")
        btn_local.clicked.connect(self.set_local_backup)
        layout.addWidget(btn_local)

        btn_cloud = QtWidgets.QPushButton("Set Cloud Backup Directory")
        btn_cloud.clicked.connect(self.set_cloud_backup)
        layout.addWidget(btn_cloud)

        self.folder_list = QtWidgets.QListWidget()
        self.folder_list.setMinimumHeight(150)
        layout.addWidget(self.folder_list)

        self.alert_box = QtWidgets.QTextEdit()
        self.alert_box.setReadOnly(True)
        self.alert_box.setMinimumHeight(200)
        layout.addWidget(self.alert_box)

        self.setLayout(layout)

    def add_monitor_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder or Disk to Monitor")
        if folder and folder not in self.folders_to_monitor:
            self.folders_to_monitor.append(folder)
            self.folder_list.addItem(f"Monitoring: {folder}")
            self.alert_box.append(f"[INFO] Added to monitor: {folder}")

    def add_backup_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Add Folder to Be Backed Up")
        if folder:
            self.backup_folders.append(folder)
            self.folder_list.addItem(f"Backup Source: {folder}")

    def set_local_backup(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Local Backup Directory")
        if folder:
            self.local_backup_path = folder
            self.folder_list.addItem(f"Local Backup Path: {folder}")

    def set_cloud_backup(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Cloud Backup Directory")
        if folder:
            self.cloud_backup_path = folder
            self.folder_list.addItem(f"Cloud Backup Path: {folder}")

    def show_alert(self, msg):
        self.alert_box.append(msg)

    def start_monitoring(self):
        if self.observer:
            self.alert_box.append("[INFO] Monitoring already running.")
            return
        if not self.folders_to_monitor:
            self.alert_box.append("[WARNING] No folders selected to monitor.")
            return

        handler = RansomwareHandler(self)
        self.observer = Observer()

        for folder in self.folders_to_monitor:
            if os.path.exists(folder):
                self.observer.schedule(handler, folder, recursive=True)
                self.alert_box.append(f"[MONITOR] Watching: {folder}")
            else:
                self.alert_box.append(f"[WARNING] Path not found: {folder}")

        self.observer.start()
        self.alert_box.append(f"[START] Monitoring started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    def stop_monitoring(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            self.alert_box.append(f"[STOP] Monitoring stopped at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            self.alert_box.append("[INFO] Monitoring is not running.")
            
    def save_log_file(self):
        logs = self.alert_box.toPlainText()
        log_path = os.path.join(os.getcwd(), f"ransomware_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(log_path, "w") as f:
            f.write(logs)
        self.alert_box.append(f"[LOG] Log file saved at: {log_path}")
       

    def send_email(self, subject, body):
        try:
            msg = MIMEText(body, 'plain', 'utf-8')
            msg['Subject'] = subject
            msg['From'] = formataddr(("Ransom Flow Alert", EMAIL_SENDER))
            msg['To'] = EMAIL_RECEIVER

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, [EMAIL_RECEIVER], msg.as_string())
            server.quit()
            
            self.alert_box.append(f"[EMAIL] Alert sent to {EMAIL_RECEIVER}")
        except Exception as e:
            self.alert_box.append(f"[ERROR] Failed to send email: {str(e)}")

    def backup_all(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if not self.backup_folders:
            self.alert_box.append("[WARNING] No folders added for backup.")
            return

        if not self.local_backup_path and not self.cloud_backup_path:
            self.alert_box.append("[WARNING] No backup destination set.")
            return

        for source in self.backup_folders:
            if not os.path.exists(source):
                self.alert_box.append(f"[WARNING] Backup source does not exist: {source}")
                continue

            for destination in [self.local_backup_path, self.cloud_backup_path]:
                if destination:
                    try:
                        dest_folder_name = os.path.basename(source.rstrip(os.sep)) + "_" + timestamp
                        final_dest = os.path.join(destination, dest_folder_name)
                        shutil.copytree(source, final_dest)
                        self.alert_box.append(f"[BACKUP] {source} ➜ {final_dest}")
                    except Exception as e:
                        self.alert_box.append(f"[ERROR] Failed to back up {source} to {destination}: {e}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
