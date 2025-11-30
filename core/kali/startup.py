#!/usr/bin/env python3
"""
startup_setup.py — Interactive version (Option A multi-select menu + GRUB prompt)

Usage:
    sudo python3 startup_setup.py

Features:
- Detect or clone 'startup' repo.
- Copy i3/rofi/picom/i3blocks configs into user's home (backups made).
- Ask whether to install GRUB theme.
- Multi-select menu (Option A) to choose which apps to install:
    1) Telegram
    2) Brave (nightly)
    3) Visual Studio Code
    4) ProtonVPN
    5) VirtualBox
    6) RustScan
    7) All
    8) None
- Installs selected apps (best-effort).
- Applies grub theme only if confirmed.
- Safe operations, logs printed.
"""
from __future__ import annotations
import os
import sys
import shutil
import subprocess
import datetime
from pathlib import Path
from typing import List

# -------------------------
# Config
# -------------------------
REPO_URL = "https://github.com/Abr-ahamis/startup.git"
REPO_DIR_NAME = "startup"

APT_PACKAGES = [
    "i3-wm", "i3blocks", "rofi", "polkitd", "xdotool", "dex", "acpi", "upower",
    "xfce4-power-manager", "i3lock", "xss-lock", "pulseaudio-utils",
    "brightnessctl", "feh", "picom", "fonts-font-awesome", "git", "rsync",
    "unzip", "curl", "wget", "grub-customizer", "timeshift"
]

# -------------------------
# Determine user & home
# -------------------------
# USER (non-root) who should receive config files
if os.environ.get("SUDO_USER"):
    USER = os.environ["SUDO_USER"]
    # typical home path; if /home/USER doesn't exist fall back to expanduser
    home_candidate = Path("/home") / USER
    USER_HOME = home_candidate if home_candidate.exists() else Path(os.path.expanduser(f"~{USER}"))
else:
    USER = os.environ.get("USER", "root")
    USER_HOME = Path(os.path.expanduser("~"))

STARTUP_BACKUP_ROOT = USER_HOME / ".config" / "startup-backups"

# -------------------------
# Utilities
# -------------------------
def die(msg: str, code: int = 1):
    print(f"[ERROR] {msg}", file=sys.stderr)
    sys.exit(code)

def run(cmd, check=False, capture_output=False, env=None):
    """Run command. cmd may be list or string. Return CompletedProcess."""
    if isinstance(cmd, (list, tuple)):
        print(f"[CMD] {' '.join(cmd)}")
    else:
        print(f"[CMD] {cmd}")
    try:
        if isinstance(cmd, (list, tuple)):
            return subprocess.run(cmd, check=check, capture_output=capture_output, text=True, env=env)
        else:
            return subprocess.run(cmd, shell=True, check=check, capture_output=capture_output, text=True, env=env)
    except subprocess.CalledProcessError as e:
        print(f"[CMD-FAIL] returncode={e.returncode} cmd={e.cmd}")
        if capture_output:
            print("stdout:", e.stdout)
            print("stderr:", e.stderr)
        if check:
            raise
        return e

def ensure_dir(p: Path, mode: int = 0o755):
    if not p.exists():
        print(f"[MKDIR] {p}")
        p.mkdir(parents=True, mode=mode, exist_ok=True)

def backup_path(target: Path) -> Path:
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = STARTUP_BACKUP_ROOT / ts
    ensure_dir(backup_dir)
    return backup_dir / target.name

def safe_copy(src: Path, dst: Path, make_backup=True, dirs_exist_ok=False) -> bool:
    src = Path(src)
    dst = Path(dst)
    if not src.exists():
        print(f"[SKIP] Source not found: {src}")
        return False
    ensure_dir(dst.parent)
    if dst.exists():
        if make_backup:
            b = backup_path(dst)
            print(f"[BACKUP] Moving existing {dst} -> {b}")
            shutil.move(str(dst), str(b))
        else:
            if dst.is_dir():
                if not dirs_exist_ok:
                    shutil.rmtree(dst)
            else:
                dst.unlink()
    # Copy file or dir
    if src.is_dir():
        print(f"[COPY-DIR] {src} -> {dst}")
        shutil.copytree(src, dst, dirs_exist_ok=dirs_exist_ok)
    else:
        print(f"[COPY-FILE] {src} -> {dst}")
        shutil.copy2(src, dst)
    return True

def safe_rm(path: Path):
    if path.exists():
        print(f"[RM] {path}")
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        else:
            path.unlink()

# -------------------------
# Root check
# -------------------------
def require_root():
    if os.geteuid() != 0:
        die("This script must be run as root. Use sudo python3 startup_setup.py")

# -------------------------
# Repo detection / cloning
# -------------------------
def detect_or_clone_repo() -> Path:
    cwd = Path.cwd()
    print(f"[INFO] cwd: {cwd}")
    # If we are already in repo root
    if (cwd / "i3").is_dir() and (cwd / "grub").is_dir() and (cwd / "wallpaper").is_dir():
        print("[INFO] Found startup files in current directory; using current dir as startup repo.")
        return cwd
    # If ./startup exists
    if (cwd / REPO_DIR_NAME).is_dir():
        print(f"[INFO] Found ./{REPO_DIR_NAME}; using it.")
        return cwd / REPO_DIR_NAME
    # Otherwise clone
    target = cwd / REPO_DIR_NAME
    if target.exists():
        print(f"[INFO] {target} exists; using it.")
        return target
    print(f"[INFO] Cloning {REPO_URL} -> {target}")
    r = run(["git", "clone", REPO_URL, str(target)], check=False)
    if r.returncode != 0:
        print("[WARN] git clone returned non-zero; continuing if repository already exists locally.")
    return target

# -------------------------
# Copy and configure core files
# -------------------------
def copy_core_configs(startup_dir: Path):
    print("[COPY] Copying configs from repo...")
    repo_i3 = startup_dir / "i3"
    # i3 config
    safe_copy(repo_i3 / ".config" / "i3" / "config", USER_HOME / ".config" / "i3" / "config", make_backup=True)
    # i3blocks
    safe_copy(repo_i3 / ".config" / "i3blocks", USER_HOME / ".config" / "i3blocks", make_backup=True, dirs_exist_ok=True)
    # rofi
    safe_copy(repo_i3 / ".config" / "rofi", USER_HOME / ".config" / "rofi", make_backup=True, dirs_exist_ok=True)
    # picom
    safe_copy(repo_i3 / ".config" / "picom" / "picom.conf", USER_HOME / ".config" / "picom" / "picom.conf", make_backup=True)
    # local bin
    src_local_bin = repo_i3 / ".local" / "bin"
    dst_local_bin = USER_HOME / ".local" / "bin"
    ensure_dir(dst_local_bin)
    if src_local_bin.exists():
        for f in sorted(src_local_bin.iterdir()):
            safe_copy(f, dst_local_bin / f.name, make_backup=True)
    # fonts
    src_fonts = repo_i3 / ".local" / "share" / "fonts"
    dst_fonts = USER_HOME / ".local" / "share" / "fonts"
    ensure_dir(dst_fonts)
    if src_fonts.exists():
        for f in sorted(src_fonts.iterdir()):
            safe_copy(f, dst_fonts / f.name, make_backup=True)
    # system rofi themes
    src_rofi_sys = repo_i3 / "usr" / "share" / "rofi" / "themes"
    dst_rofi_sys = Path("/usr/share/rofi/themes")
    ensure_dir(dst_rofi_sys)
    if src_rofi_sys.exists():
        for f in sorted(src_rofi_sys.iterdir()):
            safe_copy(f, dst_rofi_sys / f.name, make_backup=True)
    # wallpapers
    repo_wall = startup_dir / "wallpaper"
    ensure_dir(USER_HOME / "Pictures")
    for name in ("wallpaper.jpg", "wallpaper-1.jpg", "wallpaper-2.jpg"):
        s = repo_wall / name
        if s.exists():
            safe_copy(s, USER_HOME / "Pictures" / name, make_backup=True)
            backgrounds_dir = Path("/usr/share/backgrounds/kali")
            ensure_dir(backgrounds_dir)
            try:
                shutil.copy2(s, backgrounds_dir / name)
            except Exception as e:
                print(f"[WARN] copying wallpaper to system backgrounds failed: {e}")

def set_executables_and_restart_i3():
    # make scripts executable
    scripts_dir = USER_HOME / ".config" / "i3blocks" / "scripts"
    if scripts_dir.exists():
        for sh in scripts_dir.glob("*.sh"):
            print(f"[CHMOD] +x {sh}")
            sh.chmod(0o755)
    # rofi scripts
    rofi_dir = USER_HOME / ".config" / "rofi"
    if rofi_dir.exists():
        for f in rofi_dir.rglob("*.sh"):
            print(f"[CHMOD] +x {f}")
            f.chmod(0o755)
    # local bin
    local_bin = USER_HOME / ".local" / "bin"
    if local_bin.exists():
        for f in local_bin.iterdir():
            if f.is_file():
                f.chmod(0o755)
    # restart i3 (best-effort)
    print("[I3] Attempting i3-msg restart...")
    run(["i3-msg", "restart"], check=False)

# -------------------------
# GRUB theme
# -------------------------
def apply_grub_theme(startup_dir: Path):
    print("[GRUB] Applying grub theme (best-effort).")
    repo_grub = startup_dir / "grub"
    dst_boot_grub = Path("/boot/grub/themes/kali")
    # remove existing
    if dst_boot_grub.exists():
        shutil.rmtree(dst_boot_grub, ignore_errors=True)
    try:
        shutil.copytree(repo_grub, dst_boot_grub)
        print(f"[GRUB] Copied {repo_grub} -> {dst_boot_grub}")
    except Exception as e:
        print(f"[WARN] Could not copy grub theme: {e}")
    # Also copy to /usr/share/grub/themes
    dst_usr = Path("/usr/share/grub/themes")
    ensure_dir(dst_usr)
    try:
        if (dst_usr / "kali").exists():
            shutil.rmtree(dst_usr / "kali", ignore_errors=True)
        shutil.copytree(dst_boot_grub, dst_usr / "kali", dirs_exist_ok=True)
    except Exception as e:
        print(f"[WARN] Could not copy to {dst_usr}: {e}")
    # copy extra wallpapers (best-effort)
    repo_wall = startup_dir / "wallpaper"
    backgrounds_dir = Path("/usr/share/backgrounds/kali")
    ensure_dir(backgrounds_dir)
    mappings = [
        ("wallpaper-1.jpg", "login.svg"),
        ("wallpaper.jpg", "kali-maze-16x9.jpg"),
        ("wallpaper-2.jpg", "kali-tiles-16x9.jpg"),
        ("wallpaper-1.jpg", "kali-waves-16x9.png"),
        ("wallpaper.jpg", "kali-oleo-16x9.png"),
        ("wallpaper-2.jpg", "kali-tiles-purple-16x9.jpg"),
    ]
    for src_name, dst_name in mappings:
        s = repo_wall / src_name
        if s.exists():
            try:
                shutil.copy2(s, backgrounds_dir / dst_name)
            except Exception as e:
                print(f"[WARN] Could not copy {s} -> {backgrounds_dir}/{dst_name}: {e}")

# -------------------------
# App install functions
# -------------------------
def install_telegram(startup_dir: Path):
    print("[TELEGRAM] Installing Telegram (tarball) — best-effort.")
    tfile = Path("/tmp/tsetup.tar.xz")
    run(["wget", "-q", "https://telegram.org/dl/desktop/linux", "-O", str(tfile)], check=False)
    opt = Path("/opt/Telegram")
    if opt.exists():
        shutil.rmtree(opt, ignore_errors=True)
    ensure_dir(opt)
    r = run(["tar", "-xf", str(tfile), "-C", str(opt), "--strip-components=1"], check=False)
    tbin = opt / "Telegram"
    if tbin.exists():
        tbin.chmod(0o755)
        run(["ln", "-sf", str(tbin), "/usr/local/bin/telegram-desktop"], check=False)
        print("[TELEGRAM] Installed to /opt/Telegram, symlinked to /usr/local/bin/telegram-desktop")
    else:
        print("[WARN] Telegram binary not found after extraction.")

def install_brave_nightly():
    print("[BRAVE] Installing Brave (nightly) — best-effort.")
    # Using upstream install script with CHANNEL=nightly
    run('curl -fsS https://dl.brave.com/install.sh | CHANNEL=nightly bash', check=False)
    run(["apt", "install", "-y", "brave-browser-nightly"], check=False)

def install_vscode():
    print("[VSCODE] Installing Visual Studio Code (.deb) — best-effort.")
    deb = Path("/tmp/code.deb")
    run(["wget", "-q", "https://code.visualstudio.com/sha/download?build=stable&os=linux-deb-x64", "-O", str(deb)], check=False)
    if deb.exists():
        r = run(["dpkg", "-i", str(deb)], check=False)
        if r.returncode != 0:
            run(["apt", "install", "-f", "-y"], check=False)
        try:
            deb.unlink()
        except Exception:
            pass

def install_protonvpn():
    print("[PROTONVPN] Installing ProtonVPN repo package (best-effort).")
    deb = Path("/tmp/protonvpn.deb")
    url = "https://repo.protonvpn.com/debian/dists/stable/main/binary-all/protonvpn-stable-release_1.0.8_all.deb"
    run(["wget", "-q", url, "-O", str(deb)], check=False)
    if deb.exists():
        run(["dpkg", "-i", str(deb)], check=False)
        run(["apt", "update"], check=False)
        run(["apt", "install", "-f", "-y"], check=False)
        run(["apt", "install", "-y", "proton-vpn-gnome-desktop"], check=False)

def install_virtualbox():
    print("[VBOX] Installing VirtualBox (from apt) — best-effort.")
    run(["apt", "update"], check=False)
    run(["apt", "install", "-y", "virtualbox"], check=False)

def install_rustscan():
    print("[RUSTSCAN] Installing RustScan (.deb) — best-effort.")
    deb = Path("/tmp/rustscan_2.2.3_amd64.deb")
    url = "https://github.com/RustScan/RustScan/releases/download/2.2.3/rustscan_2.2.3_amd64.deb"
    run(["wget", "-q", url, "-O", str(deb)], check=False)
    if deb.exists():
        r = run(["dpkg", "-i", str(deb)], check=False)
        if r.returncode != 0:
            run(["apt", "install", "-f", "-y"], check=False)
    # attempt to raise ulimit for this process (non-persistent)
    try:
        import resource
        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        new_soft = max(soft, 5000)
        resource.setrlimit(resource.RLIMIT_NOFILE, (new_soft, hard))
        print(f"[ULIMIT] set RLIMIT_NOFILE soft={new_soft} hard={hard}")
    except Exception as e:
        print(f"[WARN] Could not adjust ulimit: {e}")

# -------------------------
# Helpers for interactive menu
# -------------------------
def prompt_yes_no(prompt: str, default: str = "y") -> bool:
    default = default.lower()
    yn = "[Y/n]" if default == "y" else "[y/N]"
    while True:
        choice = input(f"{prompt} {yn}: ").strip().lower()
        if choice == "" and default:
            return default == "y"
        if choice in ("y", "yes"):
            return True
        if choice in ("n", "no"):
            return False
        print("Please answer 'y' or 'n'.")

def prompt_multi_select() -> List[int]:
    lines = [
        "Select applications to install (enter numbers separated by spaces or commas):",
        " 1) Telegram",
        " 2) Brave (nightly)",
        " 3) Visual Studio Code",
        " 4) ProtonVPN",
        " 5) VirtualBox",
        " 6) RustScan",
        " 7) All",
        " 8) None",
    ]
    print("\n".join(lines))
    raw = input("Enter selection (e.g. '1 3 5' or '7' for All): ").strip()
    if not raw:
        print("[INPUT] No selection entered; assuming 'None'.")
        return []
    # Normalize: accept commas and spaces
    tokens = []
    for part in raw.replace(",", " ").split():
        if part.isdigit():
            tokens.append(int(part))
        else:
            # allow words like 'all', 'none'
            partl = part.lower()
            if partl in ("all", "7"):
                return list(range(1, 7))
            if partl in ("none", "0", "8"):
                return []
    # If user selected 7 (All), return all
    if 7 in tokens:
        return list(range(1, 7))
    if 8 in tokens:
        return []
    # Filter and unique
    sel = sorted(set([t for t in tokens if 1 <= t <= 6]))
    return sel

# -------------------------
# Main flow
# -------------------------
def main():
    require_root()
    startup_dir = detect_or_clone_repo()
    print(f"[USING] startup dir: {startup_dir}")

    # Ensure backup root
    ensure_dir(STARTUP_BACKUP_ROOT)

    # 1) Update & install base apt packages (non-destructive)
    print("[APT] Updating package lists and upgrading (this may take time).")
    run(["apt", "update"], check=False)
    run(["apt", "upgrade", "-y"], check=False)
    if APT_PACKAGES:
        print("[APT] Installing base packages...")
        run(["apt", "install", "-y"] + APT_PACKAGES, check=False)

    # 2) Ensure user config directories exist
    ensure_dir(USER_HOME / ".config" / "i3")
    ensure_dir(USER_HOME / ".config" / "i3blocks" / "scripts")
    ensure_dir(USER_HOME / ".config" / "rofi")
    ensure_dir(USER_HOME / ".config" / "picom")
    ensure_dir(USER_HOME / ".local" / "bin")
    ensure_dir(USER_HOME / ".local" / "share" / "fonts")
    ensure_dir(USER_HOME / "Pictures")
    ensure_dir(Path("/usr/share/rofi/themes"))

    # 3) Copy core configs from repo to user
    copy_core_configs(startup_dir)

    # 4) GRUB prompt
    install_grub = prompt_yes_no("Do you want to apply/install the GRUB theme from the repo?", default="n")
    if install_grub:
        apply_grub_theme(startup_dir)
    else:
        print("[GRUB] Skipping GRUB theme installation as requested.")

    # 5) Multi-select menu for applications (Option A)
    selections = prompt_multi_select()
    if not selections:
        print("[APPS] No applications selected for installation.")
    else:
        print(f"[APPS] Selected: {selections}")

    # Map selections to functions
    # 1 Telegram, 2 Brave, 3 VSCode, 4 ProtonVPN, 5 VirtualBox, 6 RustScan
    if 1 in selections:
        install_telegram(startup_dir)
    if 2 in selections:
        install_brave_nightly()
    if 3 in selections:
        install_vscode()
    if 4 in selections:
        install_protonvpn()
    if 5 in selections:
        install_virtualbox()
    if 6 in selections:
        install_rustscan()

    # 6) Make scripts executable and restart i3 (best-effort)
    set_executables_and_restart_i3()

    # 7) Font cache
    print("[FONTS] Updating font cache.")
    run(["fc-cache", "-fv"], check=False)

    print("🎉 Setup finished. Review the log above for any warnings or errors.")

if __name__ == "__main__":
    main()
