#!/usr/bin/env python3
"""
Download Voice Models for Chatterbox-Turbo TTS Engine.
Downloads the required model weights from HuggingFace.
"""

import os
import sys

# Configuration
VOICE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(VOICE_DIR, "models")
CACHE_DIR = os.path.join(os.path.expanduser("~"), ".cache", "chatterbox")

# Model configuration
MODEL_REPO = "ResembleAI/chatterbox-turbo"
MODEL_FILES = [
    "config.json",
    "model.safetensors",  # or pytorch_model.bin
    "vocab.json",
    "tokenizer.json",
]


def ensure_dirs():
    """Create necessary directories."""
    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)


def check_models_exist():
    """Check if models are already downloaded."""
    config_path = os.path.join(MODEL_DIR, "config.json")
    return os.path.exists(config_path)


def download_models():
    """Download models using huggingface_hub."""
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        print("Installing huggingface_hub...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "huggingface_hub", "-q"])
        from huggingface_hub import snapshot_download

    print(f"Downloading {MODEL_REPO} to {MODEL_DIR}...")

    try:
        # Download to cache first
        cached_path = snapshot_download(
            repo_id=MODEL_REPO,
            cache_dir=CACHE_DIR,
            local_dir=MODEL_DIR,
            local_dir_use_symlinks=False,
        )
        print(f"Models downloaded to: {cached_path}")
        return True
    except Exception as e:
        print(f"Error downloading models: {e}")
        return False


def main():
    ensure_dirs()

    if check_models_exist():
        print("Models already exist. Skipping download.")
        print(f"Model directory: {MODEL_DIR}")
        return 0

    print("Models not found. Starting download...")
    success = download_models()

    if success:
        print("\nDownload complete!")
        return 0
    else:
        print("\nDownload failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
