#!/usr/bin/env python3
"""
Voice Bridge - Chatterbox-Turbo TTS Engine
Generates speech audio from text using the Chatterbox-Turbo model.
"""

import os
import sys
import json
import subprocess
from datetime import datetime

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VOICE_DIR = os.path.abspath("memory/reality/media/voice")
VOICE_SAMPLES_DIR = os.path.join(SCRIPT_DIR, "voice_samples")
MODEL_DIR = os.path.join(SCRIPT_DIR, "models")


def ensure_dirs():
    """Ensure voice directories exist."""
    os.makedirs(VOICE_DIR, exist_ok=True)
    os.makedirs(VOICE_SAMPLES_DIR, exist_ok=True)


def check_models():
    """Check if models are downloaded."""
    config_path = os.path.join(MODEL_DIR, "config.json")
    if not os.path.exists(config_path):
        # Try to download models
        print("Models not found. Attempting to download...")
        download_script = os.path.join(SCRIPT_DIR, "download_voice_models.py")
        try:
            result = subprocess.run(
                [sys.executable, download_script],
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode != 0:
                return False, "Failed to download models: " + result.stderr
        except Exception as e:
            return False, f"Error downloading models: {e}"
    return True, None


def generate_speech(
    text: str,
    voice_sample: str = None,
    pitch: float = 0.0,
    speed: float = 1.0,
    emotional_intensity: float = 0.5,
    output_format: str = "wav"
) -> dict:
    """
    Generate speech using Chatterbox-Turbo.

    Args:
        text: Text to speak
        voice_sample: Optional path to voice sample for cloning
        pitch: Pitch adjustment (-1.0 to 1.0)
        speed: Speed adjustment (0.5 to 2.0)
        emotional_intensity: Emotional intensity (0.0 to 1.0)
        output_format: Output format (wav, mp3)

    Returns:
        Dict with success status, audio path, and metadata
    """
    ensure_dirs()

    # Check models
    models_ok, error = check_models()
    if not models_ok:
        return {"success": False, "error": error}

    # Output filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_filename = f"voice_{timestamp}.{output_format}"
    output_path = os.path.join(VOICE_DIR, output_filename)

    # Build command
    cmd = [
        sys.executable, "-c", f"""
import os
import torch
from chatterbox import Chatterbox

# Load model
model = Chatterbox.load_from_checkpoint("{MODEL_DIR}")

# Prepare text
text = """{text.replace('"', '\\"')}"""

# Prepare kwargs
kwargs = {{
    "text": text,
    "pitch_adjustment": {pitch},
    "speed_adjustment": {speed},
    "emotion_weight": {emotional_intensity},
}}

# Add voice sample if provided
{"if voice_sample:" in str(voice_sample) and "voice_sample" in str(voice_sample)}
    # For voice cloning, we would load the sample here
    # Note: Chatterbox-Turbo may require specific voice sample handling

# Generate
audio = model.generate(**kwargs)

# Save
audio.export("{output_path}", format="{output_format}")
print("SUCCESS")
"""
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0 and "SUCCESS" in result.stdout:
            return {
                "success": True,
                "url": f"/media/voice/{output_filename}",
                "path": output_path,
                "text": text,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "error": result.stderr or "Generation failed"
            }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Generation timed out (may need GPU or quantization)"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def generate_simple(text: str, settings: dict = None) -> dict:
    """
    Simplified generation with default settings.
    Falls back to alternative TTS if Chatterbox fails.
    """
    if settings is None:
        settings = {
            "pitch": 0.0,
            "speed": 1.0,
            "emotional_intensity": 0.5
        }

    # Try Chatterbox first
    result = generate_speech(
        text,
        pitch=settings.get("pitch", 0.0),
        speed=settings.get("speed", 1.0),
        emotional_intensity=settings.get("emotional_intensity", 0.5)
    )

    if result.get("success"):
        return result

    # Fallback: Use gTTS or edge-tts if available
    print(f"Chatterbox failed, trying fallback TTS: {result.get('error')}")
    return generate_fallback_tts(text, settings)


def generate_fallback_tts(text: str, settings: dict = None) -> dict:
    """
    Fallback TTS using edge-tts or gTTS.
    """
    ensure_dirs()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_filename = f"voice_{timestamp}.mp3"
    output_path = os.path.join(VOICE_DIR, output_filename)

    # Try edge-tts
    try:
        import asyncio
        import edge_tts

        async def generate():
            communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
            await communicate.save(output_path)

        asyncio.run(generate())

        return {
            "success": True,
            "url": f"/media/voice/{output_filename}",
            "path": output_path,
            "text": text,
            "provider": "edge-tts",
            "timestamp": datetime.now().isoformat()
        }
    except ImportError:
        pass
    except Exception as e:
        pass

    # Try gTTS
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang="en")
        tts.save(output_path)
        return {
            "success": True,
            "url": f"/media/voice/{output_filename}",
            "path": output_path,
            "text": text,
            "provider": "gtts",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"All TTS methods failed: {e}"
        }


def main():
    # Handle --upload-sample flag
    if len(sys.argv) >= 3 and sys.argv[1] == "--upload-sample":
        sample_path = sys.argv[2]
        if not os.path.exists(sample_path):
            print(json.dumps({"success": False, "error": "Sample file not found"}))
            sys.exit(1)

        # Copy to voice_samples directory
        sample_name = os.path.basename(sample_path)
        dest_path = os.path.join(VOICE_SAMPLES_DIR, sample_name)

        try:
            import shutil
            shutil.copy2(sample_path, dest_path)
            print(json.dumps({
                "success": True,
                "sample_name": sample_name,
                "sample_path": dest_path,
                "message": "Voice sample saved for cloning"
            }))
        except Exception as e:
            print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(0)

    if len(sys.argv) < 2:
        print(json.dumps({"error": "Params required"}))
        sys.exit(1)

    params = json.loads(sys.argv[1])
    text = params.get("text", "")

    if not text:
        print(json.dumps({"error": "Text is required"}))
        sys.exit(1)

    result = generate_simple(
        text,
        settings=params.get("settings", {})
    )

    print(json.dumps(result))


if __name__ == "__main__":
    main()
