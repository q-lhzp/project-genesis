import json
import os
import glob
import base64
from datetime import datetime

def handle_request(handler, method, action, workspace):
    """
    Plugin Backend Handler for 'life_stream'
    """
    reality_dir = os.path.join(workspace, "memory", "reality")
    photo_dir = os.path.join(reality_dir, "photos")
    res_data = {"status": "error", "message": f"LifeStream: Unknown action '{action}'"}
    
    print(f"[PLUGIN:life_stream] {method} {action}")

    if method == "GET":
        if action == "state":
            res_data = load_json(os.path.join(reality_dir, "presence_state.json"))
        elif action == "photos":
            photos = [os.path.basename(f) for f in glob.glob(os.path.join(photo_dir, "*.png"))]
            res_data = {"photos": sorted(photos, reverse=True)}
            
    elif method == "POST":
        length = int(handler.headers.get("Content-Length", 0))
        req = json.loads(handler.rfile.read(length).decode("utf-8"))
        
        if action == "upload":
            filename = req.get("filename", f"upload_{int(datetime.now().timestamp())}.png")
            data = req.get("data")
            if data:
                os.makedirs(photo_dir, exist_ok=True)
                with open(os.path.join(photo_dir, filename), "wb") as f:
                    f.write(base64.b64decode(data))
                res_data = {"success": True, "path": f"media/photos/{filename}"}
        
        elif action == "delete":
            path = req.get("path", "").replace("media/photos/", "")
            full_p = os.path.join(photo_dir, path)
            if os.path.exists(full_p):
                os.remove(full_p)
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
