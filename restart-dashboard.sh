#!/bin/bash
# Project Genesis Dashboard Restarter (Screen Edition)

echo "Stopping existing Screen sessions..."
screen -S genesis -X quit 2>/dev/null || true
pkill -f soul-viz.py 2>/dev/null || true
pkill -f godmode_bridge.py 2>/dev/null || true
sleep 2

echo "Starting Dashboard in Screen session 'genesis'..."
cd "/home/leo/Schreibtisch/project-genesis"
screen -dmS genesis bash -c "python3 skills/soul-evolution/tools/soul-viz.py /home/leo/Schreibtisch/project-genesis --serve 8080"

echo "Starting God-Mode Bridge..."
nohup python3 skills/soul-evolution/tools/godmode_bridge.py --serve 18795 > godmode.log 2>&1 &

sleep 3
if ss -tulpn | grep -q ":8080"; then
    echo "SUCCESS: Dashboard is running."
    echo "Main UI: http://localhost:8080/soul-evolution.html"
    echo "Use 'screen -r genesis' to see the console."
else
    echo "ERROR: Dashboard failed to start. Check 'screen -r genesis' for errors."
fi
