# File Monitoring System with Web Application

This system includes a file-monitoring component and a web application. The file monitor tracks directory changes while the web application provides a user interface for interaction.

## Author
- Saaketh Matta
- Prahlad Harsha

## Features

- Real-time file monitoring
- SHA-256 hash calculation for all files
- Detection of:
  - New files
  - Modified files
  - Deleted files
- Desktop notifications using notify-send
- Alert file generation (.alert files)
- VirusTotal URL generation for hash verification
- Known hash value tracking
- Web interface for file upload and user interaction

## Prerequisites

- Python 3.x
- Linux-based system
- notify-send (will be auto-installed if missing)
- Flask web framework

## Installation

1. Ensure Python 3.x is installed:
```bash
python3 --version
```

2. Install required system packages:
```bash
sudo apt-get update
sudo apt-get install -y libnotify-bin
pip3 install flask
```

## Configuration

Edit the following variables in `file_monitor.py`:
```python
target_directory = "/home/osboxes/Desktop"    # Directory to monitor
alert_directory = "/home/osboxes/Documents"   # Directory for alert files
```

## Usage

IMPORTANT: Start the file monitor before launching the web application.

1. First, start the file monitoring system:
```bash
python3 file_monitor.py
```

2. In a separate terminal, start the web application:
```bash
python3 app.py
```

3. Access the web interface at:
   - http://localhost:5000 or http://127.0.0.1:5000

4. The file monitor will:
   - Calculate initial hashes for all files
   - Start continuous monitoring
   - Generate desktop notifications for changes
   - Create .alert files in the specified directory

5. Stop monitoring:
   - Press Ctrl+C in both terminals
   - View list of known hash values from file monitor

## Alert Files

Alert files (.alert) contain:
- Event type (NEW_FILE, FILE_MODIFIED, FILE_REMOVED)
- Timestamp
- File path
- SHA-256 hash
- VirusTotal URL for hash verification

## Desktop Notifications

Notifications show:
- Alert title
- File path
- Event type
- VirusTotal URL

## Web Application Features

- User search interface
- File upload capability
- Simple database integration
- Command execution monitoring

## Security Note

The web application includes intentional vulnerabilities for testing purposes. Do not use in a production environment without proper security hardening.

## Note

- The system maintains a list of known hash values
- Hash values are used to detect file modifications
- VirusTotal URLs are provided for security verification
- Web application runs on port 5000 by default
