#!/usr/bin/env bash

safe_rm() {
    if [ -e "$1" ]; then
        rm -rf "$1"
    fi
}

safe_rm tsetup.tar.xz
wget -q https://telegram.org/dl/desktop/linux -O /tmp/tsetup.tar.xz

echo "📦 Extracting Telegram..."
sudo mkdir -p /opt/Telegram
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