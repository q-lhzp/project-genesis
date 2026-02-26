import json
import os
from datetime import datetime

def handle_request(handler, method, action, workspace):
    """
    Plugin Backend Handler for 'godmode'
    Route: /api/plugins/godmode/[action]
    """
    res_data = {"status": "error", "message": f"God-Mode: Unknown action '{action}'"}
    reality_dir = os.path.join(workspace, "memory", "reality")
    
    if method == "GET":
        if action == "physique":
            p = os.path.join(reality_dir, "physique.json")
            res_data = load_json(p)
            
    elif method == "POST":
        length = int(handler.headers.get("Content-Length", 0))
        req = json.loads(handler.rfile.read(length).decode("utf-8"))
        
        if action == "override/needs":
            p_path = os.path.join(reality_dir, "physique.json")
            ph = load_json(p_path)
            if "needs" not in ph: ph["needs"] = {}
            ph["needs"].update(req)
            with open(p_path, "w") as f: json.dump(ph, f, indent=2)
            res_data = {"success": True}
            
        elif action == "inject/event":
            ev_path = os.path.join(reality_dir, "social_events.json")
            events = load_json(ev_path)
            if "pending" not in events: events["pending"] = []
            req["timestamp"] = datetime.now().isoformat()
            events["pending"].append(req)
            with open(ev_path, "w") as f: json.dump(events, f, indent=2)
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
