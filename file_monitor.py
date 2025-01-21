import os
import hashlib
import time
from pathlib import Path
from typing import List, Tuple
from datetime import datetime
import subprocess

class FileMonitor:
    def __init__(self, target_dir: str, alert_dir: str):
        self.target_dir = target_dir
        self.alert_dir = alert_dir
        self.file_hashes: List[Tuple[str, str]] = []
        self.known_hashes: List[str] = []
        
        # Create alert directory if it doesn't exist
        os.makedirs(self.alert_dir, exist_ok=True)
        
        # Ensure notify-send is installed
        try:
            subprocess.run(['notify-send', '--version'], capture_output=True)
        except FileNotFoundError:
            print("Installing notify-send...")
            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'libnotify-bin'])

    def send_notification(self, title: str, message: str):
        """Send desktop notification."""
        try:
            subprocess.run(['notify-send', '-u', 'critical', title, message])
        except Exception as e:
            print(f"Error sending notification: {e}")

    def generate_alert(self, event_type: str, filepath: str, hash_value: str):
        """Generate alert file and send notification."""
        # Generate alert file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        alert_filename = f"{timestamp}_{event_type}.alert"
        alert_filepath = os.path.join(self.alert_dir, alert_filename)
        
        virustotal_url = f"https://www.virustotal.com/gui/file/{hash_value}/details"
        
        with open(alert_filepath, 'w') as f:
            f.write(f"Event Type: {event_type}\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"File Path: {filepath}\n")
            f.write(f"SHA-256 Hash: {hash_value}\n")
            f.write(f"VirusTotal URL: {virustotal_url}\n")
        
        # Send notification
        title = "File Security Alert"
        if event_type == "NEW_FILE":
            message = f"A new file has been found:\n{filepath}\n\nVirusTotal URL:\n{virustotal_url}"
        elif event_type == "FILE_MODIFIED":
            message = f"A file has been modified:\n{filepath}\n\nVirusTotal URL:\n{virustotal_url}"
        else:
            message = f"File removed:\n{filepath}"
            
        self.send_notification(title, message)
        print(f"Alert generated: {alert_filepath}")

    def calculate_file_hash(self, filepath: str) -> str:
        """Calculate SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()
        
        try:
            with open(filepath, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except (IOError, PermissionError) as e:
            print(f"Error reading file {filepath}: {e}")
            return ""

    def get_all_files(self) -> List[str]:
        """Get all files in target directory and subdirectories."""
        files = []
        for path in Path(self.target_dir).rglob('*'):
            if path.is_file():
                files.append(str(path))
        return files

    def initialize_hashes(self):
        """Initial hash calculation of all files."""
        print("Initializing file hashes...")
        files = self.get_all_files()
        self.file_hashes = [(f, self.calculate_file_hash(f)) for f in files if os.path.exists(f)]
        self.known_hashes.extend([hash_value for _, hash_value in self.file_hashes])
        print(f"Initialized {len(self.file_hashes)} file hashes")

    def check_files(self):
        """Check for file changes and new files."""
        current_files = self.get_all_files()
        
        # Check existing files for changes
        for filepath, stored_hash in self.file_hashes[:]:
            if filepath not in current_files:
                print(f"File removed: {filepath}")
                self.generate_alert("FILE_REMOVED", filepath, stored_hash)
                self.file_hashes.remove((filepath, stored_hash))
            else:
                current_hash = self.calculate_file_hash(filepath)
                if current_hash and current_hash != stored_hash:
                    print(f"File modified: {filepath}")
                    self.generate_alert("FILE_MODIFIED", filepath, current_hash)
                    
                    self.file_hashes.remove((filepath, stored_hash))
                    self.file_hashes.append((filepath, current_hash))
                    if current_hash not in self.known_hashes:
                        self.known_hashes.append(current_hash)
                        print(f"Added new hash to known hashes: {current_hash}")

        # Check for new files
        stored_filepaths = [f for f, h in self.file_hashes]
        for filepath in current_files:
            if filepath not in stored_filepaths:
                current_hash = self.calculate_file_hash(filepath)
                if current_hash:
                    print(f"New file detected: {filepath}")
                    self.generate_alert("NEW_FILE", filepath, current_hash)
                    
                    self.file_hashes.append((filepath, current_hash))
                    if current_hash not in self.known_hashes:
                        self.known_hashes.append(current_hash)
                        print(f"Added new hash to known hashes: {current_hash}")

    def monitor(self, interval: int = 1):
        """Continuous monitoring of files."""
        self.initialize_hashes()
        
        print(f"Starting continuous monitoring of {self.target_dir}")
        try:
            while True:
                self.check_files()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
            print("\nKnown hash values:")
            for hash_value in self.known_hashes:
                print(hash_value)
        except Exception as e:
            print(f"Error during monitoring: {e}")

if __name__ == "__main__":
    target_directory = "/home/osboxes/Desktop"
    alert_directory = "/home/osboxes/Documents"
    monitor = FileMonitor(target_directory, alert_directory)
    monitor.monitor()