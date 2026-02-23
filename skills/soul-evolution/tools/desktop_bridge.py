import sys
import json
import subprocess
import os
import time
from pathlib import Path

# Paths to external tools
DESKTOP_AUTO_DIR = "/home/leo/Schreibtisch/desktop-automation/scripts"
BOT_SIMPLE_DIR = "/home/leo/Schreibtisch/Bot_Simple/src"

def run_desktop_control(args):
    script = os.path.join(DESKTOP_AUTO_DIR, "desktop_control.py")
    cmd = ["python3", script] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout, result.stderr

def capture_screen():
    # Use wayland capture script
    script = os.path.join(DESKTOP_AUTO_DIR, "capture_screen_wayland.py")
    output_path = os.path.abspath("memory/reality/screen_capture.png")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    cmd = ["python3", script, output_path]
    subprocess.run(cmd, capture_output=True)
    return output_path

def perform_ocr(image_path):
    # Try to use PaddleOCR from Bot_Simple if available, else fallback to mock/simple
    # For now, let's use a simplified version or call into Bot_Simple if possible
    # Mocking for immediate result, but path is clear
    return "Detected text: [This is a placeholder for OCR result from Bot_Simple integration]"

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Action required"}))
        sys.exit(1)

    action = sys.argv[1]
    params = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}

    try:
        if action == "click":
            btn = params.get("button", "left")
            x, y = params.get("x"), params.get("y")
            stdout, stderr = run_desktop_control(["click", btn, str(x), str(y)] if x is not None else ["click", btn])
            print(json.dumps({"success": True, "output": stdout}))

        elif action == "type":
            text = params.get("text", "")
            stdout, stderr = run_desktop_control(["type", text])
            print(json.dumps({"success": True, "output": stdout}))

        elif action == "key":
            combo = params.get("combo", "")
            stdout, stderr = run_desktop_control(["key", combo])
            print(json.dumps({"success": True, "output": stdout}))

        elif action == "vision":
            img_path = capture_screen()
            # In a real scenario, we'd now run OCR
            # text = perform_ocr(img_path)
            print(json.dumps({
                "success": True, 
                "screenshot": img_path,
                "note": "Screen captured. Use this to see what is happening in games or apps."
            }))

        else:
            print(json.dumps({"error": f"Unknown action: {action}"}))

    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()
