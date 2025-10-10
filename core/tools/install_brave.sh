#!/usr/bin/env bash

echo "🦁 Installing Brave Nightly..."
{
    curl -fsS https://dl.brave.com/install.sh | CHANNEL=nightly bash
} || echo "⚠️ Brave setup script failed."

# Pin Brave if available
for entry in brave-browser.desktop brave-browser-nightly.desktop brave.desktop; do
    if [ -f "/usr/share/applications/$entry" ]; then
        desktop="$entry"
        break
    fi
done

if [ -n "${desktop:-}" ]; then
    # Use gsettings instead of gset
    if command -v gsettings >/dev/null 2>&1; then
        favs=$(gsettings get org.gnome.shell favorite-apps 2>/dev/null) || favs="[]"

        if [[ $favs != *"$desktop"* ]]; then
            new=$(echo "$favs" | sed "s/]$/, '$desktop']/") || new="$favs"
            echo "📌 Adding $desktop to GNOME favorites..."
            gsettings set org.gnome.shell favorite-apps "$new" || true
        else
            echo "✅ $desktop is already pinned to favorites."
        fi
    else
        echo "⚠️ gsettings not found. Skipping GNOME favorites pinning."
    fi
else
    echo "❌ Brave desktop entry not found. Skipping pinning."
fi
