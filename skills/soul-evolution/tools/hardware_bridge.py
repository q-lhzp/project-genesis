#!/usr/bin/env python3
"""
Hardware Bridge - System Monitoring for Q's Neural Feedback
Monitors CPU, RAM, Temperature, and Audio status.
"""

import os
import sys
import json
import time
import subprocess
from typing import Dict, Optional


def get_cpu_usage() -> float:
    """Get current CPU usage percentage."""
    try:
        # Use top command for quick CPU check
        result = subprocess.run(
            ["top", "-bn1"],
            capture_output=True,
            text=True,
            timeout=5
        )
        # Parse the CPU line from top
        for line in result.stdout.split('\n'):
            if '%Cpu(s)' in line or 'CPU' in line:
                # Try to extract idle percentage
                parts = line.split()
                for i, part in enumerate(parts):
                    if 'id' in part and i > 0:
                        try:
                            idle = float(parts[i-1].replace(',', '.'))
                            return round(100 - idle, 1)
                        except:
                            pass
        return 0.0
    except:
        return 0.0


def get_memory_usage() -> Dict:
    """Get memory usage statistics."""
    try:
        result = subprocess.run(
            ["free", "-m"],
            capture_output=True,
            text=True,
            timeout=5
        )
        lines = result.stdout.strip().split('\n')
        if len(lines) >= 2:
            parts = lines[1].split()
            if len(parts) >= 3:
                total = int(parts[1])
                used = int(parts[2])
                if total > 0:
                    percent = round((used / total) * 100, 1)
                    return {
                        "total_mb": total,
                        "used_mb": used,
                        "percent": percent
                    }
        return {"total_mb": 0, "used_mb": 0, "percent": 0}
    except:
        return {"total_mb": 0, "used_mb": 0, "percent": 0}


def get_cpu_temp() -> Optional[float]:
    """Get CPU temperature if available."""
    temp_paths = [
        "/sys/class/thermal/thermal_zone0/temp",
        "/sys/class/hwmon/hwmon0/temp1_input",
        "/sys/class/hwmon/hwmon1/temp1_input",
        "/sys/class/hwmon/hwmon2/temp1_input",
    ]

    for path in temp_paths:
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    temp_millidegrees = int(f.read().strip())
                    # Convert to celsius
                    return round(temp_millidegrees / 1000.0, 1)
        except:
            pass

    # Try sensors command
    try:
        result = subprocess.run(
            ["sensors"],
            capture_output=True,
            text=True,
            timeout=5
        )
        # Look for temperature in output
        for line in result.stdout.split('\n'):
            if 'Core 0' in line or 'CPU' in line or 'Package' in line:
                parts = line.split()
                for part in parts:
                    if '+' in part and '°C' in part:
                        temp_str = part.replace('+', '').replace('°C', '').replace(',', '.')
                        try:
                            return float(temp_str)
                        except:
                            pass
    except:
        pass

    return None


def get_uptime() -> Dict:
    """Get system uptime."""
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.read().split()[0])
            hours = int(uptime_seconds // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            return {
                "seconds": uptime_seconds,
                "hours": hours,
                "minutes": minutes
            }
    except:
        return {"seconds": 0, "hours": 0, "minutes": 0}


def get_audio_status() -> Dict:
    """Check if audio is currently playing."""
    try:
        # Check PulseAudio
        result = subprocess.run(
            ["pactl", "list", "short", "sinks"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            # Check for active connections
            result2 = subprocess.run(
                ["pactl", "get-default-sink"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result2.returncode == 0:
                sink_name = result2.stdout.strip()

                # Check if sink is running (has output)
                result3 = subprocess.run(
                    ["pactl", "list", "short", "sinks"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if sink_name in result3.stdout:
                    return {"playing": True, "sink": sink_name, "mode": "pulseaudio"}

        # Try PipeWire
        result = subprocess.run(
            ["wpctl", "status"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and "Running" in result.stdout:
            # Check for active streams
            if "Sinks:" in result.stdout:
                sinks_section = result.stdout.split("Sinks:")[1].split("Nodes:")[0] if "Nodes:" in result.stdout else result.stdout
                if "." in sinks_section:  # Has active streams
                    return {"playing": True, "sink": "pipewire", "mode": "pipewire"}

        return {"playing": False, "sink": None, "mode": None}
    except:
        return {"playing": False, "sink": None, "mode": None}


def get_load_average() -> Dict:
    """Get system load average (1, 5, 15 minutes)."""
    try:
        with open('/proc/loadavg', 'r') as f:
            parts = f.read().strip().split()
            return {
                "1min": float(parts[0]),
                "5min": float(parts[1]),
                "15min": float(parts[2])
            }
    except:
        return {"1min": 0, "5min": 0, "15min": 0}


def get_all_stats() -> Dict:
    """Get all hardware statistics."""
    cpu = get_cpu_usage()
    mem = get_memory_usage()
    temp = get_cpu_temp()
    uptime = get_uptime()
    audio = get_audio_status()
    load = get_load_average()

    return {
        "timestamp": time.time(),
        "cpu_percent": cpu,
        "memory": mem,
        "cpu_temp_c": temp,
        "uptime": uptime,
        "audio": audio,
        "load_average": load
    }


def handle_action(action: str, params: Dict = None) -> Dict:
    """Handle different monitoring actions."""
    if action == "status" or action == "all":
        return get_all_stats()

    elif action == "cpu":
        return {"cpu_percent": get_cpu_usage(), "load": get_load_average()}

    elif action == "memory":
        return get_memory_usage()

    elif action == "temp":
        temp = get_cpu_temp()
        return {"cpu_temp_c": temp}

    elif action == "audio":
        return get_audio_status()

    elif action == "uptime":
        return get_uptime()

    return {"error": f"Unknown action: {action}"}


def main():
    if len(sys.argv) < 2:
        print(json.dumps(get_all_stats()))
        sys.exit(1)

    try:
        # Handle both direct args and JSON input
        if sys.argv[1].startswith('{'):
            data = json.loads(sys.argv[1])
            action = data.get("action", "status")
        else:
            action = sys.argv[1]
            data = {}
    except:
        action = sys.argv[1] if len(sys.argv) > 1 else "status"
        data = {}

    result = handle_action(action, data)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
