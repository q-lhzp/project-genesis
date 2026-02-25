#!/usr/bin/env python3
"""
God-Mode Bridge - API für manuelle Simulation-Overrides
Phase 44: WebUI Sovereignty Controls
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

PORT = 18795  # Gateway port + 4

class GodModeHandler(BaseHTTPRequestHandler):
    workspace = None

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/physique":
            self.send_physique()
        elif path == "/api/reflex-status":
            self.send_reflex_status()
        elif path == "/api/events":
            self.send_events()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode() if content_length > 0 else ""

        if path == "/api/override/needs":
            self.override_needs(body)
        elif path == "/api/inject/event":
            self.inject_event(body)
        elif path == "/api/voice":
            self.trigger_voice(body)
        else:
            self.send_response(404)
            self.end_headers()

    def send_physique(self):
        try:
            path = os.path.join(self.workspace, "memory", "reality", "physique.json")
            if os.path.exists(path):
                with open(path) as f:
                    data = json.load(f)
            else:
                data = {}
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        except Exception as e:
            self.send_error(500, str(e))

    def send_reflex_status(self):
        """Prüft ob Reflex-Lock aktiv ist"""
        try:
            path = os.path.join(self.workspace, "memory", "reality", "physique.json")
            locked = False
            reason = ""

            if os.path.exists(path):
                with open(path) as f:
                    ph = json.load(f)
                    needs = ph.get("needs", {})
                    threshold = 95

                    critical = []
                    for k, v in needs.items():
                        if v >= threshold:
                            critical.append(f"{k}={v}")

                    if critical:
                        locked = True
                        reason = f"Critical needs: {', '.join(critical)}"

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "locked": locked,
                "reason": reason,
                "threshold": 95
            }).encode())
        except Exception as e:
            self.send_error(500, str(e))

    def send_events(self):
        """Life Events History"""
        try:
            path = os.path.join(self.workspace, "memory", "reality", "event_history.jsonl")
            events = []

            if os.path.exists(path):
                with open(path) as f:
                    for line in f:
                        try:
                            events.append(json.loads(line))
                        except:
                            pass

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(events[-10:]).encode())  # Last 10
        except Exception as e:
            self.send_error(500, str(e))

    def override_needs(self, body):
        """Überschreibt Bedürfnisse direkt"""
        try:
            params = json.loads(body)
            path = os.path.join(self.workspace, "memory", "reality", "physique.json")

            if os.path.exists(path):
                with open(path) as f:
                    ph = json.load(f)

                for key, value in params.items():
                    if key in ph.get("needs", {}):
                        ph["needs"][key] = max(0, min(100, int(value)))

                with open(path, "w") as f:
                    json.dump(ph, f, indent=2)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok", "needs": ph["needs"]}).encode())
            else:
                self.send_error(404, "physique.json not found")
        except Exception as e:
            self.send_error(500, str(e))

    def inject_event(self, body):
        """Injiziert ein Life Event"""
        try:
            params = json.loads(body)
            event = {
                "id": f"EVENT-{int(os.times().elapsed * 1000)}",
                "type": params.get("type", "neutral"),
                "event": params.get("event", "Manual event"),
                "impact": params.get("impact", 5),
                "timestamp": __import__("datetime").datetime.now().isoformat()
            }

            path = os.path.join(self.workspace, "memory", "reality", "event_history.jsonl")
            with open(path, "a") as f:
                f.write(json.dumps(event) + "\n")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "event": event}).encode())
        except Exception as e:
            self.send_error(500, str(e))

    def trigger_voice(self, body):
        """Trigger Voice Output"""
        try:
            params = json.loads(body)
            text = params.get("text", "Hello!")

            # Write to voice queue
            queue_path = os.path.join(self.workspace, "memory", "reality", "voice_queue.json")
            with open(queue_path, "w") as f:
                json.dump({"text": text, "pending": True}, f)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "queued", "text": text}).encode())
        except Exception as e:
            self.send_error(500, str(e))

    def log_message(self, format, *args):
        print(f"[GodMode] {format % args}")

def run_server(workspace: str, port: int = PORT):
    GodModeHandler.workspace = workspace

    # Create a simple wrapper
    class CustomHandler(GodModeHandler):
        pass

    CustomHandler.workspace = workspace

    server = HTTPServer(("0.0.0.0", port), CustomHandler)
    print(f"🌀 God-Mode API running at http://localhost:{port}")
    print(f"   Workspace: {workspace}")
    print(f"   Endpoints:")
    print(f"   GET  /api/physique         - Get current needs")
    print(f"   GET  /api/reflex-status     - Check if reflex-locked")
    print(f"   GET  /api/events            - Last 10 life events")
    print(f"   POST /api/override/needs    - Set needs { '{\"energy\": 100}' }")
    print(f"   POST /api/inject/event      - Inject event { '{\"type\": \"positive\", \"event\": \"Won lottery!\", \"impact\": 10}' }")
    print(f"   POST /api/voice            - Queue voice { '{\"text\": \"Hello!\"}' }")
    print()

    server.serve_forever()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: godmode_bridge.py <workspace_path> [port]")
        sys.exit(1)

    workspace = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else PORT
    run_server(workspace, port)
