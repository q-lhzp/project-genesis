import json
import os

def handle_request(handler, method, action, workspace):
    """
    Plugin Backend Handler for 'identity_journal'
    """
    reality_dir = os.path.join(workspace, "memory", "reality")
    res_data = {"status": "error", "message": f"IdentityJournal: Unknown action '{action}'"}
    
    print(f"[PLUGIN:identity_journal] {method} {action}")

    if method == "GET":
        if action == "skills":
            res_data = load_json(os.path.join(reality_dir, "skills.json"))
        elif action == "interests":
            res_data = load_json(os.path.join(reality_dir, "interests.json"))
        elif action == "dreams":
            dreams = load_jsonl(os.path.join(workspace, "memory", "dreams.jsonl"))
            res_data = {"dreams": dreams[-20:]}

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
    try:
        with open(fp, "r") as f:
            for line in f:
                if line.strip():
                    try: items.append(json.loads(line))
                    except: pass
    except: pass
    return items
