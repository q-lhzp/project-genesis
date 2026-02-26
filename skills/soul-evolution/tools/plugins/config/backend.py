import json
import os
import subprocess

def handle_request(handler, method, action, workspace):
    """
    Plugin Backend Handler for 'config'
    Route: /api/plugins/config/[action]
    """
    res_data = {"status": "error", "message": f"Config: Unknown action '{action}'"}
    reality_dir = os.path.join(workspace, "memory", "reality")
    model_config_path = os.path.join(reality_dir, "model_config.json")
    sim_config_path = os.path.join(reality_dir, "simulation_config.json")
    
    if method == "GET":
        if action == "all":
            res_data = {
                "simulation": load_json(sim_config_path),
                "models": load_json(model_config_path)
            }
            # Mask keys
            for k in ["api_key", "key_anthropic", "key_gemini", "key_xai", "key_minimax", "key_venice", "key_fal", "key_gemini_img"]:
                if res_data["models"].get(k): res_data["models"][k] = "****"
                
        elif action == "openclaw/models":
            models = []
            try:
                result = subprocess.run(["openclaw", "models", "list", "--json"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    raw = json.loads(result.stdout).get("models", [])
                    models = [{"id": m.get("key"), "name": f"{m.get('key').split('/')[0].upper()} - {m.get('name', m.get('key'))}"} for m in raw if m.get("key")]
            except: pass
            res_data = {"models": models}
            
    elif method == "POST":
        length = int(handler.headers.get("Content-Type", 0) if "Content-Length" not in handler.headers else handler.headers.get("Content-Length"))
        req = json.loads(handler.rfile.read(length).decode("utf-8"))
        
        if action == "save":
            # 1. Save Models
            if "models" in req:
                conf = load_json(model_config_path)
                for k, v in req["models"].items():
                    if v != "****": conf[k] = v
                with open(model_config_path, "w") as f: json.dump(conf, f, indent=2)
            
            # 2. Save Simulation
            if "simulation" in req:
                with open(sim_config_path, "w") as f: json.dump(req["simulation"], f, indent=2)
            
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
