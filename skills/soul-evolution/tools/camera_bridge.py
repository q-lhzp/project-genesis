import sys
import json
import subprocess
import os
from datetime import datetime

# Paths
IMAGE_GEN_SCRIPT = "/home/leo/Schreibtisch/q-image-gen/scripts/generate_image.py"
PHOTO_DIR = os.path.abspath("memory/reality/photos")

def build_prompt(params, physique, identity, wardrobe):
    """
    Builds a highly detailed photorealistic prompt.
    """
    # 1. Physical Base (from Identity Manifest)
    # We look for [VISUAL] section in IDENTITY.md or use defaults
    visual_base = identity.get("visual_description", "A beautiful young woman")
    
    # 2. Current Outfit
    outfit = physique.get("current_outfit", ["casual clothes"])
    outfit_str = ", ".join(outfit)
    
    # 3. Location & Context
    location = physique.get("current_location", "at home")
    action = params.get("action_description", "posing for a photo")
    
    # 4. Photo Type
    photo_type = params.get("type", "selfie")
    style_suffix = "shot on iPhone 15 Pro, amateur mobile photography, natural lighting, high detail, realistic skin texture"
    
    if photo_type == "mirror":
        action = "taking a mirror selfie in a bathroom, phone visible in hand, reflection in mirror"
    elif photo_type == "candid":
        action = "captured in a natural moment, not looking at camera"
    
    prompt = f"Highly detailed photorealistic {photo_type}, {visual_base}, wearing {outfit_str}, {action}, {location}, {style_suffix}"
    return prompt

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Params required"}))
        sys.exit(1)

    params = json.loads(sys.argv[1])
    
    # Load state data from caller (provided via JSON string)
    physique = params.get("physique", {})
    identity = params.get("identity_visual", {})
    
    # Build prompt
    prompt = build_prompt(params, physique, identity, {})
    
    # Output path
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_filename = f"photo_{timestamp}.png"
    output_path = os.path.join(PHOTO_DIR, output_filename)
    os.makedirs(PHOTO_DIR, exist_ok=True)
    
    # Call image generator
    cmd = [
        "python3", IMAGE_GEN_SCRIPT,
        "--prompt", prompt,
        "--output", output_path,
        "--provider", "nano" # Default to Nano for quality
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
