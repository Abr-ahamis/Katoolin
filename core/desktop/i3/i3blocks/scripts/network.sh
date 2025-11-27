#!/usr/bin/env bash
# ~/.config/i3blocks/scripts/network.sh
# Shows network speed only (upload and download), adaptive units, nicely spaced

SAMPLE_SECS=0.9

# Convert bytes/sec to KB/s or MB/s
human_rate() {
    local bps=$1
    if (( $(echo "$bps >= 1048576" | bc -l) )); then
        printf "%.1f MB/s" "$(echo "$bps / 1048576" | bc -l)"
    else
        printf "%.0f KB/s" "$(echo "$bps / 1024" | bc -l)"
    fi
}

# Pick interface: VPN > wlan0 > first UP non-loopback
INTERFACE=""
if ip -4 addr show tun0 2>/dev/null | grep -q "inet "; then
    INTERFACE="tun0"
elif ip -4 addr show wlan0 2>/dev/null | grep -q "inet "; then
    INTERFACE="wlan0"
else
    for iface in $(ls /sys/class/net); do
        [ "$iface" = "lo" ] && continue
        [ -f "/sys/class/net/$iface/operstate" ] || continue
        grep -q "up" "/sys/class/net/$iface/operstate" && { INTERFACE="$iface"; break; }
    done
fi

[ -z "$INTERFACE" ] && { echo "No connected interface"; exit 0; }

# Network stats
RX_FILE="/sys/class/net/${INTERFACE}/statistics/rx_bytes"
TX_FILE="/sys/class/net/${INTERFACE}/statistics/tx_bytes"
[ ! -r "$RX_FILE" ] || [ ! -r "$TX_FILE" ] && { echo "↑ N/A   ↓ N/A"; exit 0; }

# Read counters
RX1=$(cat "$RX_FILE")
TX1=$(cat "$TX_FILE")
sleep "$SAMPLE_SECS"
RX2=$(cat "$RX_FILE")
TX2=$(cat "$TX_FILE")

RX_DELTA=$((RX2 - RX1))
TX_DELTA=$((TX2 - TX1))

# Bytes per second
RX_BPS=$(awk -v d="$RX_DELTA" -v s="$SAMPLE_SECS" 'BEGIN {printf "%.0f", d / s}')
TX_BPS=$(awk -v d="$TX_DELTA" -v s="$SAMPLE_SECS" 'BEGIN {printf "%.0f", d / s}')

# Convert to human-readable
RX_HUMAN=$(human_rate $RX_BPS)
TX_HUMAN=$(human_rate $TX_BPS)

# Print with proper spacing (one space after icon, two spaces between up/down)
printf "↑ %s   ↓ %s\n" "$TX_HUMAN" "$RX_HUMAN"
