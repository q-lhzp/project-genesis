import json
import os
from datetime import datetime
from .data_utils import load_json

def handle_post_request(handler, workspace):
    length = int(handler.headers.get("Content-Length", 0))
    body = handler.rfile.read(length).decode("utf-8")
    req = {}
    try: req = json.loads(body)
    except: pass

    res_data = {"success": True}
    path = handler.path

    # 1. Model Config (Handling Key Masking)
    if path == "/api/model/config":
        p = os.path.join(workspace, "memory", "reality", "model_config.json")
        conf = load_json(p)
        for k, v in req.items():
            if v != "****": conf[k] = v
        with open(p, "w") as f: json.dump(conf, f, indent=2)
    
    # 2. Simulation Config Save
    elif path == "/api/config/save":
        p = os.path.join(workspace, "memory", "reality", "simulation_config.json")
        with open(p, "w") as f: json.dump(req, f, indent=2)
    
    # 3. Godmode Needs Override
    elif path == "/api/godmode/override/needs":
        p_path = os.path.join(workspace, "memory", "reality", "physique.json")
        ph = load_json(p_path)
        if "needs" not in ph: ph["needs"] = {}
        ph["needs"].update(req)
        with open(p_path, "w") as f: json.dump(ph, f, indent=2)
    
    # 4. Avatar State Update
    elif path == "/api/avatar/update":
        a_path = os.path.join(workspace, "memory", "reality", "avatar_state.json")
        astate = load_json(a_path)
        astate.update(req)
        astate["timestamp"] = datetime.now().isoformat()
        with open(a_path, "w") as f: json.dump(astate, f, indent=2)
    
    # 5. Godmode Event Injection
    elif path == "/api/godmode/inject/event":
        ev_path = os.path.join(workspace, "memory", "reality", "social_events.json")
        events = load_json(ev_path)
        if "pending" not in events: events["pending"] = []
        req["timestamp"] = datetime.now().isoformat()
        events["pending"].append(req)
        with open(ev_path, "w") as f: json.dump(events, f, indent=2)

    # 6. Social Entity Management
    elif path == "/api/social/add-entity":
        s_path = os.path.join(workspace, "memory", "reality", "social.json")
        social = load_json(s_path)
        if "entities" not in social: social["entities"] = []
        req["id"] = f"npc_{len(social['entities']) + 1}"
        req["bond"] = 0
        social["entities"].append(req)
        with open(s_path, "w") as f: json.dump(social, f, indent=2)

    # 7. Wizard Completion
    elif path == "/api/wizard/complete":
        p = os.path.join(workspace, "memory", "reality", "simulation_config.json")
        conf = load_json(p)
        conf["wizard_completed"] = True
        with open(p, "w") as f: json.dump(conf, f, indent=2)

    # 8. Genesis Bootstrap Request
    elif path == "/api/genesis/request":
        r_path = os.path.join(workspace, "memory", "reality", "genesis_request.json")
        with open(r_path, "w") as f: json.dump(req, f, indent=2)

    # 9. Vault Trade Simulation
    elif path == "/api/godmode/vault/simulate-trade":
        import subprocess
        try:
            action = req.get("action", "status")
            bridge_path = os.path.join(os.path.dirname(__import__("os").path.realpath(__file__)), "..", "vault_bridge.py")
            cmd = ["python3", bridge_path, action, "--mode", req.get("mode", "paper")]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            res_data = {"success": result.returncode == 0, "result": result.stdout}
        except Exception as e:
            res_data = {"success": False, "error": str(e)}

    # 10. Social Entity Management (Update)
    elif path == "/api/social/update-entity":
        s_path = os.path.join(workspace, "memory", "reality", "social.json")
        social = load_json(s_path)
        entity_id = req.get("entity_id")
        updated = False
        for ent in social.get("entities", []):
            if ent.get("id") == entity_id:
                ent.update(req)
                updated = True
                break
        if updated:
            with open(s_path, "w") as f: json.dump(social, f, indent=2)
        res_data = {"success": updated}

    # 11. Image Management
    elif path == "/upload-image":
        import base64
        try:
            filename = req.get("filename", "upload.png")
            data = req.get("data")
            if data:
                photo_dir = os.path.join(workspace, "memory", "reality", "photos")
                os.makedirs(photo_dir, exist_ok=True)
                with open(os.path.join(photo_dir, filename), "wb") as f:
                    f.write(base64.b64decode(data))
                res_data = {"success": True, "path": f"media/photos/{filename}"}
        except Exception as e:
            res_data = {"success": False, "error": str(e)}

    elif path == "/delete-image":
        try:
            img_path = req.get("path") # e.g. media/photos/xyz.png
            if img_path:
                full_p = os.path.join(workspace, "memory", "reality", img_path.replace("media/", ""))
                if os.path.exists(full_p):
                    os.remove(full_p)
                    res_data = {"success": True}
        except Exception as e:
            res_data = {"success": False, "error": str(e)}

    else:
        res_data = {"success": False, "message": "Unknown API endpoint"}

    # Final Response
    handler.send_response(200)
    handler.send_header("Content-Type", "application/json")
    handler.end_headers()
    handler.wfile.write(json.dumps(res_data).encode())

def handle_legacy_post(handler, workspace):
    length = int(handler.headers.get("Content-Length", 0))
    body = handler.rfile.read(length).decode("utf-8")
    
    if handler.path == "/save-soul":
        p = os.path.join(workspace, "SOUL.md")
        with open(p, "w") as f: f.write(body)
        handler.send_response(200); handler.end_headers(); handler.wfile.write(b"OK")
        return

    if handler.path == "/resolve-proposal":
        # Move proposal from pending to history
        pending_p = os.path.join(workspace, "memory", "proposals", "pending.jsonl")
        history_p = os.path.join(workspace, "memory", "proposals", "history.jsonl")
        req = json.loads(body)
        proposal_id = req.get("id")

        # Load pending proposals
        from .data_utils import load_jsonl
        pending = load_jsonl(pending_p)

        # Filter out resolved proposal and write remaining to pending
        remaining = [p for p in pending if p.get("id") != proposal_id]
        with open(pending_p, "w") as f:
            for p in remaining:
                f.write(json.dumps(p) + "\n")

        # Add to history with resolution status
        req["resolved"] = True
        req["resolved_at"] = datetime.now().isoformat()
        with open(history_p, "a") as f:
            f.write(json.dumps(req) + "\n")

        handler.send_response(200); handler.end_headers(); handler.wfile.write(b"OK")
        return

    req = json.loads(body)
    reality_dir = os.path.join(workspace, "memory", "reality")
    f_map = {
        "/update-interior": "interior.json",
        "/update-inventory": "inventory.json",
        "/update-wardrobe": "wardrobe.json",
        "/update-world": "world_state.json",
        "/update-cycle": "cycle.json"
    }
    
    if handler.path in f_map:
        p = os.path.join(reality_dir, f_map[handler.path])
        with open(p, "w") as f: json.dump(req, f, indent=2)
        handler.send_response(200); handler.end_headers(); handler.wfile.write(b"OK")
    else:
        handler.send_error(404)
