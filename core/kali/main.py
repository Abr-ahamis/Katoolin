#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil

# ===== Color Codes =====
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

# ===== Helper: Determine previous script to return to =====
def get_return_target():
    """
    Priority:
      1. Command-line: --return-to <path>
      2. Environment variable: PREV_SCRIPT
      3. None
    """
    if "--return-to" in sys.argv:
        idx = sys.argv.index("--return-to")
        if idx + 1 < len(sys.argv):
            return sys.argv[idx + 1]
    prev = os.environ.get("PREV_SCRIPT")
    if prev:
        return prev
    return None

def get_return_mode():
    """
    Return mode:
      --return-mode [exec|spawn]
    Default: exec
    """
    if "--return-mode" in sys.argv:
        idx = sys.argv.index("--return-mode")
        if idx + 1 < len(sys.argv):
            mode = sys.argv[idx + 1].lower()
            if mode in ("exec", "spawn"):
                return mode
    # also check env var
    mode_env = os.environ.get("RETURN_MODE", "").lower()
    if mode_env in ("exec", "spawn"):
        return mode_env
    return "exec"

RETURN_TARGET = get_return_target()
RETURN_MODE = get_return_mode()

def spawn_return_target(target):
    """Run the return target as a child process and wait for it to finish."""
    target = os.path.expanduser(target)
    if not os.path.exists(target):
        print(f"{YELLOW}⚠ Return target not found: {target}{RESET}")
        return False

    try:
        if target.endswith(".py"):
            print(f"{CYAN}▶ Spawning Python script: {target}{RESET}")
            subprocess.run([sys.executable, target])
            return True
        elif target.endswith(".sh"):
            bash_path = shutil.which("bash") or "/bin/bash"
            print(f"{CYAN}▶ Spawning shell script with bash: {target}{RESET}")
            subprocess.run([bash_path, target])
            return True
        elif os.access(target, os.X_OK):
            print(f"{CYAN}▶ Spawning executable: {target}{RESET}")
            subprocess.run([target])
            return True
        else:
            print(f"{YELLOW}⚠ Not executable and no interpreter detected: {target}{RESET}")
            return False
    except Exception as e:
        print(f"{RED}❌ Error spawning return target: {e}{RESET}")
        return False

def exec_return_target(target):
    """
    Replace current process with the return target.
    Supports .py with same python interpreter, .sh with bash, or executable.
    """
    target = os.path.expanduser(target)
    if not os.path.exists(target):
        print(f"{YELLOW}⚠ Return target not found: {target}{RESET}")
        return False

    try:
        if target.endswith(".py"):
            print(f"{CYAN}🔁 Exec'ing Python script: {target}{RESET}")
            os.execv(sys.executable, [sys.executable, target])
        elif target.endswith(".sh"):
            bash_path = shutil.which("bash") or "/bin/bash"
            print(f"{CYAN}🔁 Exec'ing shell script with bash: {target}{RESET}")
            os.execv(bash_path, [bash_path, target])
        elif os.access(target, os.X_OK):
            print(f"{CYAN}🔁 Exec'ing executable: {target}{RESET}")
            os.execv(target, [target])
        else:
            print(f"{YELLOW}⚠ Return target is not recognized as .py/.sh or executable: {target}{RESET}")
            return False
    except OSError as e:
        print(f"{RED}❌ Failed to exec return target: {e}{RESET}")
        return False

# ===== Root Checker =====
def ensure_root():
    """Re-run with sudo if not root. Preserve env so PREV_SCRIPT is kept."""
    if os.geteuid() != 0:
        print(f"{YELLOW}⚠ This script requires root privileges. Prompting for sudo...{RESET}")
        try:
            # Use -E to preserve environment variables (so PREV_SCRIPT survives)
            subprocess.check_call(['sudo', '-E', sys.executable] + sys.argv)
            sys.exit(0)
        except subprocess.CalledProcessError:
            print(f"{RED}❌ Failed to gain root privileges. Exiting.{RESET}")
            sys.exit(1)

# ===== Script Runner =====
def run_script(path):
    """Run a script (.py or .sh) interactively."""
    os.system("clear")
    print(f"{CYAN}🚀 Launching → {BOLD}{path}{RESET}\n")
    try:
        if path.endswith(".py"):
            subprocess.run([sys.executable, path])
        elif path.endswith(".sh"):
            subprocess.run(["bash", path])
        else:
            if os.access(path, os.X_OK):
                subprocess.run([path])
            else:
                print(f"{RED}⚠ Unsupported script type or not executable: {path}{RESET}")
    except FileNotFoundError:
        print(f"{RED}❌ Script not found: {path}{RESET}")
    except Exception as e:
        print(f"{RED}❌ Error running script {path}: {e}{RESET}")

# ===== Banner =====
def banner():
    print(f"""{CYAN}{BOLD}
███╗   ██╗███████╗ ██████╗     ██╗  ██╗ █████╗ ████████╗ ██████╗  ██████╗ ██╗     ██╗███╗   ██╗
████╗  ██║██╔════╝██╔═══██╗    ██║ ██╔╝██╔══██╗╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██║████╗  ██║
██╔██╗ ██║█████╗  ██║   ██║    █████╔╝ ███████║   ██║   ██║   ██║██║   ██║██║     ██║██╔██╗ ██║
██║╚██╗██║██╔══╝  ██║   ██║    ██╔═██╗ ██╔══██║   ██║   ██║   ██║██║   ██║██║     ██║██║╚██╗██║
██║ ╚████║███████╗╚██████╔╝    ██║  ██╗██║  ██║   ██║   ╚██████╔╝╚██████╔╝███████╗██║██║ ╚████║
╚═╝  ╚═══╝╚══════╝ ╚═════╝     ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝
{RESET}{MAGENTA}{BOLD}                      ⚡ Fast • Clean • Customizable ⚡{RESET}
""")

# ===== Main Menu =====
def main_menu():
    while True:
        os.system("clear")
        banner()
        print(f"{CYAN}{'='*80}{RESET}")
        print(f"{BOLD}{GREEN}{'NEO-Katoolin Kali Installer Menu':^80}{RESET}")
        print(f"{CYAN}{'='*80}{RESET}\n")

        print(f"{YELLOW}{BOLD}[1]{RESET}  🐉  Full Setup for Gnome ")
        print(f"{YELLOW}{BOLD}[8]{RESET}  🐉  Full Setup for i3 ")
        print(f"{YELLOW}{BOLD}[2]{RESET}  🧰  Kali Top Tools")
        print(f"{YELLOW}{BOLD}[3]{RESET}  🎨  Themes Only")
        print(f"{YELLOW}{BOLD}[4]{RESET}  🔗  Add Kali Repository")
        print(f"{YELLOW}{BOLD}[5]{RESET}  🧩  Daliy Applications ")
        print(f"{YELLOW}{BOLD}[6]{RESET}  🐉  Kali Default tools")
        print(f"{YELLOW}{BOLD}[7]{RESET}  👋  Uninstall tools")
        print(f"{YELLOW}{BOLD}[0]{RESET}  ❌  Exit\n")

        print(f"{CYAN}{'='*80}{RESET}")

        try:
            choice = input(f"{MAGENTA}{BOLD}👉 Choose an option [0-5]: {RESET}").strip()
        except KeyboardInterrupt:
            print(f"\n{GREEN}👋 Exiting Neo-Katoolin. Goodbye!{RESET}")
            # Try to return to previous script (if provided)
            if RETURN_TARGET:
                if RETURN_MODE == "exec":
                    exec_return_target(RETURN_TARGET)
                else:
                    spawn_return_target(RETURN_TARGET)
            sys.exit(0)

        if choice == '1':
            run_script("core/kali/kali_install.sh")
        elif choice == '2':
            run_script("core/both/selective.py")
        elif choice == '3':
            run_script("core/kali/theme.sh")
        elif choice == '4':
            run_script("core/kali/repo.py")
        elif choice == '5':
            run_script("core/both/sele_apps.py")
        elif choice == '6':
            run_script("core/both/default.py")
        elif choice == '7':
            run_script("core/both/uninstaller.py")
        elif choice == '8':
            run_script("core/kali/startup.py")
        elif choice == '0':
            print(f"{GREEN}👋 Exiting Neo-Katoolin. Goodbye!{RESET}")
            if RETURN_TARGET:
                if RETURN_MODE == "exec":
                    exec_return_target(RETURN_TARGET)
                else:
                    spawn_return_target(RETURN_TARGET)
            sys.exit(0)
        else:
            print(f"{RED}❌ Invalid choice. Try again.{RESET}")
            input(f"{YELLOW}Press Enter to continue...{RESET}")

# ===== Entry Point =====
if __name__ == "__main__":
    ensure_root()
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n{GREEN}👋 Exiting Neo-Katoolin. Goodbye!{RESET}")
        if RETURN_TARGET:
            if RETURN_MODE == "exec":
                exec_return_target(RETURN_TARGET)
            else:
                spawn_return_target(RETURN_TARGET)
        sys.exit(0)
