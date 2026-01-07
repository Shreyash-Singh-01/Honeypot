# Honeypot
A lightweight multi-protocol honeypot framework built in Python that simulates SSH and HTTP login services to capture and analyze malicious authentication attempts.  This project is designed for security research, intrusion detection, and attacker behavior analysis, while safely logging attacker activity for later investigation.
# 🕵️ Multi-Protocol Honeypot (SSH & HTTP)

A Python-based **multi-protocol honeypot** that simulates **SSH and HTTP login services** to capture and log malicious authentication attempts.  
Designed for **cybersecurity learning, blue-team research, and attacker behavior analysis** in controlled environments.


### 🔐 SSH Honeypot
- Simulates an OpenSSH service using **Paramiko**
- Logs attacker:
  - Username
  - Password
  - Source IP address
- Supports custom or open credentials
- Threaded connection handling
- No real shell or system access

### 🌐 HTTP Honeypot
- Flask-based fake workplace login page
- Captures submitted credentials and IP addresses
- Always-successful login flow to keep attackers engaged
- Fake internal dashboard for realism

### 🧾 Logging
- Centralized logging using `RotatingFileHandler`
- Logs stored in `audits.log`
- Timestamped attacker activity
- Automatic log rotation

### 🖥️ Command-Line Interface
- Start SSH or HTTP honeypots using flags
- Configure:
  - Bind address
  - Port
  - Username
  - Password
- Graceful shutdown support

---



