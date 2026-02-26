#!/usr/bin/env python3
"""
Soul Evolution Visualizer v5.7.0 (Modular Backend)
Backend server for the Project Genesis Singularity Dashboard.
Frontend assets are located in the ./web/ directory.
"""

import json
import re
import sys
import os
import glob
import subprocess
import threading
import base64
from datetime import datetime, timedelta
import http.server
import socketserver
from urllib.parse import parse_qs, urlparse

# --- DATA COLLECTION LOGIC ---

def parse_soul_md(content: str) -> list:
    nodes = []
    current_section = None
    current_subsection = None
    for line in content.split("\n"):
        line_stripped = line.strip()
        if not line_stripped or line_stripped.startswith(">") or line_stripped == "---": continue
        if line_stripped.startswith("# SOUL") or line_stripped.startswith("_This file"): continue
        if line_stripped.startswith("## "):
            current_section = line_stripped
            nodes.append({"type": "section", "text": line_stripped.replace("## ", ""), "raw": line_stripped, "children": []})
        elif line_stripped.startswith("### "):
            current_subsection = line_stripped
            if nodes:
                nodes[-1]["children"].append({"type": "subsection", "text": line_stripped.replace("### ", ""), "raw": line_stripped, "children": []})
        elif line_stripped.startswith("- "):
            tag = "CORE" if "[CORE]" in line_stripped else ("MUTABLE" if "[MUTABLE]" in line_stripped else "untagged")
            text = re.sub(r'\s*\[(CORE|MUTABLE)\]\s*', '', line_stripped[2:].strip()).strip()
            bullet = {"type": "bullet", "text": text, "raw": line_stripped, "tag": tag, "section": current_section, "subsection": current_subsection}
            if nodes and nodes[-1]["children"] and nodes[-1]["children"][-1]["type"] == "subsection":
                nodes[-1]["children"][-1]["children"].append(bullet)
            elif nodes: nodes[-1]["children"].append(bullet)
    return nodes

def load_json(fp):
    if not os.path.exists(fp): return {}
    try:
        with open(fp, "r") as f: return json.load(f)
    except: return {}

def load_jsonl(fp):
    items = []
    if not os.path.exists(fp): return items
    try:
        with open(fp, "r") as f:
            for line in f:
                if line.strip():
                    try: items.append(json.loads(line))
                    except: pass
    except: pass
    return items

def collect_data(workspace: str) -> dict:
    memory_dir = os.path.join(workspace, "memory")
    reality_dir = os.path.join(memory_dir, "reality")
    
    soul_path = os.path.join(workspace, "SOUL.md")
    soul_content = ""
    if os.path.exists(soul_path):
        with open(soul_path, "r") as f: soul_content = f.read()
    
    # Core Data
    data = {
        "soul_tree": parse_soul_md(soul_content),
        "identity_raw": soul_content,
        "changes": load_jsonl(os.path.join(memory_dir, "soul_changes.jsonl")),
        "experiences": [],
        "reflections": load_jsonl(os.path.join(memory_dir, "reflections.jsonl")),
        "proposals_pending": load_jsonl(os.path.join(memory_dir, "proposals", "pending.jsonl")),
        "significant": load_jsonl(os.path.join(memory_dir, "significant", "significant.jsonl")),
        "physique": load_json(os.path.join(reality_dir, "physique.json")),
        "interests": load_json(os.path.join(reality_dir, "interests.json")),
        "world_state": load_json(os.path.join(reality_dir, "world_state.json")),
        "reputation": load_json(os.path.join(reality_dir, "reputation.json")),
        "news": load_json(os.path.join(reality_dir, "news.json")),
        "social_events": load_json(os.path.join(reality_dir, "social_events.json")),
        "vault_state": load_json(os.path.join(reality_dir, "vault_state.json")),
        "interior": load_json(os.path.join(reality_dir, "interior.json")),
        "inventory": load_json(os.path.join(reality_dir, "inventory.json")),
        "wardrobe": load_json(os.path.join(reality_dir, "wardrobe.json")),
        "skills": load_json(os.path.join(reality_dir, "skills.json")),
        "photos": [os.path.basename(f) for f in glob.glob(os.path.join(reality_dir, "photos", "*.png"))],
        "system_config": {"openai_ok": True, "anthropic_ok": True} # Dynamic check could be added
    }

    # Load recent experiences from last 7 days
    exp_dir = os.path.join(memory_dir, "experiences")
    if os.path.isdir(exp_dir):
        for fp in sorted(glob.glob(os.path.join(exp_dir, "*.jsonl")))[-7:]:
            data["experiences"].extend(load_jsonl(fp))
            
    return data

# --- HTML GENERATION ---

def generate_html(data: dict) -> str:
    data_json = json.dumps(data, indent=None, default=str)
    template_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "web", "index.html")
    
    if os.path.exists(template_path):
        with open(template_path, "r") as f:
            return f.read().replace("{data_json}", data_json)
    
    return f"Template not found at {template_path}. Ensure Phase 1 and 5 were completed correctly."

def generate_mindmap_html(data: dict) -> str:
    data_json = json.dumps(data, indent=None, default=str)
    # Placeholder for modular mindmap
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Mindmap</title>
<link rel="stylesheet" href="/web/css/mindmap.css"></head>
<body><canvas id="canvas"></canvas>
<script>const DATA = {data_json};</script>
<script src="/web/js/core.js"></script>
<script src="/web/js/mindmap.js"></script></body></html>"""

# --- SERVER IMPLEMENTATION ---

def main():
    print("--- PROJECT GENESIS DASHBOARD v5.7.0 (MODULAR) STARTING ---", flush=True)
    workspace = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    port = 8080
    if "--serve" in sys.argv:
        idx = sys.argv.index("--serve")
        if idx + 1 < len(sys.argv) and sys.argv[idx + 1].isdigit():
            port = int(sys.argv[idx + 1])

    web_base = os.path.abspath(os.path.join(os.path.dirname(__file__), "web"))
    media_base = os.path.join(workspace, "memory", "reality")
    
    # Pre-calculated paths for handlers
    soul_path = os.path.join(workspace, "SOUL.md")
    model_config_path = os.path.join(workspace, "memory", "reality", "model_config.json")
    sim_config_path = os.path.join(workspace, "memory", "reality", "simulation_config.json")
    interior_path = os.path.join(workspace, "memory", "reality", "interior.json")
    inventory_path = os.path.join(workspace, "memory", "reality", "inventory.json")
    wardrobe_path = os.path.join(workspace, "memory", "reality", "wardrobe.json")
    pending_path = os.path.join(workspace, "memory", "proposals", "pending.jsonl")
    history_path = os.path.join(workspace, "memory", "proposals", "history.jsonl")

    class SoulEvolutionHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            # Log for debugging, but could be silenced for GET noise
            super().log_message(format, *args)

        def do_HEAD(self): self.do_GET()

        def do_GET(self):
            # 1. Static Web Assets
            if self.path.startswith("/web/"):
                rel = self.path[len("/web/"):]
                f_path = os.path.join(web_base, rel)
                if os.path.isfile(f_path):
                    self.serve_file(f_path)
                    return
            
            # 2. Reality Media (Images/Photos)
            if self.path.startswith("/media/"):
                rel = self.path[len("/media/"):]
                f_path = os.path.join(media_base, rel)
                if os.path.isfile(f_path):
                    self.serve_file(f_path)
                    return

            # 3. Main Application Pages
            if self.path == "/" or self.path == "/soul-evolution.html":
                data = collect_data(workspace)
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(generate_html(data).encode())
                return
            
            if self.path == "/soul-mindmap.html":
                data = collect_data(workspace)
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(generate_mindmap_html(data).encode())
                return

            # 4. API GET Endpoints
            if self.path.startswith("/api/"):
                self.handle_api_get()
                return

            self.send_error(404)

        def do_POST(self):
            # Handle non-API legacy routes
            if self.path == "/save-soul":
                self.handle_save_soul()
                return
            if self.path == "/resolve-proposal":
                self.handle_resolve_proposal()
                return
            if self.path.startswith("/update-"):
                self.handle_legacy_updates()
                return

            # Main API POST
            if self.path.startswith("/api/"):
                self.handle_api_post()
                return
            
            self.send_error(404)

        def serve_file(self, path):
            ext = os.path.splitext(path)[1].lower()
            ct = {
                ".html":"text/html", ".css":"text/css", ".js":"application/javascript",
                ".png":"image/png", ".jpg":"image/jpeg", ".jpeg":"image/jpeg", ".svg":"image/svg+xml"
            }.get(ext, "application/octet-stream")
            try:
                with open(path, "rb") as f: data = f.read()
                self.send_response(200)
                self.send_header("Content-Type", ct)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            except: self.send_error(404)

        def handle_api_get(self):
            res_data = {"status": "error", "message": "Unknown endpoint"}
            
            if self.path == "/api/openclaw/models":
                models = []
                try:
                    result = subprocess.run(["openclaw", "models", "list", "--json"], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        raw = json.loads(result.stdout).get("models", [])
                        models = [{"id": m.get("key"), "name": f"{m.get('key').split('/')[0].upper()} - {m.get('name', m.get('key'))}"} for m in raw if m.get("key")]
                except: pass
                res_data = {"models": models}
            
            elif self.path == "/api/model/config":
                res_data = load_json(model_config_path)
                for k in ["api_key", "key_anthropic", "key_gemini", "key_xai", "key_minimax", "key_venice", "key_fal", "key_gemini_img"]:
                    if res_data.get(k): res_data[k] = "****"
            
            elif self.path == "/api/config/all":
                res_data = load_json(sim_config_path)
            
            elif self.path == "/api/vault/status":
                # Call vault bridge for live status
                try:
                    res = subprocess.run(["python3", os.path.join(os.path.dirname(__file__), "vault_bridge.py"), "status"], capture_output=True, text=True, timeout=10)
                    res_data = json.loads(res.stdout) if res.returncode == 0 else load_json(os.path.join(workspace, "memory", "reality", "vault_state.json"))
                except: res_data = load_json(os.path.join(workspace, "memory", "reality", "vault_state.json"))

            elif self.path in ["/api/presence/state", "/api/hardware/resonance", "/api/interests", "/api/avatar/config", "/api/avatar/state", "/api/wizard/status"]:
                file_map = {
                    "/api/presence/state": "presence_state.json",
                    "/api/hardware/resonance": "hardware_resonance.json",
                    "/api/interests": "interests.json",
                    "/api/avatar/config": "avatar_config.json",
                    "/api/avatar/state": "avatar_state.json",
                    "/api/wizard/status": "simulation_config.json" # setup_complete is here
                }
                res_data = load_json(os.path.join(reality_dir := os.path.join(workspace, "memory", "reality"), file_map[self.path]))
                if self.path == "/api/wizard/status":
                    res_data = {"setup_complete": res_data.get("wizard_completed", False)}

            elif self.path == "/api/dreams":
                dreams = load_jsonl(os.path.join(workspace, "memory", "dreams.jsonl"))
                res_data = {"count": len(dreams), "dreams": dreams[-10:]}

            elif self.path.startswith("/api/logs/recent"):
                query = parse_qs(urlparse(self.path).query)
                lvl = query.get("level", [""])[0]
                logs = load_jsonl(os.path.join(workspace, "memory", "genesis_debug.jsonl"))
                if lvl: logs = [l for l in logs if l.get("level") == lvl]
                res_data = logs[-100:]

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(res_data).encode())

        def handle_api_post(self):
            length = int(self.headers.get("Content-Length", 0))
            req = json.loads(self.rfile.read(length).decode("utf-8"))
            res_data = {"success": True}

            if self.path == "/api/model/config":
                conf = load_json(model_config_path)
                for k, v in req.items():
                    if v != "****": conf[k] = v
                with open(model_config_path, "w") as f: json.dump(conf, f, indent=2)
            
            elif self.path == "/api/config/save":
                with open(sim_config_path, "w") as f: json.dump(req, f, indent=2)
            
            elif self.path == "/api/godmode/override/needs":
                p_path = os.path.join(workspace, "memory", "reality", "physique.json")
                ph = load_json(p_path)
                if "needs" not in ph: ph["needs"] = {}
                ph["needs"].update(req)
                with open(p_path, "w") as f: json.dump(ph, f, indent=2)
            
            elif self.path == "/api/avatar/update":
                a_path = os.path.join(workspace, "memory", "reality", "avatar_state.json")
                astate = load_json(a_path)
                astate.update(req)
                astate["timestamp"] = datetime.now().isoformat()
                with open(a_path, "w") as f: json.dump(astate, f, indent=2)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(res_data).encode())

        # --- LEGACY HANDLERS (to be modularized later) ---
        def handle_save_soul(self):
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            with open(soul_path, "w") as f: f.write(body)
            self.send_response(200); self.end_headers(); self.wfile.write(b"OK")

        def handle_legacy_updates(self):
            length = int(self.headers.get("Content-Length", 0))
            req = json.loads(self.rfile.read(length).decode("utf-8"))
            f_map = {"/update-interior": interior_path, "/update-inventory": inventory_path, "/update-wardrobe": wardrobe_path}
            if self.path in f_map:
                with open(f_map[self.path], "w") as f: json.dump(req, f, indent=2)
            self.send_response(200); self.end_headers(); self.wfile.write(b"OK")

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), SoulEvolutionHandler) as httpd:
        print(f"Server active at http://localhost:{port}")
        httpd.serve_forever()

if __name__ == "__main__":
    main()
