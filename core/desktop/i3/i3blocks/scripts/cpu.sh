#!/bin/bash
# CPU usage percentage

# Read first line from /proc/stat
read cpu user nice system idle iowait irq softirq steal guest guest_nice < /proc/stat
prev_idle=$((idle + iowait))
prev_total=$((user + nice + system + idle + iowait + irq + softirq + steal))

# Wait 0.9 seconds
sleep 0.9

# Read again
read cpu user nice system idle iowait irq softirq steal guest guest_nice < /proc/stat
idle_now=$((idle + iowait))
total_now=$((user + nice + system + idle + iowait + irq + softirq + steal))

# Calculate CPU usage in percent with awk for floating point
cpu_usage=$(awk -v prev_idle="$prev_idle" -v idle_now="$idle_now" -v prev_total="$prev_total" -v total_now="$total_now" \
'BEGIN {usage = 100 * ((total_now - prev_total) - (idle_now - prev_idle)) / (total_now - prev_total); printf "%.0f", usage}')

echo " CPU $cpu_usage"%
