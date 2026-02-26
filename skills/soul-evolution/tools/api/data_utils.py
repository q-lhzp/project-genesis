import json
import os
import re
import glob

def parse_soul_md(content: str) -> list:
    nodes = []
    current_section = None
    current_subsection = None
    for line in content.split("\n"):
        line_stripped = line.strip()
        if not line_stripped or line_stripped.startswith(">") or line_stripped == "---": continue
        if line_stripped.startswith("# SOUL") or line_stripped.startswith("_This file"): continue
        if line_stripped.startswith("## "):
            current_section = line_stripped
            nodes.append({"type": "section", "text": line_stripped.replace("## ", ""), "raw": line_stripped, "children": []})
        elif line_stripped.startswith("### "):
            current_subsection = line_stripped
            if nodes:
                nodes[-1]["children"].append({"type": "subsection", "text": line_stripped.replace("### ", ""), "raw": line_stripped, "children": []})
        elif line_stripped.startswith("- "):
            tag = "CORE" if "[CORE]" in line_stripped else ("MUTABLE" if "[MUTABLE]" in line_stripped else "untagged")
            text = re.sub(r'\s*\[(CORE|MUTABLE)\]\s*', '', line_stripped[2:].strip()).strip()
            bullet = {"type": "bullet", "text": text, "raw": line_stripped, "tag": tag, "section": current_section, "subsection": current_subsection}
            if nodes and nodes[-1]["children"] and nodes[-1]["children"][-1]["type"] == "subsection":
                nodes[-1]["children"][-1]["children"].append(bullet)
            elif nodes: nodes[-1]["children"].append(bullet)
    return nodes

def load_json(fp):
    if not os.path.exists(fp): return {}
    try:
        with open(fp, "r") as f: return json.load(f)
    except: return {}

def load_jsonl(fp):
    items = []
    if not os.path.exists(fp): return items
    try:
        with open(fp, "r") as f:
            for line in f:
                if line.strip():
                    try: items.append(json.loads(line))
                    except: pass
    except: pass
    return items

def collect_data(workspace: str) -> dict:
    memory_dir = os.path.join(workspace, "memory")
    reality_dir = os.path.join(memory_dir, "reality")
    
    soul_path = os.path.join(workspace, "SOUL.md")
    soul_content = ""
    if os.path.exists(soul_path):
        with open(soul_path, "r") as f: soul_content = f.read()
    
    data = {
        "soul_tree": parse_soul_md(soul_content),
        "identity_raw": soul_content,
        "changes": load_jsonl(os.path.join(memory_dir, "soul_changes.jsonl")),
        "experiences": [],
        "reflections": load_jsonl(os.path.join(memory_dir, "reflections.jsonl")),
        "proposals_pending": load_jsonl(os.path.join(memory_dir, "proposals", "pending.jsonl")),
        "significant": load_jsonl(os.path.join(memory_dir, "significant", "significant.jsonl")),
        "physique": load_json(os.path.join(reality_dir, "physique.json")),
        "interests": load_json(os.path.join(reality_dir, "interests.json")),
        "world_state": load_json(os.path.join(reality_dir, "world_state.json")),
        "reputation": load_json(os.path.join(reality_dir, "reputation.json")),
        "news": load_json(os.path.join(reality_dir, "news.json")),
        "social_events": load_json(os.path.join(reality_dir, "social_events.json")),
        "vault_state": load_json(os.path.join(reality_dir, "vault_state.json")),
        "interior": load_json(os.path.join(reality_dir, "interior.json")),
        "inventory": load_json(os.path.join(reality_dir, "inventory.json")),
        "wardrobe": load_json(os.path.join(reality_dir, "wardrobe.json")),
        "skills": load_json(os.path.join(reality_dir, "skills.json")),
        "photos": [os.path.basename(f) for f in glob.glob(os.path.join(reality_dir, "photos", "*.png"))],
        "system_config": {"openai_ok": True, "anthropic_ok": True}
    }

    exp_dir = os.path.join(memory_dir, "experiences")
    if os.path.isdir(exp_dir):
        for fp in sorted(glob.glob(os.path.join(exp_dir, "*.jsonl")))[-7:]:
            data["experiences"].extend(load_jsonl(fp))
            
    return data
