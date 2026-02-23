import sys
import json
import subprocess
import os
from datetime import datetime

# Paths (Relative to this script's location)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_GEN_SCRIPT = os.path.join(SCRIPT_DIR, "vision", "generate_image.py")
PHOTO_DIR = os.path.abspath("memory/reality/photos")
NPC_PHOTO_DIR = os.path.abspath("memory/reality/photos/npc")

def ensure_dirs():
    """Ensure photo directories exist."""
    os.makedirs(PHOTO_DIR, exist_ok=True)
    os.makedirs(NPC_PHOTO_DIR, exist_ok=True)

def build_prompt(params, physique, identity, wardrobe, npcs=None):
    """
    Builds a highly detailed photorealistic prompt.
    Supports multi-subject photography with NPCs.
    """
    # 1. Physical Base (from Identity Manifest)
    visual_base = identity.get("visual_description", "A beautiful young woman")

    # 2. Current Outfit
    outfit = physique.get("current_outfit", ["casual clothes"])
    outfit_str = ", ".join(outfit)

    # 3. Location & Context
    location = physique.get("current_location", "at home")
    action = params.get("action_description", "posing for a photo")

    # 4. Photo Type & Aesthetics
    photo_type = params.get("type", "selfie")

    # Cinematic parameters from Q's best practices
    aesthetic = "shot on 35mm fujifilm, depth of field, natural skin texture, highly detailed, 8k, raw photo, realistic imperfections"
    lighting = "cinematic lighting, soft shadows, natural highlights"

    if photo_type == "mirror":
        action = "taking a mirror selfie in a bathroom, phone visible in hand, reflection in mirror"
    elif photo_type == "candid":
        action = "captured in a natural moment, not looking at camera"

    # 5. Multi-Subject: Include NPCs if present
    npc_descriptions = []
    if npcs and isinstance(npcs, list):
        for npc in npcs:
            if npc.get("visual_description"):
                npc_name = npc.get("name", "person")
                npc_vis = npc.get("visual_description")
                npc_descriptions.append(f"{npc_name}: {npc_vis}")

    # Build final prompt
    if npc_descriptions:
        # Multi-subject photo: combine main character with NPCs
        npc_str = ", ".join(npc_descriptions)
        prompt = f"Highly detailed photorealistic group {photo_type}, {visual_base}, wearing {outfit_str}, {action}, {location}, together with: {npc_str}, {aesthetic}, {lighting}"
    else:
        prompt = f"Highly detailed photorealistic {photo_type}, {visual_base}, wearing {outfit_str}, {action}, {location}, {aesthetic}, {lighting}"

    return prompt

def generate_npc_portrait(npc_name, visual_description, provider="nano"):
    """
    Generate and save a portrait for an NPC.
    Returns the path to the generated image.
    """
    ensure_dirs()

    # Clean name for filename
    safe_name = "".join(c for c in npc_name if c.isalnum() or c in "_-").lower()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_filename = f"npc_{safe_name}_{timestamp}.png"
    output_path = os.path.join(NPC_PHOTO_DIR, output_filename)

    # Build portrait prompt (close-up, portrait style)
    aesthetic = "professional portrait photography, studio lighting, head and shoulders, natural skin texture, highly detailed, 8k, raw photo"
    prompt = f"Highly detailed photorealistic portrait, {visual_description}, {aesthetic}, cinematic lighting"

    # Call image generator
    cmd = [
        "python3", IMAGE_GEN_SCRIPT,
        "--prompt", prompt,
        "--output", output_path,
        "--provider", provider
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            return {
                "success": True,
                "url": f"/media/photos/npc/{output_filename}",
                "path": output_path
            }
        else:
            return {
                "success": False,
                "error": result.stderr
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Params required"}))
        sys.exit(1)

    params = json.loads(sys.argv[1])

    # Load state data from caller
    physique = params.get("physique", {})
    identity = params.get("identity_visual", {})
    provider = params.get("provider", "nano")
    npcs = params.get("npcs", [])  # Phase 19: List of NPCs for multi-subject photos

    # Build prompt with NPCs
    prompt = build_prompt(params, physique, identity, {}, npcs)

    # Output path
    ensure_dirs()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_filename = f"photo_{timestamp}.png"
    output_path = os.path.join(PHOTO_DIR, output_filename)
    
    # Call image generator
    cmd = [
        "python3", IMAGE_GEN_SCRIPT,
        "--prompt", prompt,
        "--output", output_path,
        "--provider", provider
    ]
    
    try:
        print(f"Executing: {' '.join(cmd)}", file=sys.stderr)
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(json.dumps({
                "success": True,
                "url": f"/media/photos/{output_filename}",
                "path": output_path,
                "prompt": prompt
            }))
        else:
            print(json.dumps({"error": result.stderr}))
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()
