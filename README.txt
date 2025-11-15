🛡️ Ransomware Detection System

A real-time Python-based security tool to detect ransomware-like behavior, alert users instantly through E-mail, and protect data through automated backups.

📌 About the Project

The Ransomware Detection System is a Python-based security application designed to monitor file-system activity in real time and identify ransomware behavior such as rapid file encryption or unauthorized file modifications.
It provides instant desktop notifications, E-mail alerts, detailed logs, and automatic backups, making it a lightweight but powerful security tool.

This project was developed as part of my Final Year BCA Project (2024–25).

🎯 Key Features
🔍 Real-Time File Monitoring

Monitors selected folders continuously
Detects unusual modifications or rapid encryption patterns
Shows live event logs in GUI

⚠️ Ransomware Detection Engine

Pattern-based detection logic
Alerts the user as soon as suspicious activity is detected

🖥️ Modern PyQt5 GUI

Clean, attractive, and user-friendly interface
Color-themed log window
Easy start/stop monitoring controls

🔔 Instant Alerts

✔ Desktop Notifications
Using QSystemTrayIcon, the system shows native OS notifications instantly.
✔ Email Notifications
When ransomware-like activity is detected:
An automatic email alert is sent to the user's registered email

🔄 Automatic Backup System

Creates backup copies of files before modification
Supports multiple backup paths (local & cloud folders)

📄 Logging System
Full monitoring logs saved automatically when monitoring stops
Each log file includes a timestamp
Useful for incident investigation

🏗️ Tech Stack
Frontend
PyQt5 (Modern GUI)
Backend
Python
Watchdog → Real-time file event monitoring
Cryptography (Fernet) → Used only for safe ransomware simulation
SMTP / Email Library → For real-time email notifications

**Install requirements:
pip install -r requirements.txt

🔐 Ransomware Simulation
python ransomware_simulator.py
( To make attack run this and select the file to be get attacked )
( !!! To make it work you need to off any antivirus that you have in the system )

🛠️ Future Enhancements

AI-based anomaly detection
Cloud-integrated real-time backup
Encrypted file rollback system
Network activity monitoring dashboard
Cross-platform support

🙌 Acknowledgements
Watchdog & PyQt5 community
Python open-source contributors

📞 Contact

Hithaishi S P
Cybersecurity & Ethical hacker
📧 Email: hithaishisp2004@gmail.com
🔗 GitHub: https://github.com/HithaishiSP2004
💼 LinkedIn: www.linkedin.com/in/hithaishi-s-p-192a0a244
