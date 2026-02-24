#!/usr/bin/env python3
"""
VRM Model Downloader for Project Genesis Phase 22
Downloads a free VRM 1.0 model for avatar rendering.
"""

import os
import urllib.request
import sys

# VRM model URLs (free, Creative Commons models)
VRM_SOURCES = [
    {
        "name": "AliciaSolid",
        "url": "https://github.com/vrm-c/UniVRM/releases/download/v0.108.0/AliciaSolid_vrm-0.51.zip",
        "description": "Standard VRM model from UniVRM"
    },
    {
        "name": "Kotone",
        "url": "https://hub.vroid.com/elements/8774438/models/3b0d146a83314b86957211d5134b91e4d9d6011c.vrm",
        "description": "VRM 1.0 model from VroidHub"
    }
]

# Fallback: Simple VRM sample from pixiv
FALLBACK_URL = "https://raw.githubusercontent.com/pixiv/three-vrm/master/packages/three-vrm/examples/models/VRM1_Constraint_Twist_Sample.vrm"


def download_file(url: str, dest_path: str) -> bool:
    """Download a file from URL to destination path."""
    try:
        print(f"Downloading from: {url}")
        print(f"Destination: {dest_path}")

        # Create temp file for download
        temp_path = dest_path + ".tmp"

        # Download with progress
        def report_progress(block_num, block_size, total_size):
            if total_size > 0:
                percent = min(100, (block_num * block_size * 100) // total_size)
                sys.stdout.write(f"\rDownloading: {percent}%")
                sys.stdout.flush()

        urllib.request.urlretrieve(url, temp_path, reporthook=report_progress)
        print("\nDownload complete!")

        # Move to final destination
        os.replace(temp_path, dest_path)
        return True

    except Exception as e:
        print(f"\nError downloading: {e}")
        if os.path.exists(dest_path + ".tmp"):
            os.remove(dest_path + ".tmp")
        return False


def main():
    workspace = "/home/leo/Schreibtisch"
    avatars_dir = os.path.join(workspace, "avatars")
    vrm_path = os.path.join(avatars_dir, "q_avatar.vrm")

    # Create avatars directory if it doesn't exist
    os.makedirs(avatars_dir, exist_ok=True)

    # Check if VRM already exists
    if os.path.exists(vrm_path):
        print(f"VRM model already exists at: {vrm_path}")
        print("Delete it first to re-download.")
        return

    # Try to download a VRM model
    success = False

    # First try: Use fallback URL (pixiv example model)
    print("Attempting to download sample VRM model...")
    if download_file(FALLBACK_URL, vrm_path):
        success = True
        print(f"Successfully downloaded VRM model to: {vrm_path}")

    # Print file size
    if os.path.exists(vrm_path):
        size_mb = os.path.getsize(vrm_path) / (1024 * 1024)
        print(f"VRM file size: {size_mb:.2f} MB")

    if not success:
        print("\n" + "=" * 50)
        print("Automatic download failed.")
        print("Please manually place a VRM 1.0 file at:")
        print(f"  {vrm_path}")
        print("\nYou can download free VRM models from:")
        print("  - https://vroid.com/en/studio/models")
        print("  - https://hub.vroid.com/en/models")
        print("  - https://github.com/vrm-c/UniVRM/releases")
        print("=" * 50)
        sys.exit(1)


if __name__ == "__main__":
    main()
