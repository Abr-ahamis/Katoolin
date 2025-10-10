#!/usr/bin/env python3
import subprocess
import os
import sys

# ===== Color Codes =====
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

# ===== Directories =====
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.join(BASE_DIR, "tools")

# ===== Banner =====
def banner():
    os.system("clear")
    print(f"""{CYAN}{BOLD}
███╗   ██╗███████╗ ██████╗     █████╗ ██████╗ ██████╗ ██╗   ██╗
████╗  ██║██╔════╝██╔═══██╗   ██╔══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝
██╔██╗ ██║█████╗  ██║   ██║   ███████║██║  ██║██████╔╝ ╚████╔╝ 
██║╚██╗██║██╔══╝  ██║   ██║   ██╔══██║██║  ██║██╔══██╗  ╚██╔╝  
██║ ╚████║███████╗╚██████╔╝   ██║  ██║██████╔╝██║  ██║   ██║   
╚═╝  ╚═══╝╚══════╝ ╚═════╝    ╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝   ╚═╝   
{RESET}{MAGENTA}{BOLD}                      ⚙ Application Installer ⚙{RESET}
""")

# ===== Run Bash Script =====
def execute_bash(script_name):
    """Execute a Bash script from the tools directory"""
    script_path = os.path.join(TOOLS_DIR, script_name)

    if not os.path.isfile(script_path):
        print(f"{RED}❌ Error: {script_path} not found!{RESET}")
        return

    if not os.access(script_path, os.X_OK):
        print(f"{YELLOW}⚙ Making {script_path} executable...{RESET}")
        os.chmod(script_path, 0o755)

    print(f"\n{CYAN}🚀 Running: {BOLD}{script_name}{RESET}\n")
    try:
        subprocess.run([script_path], check=True)
        print(f"\n{GREEN}✅ {script_name} completed successfully!{RESET}")
    except subprocess.CalledProcessError as e:
        print(f"{RED}❌ Error executing {script_name}: {e}{RESET}")
    input(f"\n{YELLOW}Press Enter to return to menu...{RESET}")

# ===== Display Menu =====
def display_menu():
    banner()
    print(f"{CYAN}{'='*80}{RESET}")
    print(f"{BOLD}{GREEN}{'Neo-Katoolin Application Installer':^80}{RESET}")
    print(f"{CYAN}{'='*80}{RESET}\n")

    print(f"{YELLOW}{BOLD}[1]{RESET}  🦁  Install Brave Browser")
    print(f"{YELLOW}{BOLD}[2]{RESET}  💬  Install Telegram Desktop")
    print(f"{YELLOW}{BOLD}[3]{RESET}  💻  Install Visual Studio Code")
    print(f"{YELLOW}{BOLD}[4]{RESET}  🧩  Install ProtonVPN")
    print(f"{YELLOW}{BOLD}[5]{RESET}  📦  Install VirtualBox")
    print(f"{YELLOW}{BOLD}[00]{RESET} 🌀  Install All Applications")
    print(f"{YELLOW}{BOLD}[0]{RESET}  ❌  Exit\n")

    print(f"{CYAN}{'='*80}{RESET}")

# ===== Root Checker =====
def ensure_root():
    """Ensure script runs with sudo."""
    if os.geteuid() != 0:
        print(f"{YELLOW}⚠️  This script requires root privileges.{RESET}")
        print(f"{CYAN}💡 Try running: {GREEN}sudo {sys.argv[0]}{RESET}")
        sys.exit(1)

# ===== Main Menu Logic =====
def main():
    ensure_root()
    while True:
        display_menu()
        choice = input(f"{MAGENTA}{BOLD}👉 Enter your choice [0-5, 00]: {RESET}").strip()

        if choice == '0':
            print(f"{GREEN}👋 Exiting Neo-Katoolin App Installer. Goodbye!{RESET}")
            break
        elif choice == '1':
            execute_bash("install_brave.sh")
        elif choice == '2':
            execute_bash("install_telegram.sh")
        elif choice == '3':
            execute_bash("install_vscode.sh")
        elif choice == '4':
            execute_bash("install_protonvpn.sh")
        elif choice == '5':
            execute_bash("install_virtualbox.sh")
        elif choice == '00':
            for script in [
                "install_brave.sh",
                "install_telegram.sh",
                "install_vscode.sh",
                "install_protonvpn.sh",
                "install_virtualbox.sh"
            ]:
                execute_bash(script)
        else:
            print(f"{RED}❌ Invalid choice. Please try again.{RESET}")
            input(f"{YELLOW}Press Enter to continue...{RESET}")

# ===== Entry Point =====
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{GREEN}👋 Exiting Neo-Katoolin. Goodbye!{RESET}")
        sys.exit(0)
