import json
import os
import subprocess
from urllib.parse import parse_qs, urlparse
from .data_utils import load_json, load_jsonl

def handle_get_request(handler, workspace):
    path = handler.path
    res_data = {"status": "error", "message": "Unknown endpoint"}
    
    # 1. OpenClaw Models
    if path == "/api/openclaw/models":
        models = []
        try:
            result = subprocess.run(["openclaw", "models", "list", "--json"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                raw = json.loads(result.stdout).get("models", [])
                models = [{"id": m.get("key"), "name": f"{m.get('key').split('/')[0].upper()} - {m.get('name', m.get('key'))}"} for m in raw if m.get("key")]
        except: pass
        res_data = {"models": models}
    
    # 2. Model Config (Masked)
    elif path == "/api/model/config":
        p = os.path.join(workspace, "memory", "reality", "model_config.json")
        res_data = load_json(p)
        for k in ["api_key", "key_anthropic", "key_gemini", "key_xai", "key_minimax", "key_venice", "key_fal", "key_gemini_img"]:
            if res_data.get(k): res_data[k] = "****"
    
    # 3. Simulation Config
    elif path == "/api/config/all" or path == "/api/config/simulation":
        p = os.path.join(workspace, "memory", "reality", "simulation_config.json")
        res_data = load_json(p)
    
    # 4. Vault & Economy Status
    elif path == "/api/vault/status" or path == "/api/economy/state":
        try:
            res = subprocess.run(["python3", os.path.join(os.path.dirname(__import__("os").path.realpath(__file__)), "..", "vault_bridge.py"), "status"], capture_output=True, text=True, timeout=10)
            res_data = json.loads(res.stdout) if res.returncode == 0 else load_json(os.path.join(workspace, "memory", "reality", "vault_state.json"))
        except: res_data = load_json(os.path.join(workspace, "memory", "reality", "vault_state.json"))

    # 5. Fixed Reality Data Maps
    elif path in ["/api/presence/state", "/api/hardware/resonance", "/api/interests", "/api/avatar/config", "/api/avatar/state", "/api/wizard/status", "/api/godmode/physique"]:
        file_map = {
            "/api/presence/state": "presence_state.json",
            "/api/hardware/resonance": "hardware_resonance.json",
            "/api/interests": "interests.json",
            "/api/avatar/config": "avatar_config.json",
            "/api/avatar/state": "avatar_state.json",
            "/api/wizard/status": "simulation_config.json",
            "/api/godmode/physique": "physique.json"
        }
        reality_dir = os.path.join(workspace, "memory", "reality")
        res_data = load_json(os.path.join(reality_dir, file_map[path]))
        if path == "/api/wizard/status":
            res_data = {"setup_complete": res_data.get("wizard_completed", False)}

    # 6. Profiles, Backups & Genesis
    elif path == "/api/profiles/list":
        p_dir = os.path.join(workspace, "memory", "profiles")
        res_data = [d for d in os.listdir(p_dir) if os.path.isdir(os.path.join(p_dir, d))] if os.path.exists(p_dir) else []
    
    elif path == "/api/backups/list":
        b_dir = os.path.join(workspace, "memory", "backups")
        res_data = sorted([d for d in os.listdir(b_dir) if os.path.isdir(os.path.join(b_dir, d))], reverse=True) if os.path.exists(b_dir) else []

    elif path == "/api/genesis/status":
        p = os.path.join(workspace, "memory", "reality", "simulation_config.json")
        res_data = {"enabled": load_json(p).get("genesis_enabled", False)}

    # 7. Wizard Health & Avatar Check
    elif path.startswith("/api/wizard/check/health"):
        bridges = ["soul-viz.py", "vault_bridge.py", "visual_browser.py"]
        results = []
        tools_dir = os.path.join(workspace, "skills", "soul-evolution", "tools")
        for b in bridges:
            f_path = os.path.join(tools_dir, b)
            exists = os.path.exists(f_path)
            results.append({"name": b, "exists": exists, "executable": os.access(f_path, os.X_OK) if exists else False})
        res_data = {"success": all(r["exists"] for r in results), "bridges": results}

    elif path.startswith("/api/wizard/check/avatar"):
        query = parse_qs(urlparse(path).query)
        avatar_path = query.get("path", [""])[0]
        full_path = os.path.join(workspace, avatar_path) if avatar_path else ""
        exists = os.path.exists(full_path) if full_path else False
        res_data = {"verified": exists, "exists": exists, "path": avatar_path, "message": "Model found" if exists else "Model not found"}

    # 8. Dreams & Telemetry
    elif path == "/api/dreams":
        dreams = load_jsonl(os.path.join(workspace, "memory", "dreams.jsonl"))
        res_data = {"count": len(dreams), "dreams": dreams[-10:]}

    elif path.startswith("/api/telemetry/vitals"):
        # Ensure we return a list for the charts
        res_data = load_jsonl(os.path.join(workspace, "memory", "telemetry", "vitals.jsonl"))[-50:]

    elif path.startswith("/api/logs/recent"):
        query = parse_qs(urlparse(path).query)
        lvl = query.get("level", [""])[0]
        logs = load_jsonl(os.path.join(workspace, "memory", "genesis_debug.jsonl"))
        if lvl: logs = [l for l in logs if l.get("level") == lvl]
        res_data = logs[-100:]

    # Final Response
    handler.send_response(200)
    handler.send_header("Content-Type", "application/json")
    handler.end_headers()
    handler.wfile.write(json.dumps(res_data).encode())
