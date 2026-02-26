import sys
import os
from unittest.mock import MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from spatial import backend

def test_spatial_get():
    print("[TEST] Spatial: GET interior...")
    handler = MagicMock()
    handler.send_response = MagicMock()
    workspace = os.getcwd()

    backend.handle_request(handler, "GET", "interior", workspace)
    handler.send_response.assert_called_with(200)
    print("  ✓ Spatial interior test passed.")

if __name__ == "__main__":
    test_spatial_get()
