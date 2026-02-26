import sys
import os
from unittest.mock import MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from life_stream import backend

def test_life_stream_photos():
    print("[TEST] Life Stream: GET photos...")
    handler = MagicMock()
    handler.send_response = MagicMock()
    workspace = os.getcwd()

    backend.handle_request(handler, "GET", "photos", workspace)
    handler.send_response.assert_called_with(200)
    print("  ✓ Life Stream photos test passed.")

if __name__ == "__main__":
    test_life_stream_photos()
