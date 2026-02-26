import sys
import os
import json
from unittest.mock import MagicMock

# Path setup to import the plugin
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from vault import backend

def test_vault_get_status():
    print("[TEST] Vault: GET status...")
    handler = MagicMock()
    handler.path = "/api/plugins/vault/status"
    workspace = os.getcwd() # Or specific test workspace
    
    # Mocking response methods
    handler.send_response = MagicMock()
    handler.send_header = MagicMock()
    handler.end_headers = MagicMock()
    handler.wfile.write = MagicMock()

    backend.handle_request(handler, "GET", "status", workspace)
    
    # Verify
    handler.send_response.assert_called_with(200)
    print("  ✓ Response 200 OK")
    print("  ✓ Vault status test passed.")

if __name__ == "__main__":
    test_vault_get_status()
