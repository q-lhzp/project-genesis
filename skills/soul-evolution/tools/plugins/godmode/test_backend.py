import sys
import os
from unittest.mock import MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from godmode import backend

def test_godmode_physique():
    print("[TEST] Godmode: GET physique...")
    handler = MagicMock()
    handler.send_response = MagicMock()
    handler.wfile.write = MagicMock()
    workspace = os.getcwd()

    backend.handle_request(handler, "GET", "physique", workspace)
    handler.send_response.assert_called_with(200)
    print("  ✓ Godmode physique test passed.")

if __name__ == "__main__":
    test_godmode_physique()
