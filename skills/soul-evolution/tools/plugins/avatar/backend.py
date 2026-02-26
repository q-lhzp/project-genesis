import json
import os

def handle_request(handler, method, action, workspace):
    """
    Plugin Backend Handler for 'avatar'
    Route: /api/plugins/avatar/[action]
    """
    res_data = {"status": "error", "message": f"Avatar: Unknown action '{action}'"}
    reality_dir = os.path.join(workspace, "memory", "reality")
    
    if method == "GET":
        if action == "config":
            p = os.path.join(reality_dir, "avatar_config.json")
            res_data = load_json(p)
        elif action == "state":
            p = os.path.join(reality_dir, "avatar_state.json")
            res_data = load_json(p)
            
    elif method == "POST":
        length = int(handler.headers.get("Content-Length", 0))
        req = json.loads(handler.rfile.read(length).decode("utf-8"))
        
        if action == "update":
            p = os.path.join(reality_dir, "avatar_state.json")
            state = load_json(p)
            state.update(req)
            with open(p, "w") as f: json.dump(state, f, indent=2)
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
