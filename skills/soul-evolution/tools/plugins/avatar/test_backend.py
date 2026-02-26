import sys
import os
from unittest.mock import MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from avatar import backend

def test_avatar_config():
    print("[TEST] Avatar: GET config...")
    handler = MagicMock()
    handler.send_response = MagicMock()
    handler.wfile.write = MagicMock()
    workspace = os.getcwd()

    backend.handle_request(handler, "GET", "config", workspace)
    handler.send_response.assert_called_with(200)
    print("  ✓ Avatar config test passed.")

if __name__ == "__main__":
    test_avatar_config()
