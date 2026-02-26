import json
import os

def handle_request(handler, method, action, workspace):
    """
    Plugin Backend Handler for 'spatial'
    Route: /api/plugins/spatial/[action]
    """
    reality_dir = os.path.join(workspace, "memory", "reality")
    res_data = {"status": "error", "message": f"Spatial: Unknown action '{action}'"}
    
    print(f"[PLUGIN:spatial] Handling {method} request for {action}")

    if method == "GET":
        file_map = {
            "interior": "interior.json",
            "inventory": "inventory.json",
            "wardrobe": "wardrobe.json"
        }
        if action in file_map:
            res_data = load_json(os.path.join(reality_dir, file_map[action]))
            
    elif method == "POST":
        length = int(handler.headers.get("Content-Length", 0))
        req = json.loads(handler.rfile.read(length).decode("utf-8"))
        
        file_map = {
            "update/interior": "interior.json",
            "update/inventory": "inventory.json",
            "update/wardrobe": "wardrobe.json"
        }
        
        if action in file_map:
            p = os.path.join(reality_dir, file_map[action])
            with open(p, "w") as f:
                json.dump(req, f, indent=2)
            res_data = {"success": True}
            print(f"[PLUGIN:spatial] Successfully updated {file_map[action]}")

    handler.send_response(200)
    handler.send_header("Content-Type", "application/json")
    handler.end_headers()
    handler.wfile.write(json.dumps(res_data).encode())

def load_json(fp):
    if not os.path.exists(fp): return {}
    try:
        with open(fp, "r") as f: return json.load(f)
    except: return {}
