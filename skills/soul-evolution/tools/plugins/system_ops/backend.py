import json
import os
import subprocess
from urllib.parse import parse_qs, urlparse

def handle_request(handler, method, action, workspace):
    """
    Plugin Backend Handler for 'system_ops'
    """
    reality_dir = os.path.join(workspace, "memory", "reality")
    res_data = {"status": "error", "message": f"SystemOps: Unknown action '{action}'"}
    
    print(f"[PLUGIN:system_ops] {method} {action}")

    if method == "GET":
        if action == "cycle":
            res_data = load_json(os.path.join(reality_dir, "cycle.json"))
        elif action == "health":
            # Simple health check
            res_data = {"status": "online", "uptime": "active", "memory": "ok"}
        elif action == "logs":
            query = parse_qs(urlparse(handler.path).query)
            lvl = query.get("level", [""])[0]
            logs = load_jsonl(os.path.join(workspace, "memory", "genesis_debug.jsonl"))
            if lvl: logs = [l for l in logs if l.get("level") == lvl]
            res_data = {"logs": logs[-100:]}
            
    elif method == "POST":
        length = int(handler.headers.get("Content-Length", 0))
        req = json.loads(handler.rfile.read(length).decode("utf-8"))
        
        if action == "cycle/update":
            p = os.path.join(reality_dir, "cycle.json")
            with open(p, "w") as f: json.dump(req, f, indent=2)
            res_data = {"success": True}

    handler.send_response(200)
    handler.send_header("Content-Type", "application/json")
    handler.end_headers()
    handler.wfile.write(json.dumps(res_data).encode())

def load_json(fp):
    if not os.path.exists(fp): return {}
    try:
        with open(fp, "r") as f: return json.load(f)
    except: return {}

def load_jsonl(fp):
    items = []
    if not os.path.exists(fp): return items
    with open(fp, "r") as f:
        for line in f:
            if line.strip():
                try: items.append(json.loads(line))
                except: pass
    return items
