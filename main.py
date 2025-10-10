#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
import stat

# ===== Color Codes =====
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

# ===== Root Checker =====
def ensure_root():
    if os.geteuid() != 0:
        print(f"{YELLOW}⚠ This script requires root privileges. Prompting for sudo...{RESET}")
        try:
            subprocess.check_call(['sudo', sys.executable] + sys.argv)
            sys.exit(0)
        except subprocess.CalledProcessError:
            print(f"{RED}❌ Failed to gain root privileges. Exiting.{RESET}")
            sys.exit(1)

# ===== chmod +x (recursive) =====
def run_chmod():
    print(f"{YELLOW}⚙ Setting execute permission recursively...{RESET}")
    try:
        for root, dirs, files in os.walk("."):
            for filename in files:
                if filename.endswith((".py", ".sh")) or "." not in filename:
                    filepath = os.path.join(root, filename)
                    try:
                        mode = os.stat(filepath).st_mode
                        os.chmod(filepath, mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                    except Exception:
                        # best-effort; continue
                        pass
        print(f"{GREEN}✅ Executable permissions applied to scripts.{RESET}")
    except Exception as e:
        print(f"{RED}❌ chmod failed: {e}{RESET}")

# ===== Terminal Width =====
def get_terminal_width():
    try:
        width = shutil.get_terminal_size().columns
        return min(width, 100)
    except Exception:
        return 64

# ===== ASCII Art =====
def show_ascii():
    art = f"""{CYAN}{BOLD}
███╗   ██╗███████╗ ██████╗     ██╗  ██╗ █████╗ ████████╗ ██████╗  ██████╗ ██╗     ██╗███╗   ██╗
████╗  ██║██╔════╝██╔═══██╗    ██║ ██╔╝██╔══██╗╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██║████╗  ██║
██╔██╗ ██║█████╗  ██║   ██║    █████╔╝ ███████║   ██║   ██║   ██║██║   ██║██║     ██║██╔██╗ ██║
██║╚██╗██║██╔══╝  ██║   ██║    ██╔═██╗ ██╔══██║   ██║   ██║   ██║██║   ██║██║     ██║██║╚██╗██║
██║ ╚████║███████╗╚██████╔╝    ██║  ██╗██║  ██║   ██║   ╚██████╔╝╚██████╔╝███████╗██║██║ ╚████║
╚═╝  ╚═══╝╚══════╝ ╚═════╝     ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝
{RESET}
"""
    print(art)

# ===== Draw Header =====
def draw_header(title):
    width = get_terminal_width()
    print(CYAN + "=" * width + RESET)
    print(f"{BOLD}{GREEN}{title:^{width}}{RESET}")
    print(CYAN + "=" * width + RESET)

# ===== Fast Redirection (replace current process) =====
def run_script_replace(path):
    """
    Replace current process with the target script for instant redirect.
    - For .py files: execv with the Python interpreter.
    - For .sh files: execvp 'bash'.
    """
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        print(f"{RED}❌ Target not found: {path}{RESET}")
        input(f"{YELLOW}Press Enter to continue...{RESET}")
        return

    # best-effort: make it executable
    try:
        mode = os.stat(path).st_mode
        os.chmod(path, mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    except Exception:
        pass

    if path.endswith(".py"):
        os.execv(sys.executable, [sys.executable, path])
    elif path.endswith(".sh"):
        os.execvp("bash", ["bash", path])
    else:
        os.execvp(path, [path])

# ===== Spawn & Wait (returns to menu when child exits) =====
def run_script_spawn(path, args=None, env=None):
    """
    Spawn the target script as a child, wait for it to finish, then return to menu.
    - path: script path (.py/.sh or executable)
    - args: optional list of extra args to pass to the target
    - env: optional environment dict to pass (defaults to os.environ)
    """
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        print(f"{RED}❌ Target not found: {path}{RESET}")
        input(f"{YELLOW}Press Enter to continue...{RESET}")
        return False

    # Ensure executable bit (best-effort)
    try:
        mode = os.stat(path).st_mode
        os.chmod(path, mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    except Exception:
        pass

    # Choose command based on extension
    cmd = None
    if path.endswith(".py"):
        cmd = [sys.executable, path] + (args or [])
    elif path.endswith(".sh"):
        bash = shutil.which("bash") or "/bin/bash"
        cmd = [bash, path] + (args or [])
    elif os.access(path, os.X_OK):
        cmd = [path] + (args or [])
    else:
        # fallback: try to run with sh
        cmd = ["/bin/sh", path] + (args or [])

    print(f"{CYAN}▶ Launching: {' '.join(cmd)}{RESET}")
    try:
        completed = subprocess.run(cmd, env=env or os.environ)
        # Removed the child exit print and the "Press Enter" pause as requested.
        return True
    except FileNotFoundError:
        print(f"{RED}❌ Interpreter not found for: {path}{RESET}")
        input(f"{YELLOW}Press Enter to continue...{RESET}")
        return False
    except Exception as e:
        print(f"{RED}❌ Error launching target: {e}{RESET}")
        input(f"{YELLOW}Press Enter to continue...{RESET}")
        return False

# ===== Decide launch mode (exec vs spawn) via CLI flag --exec-launch =====
USE_EXEC_LAUNCH = "--exec-launch" in sys.argv

# ===== Main Menu =====
def main_menu():
    while True:
        os.system("clear")
        show_ascii()
        draw_header("Choose Your System")

        print(f"{BOLD}{YELLOW}[1]{RESET} Kali Linux Mode  🐉")
        print(f"{BOLD}{YELLOW}[2]{RESET} Ubuntu Mode      🧩")
        print(f"{BOLD}{YELLOW}[0]{RESET} Exit             ❌")
        print(CYAN + "=" * get_terminal_width() + RESET)

        try:
            mode = input(f"{CYAN}👉 Choose a mode: {RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{GREEN}Exiting... 👋{RESET}")
            sys.exit(0)

        if mode == "1":
            target = "core/kali/main.py"
        elif mode == "2":
            target = "core/ubuntu/main.py"
        elif mode == "0":
            print(f"{GREEN}👋 Goodbye!{RESET}")
            sys.exit(0)
        else:
            print(f"{RED}❌ Invalid input. Try again.{RESET}")
            input(f"{YELLOW}Press Enter to continue...{RESET}")
            continue

        # Launch using selected mode.
        if USE_EXEC_LAUNCH:
            # Replace current process (old behaviour). Note: menu will not return.
            run_script_replace(target)
            # If exec returns, something went wrong; continue loop
            print(f"{RED}⚠ Exec launch failed; returning to menu.{RESET}")
            input(f"{YELLOW}Press Enter to continue...{RESET}")
        else:
            # Spawn and wait (default) -> returns to menu after child exits
            run_script_spawn(target)

# ===== Launch =====
if __name__ == "__main__":
    ensure_root()
    run_chmod()
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n{GREEN}Exiting... 👋{RESET}")
        sys.exit(0)
