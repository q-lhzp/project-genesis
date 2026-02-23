#!/usr/bin/env python3
# ///
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.0.0",
#     "pillow>=10.0.0",
# ]
# ///
"""
Q's Image Generation Script
Supports multiple providers:
- Venice.ai (z-image-turbo) - BEST for photorealistic
- OpenAI DALL-E 3 (dall-e-3)
- Google Gemini (gemini-2.0-flash-exp-image-generation) - via API
- xAI Grok (grok-imagine-image-pro) - fallback
- Flux (via fal.ai) - optional
- Nano Banana Pro (gemini-3-pro-image) - via uv run --script
"""
import os
import sys
import base64
import argparse
from datetime import datetime

# Config - API Keys
VENICE_API_KEY = os.environ.get("VENICE_INFERENCE_KEY", "")
XAI_API_KEY = os.environ.get("XAI_API_KEY", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
# Gemini: Needs Google AI Studio key with image generation permissions (not standard API key)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")  # Only works with special image-gen enabled keys
FAL_API_KEY = os.environ.get("FAL_API_KEY", "")

# Try to import openai
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

NANO_BANANA_SCRIPT = os.path.expanduser("~/.npm-global/lib/node_modules/openclaw/skills/nano-banana-pro/scripts/generate_image.py")

def generate_venice(prompt: str, output_path: str, size: str = "1024x1024") -> bool:
    """Generate image using Venice.ai z-image-turbo"""
    if not HAS_OPENAI:
        print("ERROR: openai package required for Venice.ai", file=sys.stderr)
        return False
    
    try:
        client = OpenAI(api_key=VENICE_API_KEY, base_url="https://api.venice.ai/api/v1")
        response = client.images.generate(
            model="z-image-turbo",
            prompt=prompt,
            size=size,
            response_format="b64_json"
        )
        with open(output_path, "wb") as f:
            f.write(base64.b64decode(response.data[0].b64_json))
        print(f"SUCCESS: Venice.ai image saved to {output_path}")
        return True
    except Exception as e:
        print(f"ERROR: Venice.ai failed: {e}", file=sys.stderr)
        return False

def generate_dalle(prompt: str, output_path: str, size: str = "1024x1024") -> bool:
    """Generate image using OpenAI DALL-E 3"""
    if not HAS_OPENAI or not OPENAI_API_KEY:
        print("ERROR: OpenAI API key required for DALL-E", file=sys.stderr)
        return False
    
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality="standard",
            n=1
        )
        # DALL-E returns URL, need to download
        import urllib.request
        img_url = response.data[0].url
        with urllib.request.urlopen(img_url) as resp:
            with open(output_path, "wb") as f:
                f.write(resp.read())
        print(f"SUCCESS: DALL-E 3 image saved to {output_path}")
        return True
    except Exception as e:
        print(f"ERROR: DALL-E failed: {e}", file=sys.stderr)
        return False

def generate_gemini(prompt: str, output_path: str) -> bool:
    """Generate image using Google Gemini (via OpenAI-compatible API)"""
    if not HAS_OPENAI or not GEMINI_API_KEY:
        print("ERROR: GEMINI_API_KEY required for Gemini", file=sys.stderr)
        return False
    
    try:
        # Gemini uses OpenAI-compatible API
        client = OpenAI(
            api_key=GEMINI_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        response = client.images.generate(
            model="gemini-2.0-flash-exp-image-generation",
            prompt=prompt,
            size="1024x1024",
            response_format="b64_json"
        )
        with open(output_path, "wb") as f:
            f.write(base64.b64decode(response.data[0].b64_json))
        print(f"SUCCESS: Gemini image saved to {output_path}")
        return True
    except Exception as e:
        print(f"ERROR: Gemini failed: {e}", file=sys.stderr)
        return False

def generate_grok(prompt: str, output_path: str) -> bool:
    """Generate image using xAI Grok (grok-imagine-image-pro)"""
    import urllib.request
    import json
    
    url = "https://api.x.ai/v1/images/generations"
    payload = {
        "model": "grok-imagine-image-pro",
        "prompt": prompt,
        "response_format": "url"
    }
    
    data = bytes(json.dumps(payload), 'utf-8')
    req = urllib.request.Request(
        url, data=data,
        headers={
            "Authorization": f"Bearer {XAI_API_KEY}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            result = json.load(response)
            image_url = result["data"][0]["url"]
            img_req = urllib.request.Request(image_url)
            with urllib.request.urlopen(img_req) as img_response:
                with open(output_path, "wb") as f:
                    f.write(img_response.read())
        print(f"SUCCESS: xAI Grok image saved to {output_path}")
        return True
    except Exception as e:
        print(f"ERROR: xAI Grok failed: {e}", file=sys.stderr)
        return False

def generate_flux(prompt: str, output_path: str) -> bool:
    """Generate image using Flux via fal.ai"""
    import urllib.request
    import json
    
    if not FAL_API_KEY:
        print("ERROR: FAL_API_KEY required for Flux (get from fal.ai)", file=sys.stderr)
        return False
    
    # Use fal.ai Flux API
    url = "https://queue.fal.run/fal-ai/flux-pro"
    payload = {
        "prompt": prompt,
        "image_size": {"width": 1024, "height": 1024},
        "num_inference_steps": 28,
        "guidance_scale": 3.5
    }
    
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode('utf-8'),
        headers={
            "Authorization": f"Key {FAL_API_KEY}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    
    try:
        # Submit request
        with urllib.request.urlopen(req) as response:
            result = json.load(response)
            request_id = result["request_id"]
        
        # Poll for result
        import time
        status_url = f"https://queue.fal.run/fal-ai/flux-pro/requests/{request_id}"
        for _ in range(60):
            time.sleep(2)
            status_req = urllib.request.Request(status_url, headers={"Authorization": f"Key {FAL_API_KEY}"})
            with urllib.request.urlopen(status_req) as resp:
                status = json.load(resp)
                if status.get("status") == "COMPLETED":
                    img_url = status["images"][0]["url"]
                    # Download
                    img_req = urllib.request.Request(img_url)
                    with urllib.request.urlopen(img_req) as img_resp:
                        with open(output_path, "wb") as f:
                            f.write(img_resp.read())
                    print(f"SUCCESS: Flux image saved to {output_path}")
                    return True
                elif status.get("status") == "FAILED":
                    print("ERROR: Flux generation failed", file=sys.stderr)
                    return False
        
        print("ERROR: Flux timeout", file=sys.stderr)
        return False
    except Exception as e:
        print(f"ERROR: Flux failed: {e}", file=sys.stderr)
        return False

def generate_nano_banana(prompt: str, output_path: str, resolution: str = "1K") -> bool:
    """Generate image using Nano Banana Pro via uv run --script"""
    import subprocess
    
    if not os.path.exists(NANO_BANANA_SCRIPT):
        print(f"ERROR: Nano Banana script not found at {NANO_BANANA_SCRIPT}", file=sys.stderr)
        return False
    
    if not GEMINI_API_KEY:
        print("ERROR: GEMINI_API_KEY required for Nano Banana Pro", file=sys.stderr)
        return False
    
    try:
        # Use uv run --script as discovered
        cmd = [
            "uv", "run", "--script", NANO_BANANA_SCRIPT,
            "-p", prompt,
            "-f", output_path,
            "-r", resolution,
            "-k", GEMINI_API_KEY
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        
        if result.returncode == 0:
            print(f"SUCCESS: Nano Banana Pro image saved to {output_path}")
            return True
        else:
            print(f"ERROR: Nano Banana failed: {result.stderr}", file=sys.stderr)
            return False
    except subprocess.TimeoutExpired:
        print("ERROR: Nano Banana timed out", file=sys.stderr)
        return False
    except Exception as e:
        print(f"ERROR: Nano Banana failed: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="Q's Multi-Provider Image Generator")
    parser.add_argument("--prompt", "-p", required=True, help="Image prompt")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--provider", choices=["venice", "dalle", "gemini", "grok", "flux", "nano", "auto"], 
                       default="auto", help="Image provider")
    parser.add_argument("--size", "-s", default="1024x1024", help="Image size")
    parser.add_argument("--resolution", "-r", choices=["1K", "2K", "4K"], default="1K", 
                       help="Resolution for Nano Banana")
    
    args = parser.parse_args()
    
    # Generate output path
    output = args.output or f"/tmp/q_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    
    success = False
    
    if args.provider == "auto":
        # Try in order of quality preference
        providers = ["venice", "dalle", "gemini", "grok"]
        for p in providers:
            if p == "venice" and HAS_OPENAI:
                success = generate_venice(args.prompt, output, args.size)
            elif p == "dalle" and HAS_OPENAI and OPENAI_API_KEY:
                success = generate_dalle(args.prompt, output, args.size)
            elif p == "gemini" and HAS_OPENAI and GEMINI_API_KEY:
                success = generate_gemini(args.prompt, output)
            elif p == "grok":
                success = generate_grok(args.prompt, output)
            if success:
                break
    
    elif args.provider == "venice":
        success = generate_venice(args.prompt, output, args.size)
    elif args.provider == "dalle":
        success = generate_dalle(args.prompt, output, args.size)
    elif args.provider == "gemini":
        success = generate_gemini(args.prompt, output)
    elif args.provider == "grok":
        success = generate_grok(args.prompt, output)
    elif args.provider == "flux":
        success = generate_flux(args.prompt, output)
    elif args.provider == "nano":
        success = generate_nano_banana(args.prompt, output, args.resolution)
    
    if success:
        print(f"MEDIA: {output}")
        return 0
    else:
        print("All providers failed or not configured.", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
