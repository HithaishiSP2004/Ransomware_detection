import sys
import os
import time
import shutil
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from PyQt5 import QtCore, QtWidgets, QtGui
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

# === CONFIGURATION - CHANGE THESE PATHS AS NEEDED === #
EMAIL_SENDER = "" # add email of sender
EMAIL_PASSWORD = ""  # App password if 2FA is enabled and passkey
EMAIL_RECEIVER = "" # add mail of reciver
# ===================================================== #

class RansomwareHandler(FileSystemEventHandler):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.encrypted_files = set()
        self.modified_files = {}  # filename -> last checked timestamp
        self.suspicious_modifications = {}  # filename -> number of suspicious events

    def on_modified(self, event):
        if event.is_directory:
            return
        filepath = event.src_path
        filename = os.path.basename(filepath)

        # Only process if file not already flagged
        if filepath in self.encrypted_files:
            return

        # Check if file size stabilizes (meaning encryption may be done)
        if self._is_file_encrypted(filepath):
            if filepath not in self.encrypted_files:
                self.encrypted_files.add(filepath)
                alert_msg = f"[ALERT] Possible ransomware encrypted file detected: {filename}"
                self.window.show_alert(alert_msg)
                self.window.send_email("Ransomware Alert - Encryption Detected", alert_msg)
                self.window.backup_all()

    def _is_file_encrypted(self, path, wait_time=3):
        try:
            size1 = os.path.getsize(path)
            time.sleep(wait_time)
            size2 = os.path.getsize(path)
            return size1 == size2 and size1 > 0  # size stable and file not empty
        except Exception:
            return False


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ransom Flow - Ransomware Defense")
        self.resize(1000, 650)  # Bigger window
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

        # Button layout for better UI
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

        btn_add_backup = QtWidgets.QPushButton("Add Folder to Back Up")
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
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Add Folder to Back Up")
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
        self.alert_box.append("[INFO] Monitoring started.")

    def stop_monitoring(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            self.alert_box.append("[INFO] Monitoring stopped.")
        else:
            self.alert_box.append("[INFO] Monitoring is not running.")

    def send_email(self, subject, body):
        try:
            msg = MIMEText(body, 'plain', 'utf-8')
            msg['Subject'] = subject
            msg['From'] = formataddr(("Ransom Flow Alert", EMAIL_SENDER))
            msg['To'] = EMAIL_RECEIVER
            msg['Reply-To'] = EMAIL_SENDER
            msg['X-Priority'] = '1'  # High priority
            msg['X-MSMail-Priority'] = 'High'
            msg['Importance'] = 'High'

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
            server.quit()

            self.alert_box.append("[INFO] Email alert sent successfully.")
        except Exception as e:
            self.alert_box.append(f"[ERROR] Failed to send email: {e}")

    def backup_all(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        for folder in self.backup_folders:
            if self.local_backup_path:
                dest = os.path.join(self.local_backup_path, f"backup_{timestamp}_{os.path.basename(folder)}")
                try:
                    shutil.copytree(folder, dest)
                    self.alert_box.append(f"[INFO] Local backup successful: {dest}")
                except Exception as e:
                    self.alert_box.append(f"[ERROR] Local backup failed: {e}")

            if self.cloud_backup_path:
                dest = os.path.join(self.cloud_backup_path, f"backup_{timestamp}_{os.path.basename(folder)}")
                try:
                    shutil.copytree(folder, dest)
                    self.alert_box.append(f"[INFO] Cloud backup successful: {dest}")
                except Exception as e:
                    self.alert_box.append(f"[ERROR] Cloud backup failed: {e}")

    def closeEvent(self, event):
        if self.observer:
            self.observer.stop()
            self.observer.join()
        event.accept()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
