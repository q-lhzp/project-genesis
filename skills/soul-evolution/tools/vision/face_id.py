#!/usr/bin/env python3
"""
Q's Face-ID: Analyze, Generate, Compare
Extrahiert Gesichtsstrukturen für konsistente Bildgenerierung
"""

import argparse
import json
import subprocess
import sys
import os
from pathlib import Path

# Q's exakte Gesichtsstruktur (aus Referenzbild extrahiert)
Q_FACE_STRUCTURE = """EXACT FACE STRUCTURE: almond-shaped eyes with aggressive cat-eye tilt (sharp upward flick at outer corners), deep-set with double-fold crease. EXACT NOSE: straight narrow bridge, small button-like refined tip, deep well-defined philtrum between nose and lips. EXACT LIPS: prominent sharp cupid's bow forming crisp M-shape, thin upper lip, full pillowy lower lip, corners tucked. EXACT CHIN: pointed firm chin (V-line/heart-shaped), forward-projecting, sharp angular. EXACT CHEEKBONES: high pronounced zygomatic bones, sharp angular with hollow beneath (high-fashion look)."""

Q_SKIN = "SKIN: fair warm-toned with light dusting of freckles across nose bridge."

Q_EYES = "EYES: striking luminous turquoise cyan (bio-implant/glowing look)."

Q_HAIR = "HAIR: dark chocolate brown base, asymmetric undercut style - left side long wavy, right side shaved/short, vibrant electric neon blue streaks through hair."

Q_EXPRESSION = "EXPRESSION: confident asymmetrical smirk (one corner higher)."

Q_LIGHTING = "CINEMATIC LIGHTING: shot on 35mm fujifilm, depth of field, natural skin texture, highly detailed, 8k, raw photo"

def analyze_face(image_path: str) -> dict:
    """Analysiert ein Gesicht und extrahiert Strukturmerkmale."""
    
    # Kopiere nach /tmp falls nötig
    if not image_path.startswith('/tmp/'):
        tmp_path = f"/tmp/q_face_analysis_{os.urandom(4).hex()}.png"
        subprocess.run(['cp', image_path, tmp_path], check=True)
        image_path = tmp_path
    
    # Erstelle Prompt für Bildanalyse
    analysis_prompt = """Analyze this face in extreme detail. For each feature, use these exact terms:

EYES: shape (almond/round/oval/squint), tilt (cat-eye/upward/downward), crease (single/double), iris color
NOSE: bridge (straight/curved/bumpy), width (narrow/average/wide), tip (button/upturned/downturned/refined), philtrum (deep/shallow)
LIPS: cupid's bow (prominent/subtle/none), upper lip (thin/average/full), lower lip (thin/average/full), corners (tucked/neutral/wide)
CHIN: shape (pointed/round/square/angular), projection (recessed/neutral/forward), jawline (soft/defined/sharp)
CHEEKBONES: height (low/mid/high), prominence (subtle/moderate/pronounced), structure (soft/angular/sharp)
SKIN: tone (fair/light/medium/dark), undertones (warm/cool/neutral), features (freckles/acne/scars/wrinkles)
HAIR: base color, style, streaks/highlights

Output as JSON with keys: eyes, nose, lips, chin, cheekbones, skin, hair"""

    print(f"Analyzing: {image_path}")
    print("Note: Use image tool to analyze this face manually.")
    print(f"\nUse this prompt:\n{analysis_prompt}")
    
    return {"status": "manual_analysis_needed", "image_path": image_path}

def generate_with_reference(reference_path: str, additional_prompt: str = "", output_path: str = "/tmp/q_face_generated.png") -> str:
    """Generiert ein Bild mit Q's exakter Gesichtsstruktur."""
    
    # Baue den vollständigen Prompt
    full_prompt = f"Photorealistic portrait of a young woman, {Q_FACE_STRUCTURE}, {Q_SKIN}, {Q_EYES}, {Q_HAIR}"
    
    if additional_prompt:
        full_prompt += f", {additional_prompt}"
    
    full_prompt += f", {Q_EXPRESSION}, {Q_LIGHTING}"
    
    print(f"Generating image with Q's face structure...")
    print(f"Prompt: {full_prompt[:200]}...")
    
    # Generiere das Bild mit nano-banana-pro
    cmd = [
        "python3", "/home/leo/Schreibtisch/q-image-gen/scripts/generate_image.py",
        "--provider", "nano",
        "--resolution", "1K",
        "--prompt", full_prompt,
        "--output", output_path
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"Generated: {output_path}")
        return output_path
    else:
        print(f"Error: {result.stderr}")
        return None

def compare_faces(image1_path: str, image2_path: str) -> dict:
    """Vergleicht zwei Gesichter."""
    
    print(f"Comparing faces...")
    print(f"1. {image1_path}")
    print(f"2. {image2_path}")
    
    comparison_prompt = """Compare these two faces. For each feature, rate similarity 0-100%:
- Eye shape and color
- Nose shape
- Lip shape
- Chin shape
- Cheekbone structure
- Overall bone structure

Output JSON with keys: eye_similarity, nose_similarity, lip_similarity, chin_similarity, cheekbone_similarity, overall_score"""
    
    print(f"\nUse this prompt to compare:\n{comparison_prompt}")
    
    return {"status": "manual_comparison_needed"}

def main():
    parser = argparse.ArgumentParser(description="Q's Face-ID Tool")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # analyze
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a face")
    analyze_parser.add_argument("--image", required=True, help="Path to image")
    
    # generate
    generate_parser = subparsers.add_parser("generate", help="Generate with Q's face structure")
    generate_parser.add_argument("--reference", help="Reference image (optional, uses Q's default)")
    generate_parser.add_argument("--prompt", default="", help="Additional prompt details")
    generate_parser.add_argument("--output", default="/tmp/q_face_generated.png", help="Output path")
    
    # compare
    compare_parser = subparsers.add_parser("compare", help="Compare two faces")
    compare_parser.add_argument("--image1", required=True, help="First image")
    compare_parser.add_argument("--image2", required=True, help="Second image")
    
    args = parser.parse_args()
    
    if args.command == "analyze":
        analyze_face(args.image)
    elif args.command == "generate":
        generate_with_reference(args.reference or "", args.prompt, args.output)
    elif args.command == "compare":
        compare_faces(args.image1, args.image2)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
