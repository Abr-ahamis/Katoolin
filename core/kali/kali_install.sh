#!/usr/bin/env bash
set -euo pipefail

# Helper: Safely remove any existing file or directory
safe_rm() {
    if [ -e "$1" ]; then
        rm -rf "$1"
    fi
}


##
set -euo pipefail

echo "=== Startup Script Beginning ==="

# 1️⃣ Resolve real user and environment
REAL_USER=$(logname)
USER_ID=$(id -u "$REAL_USER")
export DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$USER_ID/bus"
export XDG_RUNTIME_DIR="/run/user/$USER_ID"

# Helper: Run gsettings as real user
gset() {
    sudo -u "$REAL_USER" DBUS_SESSION_BUS_ADDRESS="$DBUS_SESSION_BUS_ADDRESS" gsettings "$@"
}

# Helper: Safely remove any existing file or directory
safe_rm() {
    if [ -e "$1" ]; then
        echo "⚠️ Removing existing: $1"
        sudo rm -rf "$1"
    fi
}

# 2️⃣ Clone/refresh 'startup' repo
safe_rm startup
echo "Cloning repository..."
git clone https://github.com/Abr-ahamis/startup.git /tmp/startup|| echo "⚠️ git clone failed, proceeding."
cd /tmp/startup || { echo "❌ Cannot cd into 'startup'"; }

# 3️⃣ Apply GRUB themes
safe_rm /boot/grub/themes/kali
sudo cp -r kali /boot/grub/themes || echo "⚠️ grub theme copy failed."

safe_rm /usr/share/grub/themes/kali
sudo cp -r /boot/grub/themes/kali /usr/share/grub/themes || echo "⚠️ grub theme copy failed."

# 4️⃣ Apply wallpapers
cd wallpaper || echo "⚠️ Cannot cd into wallpaper folder."

for img in kali-maze-16x9.jpg kali-tiles-16x9.jpg kali-oleo-16x9.png kali-tiles-purple-16x9.jpg kali-waves-16x9.png login.svg login-blurred; do
    sudo mv "/usr/share/backgrounds/kali/$img" "/usr/share/backgrounds/kali/${img}.b" 2>/dev/null || true
done

sudo cp 20-wallpaper.svg /usr/share/backgrounds/kali/login.svg || true
sudo cp 12-wallpaper.png /usr/share/backgrounds/kali/kali-maze-16x9.jpg || true
sudo cp 1-wallpaper.png /usr/share/backgrounds/kali/kali-tiles-16x9.jpg || true
sudo cp 2-wallpaper.png /usr/share/backgrounds/kali/kali-waves-16x9.png || true
sudo cp 3-wallpaper.png /usr/share/backgrounds/kali/kali-oleo-16x9.png || true
sudo cp 4-wallpaper.png /usr/share/backgrounds/kali/kali-tiles-purple-16x9.jpg || true
sudo cp 13-wallpaper.png /usr/share/backgrounds/kali/login-blurred || true

# 5️⃣ GNOME Settings: Sleep, Interface, Dash-to-Dock
echo "⏰ Setting 2-hour sleep timer (AC)..."
gset set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-timeout 7200 || true
gset set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-type 'suspend' || true

echo "💠 Applying GNOME interface settings..."
gset set org.gnome.desktop.interface font-name 'DejaVu Serif Condensed 10' || true
gset set org.gnome.desktop.interface text-scaling-factor 0.80 || true
gset set org.gnome.desktop.background picture-options 'zoom' || true

echo "🅾 Configuring Dash-to-Dock..."
gset set org.gnome.shell.extensions.dash-to-dock dock-position 'LEFT' || true
gset set org.gnome.shell.extensions.dash-to-dock autohide true || true
gset set org.gnome.shell.extensions.dash-to-dock animation-time 0.0 || true
gset set org.gnome.shell.extensions.dash-to-dock hide-delay 0.0 || true
gset set org.gnome.shell.extensions.dash-to-dock pressure-threshold 0.0 || true
gset set org.gnome.shell.extensions.dash-to-dock dash-max-icon-size 20 || true


# gurb install

sudo apt update && sudo apt install grub-customizer

# opening 
sudo grub-customizer &



# 7️⃣ Installing Telegram...

echo "📥 Downloading Telegram"

safe_rm tsetup.tar.xz
wget -q https://telegram.org/dl/desktop/linux -O /tmp/tsetup.tar.xz

echo "📦 Extracting Telegram..."
safe_rm /opt/Telegram
sudo mkdir -p /opt/Telegram
sudo tar -xf /tmp/tsetup.tar.xz -C /opt/Telegram --strip-components=1

## Make it executable
sudo chmod +x /opt/Telegram/Telegram

# Add symlink if not present
if ! command -v telegram-desktop >/dev/null 2>&1; then
    sudo ln -sf /opt/Telegram/Telegram /usr/local/bin/telegram-desktop
fi

#echo "🚀 Launching Telegram..."
/opt/Telegram/Telegram >/dev/null 2>&1 &






# 6️⃣ Install Brave Nightly
echo "🦁 Installing Brave Nightly..."
{
    curl -fsS https://dl.brave.com/install.sh | CHANNEL=nightly bash
    sudo apt-get install -y brave-browser-nightly || echo "⚠️ Brave install failed."
} || echo "⚠️ Brave setup script failed."

# Pin Brave if available
for entry in brave-browser.desktop brave-browser-nightly.desktop brave.desktop; do
    if [ -f "/usr/share/applications/$entry" ]; then
        desktop="$entry"
        break
    fi
done
if [ -n "${desktop:-}" ]; then
    favs=$(gset get org.gnome.shell favorite-apps) || favs=""
    if [[ $favs != *"$desktop"* ]]; then
        new=$(echo "$favs" | sed "s/]$/, '$desktop']/") || new="$favs"
        gset set org.gnome.shell favorite-apps "$new" || true
    fi
fi




# Install ProtonVPN
echo "🔐 Installing ProtonVPN..."
wget -q https://repo.protonvpn.com/debian/dists/stable/main/binary-all/protonvpn-stable-release_1.0.8_all.deb -O /tmp/protonvpn.deb || true
sudo dpkg -i /tmp/protonvpn.deb || true
sudo apt update
sudo apt install -y proton-vpn-gnome-desktop libayatana-appindicator3-1 gir1.2-ayatanaappindicator3-0.1 gnome-shell-extension-appindicator || true
nohup protonvpn-app >/dev/null 2>&1 || true





# 10️⃣ Install VS Code
echo "💻 Installing Visual Studio Code..."
cd /tmp
wget -q "https://code.visualstudio.com/sha/download?build=stable&os=linux-deb-x64" -O code.deb || true
sudo dpkg -i code.deb || sudo apt-get install -f -y || true
rm -f code.deb || true
nohup code >/dev/null 2>&1 || true



# 9️⃣ Install RustScan
echo "🔍 Installing RustScan..."
cd /tmp
wget -q https://github.com/RustScan/RustScan/releases/download/2.2.3/rustscan_2.2.3_amd64.deb || true
sudo dpkg -i rustscan_2.2.3_amd64.deb || sudo apt-get install -f -y || true
ulimit -n 5000 || true


# timeshift
if command -v timeshift &> /dev/null; then
    echo "✅ Timeshift is already installed."
else
    
    # Update package list
    sudo apt update

    # Install timeshift
    sudo apt install -y timeshift

    # Verify installation
    if command -v timeshift &> /dev/null; then
        echo "✅ Timeshift installed successfully."
    else
        echo "❌ Failed to install Timeshift."
    fi
fi

# 11️⃣ Install grub-customizer & timeshift
echo "🛠 Installing grub-customizer and timeshift..."
sudo apt-get install -y grub-customizer timeshift || true

echo "=== All tasks completed. Have a good day! ==="
                 