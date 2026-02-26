import json
import os

def handle_request(handler, method, action, workspace):
    """
    Plugin Backend Handler for 'genesis_lab'
    """
    reality_dir = os.path.join(workspace, "memory", "reality")
    res_data = {"status": "error", "message": f"GenesisLab: Unknown action '{action}'"}
    
    print(f"[PLUGIN:genesis_lab] {method} {action}")

    if method == "GET":
        if action == "status":
            p = os.path.join(reality_dir, "simulation_config.json")
            cfg = load_json(p)
            res_data = {"setup_complete": cfg.get("wizard_completed", False)}
            
    elif method == "POST":
        length = int(handler.headers.get("Content-Length", 0))
        req = json.loads(handler.rfile.read(length).decode("utf-8"))
        
        if action == "request":
            r_path = os.path.join(reality_dir, "genesis_request.json")
            with open(r_path, "w") as f: json.dump(req, f, indent=2)
            res_data = {"success": True}
        
        elif action == "complete":
            p = os.path.join(reality_dir, "simulation_config.json")
            conf = load_json(p)
            conf["wizard_completed"] = True
            with open(p, "w") as f: json.dump(conf, f, indent=2)
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
