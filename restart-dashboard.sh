#!/bin/bash
# Project Genesis Dashboard Restarter (Systemd & God-Mode Edition)

echo "Restarting project-genesis-dashboard service..."
sudo systemctl restart project-genesis-dashboard

echo "Restarting God-Mode Bridge..."
pkill -f godmode_bridge.py || true
sleep 1
cd "/home/leo/Schreibtisch/project-genesis"
nohup python3 skills/soul-evolution/tools/godmode_bridge.py --serve 18795 > godmode.log 2>&1 &

echo "Waiting for services to stabilize..."
sleep 3

if systemctl is-active --quiet project-genesis-dashboard; then
    echo "SUCCESS: Dashboard service is running."
    echo "Main Dashboard: http://localhost:8080/soul-evolution.html"
    echo "God-Mode Control: http://localhost:8080/godmode.html"
else
    echo "ERROR: Service failed to start. Check journalctl -u project-genesis-dashboard"
fi
