#!/bin/bash
if [ -d /sys/class/power_supply/BAT0 ]; then
    capacity=$(cat /sys/class/power_supply/BAT0/capacity)
    echo " $capacity%"
else
    echo " N/A"
fi
