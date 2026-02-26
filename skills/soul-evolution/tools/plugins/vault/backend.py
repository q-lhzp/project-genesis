import json
import os
import subprocess

def handle_request(handler, method, action, workspace):
    """
    Plugin Backend Handler for 'vault'
    Route: /api/plugins/vault/[action]
    """
    res_data = {"status": "error", "message": f"Vault: Unknown action '{action}'"}
    
    if method == "GET":
        if action == "status":
            try:
                bridge_path = os.path.join(os.path.dirname(__file__), "..", "..", "vault_bridge.py")
                res = subprocess.run(["python3", bridge_path, "status"], capture_output=True, text=True, timeout=10)
                res_data = json.loads(res.stdout) if res.returncode == 0 else {}
            except Exception as e:
                res_data = {"error": str(e)}
        
    elif method == "POST":
        length = int(handler.headers.get("Content-Length", 0))
        req = json.loads(handler.rfile.read(length).decode("utf-8"))
        
        if action == "trade":
            # Delegate to bridge
            try:
                bridge_path = os.path.join(os.path.dirname(__file__), "..", "..", "vault_bridge.py")
                res = subprocess.run(["python3", bridge_path, json.dumps(req)], capture_output=True, text=True, timeout=30)
                res_data = json.loads(res.stdout) if res.returncode == 0 else {"success": False}
            except Exception as e:
                res_data = {"success": False, "error": str(e)}

    # Send Response
    handler.send_response(200)
    handler.send_header("Content-Type", "application/json")
    handler.end_headers()
    handler.wfile.write(json.dumps(res_data).encode())
