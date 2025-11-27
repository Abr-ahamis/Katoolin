#!/bin/bash
# RAM and Swap usage
mem_total=$(grep MemTotal /proc/meminfo | awk '{print $2}')
mem_free=$(grep MemAvailable /proc/meminfo | awk '{print $2}')
mem_used=$((mem_total - mem_free))
swap_total=$(grep SwapTotal /proc/meminfo | awk '{print $2}')
swap_free=$(grep SwapFree /proc/meminfo | awk '{print $2}')
swap_used=$((swap_total - swap_free))

echo " $((swap_used*100/swap_total))% swap |  $((mem_used*100/mem_total))% memory"
