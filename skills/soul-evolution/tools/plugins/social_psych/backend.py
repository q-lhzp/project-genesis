import json
import os
from datetime import datetime

def handle_request(handler, method, action, workspace):
    """
    Plugin Backend Handler for 'social_psych'
    """
    reality_dir = os.path.join(workspace, "memory", "reality")
    res_data = {"status": "error", "message": f"SocialPsych: Unknown action '{action}'"}
    
    print(f"[PLUGIN:social_psych] {method} {action}")

    if method == "GET":
        file_map = {
            "psychology": "psychology.json",
            "reputation": "reputation.json",
            "entities": "social.json"
        }
        if action in file_map:
            res_data = load_json(os.path.join(reality_dir, file_map[action]))
            
    elif method == "POST":
        length = int(handler.headers.get("Content-Length", 0))
        req = json.loads(handler.rfile.read(length).decode("utf-8"))
        
        if action == "add-entity":
            s_path = os.path.join(reality_dir, "social.json")
            social = load_json(s_path)
            if "entities" not in social: social["entities"] = []
            req["id"] = f"npc_{len(social['entities']) + 1}"
            req["bond"] = req.get("bond", 0)
            social["entities"].append(req)
            with open(s_path, "w") as f: json.dump(social, f, indent=2)
            res_data = {"success": True, "id": req["id"]}
            print(f"[PLUGIN:social_psych] Added entity: {req.get('name')}")

        elif action == "update-entity":
            s_path = os.path.join(reality_dir, "social.json")
            social = load_json(s_path)
            entity_id = req.get("entity_id")
            for ent in social.get("entities", []):
                if ent.get("id") == entity_id:
                    ent.update(req)
                    break
            with open(s_path, "w") as f: json.dump(social, f, indent=2)
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
