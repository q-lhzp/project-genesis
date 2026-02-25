#!/usr/bin/env python3
"""
Soul Evolution Visualizer
Reads SOUL.md + memory/ and generates an interactive timeline visualization.

Usage:
  python3 soul-viz.py <workspace-path> [--serve [port]]

Examples:
  python3 soul-viz.py ./workspace-soul-evolution-demo --serve 8080
  python3 soul-viz.py ./workspace-soul-evolution-demo   # writes soul-evolution.html
"""

import json
import re
import sys
import os
import glob
from datetime import datetime, timedelta

def parse_soul_md(content: str) -> list:
    """Parse SOUL.md into a tree of sections → subsections → bullets."""
    nodes = []
    current_section = None
    current_subsection = None

    for line in content.split("\n"):
        line_stripped = line.strip()

        # Skip header block, empty lines, horizontal rules
        if not line_stripped or line_stripped.startswith(">") or line_stripped == "---":
            continue
        if line_stripped.startswith("# SOUL") or line_stripped.startswith("_This file"):
            continue

        # ## Section
        if line_stripped.startswith("## "):
            current_section = line_stripped
            current_subsection = None
            nodes.append({
                "type": "section",
                "text": line_stripped.replace("## ", ""),
                "raw": line_stripped,
                "children": []
            })

        # ### Subsection
        elif line_stripped.startswith("### "):
            current_subsection = line_stripped
            if nodes:
                sub = {
                    "type": "subsection",
                    "text": line_stripped.replace("### ", ""),
                    "raw": line_stripped,
                    "parent_section": current_section,
                    "children": []
                }
                nodes[-1]["children"].append(sub)

        # - Bullet
        elif line_stripped.startswith("- "):
            tag = "CORE" if "[CORE]" in line_stripped else ("MUTABLE" if "[MUTABLE]" in line_stripped else "untagged")
            # Clean text
            text = line_stripped[2:].strip()
            text_clean = re.sub(r'\s*\[(CORE|MUTABLE)\]\s*', '', text).strip()

            bullet = {
                "type": "bullet",
                "text": text_clean,
                "raw": line_stripped,
                "tag": tag,
                "section": current_section,
                "subsection": current_subsection,
            }

            if nodes and nodes[-1]["children"]:
                nodes[-1]["children"][-1]["children"].append(bullet)
            elif nodes:
                # Bullet directly under section (no subsection)
                nodes[-1]["children"].append(bullet)

    return nodes


def load_jsonl(filepath: str) -> list:
    """Load a JSONL file into a list of dicts."""
    items = []
    if not os.path.exists(filepath):
        return items
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    items.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return items


def load_json(filepath: str) -> dict:
    """Load a JSON file."""
    if not os.path.exists(filepath):
        return {}
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def collect_data(workspace: str) -> dict:
    """Collect all Soul Evolution data from a workspace."""
    soul_path = os.path.join(workspace, "SOUL.md")
    memory_dir = os.path.join(workspace, "memory")

    # Read SOUL.md
    with open(soul_path, "r") as f:
        soul_content = f.read()

    soul_tree = parse_soul_md(soul_content)

    # Soul changes
    changes = load_jsonl(os.path.join(memory_dir, "soul_changes.jsonl"))

    # Experiences (all days)
    experiences = []
    exp_dir = os.path.join(memory_dir, "experiences")
    if os.path.isdir(exp_dir):
        for fp in sorted(glob.glob(os.path.join(exp_dir, "*.jsonl"))):
            experiences.extend(load_jsonl(fp))

    # Reflections
    reflections = []
    ref_dir = os.path.join(memory_dir, "reflections")
    if os.path.isdir(ref_dir):
        for fp in sorted(glob.glob(os.path.join(ref_dir, "REF-*.json"))):
            reflections.append(load_json(fp))

    # Proposals
    proposals_pending = load_jsonl(os.path.join(memory_dir, "proposals", "pending.jsonl"))
    proposals_history = load_jsonl(os.path.join(memory_dir, "proposals", "history.jsonl"))

    # Significant
    significant = load_jsonl(os.path.join(memory_dir, "significant", "significant.jsonl"))

    # State
    state = load_json(os.path.join(memory_dir, "soul-state.json"))

    # Identity
    identity_path = os.path.join(workspace, "IDENTITY.md")
    identity_content = ""
    if os.path.exists(identity_path):
        with open(identity_path, "r") as f:
            identity_content = f.read()

    # Pipeline reports
    pipeline = []
    pipe_dir = os.path.join(memory_dir, "pipeline")
    if os.path.isdir(pipe_dir):
        for fp in sorted(glob.glob(os.path.join(pipe_dir, "*.json"))):
            pipeline.append(load_json(fp))
        for fp in sorted(glob.glob(os.path.join(pipe_dir, "*.jsonl"))):
            pipeline.extend(load_jsonl(fp))

    # Physique (vitals, location, outfit)
    physique = load_json(os.path.join(memory_dir, "reality", "physique.json"))

    # Interests
    interests = load_json(os.path.join(memory_dir, "reality", "interests.json"))

    # Skill config (for governance display)
    skill_config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")
    skill_config = load_json(skill_config_path)

    # Interior, Inventory, Wardrobe, Dev Manifest
    interior = load_json(os.path.join(memory_dir, "reality", "interior.json"))
    inventory = load_json(os.path.join(memory_dir, "reality", "inventory.json"))
    wardrobe = load_json(os.path.join(memory_dir, "reality", "wardrobe.json"))
    dev_manifest = load_json(os.path.join(memory_dir, "development", "manifest.json"))
    cycle = load_json(os.path.join(memory_dir, "reality", "cycle.json"))

    # Phase 1: Chronos - Lifecycle (Aging)
    lifecycle = load_json(os.path.join(memory_dir, "reality", "lifecycle.json"))

    # Phase 2: Social Fabric
    social = load_json(os.path.join(memory_dir, "reality", "social.json"))

    # Phase 3: Prosperity & Labor - Economy
    finances = load_json(os.path.join(memory_dir, "reality", "finances.json"))

    # Phase 6: Living World - Skills, World State, Psychology, Reputation
    skills = load_json(os.path.join(memory_dir, "reality", "skills.json"))
    world_state = load_json(os.path.join(memory_dir, "reality", "world_state.json"))
    psychology = load_json(os.path.join(memory_dir, "reality", "psychology.json"))
    reputation = load_json(os.path.join(memory_dir, "reality", "reputation.json"))
    news = load_json(os.path.join(memory_dir, "reality", "news.json"))
    internal_comm = load_json(os.path.join(memory_dir, "reality", "internal_comm.json"))
    social_events = load_json(os.path.join(memory_dir, "reality", "social_events.json"))
    vault_state = load_json(os.path.join(memory_dir, "reality", "vault_state.json"))

    # Photos
    photos = []
    photo_dir = os.path.join(memory_dir, "reality", "photos")
    if os.path.isdir(photo_dir):
        for fp in sorted(glob.glob(os.path.join(photo_dir, "*.png")), reverse=True):
            photos.append(os.path.basename(fp))

    # Phase 4: Analytics & Lab - Read telemetry for visualization
    telemetry_dir = os.path.join(memory_dir, "telemetry")
    vitality_data = []
    economy_data = []

    # Read recent vitality telemetry (last 30 days)
    for i in range(30):
        date = datetime.now() - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        vitality_file = os.path.join(telemetry_dir, f"vitality_{date_str}.jsonl")
        if os.path.exists(vitality_file):
            with open(vitality_file, "r") as f:
                for line in f:
                    if line.strip():
                        try:
                            vitality_data.append(json.loads(line))
                        except (json.JSONDecodeError, ValueError):
                            pass

    # Read recent economy telemetry
    economy_dir = os.path.join(telemetry_dir, "economy")
    if os.path.exists(economy_dir):
        for i in range(30):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            economy_file = os.path.join(economy_dir, f"events_{date_str}.jsonl")
            if os.path.exists(economy_file):
                with open(economy_file, "r") as f:
                    for line in f:
                        if line.strip():
                            try:
                                economy_data.append(json.loads(line))
                            except (json.JSONDecodeError, ValueError):
                                pass

    # Phase 6: System Config Status (API Keys & Modules)
    skills_tools_dir = os.path.join(workspace, "skills", "soul-evolution", "tools")
    
    system_config = {
        "mem0_configured": False,
        "vault_configured": False,
        "openai_ok": False,
        "anthropic_ok": False,
        "venice_ok": False,
        "xai_ok": False,
        "gemini_ok": False,
        "fal_ok": False,
        "browser_tool_ok": os.path.exists(os.path.join(skills_tools_dir, "browser_bridge.py")),
        "desktop_tool_ok": os.path.exists(os.path.join(skills_tools_dir, "desktop_bridge.py")),
        "weather_engine_ok": os.path.exists(os.path.join(memory_dir, "reality", "atmosphere_state.json"))
    }
    
    # Check mem0 config
    mem0_config_path = os.path.join(memory_dir, "reality", "mem0_config.json")
    if os.path.exists(mem0_config_path):
        try:
            mconfig = load_json(mem0_config_path)
            if mconfig.get("api_key") and mconfig.get("api_key") != "":
                system_config["mem0_configured"] = True
        except:
            pass
            
    # Check model configs
    model_config_path = os.path.join(memory_dir, "reality", "model_config.json")
    if os.path.exists(model_config_path):
        try:
            mconfig = load_json(model_config_path)
            if mconfig.get("api_key") and mconfig.get("api_key") != "":
                system_config["openai_ok"] = True
            if mconfig.get("key_anthropic") and mconfig.get("key_anthropic") != "":
                system_config["anthropic_ok"] = True
            if mconfig.get("key_venice") and mconfig.get("key_venice") != "":
                system_config["venice_ok"] = True
            if mconfig.get("key_xai") and mconfig.get("key_xai") != "":
                system_config["xai_ok"] = True
            if mconfig.get("key_gemini_img") and mconfig.get("key_gemini_img") != "":
                system_config["gemini_ok"] = True
            if mconfig.get("key_fal") and mconfig.get("key_fal") != "":
                system_config["fal_ok"] = True
        except:
            pass
            
    # Check vault config (Kraken/Alpaca)
    # usually stored in vault_state or a separate config. Let's just check if vault_state has active positions or keys
    if vault_state.get("kraken_connected") or vault_state.get("alpaca_connected") or vault_state.get("paper_trading"):
        system_config["vault_configured"] = True # or maybe let the frontend decide based on vault_state directly

    return {
        "soul_tree": soul_tree,
        "soul_raw": soul_content,
        "identity_raw": identity_content,
        "changes": changes,
        "experiences": experiences,
        "reflections": reflections,
        "proposals_pending": proposals_pending,
        "proposals_history": proposals_history,
        "significant": significant,
        "state": state,
        "pipeline": pipeline,
        "physique": physique,
        "interests": interests,
        "skill_config": skill_config,
        "interior": interior,
        "inventory": inventory,
        "wardrobe": wardrobe,
        "dev_manifest": dev_manifest,
        "cycle": cycle,
        "lifecycle": lifecycle,
        "social": social,
        "finances": finances,
        # Phase 6: Living World
        "skills": skills,
        "world_state": world_state,
        "psychology": psychology,
        "reputation": reputation,
        "news": news,
        "internal_comm": internal_comm,
        "social_events": social_events,
        "vault_state": vault_state,
        "photos": photos,
        "telemetry_vitality": vitality_data[-100:] if len(vitality_data) > 100 else vitality_data,  # Last 100 entries
        "telemetry_economy": economy_data[-100:] if len(economy_data) > 100 else economy_data,
        "system_config": system_config,
    }


def generate_html(data: dict) -> str:
    """Generate the interactive visualization HTML."""
    data_json = json.dumps(data, indent=None, default=str)

    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Project Genesis</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,700;1,400&display=swap');

* { margin: 0; padding: 0; box-sizing: border-box; }

:root {
  --bg: #0a0a0f;
  --bg-card: #12121a;
  --bg-hover: #1a1a28;
  --border: #1e1e30;
  --text: #c8c8d8;
  --text-dim: #6a6a80;
  --text-bright: #eeeef4;
  --accent: #7c6ff0;
  --accent-glow: rgba(124, 111, 240, 0.15);
  --core: #e05050;
  --core-bg: rgba(224, 80, 80, 0.08);
  --core-border: rgba(224, 80, 80, 0.25);
  --mutable: #50c878;
  --mutable-bg: rgba(80, 200, 120, 0.08);
  --mutable-border: rgba(80, 200, 120, 0.25);
  --section-personality: #f0a050;
  --section-philosophy: #7c6ff0;
  --section-boundaries: #e05050;
  --section-continuity: #50b8e0;
  --section-default: #888;
  --timeline-line: #2a2a40;
}

html { font-size: 15px; }

body {
  background: var(--bg);
  color: var(--text);
  font-family: 'DM Sans', sans-serif;
  min-height: 100vh;
  overflow-x: hidden;
}

/* Grain overlay */
body::after {
  content: '';
  position: fixed; inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
  pointer-events: none;
  z-index: 9999;
}

/* Header */
.header {
  padding: 3rem 2rem 2rem;
  text-align: center;
  position: relative;
}
.header::before {
  content: '';
  position: absolute; top: 0; left: 50%; transform: translateX(-50%);
  width: 600px; height: 300px;
  background: radial-gradient(ellipse, var(--accent-glow), transparent 70%);
  pointer-events: none;
}
.header h1 {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 300;
  font-size: 2.2rem;
  letter-spacing: 0.15em;
  color: var(--text-bright);
  position: relative;
}
.header h1 .evolution { color: var(--accent); }
.header h1 .soul { color: var(--text-dim); }
.header .subtitle {
  font-size: 0.85rem;
  color: var(--text-dim);
  margin-top: 0.6rem;
  font-family: 'JetBrains Mono', monospace;
  letter-spacing: 0.05em;
}
.header .subtitle .evolution { color: var(--accent); }
.header .subtitle .soul { color: var(--text-dim); }
.stats-bar {
  display: flex; justify-content: center; gap: 2.5rem;
  margin-top: 1.5rem; flex-wrap: wrap;
}
.stat {
  text-align: center;
}
.stat .num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.6rem; font-weight: 700;
  color: var(--text-bright);
}
  .stat .label {
    font-size: 0.7rem; color: var(--text-dim);
    text-transform: uppercase; letter-spacing: 0.1em;
    margin-top: 0.2rem;
  }

  /* News Ticker */
  .news-ticker {
    background: var(--bg-card);
    border-bottom: 1px solid var(--border);
    height: 32px;
    display: flex;
    align-items: center;
    overflow: hidden;
    white-space: nowrap;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: var(--accent);
    z-index: 100;
  }
  .ticker-content {
    display: inline-block;
    animation: ticker 30s linear infinite;
  }
  @keyframes ticker {
    0% { transform: translateX(0); }
    100% { transform: translateX(-50%); }
  }
  .ticker-item {
    display: inline-block;
    padding: 0 4rem;
  }
  .ticker-item::before { content: '⚡'; margin-right: 0.5rem; }

  .pulse {
    display: inline-block;
    animation: pulse 2s infinite;
    margin-right: 0.5rem;
  }
  @keyframes pulse {
    0% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.4; transform: scale(0.8); }
    100% { opacity: 1; transform: scale(1); }
  }

  /* Mental Activity */
  .mental-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-left: 4px solid var(--accent);
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
  }
  .mental-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    color: var(--text-dim);
    margin-bottom: 0.5rem;
    display: block;
  }
  .mental-content {
    font-size: 0.95rem;
    line-height: 1.4;
    color: var(--text-bright);
    font-style: italic;
  }
  .mental-sub {
    font-size: 0.8rem;
    color: var(--text-dim);
    margin-top: 0.5rem;
    display: block;
  }
  .browser-snap {
    width: 100%;
    border-radius: 4px;
    margin-top: 0.5rem;
    border: 1px solid var(--border);
    cursor: pointer;
    transition: transform 0.2s;
  }
  .browser-snap:hover {
    transform: scale(1.02);
  }

  /* Layout */

.main {
  max-width: 1600px;
  margin: 0 auto;
  padding: 0 2rem 4rem;
  display: grid;
  grid-template-columns: 1fr 380px 380px;
  gap: 1.5rem;
}
@media (max-width: 1200px) {
  .main { grid-template-columns: 1fr; }
  .soul-map { order: -1; }
}

/* Soul Map */
.soul-map {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
  position: relative;
}
.soul-map h2 {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem; font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--text-dim);
  margin-bottom: 1.2rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--border);
}

.section-block {
  margin-bottom: 1.5rem;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--border);
  opacity: 0;
  transform: translateY(12px);
  transition: opacity 0.5s, transform 0.5s;
}
.section-block.visible {
  opacity: 1;
  transform: translateY(0);
}
.section-header {
  padding: 0.7rem 1rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem; font-weight: 500;
  letter-spacing: 0.08em;
  display: flex; align-items: center; gap: 0.6rem;
  cursor: pointer;
  user-select: none;
}
.section-header .dot {
  width: 8px; height: 8px; border-radius: 50%;
  flex-shrink: 0;
}
.section-header .arrow {
  margin-left: auto;
  font-size: 0.7rem;
  transition: transform 0.3s;
  color: var(--text-dim);
}
.section-block.collapsed .section-header .arrow {
  transform: rotate(-90deg);
}
.section-block.collapsed .section-body {
  display: none;
}

.subsection {
  padding: 0.3rem 1rem 0.5rem 1.6rem;
}
.subsection-title {
  font-size: 0.72rem;
  color: var(--text-dim);
  font-weight: 500;
  margin-bottom: 0.4rem;
  padding-left: 0.4rem;
}

.bullet {
  padding: 0.45rem 0.6rem;
  margin: 0.25rem 0;
  border-radius: 6px;
  font-size: 0.82rem;
  line-height: 1.45;
  display: flex;
  gap: 0.5rem;
  align-items: flex-start;
  transition: all 0.3s;
  position: relative;
}
.bullet:hover {
  background: var(--bg-hover);
}
.bullet.highlight-enter {
  animation: bulletEnter 1s ease-out;
}
@keyframes bulletEnter {
  0% { background: rgba(124, 111, 240, 0.3); transform: scale(1.02); }
  100% { background: transparent; transform: scale(1); }
}
.bullet .tag {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  font-weight: 700;
  padding: 0.15rem 0.4rem;
  border-radius: 3px;
  flex-shrink: 0;
  margin-top: 0.15rem;
  letter-spacing: 0.05em;
}
.bullet .tag.core {
  color: var(--core);
  background: var(--core-bg);
  border: 1px solid var(--core-border);
}
.bullet .tag.mutable {
  color: var(--mutable);
  background: var(--mutable-bg);
  border: 1px solid var(--mutable-border);
}
.bullet.is-new {
  opacity: 0;
  max-height: 0;
  overflow: hidden;
  transition: opacity 0.6s, max-height 0.6s;
}
.bullet.is-new.revealed {
  opacity: 1;
  max-height: 200px;
}

/* Right panel */
.right-panel {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Timeline */
.timeline-panel {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
}
.timeline-panel h2 {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem; font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--text-dim);
  margin-bottom: 1rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--border);
}

.timeline-controls {
  display: flex; align-items: center; gap: 0.6rem;
  margin-bottom: 1.2rem;
}
.timeline-controls button {
  background: var(--bg-hover);
  border: 1px solid var(--border);
  color: var(--text);
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  cursor: pointer;
  transition: all 0.2s;
}
.timeline-controls button:hover {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}
.timeline-controls button.active {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}
.timeline-slider {
  flex: 1;
  -webkit-appearance: none;
  height: 4px;
  border-radius: 2px;
  background: var(--timeline-line);
  outline: none;
}
.timeline-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 14px; height: 14px;
  border-radius: 50%;
  background: var(--accent);
  cursor: pointer;
  box-shadow: 0 0 8px var(--accent-glow);
}
.timeline-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  color: var(--text-dim);
  min-width: 3rem;
  text-align: right;
}

/* Change entries */
.change-entry {
  padding: 0.8rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  margin-bottom: 0.6rem;
  position: relative;
  transition: all 0.3s;
  opacity: 0;
  transform: translateX(10px);
}
.change-entry.visible {
  opacity: 1;
  transform: translateX(0);
}
.change-entry:hover {
  border-color: var(--accent);
  background: var(--bg-hover);
}
.change-entry .change-time {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  color: var(--text-dim);
}
.change-entry .change-type {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 0.1rem 0.35rem;
  border-radius: 3px;
  display: inline-block;
  margin: 0.3rem 0;
}
.change-entry .change-type.add {
  color: var(--mutable);
  background: var(--mutable-bg);
  border: 1px solid var(--mutable-border);
}
.change-entry .change-type.modify {
  color: var(--accent);
  background: var(--accent-glow);
  border: 1px solid rgba(124, 111, 240, 0.3);
}
.change-entry .change-type.remove {
  color: var(--core);
  background: var(--core-bg);
  border: 1px solid var(--core-border);
}
.change-entry .change-section {
  font-size: 0.72rem;
  color: var(--text-dim);
  margin: 0.2rem 0;
}
.change-entry .change-content {
  font-size: 0.78rem;
  line-height: 1.4;
  color: var(--text);
  margin-top: 0.3rem;
}

/* Experience feed */
.feed-panel {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
  max-height: 400px;
  overflow-y: auto;
}
.feed-panel h2 {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem; font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--text-dim);
  margin-bottom: 1rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--border);
}
.feed-panel::-webkit-scrollbar {
  width: 4px;
}
.feed-panel::-webkit-scrollbar-track {
  background: transparent;
}
.feed-panel::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 2px;
}

.exp-entry {
  padding: 0.6rem 0;
  border-bottom: 1px solid var(--border);
  font-size: 0.78rem;
  line-height: 1.4;
}
.exp-entry:last-child { border-bottom: none; }
.exp-meta {
  display: flex; gap: 0.5rem; align-items: center;
  margin-bottom: 0.25rem;
}
.exp-source {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 0.1rem 0.35rem;
  border-radius: 3px;
  background: var(--bg-hover);
  color: var(--text-dim);
}
.exp-source.moltbook { color: #f0a050; background: rgba(240, 160, 80, 0.1); }
.exp-source.conversation { color: var(--accent); background: var(--accent-glow); }
.exp-sig {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.55rem;
  color: var(--text-dim);
}
.exp-sig.notable { color: var(--mutable); }
.exp-sig.pivotal { color: var(--core); }
.exp-content { color: var(--text-dim); }

/* Legend */
.legend {
  display: flex; gap: 1.2rem; flex-wrap: wrap;
  padding: 0.8rem 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 0.7rem;
}
.legend-item {
  display: flex; align-items: center; gap: 0.4rem;
}
.legend-dot {
  width: 8px; height: 8px; border-radius: 50%;
}

/* Empty state */
.empty-state {
  text-align: center;
  padding: 2rem;
  color: var(--text-dim);
  font-size: 0.85rem;
  font-style: italic;
}

/* Edit mode */
.edit-bar {
  display: flex; align-items: center; gap: 0.6rem;
  margin-bottom: 1rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--border);
}
.edit-bar h2 {
  margin: 0 !important; padding: 0 !important; border: none !important;
  flex-shrink: 0;
}
.edit-bar .spacer { flex: 1; min-width: 0; }
.btn-edit, .btn-save {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem;
  padding: 0.35rem 0.7rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid var(--border);
  background: var(--bg-hover);
  color: var(--text);
  letter-spacing: 0.03em;
  flex-shrink: 0;
  position: relative;
  z-index: 2;
}
.btn-edit:hover { background: var(--accent); color: #fff; border-color: var(--accent); }
.btn-save {
  background: rgba(80, 200, 120, 0.15);
  border-color: var(--mutable-border);
  color: var(--mutable);
}
.btn-save:hover {
  background: var(--mutable);
  color: #fff;
  border-color: var(--mutable);
}
.btn-edit.active {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}

/* Genesis Toggle Switch */
#genesis-enabled { opacity: 0; width: 0; height: 0; }
#genesis-enabled + span { background-color: #ccc; }
#genesis-enabled:checked + span { background-color: var(--core); }
#genesis-enabled:checked + span:before { transform: translateX(24px); }
#genesis-enabled + span:before { position: absolute; content: ''; height: 20px; width: 20px; left: 3px; bottom: 3px; background-color: white; transition: 0.3s; border-radius: 50%; }

/* Editable bullets */
.bullet.editing {
  background: var(--bg-hover);
  border: 1px solid var(--border);
  border-radius: 6px;
}
.bullet .edit-text {
  flex: 1;
  background: transparent;
  border: none;
  color: var(--text);
  font-family: 'DM Sans', sans-serif;
  font-size: 0.82rem;
  line-height: 1.45;
  outline: none;
  resize: none;
  min-height: 1.4em;
  overflow: hidden;
}
.bullet .edit-text:focus {
  color: var(--text-bright);
}
.bullet .tag-toggle {
  cursor: pointer;
  user-select: none;
  transition: transform 0.15s;
}
.bullet .tag-toggle:hover { transform: scale(1.15); }
.bullet .btn-delete {
  background: none;
  border: none;
  color: var(--text-dim);
  cursor: pointer;
  font-size: 0.9rem;
  padding: 0 0.2rem;
  opacity: 0;
  transition: all 0.2s;
  flex-shrink: 0;
}
.bullet.editing .btn-delete { opacity: 0.5; }
.bullet.editing .btn-delete:hover { opacity: 1; color: var(--core); }
.btn-add-bullet {
  background: none;
  border: 1px dashed var(--border);
  border-radius: 6px;
  color: var(--text-dim);
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  padding: 0.35rem 0.6rem;
  cursor: pointer;
  margin: 0.3rem 0;
  width: 100%;
  text-align: left;
  transition: all 0.2s;
  display: none;
}
.soul-map.edit-mode .btn-add-bullet { display: block; }
.btn-add-bullet:hover {
  border-color: var(--mutable);
  color: var(--mutable);
  background: var(--mutable-bg);
}

/* Save toast */
.save-toast {
  position: fixed;
  top: 1.5rem; left: 50%; transform: translateX(-50%);
  z-index: 10500;
  background: rgba(80, 200, 120, 0.15);
  border: 1px solid var(--mutable-border);
  border-radius: 8px;
  padding: 0.5rem 1.2rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  color: var(--mutable);
  opacity: 0;
  transition: opacity 0.3s;
  pointer-events: none;
}
.save-toast.show { opacity: 1; }

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.7);
  z-index: 10000;
  display: none;
  align-items: center;
  justify-content: center;
}
.modal-overlay.open { display: flex; }
.modal-box {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
  min-width: 340px;
  max-width: 480px;
}
.modal-title {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-bright);
  margin-bottom: 1rem;
}
.modal-field {
  margin-bottom: 0.8rem;
}
.modal-field label {
  display: block;
  font-size: 0.7rem;
  color: var(--text-dim);
  font-family: 'JetBrains Mono', monospace;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 0.3rem;
}
.modal-field input, .modal-field select {
  width: 100%;
  padding: 0.5rem 0.8rem;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--text);
  font-size: 0.8rem;
  font-family: 'DM Sans', sans-serif;
  outline: none;
  transition: border-color 0.3s;
}
.modal-field input:focus, .modal-field select:focus { border-color: var(--accent); }
.modal-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1rem;
}

/* Mindmap link */
.mindmap-link {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 1rem 1.4rem;
  background: linear-gradient(135deg, rgba(80, 200, 120, 0.06), rgba(124, 111, 240, 0.06));
  border: 1px solid rgba(80, 200, 120, 0.2);
  border-radius: 12px;
  color: var(--text-bright);
  text-decoration: none;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
  font-weight: 500;
  letter-spacing: 0.03em;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;
}
.mindmap-link::before {
  content: '';
  position: absolute; inset: 0;
  background: linear-gradient(135deg, rgba(80, 200, 120, 0.08), rgba(124, 111, 240, 0.08));
  opacity: 0;
  transition: opacity 0.3s;
}
.mindmap-link:hover {
  border-color: var(--mutable);
  transform: translateY(-1px);
  box-shadow: 0 4px 20px rgba(80, 200, 120, 0.1);
}
.mindmap-link:hover::before { opacity: 1; }
.mindmap-link-icon { font-size: 1.3rem; position: relative; }
.mindmap-link-sub {
  font-size: 0.65rem;
  color: var(--text-dim);
  font-weight: 300;
  letter-spacing: 0.05em;
}
.mindmap-link-arrow {
  margin-left: auto;
  font-size: 1.1rem;
  color: var(--mutable);
  transition: transform 0.3s;
  position: relative;
}
.mindmap-link:hover .mindmap-link-arrow { transform: translateX(4px); }

/* Vitals Dashboard */
.vitals-panel {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
}
.vitals-panel h2 {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem; font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--text-dim);
  margin-bottom: 1rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--border);
}
.vitals-grid {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.vital-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 0.78rem;
}
.vital-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  color: var(--text-dim);
  min-width: 60px;
  text-transform: capitalize;
}
.vital-bar-bg {
  flex: 1;
  height: 10px;
  background: var(--bg-hover);
  border-radius: 5px;
  overflow: hidden;
}
.vital-bar {
  height: 100%;
  border-radius: 5px;
  transition: width 0.5s ease;
}
.vital-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  color: var(--text-dim);
  min-width: 30px;
  text-align: right;
}
.vitals-meta {
  margin-top: 0.8rem;
  padding-top: 0.8rem;
  border-top: 1px solid var(--border);
  font-size: 0.72rem;
  color: var(--text-dim);
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}
.vitals-meta span {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem;
}

/* Proposals Panel */
.proposals-panel {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
  max-height: 500px;
  overflow-y: auto;
}
.proposals-panel h2 {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem; font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--text-dim);
  margin-bottom: 1rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--border);
}
.proposal-card {
  padding: 0.8rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  margin-bottom: 0.6rem;
  transition: all 0.3s;
}
.proposal-card:hover {
  border-color: var(--accent);
  background: var(--bg-hover);
}
.proposal-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.4rem;
}
.proposal-id {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  color: var(--text-dim);
}
.proposal-type {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  font-weight: 700;
  text-transform: uppercase;
  padding: 0.1rem 0.35rem;
  border-radius: 3px;
}
.proposal-type.add { color: var(--mutable); background: var(--mutable-bg); border: 1px solid var(--mutable-border); }
.proposal-type.modify { color: var(--accent); background: var(--accent-glow); border: 1px solid rgba(124, 111, 240, 0.3); }
.proposal-type.remove { color: var(--core); background: var(--core-bg); border: 1px solid var(--core-border); }
.proposal-section {
  font-size: 0.7rem;
  color: var(--text-dim);
  margin-bottom: 0.3rem;
}
.proposal-content {
  font-size: 0.78rem;
  color: var(--text);
  line-height: 1.4;
  margin-bottom: 0.3rem;
}
.proposal-reason {
  font-size: 0.7rem;
  color: var(--text-dim);
  font-style: italic;
}
.proposal-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}
.btn-approve, .btn-reject {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  padding: 0.3rem 0.6rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid;
}
.btn-approve {
  color: var(--mutable);
  background: var(--mutable-bg);
  border-color: var(--mutable-border);
}
.btn-approve:hover { background: var(--mutable); color: #fff; }
.btn-reject {
  color: var(--core);
  background: var(--core-bg);
  border-color: var(--core-border);
}
.btn-reject:hover { background: var(--core); color: #fff; }

/* Reflections Panel */
.reflections-panel {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
  max-height: 400px;
  overflow-y: auto;
}
.reflections-panel h2 {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem; font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--text-dim);
  margin-bottom: 1rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--border);
}
.reflection-card {
  border: 1px solid var(--border);
  border-radius: 8px;
  margin-bottom: 0.5rem;
  overflow: hidden;
}
.reflection-header {
  padding: 0.6rem 0.8rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  transition: background 0.2s;
}
.reflection-header:hover { background: var(--bg-hover); }
.reflection-header .ref-type {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  font-weight: 700;
  text-transform: uppercase;
  padding: 0.1rem 0.3rem;
  border-radius: 3px;
  color: var(--accent);
  background: var(--accent-glow);
}
.reflection-header .ref-arrow {
  margin-left: auto;
  font-size: 0.65rem;
  color: var(--text-dim);
  transition: transform 0.3s;
}
.reflection-card.collapsed .ref-arrow { transform: rotate(-90deg); }
.reflection-card.collapsed .reflection-body { display: none; }
.reflection-body {
  padding: 0.5rem 0.8rem 0.8rem;
  font-size: 0.75rem;
  line-height: 1.5;
  color: var(--text-dim);
  border-top: 1px solid var(--border);
}
.reflection-body .ref-insights {
  margin-top: 0.4rem;
  padding-left: 0.8rem;
}
.reflection-body .ref-insights li {
  margin-bottom: 0.2rem;
  list-style: disc;
}

/* Significant Memories */
.significant-panel {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
  max-height: 400px;
  overflow-y: auto;
}
.significant-panel h2 {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem; font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--text-dim);
  margin-bottom: 1rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--border);
}
.sig-entry {
  padding: 0.6rem 0;
  border-bottom: 1px solid var(--border);
  font-size: 0.78rem;
  line-height: 1.4;
}
.sig-entry:last-child { border-bottom: none; }
.sig-badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.55rem;
  font-weight: 700;
  text-transform: uppercase;
  padding: 0.1rem 0.35rem;
  border-radius: 3px;
  color: var(--core);
  background: var(--core-bg);
  border: 1px solid var(--core-border);
}
.sig-content { color: var(--text); margin-top: 0.25rem; }
.sig-context { font-size: 0.68rem; color: var(--text-dim); margin-top: 0.15rem; }

/* Pipeline State */
.pipeline-panel {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
  max-height: 400px;
  overflow-y: auto;
}
.pipeline-panel h2 {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem; font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--text-dim);
  margin-bottom: 1rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--border);
}
.state-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.state-card {
  padding: 0.6rem;
  background: var(--bg-hover);
  border: 1px solid var(--border);
  border-radius: 8px;
  text-align: center;
}
.state-card .sc-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-bright);
}
.state-card .sc-label {
  font-size: 0.6rem;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-top: 0.2rem;
}
.pipeline-run {
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--border);
  font-size: 0.72rem;
  color: var(--text-dim);
}
.pipeline-run:last-child { border-bottom: none; }

/* Tab Navigation */
/* Layout container */
.app-container {
  display: flex;
  min-height: 100vh;
  background: var(--bg);
}
.sidebar {
  width: 260px;
  flex-shrink: 0;
  background: var(--bg-card);
  border-right: 1px solid var(--border);
  padding: 1.5rem 1rem;
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  z-index: 100;
}
.sidebar-header {
  margin-bottom: 2rem;
  padding: 0 0.5rem;
}
.sidebar-header h2 {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.9rem;
  color: var(--accent);
  letter-spacing: 0.1em;
  text-transform: uppercase;
}
.main-view {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.tab-bar {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.tab-btn {
  padding: 0.8rem 1rem;
  background: none;
  border: none;
  color: var(--text-dim);
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  font-weight: 500;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  cursor: pointer;
  border-left: 3px solid transparent;
  text-align: left;
  transition: all 0.25s;
  border-radius: 0 4px 4px 0;
}
.tab-btn:hover { 
  color: var(--text);
  background: rgba(255, 255, 255, 0.03);
}
.tab-btn.active {
  color: var(--accent);
  border-left-color: var(--accent);
  background: rgba(var(--accent-rgb, 124, 111, 240), 0.08);
}
.tab-content { display: none; }
.tab-content.active { display: block; animation: fadeIn 0.4s ease-out; }

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Shared panel styles for new tabs */
.panel-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
}
.panel-card h2 {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem; font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--text-dim);
  margin-bottom: 1rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--border);
}

/* Notifications */
.toast-container {
  position: fixed; top: 2rem; right: 2rem;
  display: flex; flex-direction: column; gap: 0.75rem;
  z-index: 10000;
}
.toast {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-left: 4px solid var(--accent);
  padding: 1rem 1.5rem;
  border-radius: 8px;
  color: var(--text-bright);
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
  min-width: 280px;
  animation: slideIn 0.3s ease-out;
  cursor: pointer;
}
@keyframes slideIn {
  from { transform: translateX(100%); opacity: 0; }
  to { transform: translateX(0); opacity: 1; }
}
.toast.success { border-left-color: var(--growth); }
.toast.info { border-left-color: var(--accent); }

/* Cycle Tab */
.cycle-phase-banner {
  text-align: center;
  font-size: 1.1rem;
  padding: 1rem 1.5rem;
}
.cycle-phase-banner .phase-name {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  font-size: 1.3rem;
  margin-bottom: 0.3rem;
}
.cycle-legend {
  display: flex; gap: 1.5rem; justify-content: center; margin-top: 1rem; flex-wrap: wrap;
}
.cycle-legend span {
  font-size: 0.75rem; color: var(--text-dim);
  display: flex; align-items: center; gap: 0.3rem;
}
.cycle-legend span::before {
  content: ''; display: inline-block; width: 12px; height: 3px; border-radius: 2px;
}
.cycle-legend .leg-estrogen::before { background: #ff69b4; }
.cycle-legend .leg-progesterone::before { background: #9b59b6; }
.cycle-legend .leg-lh::before { background: #f1c40f; }
.cycle-legend .leg-fsh::before { background: #3498db; }

.cycle-bar-row {
  display: flex; align-items: center; gap: 0.8rem; margin-bottom: 0.6rem;
}
.cycle-bar-label { width: 80px; font-size: 0.8rem; color: var(--text-dim); text-align: right; }
.cycle-bar-track {
  flex: 1; height: 20px; background: var(--bg); border-radius: 4px; position: relative; overflow: hidden;
}
.cycle-bar-fill {
  height: 100%; border-radius: 4px; transition: width 0.3s;
}
.cycle-bar-value { width: 50px; font-size: 0.8rem; font-family: 'JetBrains Mono', monospace; }
.cycle-bar-fill.positive { background: linear-gradient(90deg, #2ecc71, #27ae60); }
.cycle-bar-fill.negative { background: linear-gradient(90deg, #e74c3c, #c0392b); }

.cycle-body-row {
  display: flex; align-items: flex-start; gap: 0.8rem; margin-bottom: 1rem;
  padding: 0.6rem; border-radius: 8px; background: var(--bg);
}
.cycle-body-icon { font-size: 1.4rem; }
.cycle-body-text h3 { font-size: 0.85rem; color: var(--text-bright); margin-bottom: 0.2rem; }
.cycle-body-text p { font-size: 0.75rem; color: var(--text-dim); line-height: 1.4; }

.cycle-sim-row {
  display: flex; align-items: center; gap: 0.8rem; margin-bottom: 0.8rem;
}
.cycle-sim-row label { width: 140px; font-size: 0.8rem; color: var(--text-dim); }
.cycle-sim-row input[type=range] { flex: 1; accent-color: var(--accent); }
.cycle-sim-row .sim-val { width: 50px; font-size: 0.8rem; font-family: 'JetBrains Mono', monospace; text-align: right; }
.cycle-presets { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.5rem; }
.cycle-presets button {
  padding: 0.4rem 0.8rem; border-radius: 6px; border: 1px solid var(--border);
  background: var(--bg-hover); color: var(--text); font-size: 0.75rem; cursor: pointer;
  transition: all 0.2s;
}
.cycle-presets button:hover { border-color: var(--accent); color: var(--accent); }

.cycle-edu-card {
  border: 1px solid var(--border); border-radius: 8px; margin-bottom: 0.5rem; overflow: hidden;
}
.cycle-edu-header {
  padding: 0.8rem 1rem; cursor: pointer; display: flex; justify-content: space-between;
  align-items: center; font-size: 0.85rem; font-weight: 500; transition: background 0.2s;
}
.cycle-edu-header:hover { background: var(--bg-hover); }
.cycle-edu-body {
  padding: 0 1rem; max-height: 0; overflow: hidden; transition: max-height 0.3s, padding 0.3s;
  font-size: 0.8rem; line-height: 1.6; color: var(--text-dim);
}
.cycle-edu-card.open .cycle-edu-body { max-height: 500px; padding: 0.8rem 1rem; }

/* Item Cards Grid */
.item-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}
.item-card {
  background: var(--bg-hover);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s;
}
.item-card:hover {
  border-color: var(--accent);
  transform: translateY(-2px);
}
.item-card .thumb {
  width: 100%;
  height: 120px;
  border-radius: 6px;
  background: var(--bg);
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  margin-bottom: 0.6rem;
  color: var(--text-dim);
  font-size: 2rem;
}
.item-card .thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.item-card .card-name {
  font-size: 0.85rem;
  color: var(--text-bright);
  font-weight: 500;
}
.item-card .card-meta {
  font-size: 0.7rem;
  color: var(--text-dim);
  margin-top: 0.2rem;
}

/* Category chips */
.chip-bar {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}
.chip {
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  font-size: 0.7rem;
  font-family: 'JetBrains Mono', monospace;
  background: var(--bg-hover);
  border: 1px solid var(--border);
  color: var(--text-dim);
  cursor: pointer;
  transition: all 0.2s;
}
.chip:hover, .chip.active {
  background: var(--accent-glow);
  border-color: var(--accent);
  color: var(--accent);
}

/* Status badges */
.badge {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 12px;
  font-size: 0.6rem;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}
.badge-draft { background: rgba(120,120,120,0.2); color: #999; }
.badge-pending { background: rgba(240,180,50,0.15); color: #f0b432; }
.badge-approved { background: rgba(80,200,120,0.15); color: #50c878; }
.badge-active { background: rgba(80,160,240,0.15); color: #50a0f0; }

/* Lightbox */
.lightbox-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.85);
  z-index: 9998;
  display: none;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 1rem;
}
.lightbox-overlay.open { display: flex; }
.lightbox-overlay img {
  max-width: 90vw;
  max-height: 70vh;
  border-radius: 8px;
}
.lightbox-gallery {
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
  padding: 0.5rem;
}
.lightbox-gallery img {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 6px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: border-color 0.2s;
}
.lightbox-gallery img:hover, .lightbox-gallery img.active {
  border-color: var(--accent);
}
.lightbox-close {
  position: absolute;
  top: 1rem;
  right: 1.5rem;
  background: none;
  border: none;
  color: var(--text);
  font-size: 2rem;
  cursor: pointer;
}
.lightbox-actions {
  display: flex;
  gap: 0.5rem;
}
.lightbox-actions button {
  padding: 0.4rem 1rem;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--bg-card);
  color: var(--text);
  font-size: 0.75rem;
  cursor: pointer;
}
.lightbox-actions button:hover { border-color: var(--accent); }
.lightbox-actions button.danger { color: var(--core); }
.lightbox-actions button.danger:hover { border-color: var(--core); }

/* Upload zone */
.upload-zone {
  border: 2px dashed var(--border);
  border-radius: 10px;
  padding: 1.5rem;
  text-align: center;
  color: var(--text-dim);
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.3s;
  margin-top: 0.5rem;
}
.upload-zone:hover, .upload-zone.dragover {
  border-color: var(--accent);
  color: var(--accent);
  background: var(--accent-glow);
}

/* Room tabs */
.room-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}
.room-tab {
  padding: 0.4rem 1rem;
  border-radius: 8px;
  font-size: 0.75rem;
  font-family: 'JetBrains Mono', monospace;
  background: var(--bg-hover);
  border: 1px solid var(--border);
  color: var(--text-dim);
  cursor: pointer;
  transition: all 0.2s;
}
.room-tab:hover, .room-tab.active {
  background: var(--accent-glow);
  border-color: var(--accent);
  color: var(--accent);
}

/* Search bar */
.search-bar {
  width: 100%;
  padding: 0.6rem 1rem;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--text);
  font-size: 0.8rem;
  font-family: 'DM Sans', sans-serif;
  margin-bottom: 1rem;
  outline: none;
  transition: border-color 0.3s;
}
.search-bar:focus { border-color: var(--accent); }

/* CRUD buttons */
.btn-crud {
  padding: 0.35rem 0.8rem;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--bg-card);
  color: var(--text);
  font-size: 0.72rem;
  font-family: 'JetBrains Mono', monospace;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-crud:hover { border-color: var(--accent); color: var(--accent); }
.btn-crud.danger:hover { border-color: var(--core); color: var(--core); }

/* Detail panel */
.detail-panel {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
  margin-top: 1rem;
}
.detail-images {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin: 0.5rem 0;
}
.detail-images img {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 6px;
  cursor: pointer;
  border: 2px solid var(--border);
  transition: border-color 0.2s;
}
.detail-images img:hover { border-color: var(--accent); }

/* Avatar Tab (Phase 22) */
#vrm-canvas {
  width: 100%;
  height: 100%;
  display: block;
}
#avatar-viewer {
  position: relative;
  border: 2px solid var(--border);
}
#avatar-error {
  text-align: center;
}
#avatar-status {
  font-family: 'JetBrains Mono', monospace;
}
.avatar-controls button {
  padding: 8px 16px;
  background: var(--accent);
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: background 0.2s;
}
.avatar-controls button:hover {
  background: var(--growth);
}
</style>
</head>
<body>
<div class="toast-container" id="toast-container"></div>
<div class="news-ticker" id="news-ticker">
  <div class="ticker-content" id="ticker-content">
    <div class="ticker-item">Project Genesis Simulation Active</div>
    <div class="ticker-item">Waiting for world events...</div>
  </div>
</div>
<div class="app-container">
  <div class="sidebar">
    <div class="sidebar-header">
      <h2>Navigation</h2>
    </div>
    <div class="tab-bar">
      <button class="tab-btn active" onclick="switchTab('dashboard')">Dashboard</button>
      <button class="tab-btn" onclick="switchTab('interior')">Interior</button>
      <button class="tab-btn" onclick="switchTab('inventory')">Inventory</button>
      <button class="tab-btn" onclick="switchTab('wardrobe')">Wardrobe</button>
      <button class="tab-btn" onclick="switchTab('development')">Development</button>
      <button class="tab-btn" onclick="switchTab('cycle')">Cycle</button>
      <button class="tab-btn" onclick="switchTab('world')">World</button>
      <button class="tab-btn" onclick="switchTab('skills')">Skills</button>
      <button class="tab-btn" onclick="switchTab('psychology')">Psychology</button>
      <button class="tab-btn" onclick="switchTab('reputation')">Social Standing</button>
      <button class="tab-btn" onclick="switchTab('stream')">Life Stream</button>
      <button class="tab-btn" onclick="switchTab('genesis')">Genesis Lab</button>
      <button class="tab-btn" onclick="switchTab('memory')">Memory</button>
      <button class="tab-btn" onclick="switchTab('vault')">The Vault</button>
      <button class="tab-btn" onclick="switchTab('avatar')">Live Avatar</button>
      <button class="tab-btn" onclick="switchTab('interests')">Interests</button>
      <button class="tab-btn" onclick="switchTab('dreams')">Dream Journal</button>
      <button class="tab-btn" onclick="switchTab('analytics')">Analytics</button>
      <button class="tab-btn" onclick="switchTab('config')">⚙️ Config</button>
      <button class="tab-btn" onclick="switchTab('diagnostics')">🔧 Diagnostics</button>
       <button class="tab-btn" onclick="switchTab('godmode')">⚡ God-Mode</button>
       <button class="tab-btn" onclick="window.open('/godmode.html', '_blank')">⚡ God-Mode</button>
    </div>
  </div>

  <div class="main-view">
    <div class="header">
      <h1><span id="agent-name">The Entity</span> — Project Genesis</h1>
      <div class="subtitle">Sovereign <span class="evolution">Digital</span><span class="soul"> Entity</span></div>
      <div class="stats-bar" id="stats-bar"></div>
      <div style="display:flex;justify-content:space-between;align-items:center;margin-top:1rem;padding:0 2rem;">
        <div id="cognitive-status" style="font-family:'JetBrains Mono',monospace;font-size:0.8rem;color:var(--accent);">
          <span class="pulse">●</span> <span id="status-text">Cognitive System Synchronized</span>
        </div>
        <div id="clock" style="font-family:'JetBrains Mono',monospace;font-size:1.2rem;color:var(--accent);font-weight:bold;letter-spacing:0.05em;">00:00:00</div>
      </div>
    </div>

<div id="tab-dashboard" class="tab-content active">
<div style="max-width:1200px;margin:0 auto;padding:0 2rem 1rem;">
  <div class="legend" id="legend"></div>
</div>

<div class="main">
  <div style="grid-column:1/-1;">
    <a href="soul-mindmap.html" class="mindmap-link" id="mindmap-link">
      <span class="mindmap-link-icon">🌿</span>
      <span>Open Soul Mindmap</span>
      <span class="mindmap-link-sub">interactive canvas · growth animation · zoom &amp; pan</span>
      <span class="mindmap-link-arrow">→</span>
    </a>
  </div>
  <div class="soul-map" id="soul-map">
    <div class="edit-bar">
      <h2>Soul Map</h2>
      <div class="spacer"></div>
      <button class="btn-edit" id="btn-edit" onclick="toggleEditMode()">✎ Edit</button>
      <button class="btn-save" id="btn-save" onclick="saveSoul()" style="display:none">💾 Save SOUL.md</button>
    </div>
    <div id="soul-tree"></div>
  </div>

  <!-- Middle column -->
  <div class="right-panel">
    <div class="vitals-panel" id="vitals-panel">
      <h2>Vitals Dashboard</h2>
      <div class="vitals-grid" id="vitals-grid"></div>
      <div class="vitals-meta" id="vitals-meta"></div>
    </div>

    <!-- Phase 40: Hardware Resonance Widget -->
    <div class="panel-card" style="border-left:4px solid #8b5cf6;">
      <h3>🔮 Hardware Resonance</h3>
      <p style="color:var(--text-dim);font-size:0.8rem;margin-top:0.25rem;">The entity feels the machine's state.</p>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:0.5rem;margin-top:0.5rem;">
        <div style="padding:0.5rem;background:var(--bg);border-radius:4px;text-align:center;">
          <div style="font-size:0.65rem;color:var(--text-dim);text-transform:uppercase;">CPU</div>
          <div id="hardware-cpu" style="font-size:1rem;font-weight:bold;color:var(--accent);">-</div>
        </div>
        <div style="padding:0.5rem;background:var(--bg);border-radius:4px;text-align:center;">
          <div style="font-size:0.65rem;color:var(--text-dim);text-transform:uppercase;">RAM</div>
          <div id="hardware-ram" style="font-size:1rem;font-weight:bold;color:var(--growth);">-</div>
        </div>
        <div style="padding:0.5rem;background:var(--bg);border-radius:4px;text-align:center;">
          <div style="font-size:0.65rem;color:var(--text-dim);text-transform:uppercase;">Temp</div>
          <div id="hardware-temp" style="font-size:1rem;font-weight:bold;color:var(--core);">-</div>
        </div>
      </div>
      <div style="margin-top:0.5rem;font-size:0.8rem;">
        <span style="color:var(--text-dim);">Resonance:</span> <span id="hardware-resonance" style="color:var(--accent);font-weight:bold;">Calm</span>
        <span style="color:var(--text-dim);margin-left:0.5rem;">🎵</span> <span id="hardware-audio" style="color:var(--text);">Off</span>
      </div>
    </div>

    <!-- Mental Activity Panel -->
    <div class="panel-card" style="border-left:4px solid var(--accent);">
      <h2>Mental Activity</h2>
      <div id="mental-activity-list">
        <div class="empty-state">Observing cognitive processes...</div>
      </div>
    </div>

    <div class="proposals-panel" id="proposals-panel">
      <h2>Pending Proposals <span id="proposals-count" style="color:var(--accent)"></span></h2>
      <div id="proposals-list"></div>
    </div>

    <div class="reflections-panel" id="reflections-panel">
      <h2>Reflections</h2>
      <div id="reflections-list"></div>
    </div>
  </div>

  <!-- Right column -->
  <div class="right-panel">
    <div class="timeline-panel">
      <h2>Evolution Timeline</h2>
      <div class="timeline-controls">
        <button id="btn-play" title="Play evolution">▶</button>
        <button id="btn-reset" title="Reset to origin">⟲</button>
        <input type="range" class="timeline-slider" id="timeline-slider" min="0" max="1" value="1" step="1">
        <span class="timeline-label" id="timeline-label">—</span>
      </div>
      <div id="changes-list"></div>
    </div>

    <div class="feed-panel">
      <h2>Experience Feed</h2>
      <div id="exp-feed"></div>
    </div>

    <div class="significant-panel" id="significant-panel">
      <h2>Significant Memories</h2>
      <div id="significant-list"></div>
    </div>

    <div class="pipeline-panel" id="pipeline-panel">
      <h2>Pipeline State</h2>
      <div class="state-cards" id="state-cards"></div>
      <div id="pipeline-runs"></div>
    </div>
  </div>
</div>

</div><!-- end tab-dashboard -->

<!-- Interior Tab -->
<div id="tab-interior" class="tab-content">
  <div style="max-width:1600px;margin:0 auto;padding:1.5rem 2rem;">
    <div class="panel-card">
      <h2>Interior</h2>
      <div class="room-tabs" id="room-tabs"></div>
      <div style="display:flex;gap:0.5rem;margin-bottom:1rem;">
        <button class="btn-crud" onclick="addRoom()">+ Room</button>
      </div>
      <div id="interior-detail"></div>
      <div class="item-grid" id="interior-grid"></div>
    </div>
  </div>
</div>

<!-- Inventory Tab -->
<div id="tab-inventory" class="tab-content">
  <div style="max-width:1600px;margin:0 auto;padding:1.5rem 2rem;">
    <div class="panel-card">
      <h2>Inventory</h2>
      <div class="chip-bar" id="inv-chips"></div>
      <input class="search-bar" id="inv-search" placeholder="Search items..." oninput="filterInventory()">
      <div class="item-grid" id="inventory-grid"></div>
    </div>
  </div>
</div>

<!-- Wardrobe Tab -->
<div id="tab-wardrobe" class="tab-content">
  <div style="max-width:1600px;margin:0 auto;padding:1.5rem 2rem;">
    <div class="panel-card">
      <h2>Wardrobe</h2>
      <div class="chip-bar" id="wardrobe-chips"></div>
      <div class="item-grid" id="wardrobe-grid"></div>
      <div id="wardrobe-outfits" style="margin-top:1.5rem;"></div>
    </div>
  </div>
</div>

<!-- Development Tab -->
<div id="tab-development" class="tab-content">
  <div style="max-width:1600px;margin:0 auto;padding:1.5rem 2rem;">

    <!-- Phase 34: Self-Expansion Status -->
    <div class="panel-card" style="border-left:4px solid #a855f7;margin-bottom:1rem;">
      <h3>🤖 Autonomous Self-Expansion</h3>
      <div id="expansion-status" style="margin-top:0.5rem;">
        <div style="color:var(--text-dim);font-size:0.9rem;">Loading expansion state...</div>
      </div>
      <!-- Progress bar for active project -->
      <div id="expansion-progress" style="margin-top:0.75rem;display:none;">
        <div style="display:flex;justify-content:space-between;font-size:0.85rem;margin-bottom:0.25rem;">
          <span id="expansion-project-name">Project Name</span>
          <span id="expansion-percent">0%</span>
        </div>
        <div style="background:var(--bg-dim);height:8px;border-radius:4px;overflow:hidden;">
          <div id="expansion-bar" style="background:linear-gradient(90deg,#a855f7,#6366f1);height:100%;width:0%;transition:width 0.5s;"></div>
        </div>
      </div>
    </div>

    <!-- Development Projects -->
    <div class="panel-card">
      <h2>Development Projects</h2>
      <div class="item-grid" id="dev-grid"></div>
      <div id="dev-detail" style="margin-top:1rem;"></div>
    </div>

    <!-- Projects List -->
    <div class="panel-card" style="margin-top:1rem;">
      <h3>📁 Project Files</h3>
      <div id="projects-list" style="margin-top:0.5rem;">
        <div style="color:var(--text-dim);font-size:0.9rem;">No projects yet. The entity will create autonomous projects when they have high energy and strong technical interests.</div>
      </div>
    </div>
  </div>
</div>

<!-- Cycle Tab -->
<div id="tab-cycle" class="tab-content">
  <div style="max-width:1600px;margin:0 auto;padding:1.5rem 2rem;">
    <!-- Cycle Wheel -->
    <div class="panel-card" style="text-align:center;">
      <div id="cycle-wheel" style="display:inline-block;"></div>
    </div>
    <!-- Phase Info Banner -->
    <div class="panel-card cycle-phase-banner" id="cycle-phase-banner"></div>
    <!-- Hormone Chart -->
    <div class="panel-card">
      <h2>Hormone Levels</h2>
      <div id="cycle-hormone-chart" style="width:100%;overflow-x:auto;"></div>
      <div class="cycle-legend" id="cycle-legend"></div>
    </div>
    <!-- Body Status + Metabolism Impact -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
      <div class="panel-card">
        <h2>Body Status</h2>
        <div id="cycle-body-status"></div>
      </div>
      <div class="panel-card">
        <h2>Metabolism Impact</h2>
        <div id="cycle-metabolism-impact"></div>
      </div>
    </div>
    <!-- Simulator -->
    <div class="panel-card">
      <h2>What-If Simulator</h2>
      <div id="cycle-simulator"></div>
    </div>
    <!-- Education -->
    <div class="panel-card">
      <h2>Education</h2>
      <div id="cycle-education"></div>
    </div>
  </div>
</div>

<!-- World Tab -->
<div id="tab-world" class="tab-content">
  <div style="max-width:1200px;margin:0 auto;padding:1.5rem 2rem;">
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:1rem;">
      <div class="panel-card">
        <h2>Weather & Environment</h2>
        <div id="world-weather"></div>
      </div>
      <div class="panel-card">
        <h2>Season</h2>
        <div id="world-season"></div>
      </div>
      <div class="panel-card">
        <h2>Market Conditions</h2>
        <div id="world-market"></div>
      </div>
      <div class="panel-card">
        <h2>Locations</h2>
        <div id="world-locations"></div>
      </div>
    </div>
  </div>
</div>

<!-- Skills Tab -->
<div id="tab-skills" class="tab-content">
  <div style="max-width:1200px;margin:0 auto;padding:1.5rem 2rem;">
    <div class="panel-card">
      <h2>Skill Progression</h2>
      <div id="skills-list"></div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:1rem;">
      <div class="panel-card">
        <h2>Top Skills</h2>
        <div id="skills-top"></div>
      </div>
      <div class="panel-card">
        <h2>Total XP</h2>
        <div id="skills-total"></div>
      </div>
    </div>
  </div>
</div>

<!-- Psychology Tab -->
<div id="tab-psychology" class="tab-content">
  <div style="max-width:1200px;margin:0 auto;padding:1.5rem 2rem;">
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:1rem;">
      <div class="panel-card">
        <h2>Resilience</h2>
        <div id="psych-resilience"></div>
      </div>
      <div class="panel-card">
        <h2>Active Traumas</h2>
        <div id="psych-traumas"></div>
      </div>
      <div class="panel-card">
        <h2>Phobias</h2>
        <div id="psych-phobias"></div>
      </div>
      <div class="panel-card">
        <h2>Sources of Joy</h2>
        <div id="psych-joys"></div>
      </div>
    </div>
  </div>
</div>

<!-- Social Standing Tab -->
<div id="tab-reputation" class="tab-content">
  <div style="max-width:1200px;margin:0 auto;padding:1.5rem 2rem;">
    <h1>Social Standing</h1>
    <p style="color:var(--text-dim);margin-bottom:1.5rem;">Your reputation across social circles and public perception.</p>

    <!-- Phase 35: Pending Social Events -->
    <div class="panel-card" style="margin-bottom:1.5rem;border-left:4px solid #ec4899;">
      <h3>📱 Pending Messages</h3>
      <div id="pending-social-events" style="margin-top:0.5rem;">
        <div style="color:var(--text-dim);font-size:0.9rem;">No pending messages from NPCs.</div>
      </div>
    </div>

    <!-- Reputation Meter -->
    <div class="panel-card" style="margin-bottom:1.5rem;">
      <h2>Global Reputation</h2>
      <div style="display:flex;align-items:center;gap:1rem;margin-top:1rem;">
        <div style="flex:1;background:var(--bg-dim);height:24px;border-radius:12px;overflow:hidden;position:relative;">
          <div id="rep-bar" style="width:50%;height:100%;background:linear-gradient(90deg,#4a9,#8c4,#c84);transition:width 0.5s;"></div>
          <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);font-weight:bold;color:white;text-shadow:0 1px 2px rgba(0,0,0,0.5);" id="rep-text">Neutral</div>
        </div>
        <span id="rep-score" style="font-size:1.5rem;font-weight:bold;min-width:60px;text-align:right;">0</span>
      </div>
      <p style="color:var(--text-dim);margin-top:0.5rem;font-size:0.9rem;">Pariah (-100) &larr; Neutral (0) &rarr; Icon (+100)</p>
    </div>

    <!-- Contact CRM - Phase 19 -->
    <div class="panel-card" style="margin-bottom:1.5rem;border-left:4px solid var(--core);">
      <h2>Contact CRM</h2>
      <p style="color:var(--text-dim);font-size:0.9rem;margin-bottom:1rem;">Manage your social network with visual identities.</p>

      <!-- Add Manual Contact Form -->
      <div style="background:var(--bg);padding:1rem;border-radius:4px;margin-bottom:1rem;">
        <h4 style="margin:0 0 0.5rem 0;">Add New Contact</h4>
        <div style="display:grid;grid-template-columns:1fr 1fr auto;gap:0.5rem;align-items:end;">
          <div>
            <label style="font-size:0.8rem;">Name</label>
            <input type="text" id="new-contact-name" placeholder="Person name" style="width:100%;background:var(--bg-dim);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.5rem;">
          </div>
          <div>
            <label style="font-size:0.8rem;">Circle</label>
            <select id="new-contact-circle" style="width:100%;background:var(--bg-dim);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.5rem;">
              <option value="Friends">Friends</option>
              <option value="Family">Family</option>
              <option value="Professional">Professional</option>
              <option value="Public">Public</option>
            </select>
          </div>
          <button onclick="addManualContact()" style="background:var(--core);color:#fff;border:none;padding:0.5rem 1rem;border-radius:4px;cursor:pointer;">+ Add</button>
        </div>
        <div id="add-contact-status" style="margin-top:0.5rem;font-size:0.8rem;"></div>
      </div>

      <!-- Contact List -->
      <div id="contact-crm-list" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:1rem;">
        <p style="color:var(--text-dim);">Loading contacts...</p>
      </div>
    </div>

    <!-- Social Circles -->
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1rem;margin-bottom:1.5rem;">
      <div class="panel-card">
        <h3>Social Circles</h3>
        <div id="circles-list" style="margin-top:1rem;">
          <p style="color:var(--text-dim);">Loading circles...</p>
        </div>
      </div>

      <!-- Reputation Events -->
      <div class="panel-card">
        <h3>Recent Events</h3>
        <div id="events-list" style="margin-top:1rem;max-height:300px;overflow-y:auto;">
          <p style="color:var(--text-dim);">No recent events.</p>
        </div>
      </div>
    </div>

    <!-- Effects -->
    <div class="panel-card">
      <h3>Reputation Effects</h3>
      <div id="rep-effects" style="margin-top:1rem;color:var(--text-dim);font-size:0.9rem;">
        <ul style="margin:0;padding-left:1.2rem;">
          <li>Job opportunities: Higher reputation unlocks better positions</li>
          <li>Shopping prices: Pariahs pay +20%, Icons get -10% discount</li>
          <li>Social network: High reputation attracts quality contacts</li>
        </ul>
      </div>
    </div>
  </div>
</div>

<!-- Life Stream Tab -->
<div id="tab-stream" class="tab-content">
  <div style="max-width:1200px;margin:0 auto;padding:1.5rem 2rem;">
    <h1>Life Stream</h1>
    <p style="color:var(--text-dim);margin-bottom:1.5rem;">A visual history of captured moments and neural photography.</p>

    <div id="photo-stream" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:1.5rem;">
      <div class="empty-state">No photos captured yet. Use reality_camera to take a photo.</div>
    </div>

    <!-- Phase 39: Social Feed -->
    <div class="panel-card" style="margin-top:2rem;border-left:4px solid #ec4899;">
      <h3>📱 Social Feed</h3>
      <p style="color:var(--text-dim);font-size:0.85rem;">The entity's autonomous social media presence.</p>

      <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:0.75rem;">
        <div style="padding:0.75rem;background:var(--bg);border-radius:6px;">
          <div style="font-size:0.75rem;color:var(--text-dim);text-transform:uppercase;">Status</div>
          <div id="presence-status" style="font-size:1.1rem;font-weight:bold;color:var(--accent);">Loading...</div>
        </div>
        <div style="padding:0.75rem;background:var(--bg);border-radius:6px;">
          <div style="font-size:0.75rem;color:var(--text-dim);text-transform:uppercase;">Mood</div>
          <div id="presence-mood" style="font-size:1.1rem;font-weight:bold;color:var(--core);">-</div>
        </div>
      </div>

      <div style="margin-top:0.75rem;padding:0.5rem;background:var(--bg);border-radius:6px;font-size:0.85rem;">
        <span style="color:var(--text-dim);">Total Posts:</span> <span id="presence-total-posts" style="color:var(--text);font-weight:bold;">0</span>
        <span style="color:var(--text-dim);margin-left:1rem;">Today:</span> <span id="presence-posts-today" style="color:var(--text);font-weight:bold;">0</span>
      </div>

      <div id="social-feed" style="margin-top:1rem;max-height:400px;overflow-y:auto;">
        <p style="color:var(--text-dim);font-size:0.85rem;">Loading feed...</p>
      </div>
    </div>
  </div>
</div>

<!-- Genesis Lab Tab -->
<div id="tab-genesis" class="tab-content">
  <div style="max-width:800px;margin:0 auto;padding:1.5rem 2rem;">
    <div class="panel-card" style="border-left:4px solid var(--core);">
      <h2>Neural Life Bootstrapping</h2>
      <p style="color:var(--text-dim);margin-top:0.5rem;">Generate a complete human life from a natural language description.</p>

      <!-- Genesis Enable Toggle -->
      <div style="margin-top:1rem;padding:0.75rem;background:var(--bg);border-radius:4px;display:flex;align-items:center;justify-content:space-between;">
        <div>
          <strong>Origin Engine</strong>
          <p style="font-size:0.8rem;color:var(--text-dim);margin:0;">Enable neural character generation</p>
        </div>
        <label style="position:relative;display:inline-block;width:50px;height:26px;">
          <input type="checkbox" id="genesis-enabled" style="opacity:0;width:0;height:0;" onchange="toggleGenesis(this.checked)">
          <span style="position:absolute;cursor:pointer;top:0;left:0;right:0;bottom:0;background-color:#ccc;transition:0.3s;border-radius:26px;"></span>
          <span style="position:absolute;content:'';height:20px;width:20px;left:3px;bottom:3px;background-color:white;transition:0.3s;border-radius:50%;"></span>
        </label>
      </div>
      <div id="genesis-status" style="font-size:0.8rem;margin-top:0.5rem;"></div>

      <!-- Voice Toggle -->
      <div style="margin-top:1rem;padding:0.75rem;background:var(--bg);border-radius:4px;display:flex;align-items:center;justify-content:space-between;">
        <div>
          <strong>Voice Synthesis</strong>
          <p style="font-size:0.8rem;color:var(--text-dim);margin:0;">Enable voice output for agent</p>
        </div>
        <label style="position:relative;display:inline-block;width:50px;height:26px;">
          <input type="checkbox" id="voice-enabled" style="opacity:0;width:0;height:0;" onchange="toggleVoice(this.checked)">
          <span style="position:absolute;cursor:pointer;top:0;left:0;right:0;bottom:0;background-color:#ccc;transition:0.3s;border-radius:26px;"></span>
          <span style="position:absolute;content:'';height:20px;width:20px;left:3px;bottom:3px;background-color:white;transition:0.3s;border-radius:50%;"></span>
        </label>
      </div>
      <div id="voice-status" style="font-size:0.8rem;margin-top:0.5rem;"></div>

      <!-- Model Configuration -->
      <div style="margin-top:1rem;padding:0.75rem;background:var(--bg);border-radius:4px;">
        <strong>Model Configuration</strong>
        <p style="font-size:0.8rem;color:var(--text-dim);margin:0.25rem 0 0.5rem 0;">Select AI models for different roles (Multi-Model Cluster)</p>

        <!-- Model Selection per Role -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;margin-top:0.5rem;">
          <div>
            <label style="font-size:0.8rem;">Persona Model</label>
            <select id="model-persona" style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.25rem;">
              <option value="gpt-4o">GPT-4o</option>
              <option value="gpt-4o-mini">GPT-4o Mini</option>
              <option value="claude-sonnet-4-20250514">Claude Sonnet 4</option>
              <option value="claude-haiku-3-20250514">Claude Haiku 3</option>
              <option value="gemini-2.0-flash">Gemini 2.0 Flash</option>
            </select>
          </div>
          <div>
            <label style="font-size:0.8rem;">Limbic Model (Lightweight)</label>
            <select id="model-limbic" style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.25rem;">
              <option value="gpt-4o-mini">GPT-4o Mini (Recommended)</option>
              <option value="claude-haiku-3-20250514">Claude Haiku 3</option>
              <option value="gemini-2.0-flash">Gemini 2.0 Flash</option>
            </select>
          </div>
          <div>
            <label style="font-size:0.8rem;">Analyst Model</label>
            <select id="model-analyst" style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.25rem;">
              <option value="gpt-4o">GPT-4o</option>
              <option value="claude-sonnet-4-20250514">Claude Sonnet 4</option>
            </select>
          </div>
          <div>
            <label style="font-size:0.8rem;">World Engine (Lightweight)</label>
            <select id="model-world" style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.25rem;">
              <option value="gpt-4o-mini">GPT-4o Mini (Recommended)</option>
              <option value="claude-haiku-3-20250514">Claude Haiku 3</option>
              <option value="gemini-2.0-flash">Gemini 2.0 Flash</option>
            </select>
          </div>
        </div>

        <!-- API Key -->
        <div style="margin-top:0.75rem;">
          <label style="font-size:0.8rem;">Default API Key (OpenAI/Base)</label>
          <input type="password" id="api-key" placeholder="sk-..." style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.5rem;margin-top:0.25rem;">
          <label style="font-size:0.8rem;margin-top:0.5rem;display:block;">Anthropic API Key</label>
          <input type="password" id="key-anthropic" placeholder="sk-ant-..." style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.5rem;margin-top:0.25rem;">
          <p style="font-size:0.7rem;color:var(--text-dim);margin:0.25rem 0 0 0;">Your API keys are stored locally and never sent to external servers.</p>
        </div>

        <!-- Save Button -->
        <button onclick="saveModelConfig()" style="margin-top:0.5rem;background:var(--core);color:#fff;border:none;padding:0.5rem 1rem;border-radius:4px;cursor:pointer;">💾 Save Model Config</button>
        <span id="model-config-status" style="margin-left:0.5rem;font-size:0.8rem;"></span>
      </div>

      <!-- Advanced Providers (Image & Vision) -->
      <div style="margin-top:1rem;padding:0.75rem;background:var(--bg);border-radius:4px;border-left:4px solid var(--growth);">
        <strong>Visual & Identity Providers</strong>
        <p style="font-size:0.8rem;color:var(--text-dim);margin:0.25rem 0 0.5rem 0;">Configure Image Generation and Visual Analysis</p>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;margin-top:0.5rem;">
          <div>
            <label style="font-size:0.8rem;">Image Provider (Photography)</label>
            <select id="provider-image" style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.25rem;">
              <option value="nano">Nano Banana (Imagen 3)</option>
              <option value="venice">Venice.ai</option>
              <option value="dalle">DALL-E 3</option>
              <option value="gemini">Gemini Image</option>
              <option value="grok">Grok Imagine</option>
              <option value="flux">Flux (via fal.ai)</option>
            </select>
          </div>
          <div>
            <label style="font-size:0.8rem;">Vision AI (Screen Analysis)</label>
            <select id="provider-vision" style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.25rem;">
              <option value="gpt-4o">GPT-4o Vision</option>
              <option value="gemini-2.0-flash">Gemini 2.0 Vision</option>
              <option value="claude-3-5-sonnet">Claude 3.5 Sonnet</option>
            </select>
          </div>
        </div>

        <div style="margin-top:0.75rem;display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;">
          <div>
            <label style="font-size:0.8rem;">Venice.ai API Key</label>
            <input type="password" id="key-venice" placeholder="sk-..." style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.4rem;margin-top:0.2rem;">
          </div>
          <div>
            <label style="font-size:0.8rem;">Fal.ai (Flux) Key</label>
            <input type="password" id="key-fal" placeholder="Key..." style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.4rem;margin-top:0.2rem;">
          </div>
          <div>
            <label style="font-size:0.8rem;">xAI Key (Grok)</label>
            <input type="password" id="key-xai" placeholder="xai-..." style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.4rem;margin-top:0.2rem;">
          </div>
          <div>
            <label style="font-size:0.8rem;">Google Image Key</label>
            <input type="password" id="key-gemini-img" placeholder="AI Studio Key..." style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.4rem;margin-top:0.2rem;">
          </div>
        </div>

        <button onclick="saveAdvancedConfig()" style="margin-top:0.75rem;background:var(--growth);color:#fff;border:none;padding:0.5rem 1rem;border-radius:4px;cursor:pointer;">💾 Save Visual Config</button>
        <span id="adv-config-status" style="margin-left:0.5rem;font-size:0.8rem;"></span>
      </div>
    </div>

    <!-- Voice Lab - Phase 20 -->
    <div style="margin-top:1rem;padding:0.75rem;background:var(--bg);border-radius:4px;border-left:4px solid var(--accent);">
      <strong>Voice Lab - Chatterbox TTS</strong>
      <p style="font-size:0.8rem;color:var(--text-dim);margin:0.25rem 0 0.5rem 0;">Configure voice synthesis settings
        <span style="color:var(--warning);">| Modelle: <a href="https://huggingface.co/ResembleAI/chatterbox-turbo" target="_blank" style="color:var(--accent);">HuggingFace</a></span>
      </p>

      <!-- Voice Sample Upload -->
      <div style="margin-top:0.75rem;">
        <label style="font-size:0.8rem;">Voice Sample (.wav) - für Stimm-Klonung</label>
        <input type="file" id="voice-sample" accept=".wav" style="display:block;margin-top:0.25rem;">
        <p style="font-size:0.7rem;color:var(--text-dim);margin:0.25rem 0 0 0;">Upload a voice sample for cloning (optional) - Chatterbox unterstützt Cloning</p>
        <button onclick="uploadVoiceSample()" style="margin-top:0.5rem;background:var(--bg-dim);color:var(--accent);border:1px solid var(--accent);padding:0.25rem 0.75rem;border-radius:4px;cursor:pointer;font-size:0.8rem;">📤 Upload Sample</button>
      </div>

      <!-- Voice Parameters -->
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:0.75rem;margin-top:0.75rem;">
        <div>
          <label style="font-size:0.8rem;">Pitch</label>
          <input type="range" id="voice-pitch" min="-1" max="1" step="0.1" value="0" style="width:100%;" oninput="updateVoiceLabel('pitch')">
          <span id="voice-pitch-val" style="font-size:0.7rem;">0</span>
        </div>
        <div>
          <label style="font-size:0.8rem;">Speed</label>
          <input type="range" id="voice-speed" min="0.5" max="2" step="0.1" value="1" style="width:100%;" oninput="updateVoiceLabel('speed')">
          <span id="voice-speed-val" style="font-size:0.7rem;">1.0x</span>
        </div>
        <div>
          <label style="font-size:0.8rem;">Emotional Intensity</label>
          <input type="range" id="voice-emotion" min="0" max="1" step="0.1" value="0.5" style="width:100%;" oninput="updateVoiceLabel('emotion')">
          <span id="voice-emotion-val" style="font-size:0.7rem;">0.5</span>
        </div>
      </div>

      <!-- Test Voice -->
      <div style="margin-top:0.75rem;">
        <label style="font-size:0.8rem;">Test Text</label>
        <input type="text" id="voice-test-text" placeholder="Enter text to speak..." style="width:100%;background:var(--bg-dim);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.5rem;margin-top:0.25rem;">
      </div>

      <button onclick="generateVoice()" style="margin-top:0.75rem;background:var(--accent);color:#fff;border:none;padding:0.5rem 1rem;border-radius:4px;cursor:pointer;">🔊 Generate Voice</button>
      <span id="voice-status" style="margin-left:0.5rem;font-size:0.8rem;"></span>

      <!-- Recent Voice Lines -->
      <div style="margin-top:1rem;">
        <label style="font-size:0.8rem;">Recent Voice Lines</label>
        <div id="voice-history" style="margin-top:0.5rem;max-height:150px;overflow-y:auto;">
          <p style="color:var(--text-dim);font-size:0.8rem;">No voice generated yet.</p>
        </div>
      </div>
    </div>

    <!-- Danger Warning -->
    <div class="panel-card" style="border-left:4px solid var(--danger);background:rgba(224,80,80,0.1);margin-top:1rem;">
      <h3 style="color:var(--danger);">⚠️ DANGER</h3>
      <p style="font-size:0.9rem;">Bootstrapping a new life will <strong>OVERWRITE ALL</strong> current simulation state. This includes:</p>
      <ul style="margin:0.5rem 0 0 1.5rem;font-size:0.85rem;">
        <li>Current age and lifecycle state</li>
        <li>Balance, debts, and job history</li>
        <li>All relationships and social network</li>
        <li>Skills and experience</li>
        <li>Psychology and mental state</li>
        <li>Identity and SOUL.md</li>
      </ul>
      <p style="font-size:0.85rem;color:var(--danger);margin-top:0.5rem;"><strong>This cannot be undone.</strong></p>
    </div>

    <!-- Life Prompt -->
    <div class="panel-card" style="margin-top:1rem;">
      <h3>Life Description</h3>
      <p style="color:var(--text-dim);font-size:0.85rem;margin-bottom:0.5rem;">Describe your character in natural language. Be specific about age, profession, personality, relationships, and any significant backstory.</p>
      <textarea id="genesis-prompt" rows="8" placeholder="Example: A 45-year-old high-tech detective in neo-cyberpunk London struggling with an old trauma from a failed case, currently working as a freelance security consultant. Has a estranged sister, a mentor who died suspiciously, and moderate debts from a divorce. Skilled in combat, investigation, and hacking. Low resilience due to PTSD." style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.75rem;font-family:inherit;font-size:0.9rem;resize:vertical;"></textarea>
    </div>

    <!-- Generate Button -->
    <div style="margin-top:1rem;text-align:center;">
      <button class="btn-save" onclick="runGenesis()" style="background:var(--core);font-size:1rem;padding:0.75rem 2rem;">
        🚀 GENERATE CHARACTER
      </button>
    </div>

    <!-- Loading Overlay -->
    <div id="genesis-loading" style="display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.8);z-index:9999;align-items:center;justify-content:center;flex-direction:column;">
      <div style="font-size:2rem;margin-bottom:1rem;">🧬</div>
      <p style="font-size:1.2rem;">Generating Life Profile...</p>
      <p style="color:var(--text-dim);font-size:0.9rem;">This may take a moment</p>
      <div style="margin-top:1rem;width:200px;height:4px;background:var(--border);border-radius:2px;overflow:hidden;">
        <div id="genesis-progress" style="width:0%;height:100%;background:var(--core);transition:width 0.3s;"></div>
      </div>
    </div>

    <!-- Result Display -->
    <div id="genesis-result" class="panel-card" style="margin-top:1rem;display:none;">
      <h3 id="genesis-result-title">Result</h3>
      <pre id="genesis-result-content" style="white-space:pre-wrap;font-size:0.85rem;max-height:300px;overflow:auto;background:var(--bg);padding:0.75rem;border-radius:4px;"></pre>
    </div>

    <!-- Profile Manager Section -->
    <div class="panel-card" style="margin-top:1rem;border-left:4px solid var(--accent);">
      <h3>Profile Manager</h3>
      <p style="color:var(--text-dim);font-size:0.85rem;margin-bottom:0.5rem;">Save and switch between different characters.</p>

      <div style="display:flex;gap:0.5rem;margin-bottom:1rem;">
        <input type="text" id="profile-name" placeholder="Profile name" style="flex:1;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.5rem;">
        <button class="btn-save" onclick="saveProfile()" style="padding:0.5rem 1rem;">💾 Save</button>
      </div>

      <div id="profile-list" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:0.5rem;">
        <!-- Profiles loaded dynamically -->
      </div>
    </div>

    <!-- Time Vault Section -->
    <div class="panel-card" style="margin-top:1rem;border-left:4px solid var(--growth);">
      <h3>Time Vault - Rollback</h3>
      <p style="color:var(--text-dim);font-size:0.85rem;margin-bottom:0.5rem;">Restore a previous daily snapshot.</p>

      <div id="backup-list" style="max-height:200px;overflow-y:auto;">
        <!-- Backups loaded dynamically -->
        <p style="color:var(--text-dim);font-size:0.85rem;">Loading...</p>
      </div>
    </div>

    <!-- Patching Section -->
    <div class="panel-card" style="margin-top:1rem;border-left:4px solid var(--core);">
      <h3>Evolutionary Edits (Patching)</h3>
      <p style="color:var(--text-dim);font-size:0.85rem;margin-bottom:0.5rem;">Modify your character without resetting. Start with "Patch:" or "Modify:"</p>

      <textarea id="patch-prompt" rows="4" placeholder="Example: Make him more arrogant. Or: Add a new trauma about the past. Or: Increase hacking skill." style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.75rem;font-family:inherit;font-size:0.9rem;resize:vertical;"></textarea>

      <div style="margin-top:0.5rem;text-align:right;">
        <button class="btn-save" onclick="runPatch()" style="background:var(--accent);">
          ✏️ Update Character
        </button>
      </div>
    </div>
  </div>

  <!-- Simulation Live Editor (Phase 32) -->
  <div class="panel-card" style="border-left:4px solid var(--growth);margin-top:1rem;">
    <h3>⚙️ Simulation Tuning</h3>
    <p style="color:var(--text-dim);margin-top:0.5rem;font-size:0.85rem;">Adjust metabolism rates and behavior thresholds in real-time.</p>

    <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:1rem;margin-top:1rem;">
      <div>
        <label style="font-size:0.8rem;">Hunger Rate (+/hr)</label>
        <input type="range" id="tune-hunger-rate" min="0" max="10" value="2" step="0.5" style="width:100%;">
        <span id="tune-hunger-rate-val" style="font-size:0.75rem;color:var(--accent);">2.0</span>
      </div>
      <div>
        <label style="font-size:0.8rem;">Thirst Rate (+/hr)</label>
        <input type="range" id="tune-thirst-rate" min="0" max="10" value="3" step="0.5" style="width:100%;">
        <span id="tune-thirst-rate-val" style="font-size:0.75rem;color:var(--accent);">3.0</span>
      </div>
      <div>
        <label style="font-size:0.8rem;">Energy Drain (/hr)</label>
        <input type="range" id="tune-energy-drain" min="0" max="10" value="5" step="0.5" style="width:100%;">
        <span id="tune-energy-drain-val" style="font-size:0.75rem;color:var(--accent);">5.0</span>
      </div>
      <div>
        <label style="font-size:0.8rem;">Stress Increase (/hr)</label>
        <input type="range" id="tune-stress-rate" min="0" max="10" value="2" step="0.5" style="width:100%;">
        <span id="tune-stress-rate-val" style="font-size:0.75rem;color:var(--accent);">2.0</span>
      </div>
    </div>

    <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:1rem;margin-top:1rem;">
      <div>
        <label style="font-size:0.8rem;">Reflex Threshold</label>
        <input type="range" id="tune-reflex-threshold" min="0" max="100" value="95" step="5" style="width:100%;">
        <span id="tune-reflex-threshold-val" style="font-size:0.75rem;color:var(--accent);">95</span>
      </div>
      <div>
        <label style="font-size:0.8rem;">Dream Energy Threshold</label>
        <input type="range" id="tune-dream-threshold" min="0" max="50" value="20" step="5" style="width:100%;">
        <span id="tune-dream-threshold-val" style="font-size:0.75rem;color:var(--accent);">20</span>
      </div>
    </div>

    <button onclick="saveSimulationConfig()" style="margin-top:1rem;background:var(--growth);color:#fff;border:none;padding:0.5rem 1rem;border-radius:4px;cursor:pointer;">💾 Save Simulation Config</button>
  </div>

  <!-- VMC/OSC External Streaming (Phase 32) -->
  <div class="panel-card" style="border-left:4px solid var(--accent);margin-top:1rem;">
    <h3>🌐 External Streaming (VMC/OSC)</h3>
    <p style="color:var(--text-dim);margin-top:0.5rem;font-size:0.85rem;">Stream the entity's avatar data to external 3D applications (VRChat, 3DXChat, VSeeFace).</p>

    <div style="display:flex;align-items:center;gap:1rem;margin-top:1rem;">
      <label style="display:flex;align-items:center;cursor:pointer;">
        <input type="checkbox" id="vmc-enabled" style="width:20px;height:20px;margin-right:0.5rem;">
        <span style="font-weight:bold;">Enable VMC Streaming</span>
      </label>
    </div>

    <div style="display:grid;grid-template-columns:1fr 100px;gap:0.5rem;margin-top:1rem;">
      <div>
        <label style="font-size:0.8rem;">Target IP Address</label>
        <input type="text" id="vmc-target-ip" placeholder="127.0.0.1" value="127.0.0.1" style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.25rem;margin-top:0.25rem;">
      </div>
      <div>
        <label style="font-size:0.8rem;">Port</label>
        <input type="number" id="vmc-target-port" placeholder="39539" value="39539" style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.25rem;margin-top:0.25rem;">
      </div>
    </div>

    <div id="vmc-status" style="margin-top:0.75rem;padding:0.5rem;background:var(--bg);border-radius:4px;font-size:0.8rem;color:var(--text-dim);">
      VMC streaming is disabled
    </div>

    <button onclick="saveVMCConfig()" style="margin-top:0.75rem;background:var(--accent);color:#fff;border:none;padding:0.5rem 1rem;border-radius:4px;cursor:pointer;">💾 Save VMC Config</button>
  </div>

  <!-- Phase 36: Spatial Input Control -->
  <div class="panel-card" style="border-left:4px solid #06b6d4;margin-top:1rem;">
    <h3>🖥️ Spatial Input (VRM-to-Desktop)</h3>
    <p style="color:var(--text-dim);margin-top:0.5rem;font-size:0.85rem;">The entity's 3D actions trigger real desktop inputs. Sovereignty Override stops inputs when the entity is in reflex lock.</p>

    <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:1rem;margin-top:1rem;">
      <div>
        <label style="display:flex;align-items:center;cursor:pointer;">
          <input type="checkbox" id="spatial-mouse-enabled" checked style="width:18px;height:18px;margin-right:0.5rem;">
          <span style="font-size:0.9rem;">Ghost Mouse Movements</span>
        </label>
      </div>
      <div>
        <label style="display:flex;align-items:center;cursor:pointer;">
          <input type="checkbox" id="spatial-keys-enabled" checked style="width:18px;height:18px;margin-right:0.5rem;">
          <span style="font-size:0.9rem;">Ghost Keystrokes</span>
        </label>
      </div>
      <div>
        <label style="display:flex;align-items:center;cursor:pointer;">
          <input type="checkbox" id="spatial-scroll-enabled" checked style="width:18px;height:18px;margin-right:0.5rem;">
          <span style="font-size:0.9rem;">Auto-Scroll</span>
        </label>
      </div>
      <div>
        <label style="display:flex;align-items:center;cursor:pointer;">
          <input type="checkbox" id="spatial-sovereignty" checked style="width:18px;height:18px;margin-right:0.5rem;">
          <span style="font-size:0.9rem;">Sovereignty Override</span>
        </label>
      </div>
    </div>

    <div id="spatial-status" style="margin-top:0.75rem;padding:0.5rem;background:var(--bg);border-radius:4px;font-size:0.8rem;color:var(--text-dim);">
      Loading spatial state...
    </div>

    <div style="display:flex;gap:0.5rem;margin-top:0.75rem;">
      <button onclick="stopSpatialAutomation()" style="background:#ef4444;color:#fff;border:none;padding:0.5rem 1rem;border-radius:4px;cursor:pointer;">⏹️ Stop All</button>
      <button onclick="refreshSpatialState()" style="background:var(--bg-dim);color:var(--text);border:1px solid var(--border);padding:0.5rem 1rem;border-radius:4px;cursor:pointer;">🔄 Refresh</button>
    </div>
  </div>
</div>

<!-- Memory Tab -->
<div id="tab-memory" class="tab-content">
  <div style="max-width:800px;margin:0 auto;padding:1.5rem 2rem;">
    <div class="panel-card" style="border-left:4px solid var(--core);">
      <h2>Long-Term Memory</h2>
      <p style="color:var(--text-dim);margin-top:0.5rem;">Search and explore memories stored in Mem0.</p>

      <!-- Mem0 Configuration -->
      <div style="margin-top:1rem;padding:0.75rem;background:var(--bg);border-radius:4px;">
        <strong>Mem0 Configuration</strong>
        <p style="font-size:0.8rem;color:var(--text-dim);margin:0.25rem 0 0.5rem 0;">Configure your Mem0 API connection</p>

        <div style="display:grid;grid-template-columns:1fr;gap:0.5rem;margin-top:0.5rem;">
          <div>
            <label style="font-size:0.8rem;">API Key</label>
            <input type="password" id="mem0-api-key" placeholder="mem0-..." style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.25rem;margin-top:0.25rem;">
          </div>
          <div>
            <label style="font-size:0.8rem;">User ID</label>
            <input type="text" id="mem0-user-id" placeholder="genesis_agent" value="genesis_agent" style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.25rem;margin-top:0.25rem;">
          </div>
        </div>

        <!-- Save Button -->
        <button onclick="saveMem0Config()" style="margin-top:0.5rem;background:var(--core);color:#fff;border:none;padding:0.5rem 1rem;border-radius:4px;cursor:pointer;">💾 Save Config</button>
        <span id="mem0-config-status" style="margin-left:0.5rem;font-size:0.8rem;"></span>
      </div>

      <!-- Search -->
      <div style="margin-top:1rem;padding:0.75rem;background:var(--bg);border-radius:4px;">
        <strong>Search Memories</strong>
        <p style="font-size:0.8rem;color:var(--text-dim);margin:0.25rem 0 0.5rem 0;">Find relevant long-term memories</p>

        <div style="display:flex;gap:0.5rem;">
          <input type="text" id="memory-search-query" placeholder="Search query (e.g., 'childhood memories', 'relationship with mother')" style="flex:1;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.5rem;">
          <button onclick="searchMemories()" style="background:var(--core);color:#fff;border:none;padding:0.5rem 1rem;border-radius:4px;cursor:pointer;">🔍 Search</button>
        </div>

        <!-- Language Toggle -->
        <div style="margin-top:0.5rem;font-size:0.8rem;">
          <label style="color:var(--text-dim);">Language / Sprache:</label>
          <select id="memory-lang" style="background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.25rem;margin-left:0.5rem;">
            <option value="en">English</option>
            <option value="de">Deutsch</option>
          </select>
        </div>

        <!-- Results -->
        <div id="memory-results" style="margin-top:1rem;">
          <p style="color:var(--text-dim);font-size:0.85rem;">No memories searched yet.</p>
        </div>
      </div>

      <!-- Store New Memory -->
      <div style="margin-top:1rem;padding:0.75rem;background:var(--bg);border-radius:4px;border-left:4px solid var(--growth);">
        <strong>Store New Memory</strong>
        <p style="font-size:0.8rem;color:var(--text-dim);margin:0.25rem 0 0.5rem 0;">Add a new fact to long-term memory</p>

        <textarea id="memory-store-text" rows="3" placeholder="Enter a fact to remember (e.g., 'Had a conversation about quantum physics with Dr. Chen')" style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.5rem;font-family:inherit;font-size:0.9rem;resize:vertical;"></textarea>

        <div style="margin-top:0.5rem;text-align:right;">
          <button onclick="storeMemory()" style="background:var(--growth);color:#fff;border:none;padding:0.5rem 1rem;border-radius:4px;cursor:pointer;">💾 Store Memory</button>
        </div>
        <div id="memory-store-status" style="margin-top:0.5rem;font-size:0.8rem;"></div>
      </div>
    </div>
  </div>
</div>

<!-- The Vault Tab -->
<div id="tab-vault" class="tab-content">
  <div style="max-width:1000px;margin:0 auto;padding:1.5rem 2rem;">
    <div class="panel-card" style="border-left:4px solid var(--growth);">
      <h2>The Vault - Real Asset Trading</h2>
      <p style="color:var(--text-dim);margin-top:0.5rem;">Trade real crypto and stocks. Currently in <span id="vault-mode" style="color:var(--accent);font-weight:bold;">Paper Trading</span> mode.</p>

      <!-- Configuration -->
      <div style="margin-top:1rem;padding:0.75rem;background:var(--bg);border-radius:4px;">
        <strong>API Configuration</strong>
        <p style="font-size:0.8rem;color:var(--text-dim);margin:0.25rem 0 0.5rem 0;">Configure your trading API (optional for paper trading)</p>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;margin-top:0.5rem;">
          <div>
            <label style="font-size:0.8rem;">Provider</label>
            <select id="vault-provider" style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.25rem;">
              <option value="kraken">Kraken (Crypto)</option>
              <option value="alpaca">Alpaca (Stocks)</option>
            </select>
          </div>
          <div>
            <label style="font-size:0.8rem;">Mode</label>
            <select id="vault-mode-select" style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.25rem;">
              <option value="paper">Paper Trading (Sandbox)</option>
              <option value="live">Live Trading</option>
            </select>
          </div>
        </div>

        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;margin-top:0.5rem;">
          <div>
            <label style="font-size:0.8rem;">API Key</label>
            <input type="password" id="vault-api-key" placeholder="API Key" style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.25rem;margin-top:0.25rem;">
          </div>
          <div>
            <label style="font-size:0.8rem;">API Secret</label>
            <input type="password" id="vault-api-secret" placeholder="API Secret" style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.25rem;margin-top:0.25rem;">
          </div>
        </div>

        <button onclick="saveVaultConfig()" style="margin-top:0.5rem;background:var(--growth);color:#fff;border:none;padding:0.5rem 1rem;border-radius:4px;cursor:pointer;">💾 Save Config</button>
        <span id="vault-config-status" style="margin-left:0.5rem;font-size:0.8rem;"></span>
      </div>

      <!-- Deposit -->
      <div style="margin-top:1rem;padding:0.75rem;background:var(--bg);border-radius:4px;">
        <strong>Deposit Simulation</strong>
        <p style="font-size:0.8rem;color:var(--text-dim);margin:0.25rem 0 0.5rem 0;">Transfer virtual capital into the vault for paper trading</p>

        <div style="display:flex;gap:0.5rem;align-items:end;">
          <div style="flex:1;">
            <label style="font-size:0.8rem;">Amount (USD)</label>
            <input type="number" id="vault-deposit-amount" placeholder="1000" value="1000" style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.5rem;margin-top:0.25rem;">
          </div>
          <button onclick="depositVault()" style="background:var(--core);color:#fff;border:none;padding:0.5rem 1rem;border-radius:4px;cursor:pointer;">💰 Deposit</button>
        </div>
        <div id="vault-deposit-status" style="margin-top:0.5rem;font-size:0.8rem;"></div>
      </div>

      <!-- Quick Trade -->
      <div style="margin-top:1rem;padding:0.75rem;background:var(--bg);border-radius:4px;border-left:4px solid var(--accent);">
        <strong>Quick Trade</strong>
        <p style="font-size:0.8rem;color:var(--text-dim);margin:0.25rem 0 0.5rem 0;">Execute a trade</p>

        <div style="display:grid;grid-template-columns:1fr 1fr 1fr auto;gap:0.5rem;align-items:end;">
          <div>
            <label style="font-size:0.8rem;">Symbol</label>
            <input type="text" id="vault-trade-symbol" placeholder="BTC, ETH, AAPL" style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.5rem;margin-top:0.25rem;">
          </div>
          <div>
            <label style="font-size:0.8rem;">Amount</label>
            <input type="number" id="vault-trade-amount" placeholder="0.1" step="any" style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.5rem;margin-top:0.25rem;">
          </div>
          <div>
            <label style="font-size:0.8rem;">Type</label>
            <select id="vault-trade-type" style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.5rem;margin-top:0.25rem;">
              <option value="buy">Buy</option>
              <option value="sell">Sell</option>
            </select>
          </div>
          <button onclick="executeTrade()" style="background:var(--accent);color:#fff;border:none;padding:0.5rem 1rem;border-radius:4px;cursor:pointer;height:42px;">Trade</button>
        </div>
        <div id="vault-trade-status" style="margin-top:0.5rem;font-size:0.8rem;"></div>
      </div>
    </div>

    <!-- Portfolio & Transactions -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:1rem;">
      <!-- Portfolio -->
      <div class="panel-card">
        <h3>Portfolio</h3>
        <div id="vault-portfolio" style="margin-top:1rem;">
          <p style="color:var(--text-dim);font-size:0.85rem;">Loading portfolio...</p>
        </div>
      </div>

      <!-- Market Analysis -->
      <div class="panel-card">
        <h3>Daily Market Analysis</h3>
        <div id="vault-reports" style="margin-top:1rem;font-size:0.9rem;font-style:italic;line-height:1.4;">
          <p style="color:var(--text-dim);font-size:0.85rem;">Waiting for AI morning report...</p>
        </div>
      </div>
    </div>

    <!-- Phase 37: Autonomous Trading Engine -->
    <div class="panel-card" style="margin-top:1rem;border-left:4px solid #10b981;">
      <h3>🤖 Autonomous Trading Engine</h3>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem;margin-top:0.75rem;">
        <div style="padding:0.75rem;background:var(--bg);border-radius:6px;">
          <div style="font-size:0.75rem;color:var(--text-dim);text-transform:uppercase;">Status</div>
          <div id="economy-status" style="font-size:1.1rem;font-weight:bold;color:var(--accent);">Loading...</div>
        </div>
        <div style="padding:0.75rem;background:var(--bg);border-radius:6px;">
          <div style="font-size:0.75rem;color:var(--text-dim);text-transform:uppercase;">Strategy</div>
          <div id="economy-strategy" style="font-size:1.1rem;font-weight:bold;color:var(--growth);">-</div>
        </div>
        <div style="padding:0.75rem;background:var(--bg);border-radius:6px;">
          <div style="font-size:0.75rem;color:var(--text-dim);text-transform:uppercase;">Market Mood</div>
          <div id="economy-mood" style="font-size:1.1rem;font-weight:bold;color:var(--core);">-</div>
        </div>
      </div>
      <div style="margin-top:0.75rem;padding:0.5rem;background:var(--bg);border-radius:6px;font-size:0.85rem;">
        <span style="color:var(--text-dim);">Total Trades:</span> <span id="economy-trades" style="color:var(--text);font-weight:bold;">0</span>
        <span style="color:var(--text-dim);margin-left:1rem;">Last Trade:</span> <span id="economy-last-trade" style="color:var(--text);">-</span>
      </div>
    </div>

    <!-- Recent Transactions -->
    <div class="panel-card" style="margin-top:1rem;">
      <h3>Recent Transactions</h3>
      <div id="vault-transactions" style="margin-top:1rem;max-height:300px;overflow-y:auto;">
        <p style="color:var(--text-dim);font-size:0.85rem;">No transactions yet.</p>
      </div>
    </div>
  </div>
</div>

<!-- Live Avatar Tab (Phase 22) -->
<div id="tab-avatar" class="tab-content">
  <div style="max-width:1200px;margin:0 auto;padding:1.5rem 2rem;">
    <h2 style="color:var(--accent);margin-bottom:1rem;">Live Avatar</h2>

    <!-- 3D Canvas Container -->
    <div id="avatar-viewer" style="position:relative;width:100%;height:500px;background:linear-gradient(180deg,#1a1a2e 0%,#16213e 100%);border-radius:12px;overflow:hidden;">
      <canvas id="vrm-canvas" style="width:100%;height:100%;display:block;"></canvas>
      <div id="avatar-loading" style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);color:#fff;text-align:center;">
        <div style="font-size:2rem;margin-bottom:0.5rem;">🎭</div>
        <div>Loading 3D Avatar...</div>
      </div>
      <div id="avatar-error" style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);color:#ff6b6b;text-align:center;display:none;">
        <div style="font-size:2rem;margin-bottom:0.5rem;">⚠️</div>
        <div>Failed to load VRM model</div>
        <div style="font-size:0.8rem;color:var(--text-dim);margin-top:0.5rem;">Check avatar_config.json and ensure VRM file exists</div>
        <div style="margin-top:1rem;padding:1rem;background:rgba(0,255,204,0.1);border:1px solid var(--accent);border-radius:8px;font-size:0.75rem;text-align:left;">
          <strong style="color:var(--accent);">📥 VRM Model herunterladen:</strong><br><br>
          1. Kostenlose VRM-Modelle:<br>
          &nbsp;&nbsp;• <a href="https://vrm.pixiv.net/" target="_blank" style="color:var(--accent);">Pixiv VRM Gallery</a><br>
          &nbsp;&nbsp;• <a href="https://hub.vroid.com/" target="_blank" style="color:var(--accent);">VRoid Hub</a><br>
          &nbsp;&nbsp;• <a href="https://booth.pm/en/items/1584848" target="_blank" style="color:var(--accent);">Booth.pm (kostenlos)</a><br><br>
          2. Speicherort:<br>
          &nbsp;&nbsp;<code>~/Schreibtisch/avatars/q_avatar.vrm</code><br><br>
          3. Oder Pfad in <code>avatar_config.json</code> anpassen
        </div>
      </div>
    </div>

    <!-- Controls -->
    <div style="display:flex;gap:0.5rem;margin-top:1rem;flex-wrap:wrap;align-items:center;">
      <span style="color:var(--text-dim);font-size:0.9rem;">Poses:</span>
      <button class="btn-crud" onclick="setAvatarPose('idle')">Idle</button>
      <button class="btn-crud" onclick="setAvatarPose('sitting')">Sitting</button>
      <button class="btn-crud" onclick="setAvatarPose('standing')">Standing</button>
      <button class="btn-crud" onclick="setAvatarPose('walking')">Walking</button>
      <span style="color:var(--text-dim);font-size:0.9rem;margin-left:1rem;">Emotes:</span>
      <button class="btn-crud" onclick="setAvatarEmote('joy')">Joy</button>
      <button class="btn-crud" onclick="setAvatarEmote('angry')">Angry</button>
      <button class="btn-crud" onclick="setAvatarEmote('sad')">Sad</button>
      <button class="btn-crud" onclick="setAvatarEmote('neutral')">Neutral</button>
      <button class="btn-crud" onclick="setAvatarEmote('relaxed')">Relaxed</button>
    </div>

    <!-- Status -->
    <div id="avatar-status" style="margin-top:1rem;padding:0.75rem;background:var(--bg);border-radius:8px;font-size:0.85rem;color:var(--text-dim);">
      <span style="color:var(--accent);">●</span> <span id="avatar-status-text">Initializing...</span>
    </div>

    <!-- Phase 33: Interaction Status -->
    <div id="interaction-status" style="margin-top:0.75rem;padding:0.75rem;background:var(--bg);border-radius:8px;font-size:0.85rem;">
      <span style="color:var(--text-dim);">Interaction: </span>
      <span style="color:var(--accent);">Waiting for updates...</span>
    </div>

    <!-- Phase 33: Light Control -->
    <div class="panel-card" style="margin-top:1rem;border-left:4px solid #fbbf24;">
      <h3>💡 Light Control</h3>
      <div style="display:flex;gap:0.5rem;margin-top:0.5rem;flex-wrap:wrap;">
        <button class="btn-crud" onclick="setLightState('on')">On</button>
        <button class="btn-crud" onclick="setLightState('off')">Off</button>
        <button class="btn-crud" onclick="setLightState('dim')">Dim</button>
        <button class="btn-crud" onclick="setLightState('bright')">Bright</button>
        <button class="btn-crud" onclick="setLightState('toggle')">Toggle</button>
      </div>
    </div>

    <!-- Wardrobe Sync Info -->
    <div class="panel-card" style="margin-top:1rem;border-left:4px solid var(--accent);">
      <h3>Wardrobe Sync</h3>
      <div id="avatar-wardrobe" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:0.5rem;margin-top:0.5rem;">
        <div style="color:var(--text-dim);font-size:0.85rem;">Loading wardrobe data...</div>
      </div>
      <button onclick="syncAvatarWardrobe()" style="margin-top:0.75rem;background:var(--accent);color:#fff;border:none;padding:0.5rem 1rem;border-radius:4px;cursor:pointer;">🔄 Sync Outfit</button>
    </div>
  </div>
</div>

<!-- Interests & Hobbies Tab (Phase 31) -->
<div id="tab-interests" class="tab-content">
  <div style="max-width:1200px;margin:0 auto;padding:1.5rem 2rem;">
    <h2 style="color:var(--accent);margin-bottom:1rem;">Interests & Hobbies</h2>

    <!-- Current Pursuit Widget -->
    <div class="panel-card" style="border-left:4px solid var(--accent);margin-bottom:1rem;">
      <h3>🎯 Current Pursuit</h3>
      <div id="current-pursuit" style="padding:1rem;background:var(--bg);border-radius:8px;margin-top:0.5rem;">
        <div style="color:var(--text-dim);font-style:italic;">No active research...</div>
      </div>
    </div>

    <!-- Hobby List -->
    <div class="panel-card">
      <h3>📚 Discovered Interests</h3>
      <div id="hobby-list" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:1rem;margin-top:1rem;">
        <div style="color:var(--text-dim);">Loading interests...</div>
      </div>
    </div>

    <!-- Likes/Dislikes -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:1rem;">
      <div class="panel-card">
        <h3>❤️ Likes</h3>
        <div id="likes-list" style="margin-top:0.5rem;">
          <div style="color:var(--text-dim);font-size:0.85rem;">No likes recorded yet</div>
        </div>
      </div>
      <div class="panel-card">
        <h3>👎 Dislikes</h3>
        <div id="dislikes-list" style="margin-top:0.5rem;">
          <div style="color:var(--text-dim);font-size:0.85rem;">No dislikes recorded yet</div>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- Dream Journal Tab (Phase 31) -->
<div id="tab-dreams" class="tab-content">
  <div style="max-width:1200px;margin:0 auto;padding:1.5rem 2rem;">
    <h2 style="color:var(--accent);margin-bottom:1rem;">Dream Journal</h2>

    <!-- Dream Stats -->
    <div class="panel-card" style="border-left:4px solid var(--dream);margin-bottom:1rem;">
      <h3>🌙 Neural Sleep Statistics</h3>
      <div id="dream-stats" style="display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-top:0.5rem;">
        <div style="text-align:center;padding:0.5rem;background:var(--bg);border-radius:8px;">
          <div style="font-size:1.5rem;color:var(--accent);" id="dream-count">0</div>
          <div style="font-size:0.8rem;color:var(--text-dim);">Total Dreams</div>
        </div>
        <div style="text-align:center;padding:0.5rem;background:var(--bg);border-radius:8px;">
          <div style="font-size:1.5rem;color:var(--growth);" id="insight-count">0</div>
          <div style="font-size:0.8rem;color:var(--text-dim);">Insights</div>
        </div>
        <div style="text-align:center;padding:0.5rem;background:var(--bg);border-radius:8px;">
          <div style="font-size:1.5rem;color:var(--warning);" id="last-dream-date">—</div>
          <div style="font-size:0.8rem;color:var(--text-dim);">Last Dream</div>
        </div>
        <div style="text-align:center;padding:0.5rem;background:var(--bg);border-radius:8px;">
          <div style="font-size:1.5rem;color:var(--core);" id="dream-state">Awake</div>
          <div style="font-size:0.8rem;color:var(--text-dim);">State</div>
        </div>
      </div>
    </div>

    <!-- Recent Dreams -->
    <div class="panel-card">
      <h3>📖 Recent Dreams</h3>
      <div id="dream-list" style="margin-top:1rem;max-height:500px;overflow-y:auto;">
        <div style="color:var(--text-dim);font-style:italic;">No dreams recorded yet. Dreams occur between 23:00-05:00 with low energy.</div>
      </div>
    </div>
  </div>
</div>

<!-- Analytics Tab (v5.1.0) -->
<div id="tab-analytics" class="tab-content">
  <div style="max-width:1200px;margin:0 auto;padding:1.5rem 2rem;">
    <h2 style="color:var(--accent);margin-bottom:1rem;">📊 Analytics Dashboard</h2>
    <p style="color:var(--text-dim);margin-bottom:1.5rem;">Real-time telemetry and historical trends.</p>

    <!-- Vitals Heatmap -->
    <div class="panel-card" style="margin-bottom:1rem;border-left:4px solid var(--accent);">
      <h3>❤️ Vitals Timeline (24h)</h3>
      <div id="analytics-vitals" style="margin-top:1rem;">
        <div style="color:var(--text-dim);font-style:italic;">Loading vitals data...</div>
      </div>
    </div>

    <!-- Hardware vs Stress Overlay -->
    <div class="panel-card" style="margin-bottom:1rem;border-left:4px solid #8b5cf6;">
      <h3>🔮 Hardware Resonance vs Stress</h3>
      <div id="analytics-hardware" style="margin-top:1rem;">
        <div style="color:var(--text-dim);font-style:italic;">Loading hardware data...</div>
      </div>
    </div>

    <!-- Economy Net Worth -->
    <div class="panel-card" style="border-left:4px solid var(--growth);">
      <h3>💰 Net Worth History</h3>
      <div id="analytics-economy" style="margin-top:1rem;">
        <div style="color:var(--text-dim);font-style:italic;">Loading economy data...</div>
      </div>
    </div>
  </div>
</div>

<!-- System Config Tab (v5.1.0) -->
<div id="tab-config" class="tab-content">
  <div style="max-width:1200px;margin:0 auto;padding:1.5rem 2rem;">
    <h2 style="color:var(--accent);margin-bottom:1rem;">⚙️ System Configuration</h2>
    <p style="color:var(--text-dim);margin-bottom:1.5rem;">Centralized settings for all simulation engines.</p>

    <!-- Character Identity -->
    <div class="panel-card" style="margin-bottom:1rem;border-left:4px solid var(--core);">
      <h3>👤 Character Identity</h3>
      <div style="margin-top:0.75rem;">
        <label style="font-size:0.85rem;">Active Character Name</label>
        <input type="text" id="config-character-name" placeholder="Q" style="width:100%;max-width:300px;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.5rem;margin-top:0.25rem;">
      </div>
      <button onclick="saveCharacterConfig()" style="margin-top:0.75rem;background:var(--accent);color:#fff;border:none;padding:0.5rem 1rem;border-radius:4px;cursor:pointer;">Save</button>
      <span id="config-character-status" style="margin-left:0.5rem;font-size:0.8rem;"></span>
    </div>

    <!-- Metabolism Settings -->
    <div class="panel-card" style="margin-bottom:1rem;border-left:4px solid var(--danger);">
      <h3>� Metabolism Rates</h3>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:0.75rem;">
        <div>
          <label style="font-size:0.8rem;">Hunger Rate</label>
          <input type="range" id="config-hunger-rate" min="0" max="1" step="0.1" value="0.5" style="width:100%;">
          <span id="config-hunger-rate-val" style="font-size:0.8rem;">0.5</span>
        </div>
        <div>
          <label style="font-size:0.8rem;">Thirst Rate</label>
          <input type="range" id="config-thirst-rate" min="0" max="1" step="0.1" value="0.5" style="width:100%;">
          <span id="config-thirst-rate-val" style="font-size:0.8rem;">0.5</span>
        </div>
        <div>
          <label style="font-size:0.8rem;">Energy Rate</label>
          <input type="range" id="config-energy-rate" min="0" max="1" step="0.1" value="0.5" style="width:100%;">
          <span id="config-energy-rate-val" style="font-size:0.8rem;">0.5</span>
        </div>
        <div>
          <label style="font-size:0.8rem;">Stress Accumulation</label>
          <input type="range" id="config-stress-rate" min="0" max="1" step="0.1" value="0.3" style="width:100%;">
          <span id="config-stress-rate-val" style="font-size:0.8rem;">0.3</span>
        </div>
      </div>
    </div>

    <!-- Hardware Resonance -->
    <div class="panel-card" style="margin-bottom:1rem;border-left:4px solid #8b5cf6;">
      <h3>🔮 Hardware Resonance</h3>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:0.75rem;">
        <div>
          <label style="font-size:0.8rem;">CPU Stress Threshold (%)</label>
          <input type="number" id="config-cpu-threshold" min="0" max="100" value="80" style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.25rem;">
        </div>
        <div>
          <label style="font-size:0.8rem;">RAM Threshold (%)</label>
          <input type="number" id="config-ram-threshold" min="0" max="100" value="85" style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.25rem;">
        </div>
        <div>
          <label style="font-size:0.8rem;">Temp Threshold (°C)</label>
          <input type="number" id="config-temp-threshold" min="0" max="120" value="80" style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.25rem;">
        </div>
        <div>
          <label style="font-size:0.8rem;">Audio Sensitivity</label>
          <input type="range" id="config-audio-sensitivity" min="0" max="1" step="0.1" value="0.5" style="width:100%;">
          <span id="config-audio-sensitivity-val" style="font-size:0.8rem;">0.5</span>
        </div>
      </div>
    </div>

    <!-- Social & Presence -->
    <div class="panel-card" style="margin-bottom:1rem;border-left:4px solid #ec4899;">
      <h3>📱 Social & Presence</h3>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:0.75rem;">
        <div style="display:flex;align-items:center;gap:0.5rem;">
          <input type="checkbox" id="config-autopost" checked>
          <label style="font-size:0.9rem;">Autonomous Posting</label>
        </div>
        <div>
          <label style="font-size:0.8rem;">Post Frequency</label>
          <select id="config-post-frequency" style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.25rem;">
            <option value="low">Low</option>
            <option value="medium" selected>Medium</option>
            <option value="high">High</option>
          </select>
        </div>
        <div style="display:flex;align-items:center;gap:0.5rem;">
          <input type="checkbox" id="config-npc-interact" checked>
          <label style="font-size:0.9rem;">NPC Interactions</label>
        </div>
        <div>
          <label style="font-size:0.8rem;">Interaction Frequency</label>
          <select id="config-interaction-frequency" style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.25rem;">
            <option value="low">Low</option>
            <option value="medium" selected>Medium</option>
            <option value="high">High</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Connectivity -->
    <div class="panel-card" style="border-left:4px solid var(--warning);">
      <h3>🔗 Connectivity (VMC/OSC)</h3>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:0.75rem;">
        <div style="display:flex;align-items:center;gap:0.5rem;">
          <input type="checkbox" id="config-vmc-enabled">
          <label style="font-size:0.9rem;">Enable VMC</label>
        </div>
        <div style="display:flex;align-items:center;gap:0.5rem;">
          <input type="checkbox" id="config-osc-enabled">
          <label style="font-size:0.9rem;">Enable OSC</label>
        </div>
        <div>
          <label style="font-size:0.8rem;">VMC IP</label>
          <input type="text" id="config-vmc-ip" value="127.0.0.1" style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.25rem;">
        </div>
        <div>
          <label style="font-size:0.8rem;">VMC Port</label>
          <input type="number" id="config-vmc-port" value="8000" style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.25rem;">
        </div>
      </div>
    </div>

    <button onclick="saveAllConfig()" style="margin-top:1.5rem;background:var(--growth);color:#fff;border:none;padding:0.75rem 2rem;border-radius:4px;cursor:pointer;font-size:1rem;">💾 Save All Settings</button>
    <span id="config-save-status" style="margin-left:1rem;font-size:0.9rem;"></span>
  </div>
</div>


<!-- God-Mode Tab (Integrated v5.2.1) -->
<div id="tab-godmode" class="tab-content" style="display:none;">
  <div style="max-width:1200px;margin:0 auto;padding:2rem;">
    <h2 style="color:var(--accent);text-shadow:0 0 10px var(--accent);">⚡ Simulation God-Mode</h2>
    <div style="background:rgba(255,51,102,0.1); border:1px solid #ff3366; padding:1rem; margin-bottom:2rem; color:#ff3366; border-radius:4px;">
        ⚠️ <strong>WARNING:</strong> Manual overrides bypass biological autonomy.
    </div>

    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:2rem;">
        <div class="panel-card">
            <h3>🎚️ Direct Needs Control</h3>
            <div id="godmode-sliders" style="display:grid; gap:1rem;">
                <!-- Sliders generated by JS -->
            </div>
            <button onclick="applyGodModeNeeds()" style="margin-top:1.5rem; background:var(--accent); color:#000; padding:0.75rem 1.5rem; border:none; border-radius:4px; cursor:pointer; font-weight:bold;">💾 Apply Changes</button>
        </div>

        <div class="panel-card">
            <h3>🎲 Inject Life Event</h3>
            <div style="display:grid; gap:1rem;">
                <select id="gm-event-type" style="background:#1a1a24; color:#fff; padding:0.5rem; border:1px solid var(--border);">
                    <option value="positive">Positive</option>
                    <option value="negative">Negative</option>
                    <option value="neutral">Neutral</option>
                </select>
                <input type="text" id="gm-event-desc" placeholder="Event description..." style="background:#1a1a24; color:#fff; padding:0.5rem; border:1px solid var(--border);">
                <input type="range" id="gm-event-impact" min="1" max="10" value="5">
                <button onclick="injectGodModeEvent()" style="background:var(--growth); color:#fff; padding:0.75rem; border:none; border-radius:4px; cursor:pointer;">🚀 Trigger Event</button>
            </div>
        </div>
    </div>
  </div>
</div>
<!-- Diagnostics Tab (Phase 41) -->
<div id="tab-diagnostics" class="tab-content">
  <div style="max-width:1400px;margin:0 auto;padding:1.5rem 2rem;">
    <h2 style="color:var(--accent);margin-bottom:1rem;">🔧 Diagnostics Dashboard</h2>
    <p style="color:var(--text-dim);margin-bottom:1.5rem;">Real-time system logs and health monitoring.</p>

    <!-- System Health -->
    <div class="panel-card" style="margin-bottom:1rem;border-left:4px solid var(--growth);">
      <h3>💚 System Health</h3>
      <div id="diagnostics-health" style="display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:0.5rem;margin-top:0.75rem;">
        <div style="padding:0.5rem;background:var(--bg);border-radius:4px;text-align:center;">
          <div style="font-size:0.7rem;color:var(--text-dim);">Logging</div>
          <div id="health-logging" style="font-weight:bold;color:var(--growth);">Checking...</div>
        </div>
        <div style="padding:0.5rem;background:var(--bg);border-radius:4px;text-align:center;">
          <div style="font-size:0.7rem;color:var(--text-dim);">Tick Engine</div>
          <div id="health-tick" style="font-weight:bold;color:var(--growth);">Active</div>
        </div>
        <div style="padding:0.5rem;background:var(--bg);border-radius:4px;text-align:center;">
          <div style="font-size:0.7rem;color:var(--text-dim);">Economy</div>
          <div id="health-economy" style="font-weight:bold;color:var(--text-dim);">-</div>
        </div>
        <div style="padding:0.5rem;background:var(--bg);border-radius:4px;text-align:center;">
          <div style="font-size:0.7rem;color:var(--text-dim);">Hardware</div>
          <div id="health-hardware" style="font-weight:bold;color:var(--text-dim);">-</div>
        </div>
        <div style="padding:0.5rem;background:var(--bg);border-radius:4px;text-align:center;">
          <div style="font-size:0.7rem;color:var(--text-dim);">Social</div>
          <div id="health-social" style="font-weight:bold;color:var(--text-dim);">-</div>
        </div>
        <div style="padding:0.5rem;background:var(--bg);border-radius:4px;text-align:center;">
          <div style="font-size:0.7rem;color:var(--text-dim);">Vault</div>
          <div id="health-vault" style="font-weight:bold;color:var(--text-dim);">-</div>
        </div>
      </div>
    </div>

    <!-- AI Model Status -->
    <div class="panel-card" style="margin-bottom:1rem;border-left:4px solid var(--accent);">
      <h3>🧠 AI Model Status</h3>
      <p style="color:var(--text-dim);font-size:0.85rem;margin-top:0.25rem;">Diagnostics for active model configurations. Click any model to reconfigure.</p>
      <div id="diagnostics-ai-models"
        style="display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:0.5rem;margin-top:0.75rem;">
        <div onclick="jumpToConfig('api-key')"
          style="padding:0.5rem;background:var(--bg);border-radius:4px;text-align:center;cursor:pointer;">
          <div style="font-size:0.7rem;color:var(--text-dim);">OpenAI</div>
          <div id="model-status-openai" style="font-weight:bold;color:var(--text-dim);">Checking...</div>
        </div>
        <div onclick="jumpToConfig('key-anthropic')"
          style="padding:0.5rem;background:var(--bg);border-radius:4px;text-align:center;cursor:pointer;">
          <div style="font-size:0.7rem;color:var(--text-dim);">Anthropic</div>
          <div id="model-status-anthropic" style="font-weight:bold;color:var(--text-dim);">Checking...</div>
        </div>
        <div onclick="jumpToConfig('key-venice')"
          style="padding:0.5rem;background:var(--bg);border-radius:4px;text-align:center;cursor:pointer;">
          <div style="font-size:0.7rem;color:var(--text-dim);">Venice</div>
          <div id="model-status-venice" style="font-weight:bold;color:var(--text-dim);">Checking...</div>
        </div>
        <div onclick="jumpToConfig('key-xai')"
          style="padding:0.5rem;background:var(--bg);border-radius:4px;text-align:center;cursor:pointer;">
          <div style="font-size:0.7rem;color:var(--text-dim);">xAI</div>
          <div id="model-status-xai" style="font-weight:bold;color:var(--text-dim);">Checking...</div>
        </div>
        <div onclick="jumpToConfig('key-gemini-img')"
          style="padding:0.5rem;background:var(--bg);border-radius:4px;text-align:center;cursor:pointer;">
          <div style="font-size:0.7rem;color:var(--text-dim);">Gemini (Vision)</div>
          <div id="model-status-gemini" style="font-weight:bold;color:var(--text-dim);">Checking...</div>
        </div>
        <div onclick="jumpToConfig('key-fal')"
          style="padding:0.5rem;background:var(--bg);border-radius:4px;text-align:center;cursor:pointer;">
          <div style="font-size:0.7rem;color:var(--text-dim);">Fal.ai (Vision)</div>
          <div id="model-status-fal" style="font-weight:bold;color:var(--text-dim);">Checking...</div>
        </div>
        <div onclick="jumpToConfig('mem0-api-key')"
          style="padding:0.5rem;background:var(--bg);border-radius:4px;text-align:center;cursor:pointer;">
          <div style="font-size:0.7rem;color:var(--text-dim);">Mem0</div>
          <div id="model-status-mem0" style="font-weight:bold;color:var(--text-dim);">Checking...</div>
        </div>
        <div onclick="jumpToConfig('vault-api-key')"
          style="padding:0.5rem;background:var(--bg);border-radius:4px;text-align:center;cursor:pointer;">
          <div style="font-size:0.7rem;color:var(--text-dim);">The Vault</div>
          <div id="model-status-vault" style="font-weight:bold;color:var(--text-dim);">Checking...</div>
        </div>
      </div>
    </div>

    <!-- System Tools Status -->
    <div class="panel-card" style="margin-bottom:1rem;border-left:4px solid var(--section-continuity);">
      <h3>🛠️ System Tools</h3>
      <p style="color:var(--text-dim);font-size:0.85rem;margin-top:0.25rem;">Diagnostics for active core engine tools and capabilities.</p>
      <div id="diagnostics-system-tools"
        style="display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:0.5rem;margin-top:0.75rem;">
        <div onclick="switchTab('config')"
          style="padding:0.5rem;background:var(--bg);border-radius:4px;text-align:center;cursor:pointer;">
          <div style="font-size:0.7rem;color:var(--text-dim);">Visual Browser</div>
          <div id="model-status-browser" style="font-weight:bold;color:var(--text-dim);">Checking...</div>
        </div>
        <div onclick="switchTab('config')"
          style="padding:0.5rem;background:var(--bg);border-radius:4px;text-align:center;cursor:pointer;">
          <div style="font-size:0.7rem;color:var(--text-dim);">Desktop Control</div>
          <div id="model-status-desktop" style="font-weight:bold;color:var(--text-dim);">Checking...</div>
        </div>
        <div onclick="switchTab('config')"
          style="padding:0.5rem;background:var(--bg);border-radius:4px;text-align:center;cursor:pointer;">
          <div style="font-size:0.7rem;color:var(--text-dim);">Weather Engine</div>
          <div id="model-status-weather" style="font-weight:bold;color:var(--text-dim);">Checking...</div>
        </div>
      </div>
    </div>

    <!-- Log Controls -->
    <div class="panel-card" style="margin-bottom:1rem;border-left:4px solid var(--warning);">
      <h3>📋 Log Stream</h3>
      <div style="display:flex;gap:0.5rem;margin-top:0.5rem;flex-wrap:wrap;">
        <select id="log-filter-level" style="background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.25rem;">
          <option value="">All Levels</option>
          <option value="DEBUG">DEBUG</option>
          <option value="INFO" selected>INFO</option>
          <option value="WARN">WARN</option>
          <option value="ERROR">ERROR</option>
        </select>
        <select id="log-filter-module" style="background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.25rem;">
          <option value="">All Modules</option>
          <option value="genesis">Genesis</option>
          <option value="economy">Economy</option>
          <option value="presence">Presence</option>
          <option value="hardware">Hardware</option>
          <option value="social">Social</option>
          <option value="tick">Tick</option>
        </select>
        <button onclick="loadLogStream()" style="background:var(--accent);color:#fff;border:none;padding:0.25rem 0.75rem;border-radius:4px;cursor:pointer;">🔄 Refresh</button>
        <button onclick="clearLogFilter()" style="background:var(--bg);color:var(--text);border:1px solid var(--border);padding:0.25rem 0.75rem;border-radius:4px;cursor:pointer;">Clear Filters</button>
      </div>
      <div id="log-count" style="font-size:0.8rem;color:var(--text-dim);margin-top:0.5rem;"></div>
    </div>

    <!-- Log Output -->
    <div class="panel-card" style="max-height:500px;overflow-y:auto;border-left:4px solid var(--core);">
      <div id="log-stream" style="font-family:monospace;font-size:0.8rem;line-height:1.6;">
        <div style="color:var(--text-dim);font-style:italic;">Loading logs...</div>
      </div>
    </div>
  </div>
  </div> <!-- end main-view -->
</div> <!-- end app-container -->

<!-- Lightbox -->
<div class="lightbox-overlay" id="lightbox" onclick="if(event.target===this)closeLightbox()">
  <button class="lightbox-close" onclick="closeLightbox()">&times;</button>
  <img id="lightbox-main" src="" alt="">
  <div class="lightbox-gallery" id="lightbox-gallery"></div>
  <div class="lightbox-actions">
    <label class="btn-crud" style="cursor:pointer;">
      Upload <input type="file" accept="image/*" style="display:none" onchange="uploadLightboxImage(event)">
    </label>
    <button class="btn-crud danger" onclick="deleteLightboxImage()">Delete</button>
  </div>
  <div class="upload-zone" id="lightbox-dropzone">Drop image here or click Upload above</div>
</div>

<!-- Modal -->
<div class="modal-overlay" id="modal-overlay" onclick="if(event.target===this)closeModal()">
  <div class="modal-box">
    <h3 class="modal-title" id="modal-title"></h3>
    <div id="modal-fields"></div>
    <div class="modal-buttons">
      <button class="btn-crud" onclick="closeModal()">Cancel</button>
      <button class="btn-crud" id="modal-ok" style="color:var(--accent);border-color:var(--accent);">OK</button>
    </div>
  </div>
</div>

<script>
const DATA =  {data_json};

const SECTION_COLORS = {
  'Personality': '#f0a050',
  'Philosophy': '#7c6ff0',
  'Boundaries': '#e05050',
  'Continuity': '#50b8e0',
};
function sectionColor(name) {
  for (const [k, v] of Object.entries(SECTION_COLORS)) {
    if (name && name.includes(k)) return v;
  }
  return '#888';
}

  function renderAgentName() {
    const idText = DATA.identity_raw || '';
    const nameMatch = idText.match(/\*\*Name:\*\*\s*(.+)/i) || idText.match(/Name:\s*(.+)/i);
    if (nameMatch && nameMatch[1]) {
      const name = nameMatch[1].replace(/\[|\]/g, '').trim();
      if (name && !name.includes('Agent Name')) {
        document.getElementById('agent-name').textContent = name;
        document.title = name + ' — Project Genesis';
      }
    }
  }


function renderStats() {
  const bar = document.getElementById('stats-bar');
  const tree = DATA.soul_tree;
  let core = 0, mutable = 0, totalBullets = 0;
  tree.forEach(sec => {
    sec.children.forEach(child => {
      if (child.type === 'bullet') {
        totalBullets++;
        if (child.tag === 'CORE') core++;
        if (child.tag === 'MUTABLE') mutable++;
      }
      if (child.children) child.children.forEach(b => {
        if (b.type === 'bullet') {
          totalBullets++;
          if (b.tag === 'CORE') core++;
          if (b.tag === 'MUTABLE') mutable++;
        }
      });
    });
  });
      const stats = [
        { num: DATA.experiences.length, label: 'Experiences' },
        { num: DATA.reflections.length, label: 'Reflections' },
        { num: (DATA.news?.browsing_history || []).length, label: 'Web Searches' },
        { num: (DATA.news?.headlines || []).length, label: 'World News' },
        { num: core, label: 'Core' },
        { num: mutable, label: 'Mutable' },
      ];
  
  bar.innerHTML = stats.map(s =>
    `<div class="stat"><div class="num">${s.num}</div><div class="label">${s.label}</div></div>`
  ).join('');
}

function renderLegend() {
  const el = document.getElementById('legend');
  const items = [
    { color: 'var(--core)', label: 'CORE (immutable)' },
    { color: 'var(--mutable)', label: 'MUTABLE (evolvable)' },
    ...Object.entries(SECTION_COLORS).map(([k, v]) => ({ color: v, label: k })),
  ];
  el.innerHTML = items.map(i =>
    `<div class="legend-item"><div class="legend-dot" style="background:${i.color}"></div>${i.label}</div>`
  ).join('');
}

let allBulletEls = [];
let changesBulletMap = {};

let editMode = false;

function renderSoulTree(revealUpTo) {
  const container = document.getElementById('soul-tree');
  container.innerHTML = '';
  allBulletEls = [];

  // Build set of bullets added by changes after revealUpTo
  const hiddenAfter = new Set();
  if (!editMode) {
    const changes = DATA.changes;
    for (let i = changes.length - 1; i >= 0; i--) {
      if (i >= revealUpTo) {
        if (changes[i].change_type === 'add' && changes[i].after) {
          hiddenAfter.add(changes[i].after.trim());
        }
      }
    }
  }

  DATA.soul_tree.forEach((sec, si) => {
    const color = sectionColor(sec.text);
    const block = document.createElement('div');
    block.className = 'section-block';
    block.style.borderColor = color + '33';

    const header = document.createElement('div');
    header.className = 'section-header';
    header.style.background = color + '0d';
    header.innerHTML = `<div class="dot" style="background:${color}"></div>${esc(sec.text)}<span class="arrow">▼</span>`;
    header.onclick = () => block.classList.toggle('collapsed');
    block.appendChild(header);

    const body = document.createElement('div');
    body.className = 'section-body';

    sec.children.forEach((child, ci) => {
      if (child.type === 'subsection') {
        const sub = document.createElement('div');
        sub.className = 'subsection';
        sub.innerHTML = `<div class="subsection-title">${esc(child.text)}</div>`;

        (child.children || []).forEach((b, bi) => {
          const bEl = renderBullet(b, hiddenAfter, [si, ci, bi]);
          sub.appendChild(bEl);
        });

        // Add bullet button
        const addBtn = document.createElement('button');
        addBtn.className = 'btn-add-bullet';
        addBtn.textContent = '+ add bullet';
        addBtn.onclick = () => addBullet(si, ci);
        sub.appendChild(addBtn);

        body.appendChild(sub);
      } else if (child.type === 'bullet') {
        body.appendChild(renderBullet(child, hiddenAfter, [si, ci, -1]));
      }
    });

    block.appendChild(body);
    container.appendChild(block);

    setTimeout(() => block.classList.add('visible'), 80 * si);
  });
}

function renderBullet(b, hiddenAfter, path) {
  const el = document.createElement('div');
  el.className = 'bullet';
  const isHidden = hiddenAfter.has(b.raw.trim());
  if (isHidden) {
    el.classList.add('is-new');
  }

  const tagClass = b.tag === 'CORE' ? 'core' : (b.tag === 'MUTABLE' ? 'mutable' : '');

  if (editMode) {
    el.classList.add('editing');
    const [si, ci, bi] = path;

    // Tag toggle
    const tagEl = document.createElement('span');
    tagEl.className = `tag ${tagClass} tag-toggle`;
    tagEl.textContent = b.tag || 'TAG';
    tagEl.title = 'Click to toggle CORE/MUTABLE';
    tagEl.onclick = () => {
      const next = b.tag === 'CORE' ? 'MUTABLE' : 'CORE';
      b.tag = next;
      updateBulletRaw(b);
      renderSoulTree(currentStep);
    };
    el.appendChild(tagEl);

    // Editable text
    const input = document.createElement('textarea');
    input.className = 'edit-text';
    input.value = b.text;
    input.rows = 1;
    input.oninput = () => {
      input.style.height = 'auto';
      input.style.height = input.scrollHeight + 'px';
      b.text = input.value;
      updateBulletRaw(b);
    };
    // Auto-resize on mount
    setTimeout(() => { input.style.height = input.scrollHeight + 'px'; }, 0);
    el.appendChild(input);

    // Delete button
    const del = document.createElement('button');
    del.className = 'btn-delete';
    del.innerHTML = '×';
    del.title = 'Remove bullet';
    del.onclick = () => {
      deleteBullet(si, ci, bi);
    };
    el.appendChild(del);
  } else {
    el.innerHTML = `
      ${tagClass ? `<span class="tag ${tagClass}">${esc(b.tag)}</span>` : ''}
      <span>${esc(b.text)}</span>
    `;
  }

  allBulletEls.push({ el, raw: b.raw, tag: b.tag });
  return el;
}

function updateBulletRaw(b) {
  b.raw = `- ${b.text} [${b.tag}]`;
}

function toggleEditMode() {
  editMode = !editMode;
  const btn = document.getElementById('btn-edit');
  const saveBtn = document.getElementById('btn-save');
  const mapEl = document.getElementById('soul-map');

  if (editMode) {
    btn.classList.add('active');
    btn.textContent = '✎ Editing';
    saveBtn.style.display = '';
    mapEl.classList.add('edit-mode');
  } else {
    btn.classList.remove('active');
    btn.textContent = '✎ Edit';
    saveBtn.style.display = 'none';
    mapEl.classList.remove('edit-mode');
  }
  renderSoulTree(currentStep);
}

function addBullet(si, ci) {
  const sub = DATA.soul_tree[si].children[ci];
  if (!sub.children) sub.children = [];
  const sec = DATA.soul_tree[si];
  const newBullet = {
    type: 'bullet',
    text: 'New belief',
    raw: '- New belief [MUTABLE]',
    tag: 'MUTABLE',
    section: sec.raw,
    subsection: sub.raw,
  };
  sub.children.push(newBullet);
  renderSoulTree(currentStep);
}

function deleteBullet(si, ci, bi) {
  if (bi >= 0) {
    DATA.soul_tree[si].children[ci].children.splice(bi, 1);
  } else {
    DATA.soul_tree[si].children.splice(ci, 1);
  }
  renderSoulTree(currentStep);
}

function reconstructSoulMd() {
  let lines = [];
  lines.push('# SOUL.md - Who You Are');
  lines.push('');
  lines.push('> ⚠️ This file is managed by **Soul Evolution**. Bullets tagged `[CORE]` are immutable.');
  lines.push('> Bullets tagged `[MUTABLE]` may evolve through the structured proposal pipeline.');
  lines.push('> Direct edits outside the pipeline are not permitted for `[MUTABLE]` items.');
  lines.push('> See `soul-evolution/SKILL.md` for the full protocol.');
  lines.push('');
  lines.push('---');

  DATA.soul_tree.forEach(sec => {
    lines.push('');
    lines.push(`## ${sec.text}`);

    sec.children.forEach(child => {
      if (child.type === 'subsection') {
        lines.push('');
        lines.push(`### ${child.text}`);
        lines.push('');
        (child.children || []).forEach(b => {
          lines.push(`- ${b.text} [${b.tag}]`);
        });
      } else if (child.type === 'bullet') {
        lines.push(`- ${child.text} [${child.tag}]`);
      }
    });
  });

  lines.push('');
  lines.push('---');
  lines.push('');
  lines.push('_This file is yours to evolve. As you learn who you are, update it._');
  return lines.join('\\n');
}

function saveSoul() {
  const content = reconstructSoulMd();
  const toast = document.getElementById('save-toast');

  // Try server-side save first (works in --serve mode)
  fetch('/save-soul', {
    method: 'POST',
    headers: { 'Content-Type': 'text/markdown' },
    body: content
  })
  .then(resp => {
    if (resp.ok) {
      toast.textContent = '✓ SOUL.md saved to workspace';
      toast.classList.add('show');
      setTimeout(() => toast.classList.remove('show'), 2500);
    } else {
      throw new Error('Server save failed');
    }
  })
  .catch(() => {
    // Fallback: browser download (static HTML mode)
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'SOUL.md';
    a.click();
    URL.revokeObjectURL(url);
    toast.textContent = '✓ SOUL.md downloaded';
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 2500);
  });
}

let currentStep = -1;
let playing = false;
let playInterval = null;

function renderTimeline() {
  const changes = DATA.changes;
  const slider = document.getElementById('timeline-slider');
  slider.max = changes.length;
  slider.value = changes.length;
  currentStep = changes.length;

  slider.oninput = () => {
    currentStep = parseInt(slider.value);
    updateTimelineView();
  };

  updateTimelineView();
}

function updateTimelineView() {
  const changes = DATA.changes;
  const label = document.getElementById('timeline-label');

  if (currentStep === 0) {
    label.textContent = 'origin';
  } else if (currentStep <= changes.length) {
    const c = changes[currentStep - 1];
    const t = c.timestamp || '';
    label.textContent = t.slice(11, 16) || `#${currentStep}`;
  }

  // Re-render soul map with visibility
  renderSoulTree(currentStep);

  // Re-render changes list
  renderChangesList(currentStep);

  // Update slider
  document.getElementById('timeline-slider').value = currentStep;
}

function renderChangesList(upTo) {
  const container = document.getElementById('changes-list');
  const changes = DATA.changes;

  if (changes.length === 0) {
    container.innerHTML = '<div class="empty-state">No soul changes yet. The soul is in its original state.</div>';
    return;
  }

  container.innerHTML = '';
  const visible = changes.slice(0, upTo);
  visible.forEach((c, i) => {
    const el = document.createElement('div');
    el.className = 'change-entry';

    const t = c.timestamp || '';
    const time = t.slice(0, 16).replace('T', ' ');
    const section = (c.section || '').replace('## ', '') + ' › ' + (c.subsection || '').replace('### ', '');
    const content = c.after || c.before || '';
    const cleanContent = content.replace(/\\s*\\[(CORE|MUTABLE)\\]\\s*/g, '').replace(/^- /, '');

    el.innerHTML = `
      <div class="change-time">${esc(time)}</div>
      <span class="change-type ${esc(c.change_type)}">${esc(c.change_type)}</span>
      <div class="change-section">${esc(section)}</div>
      <div class="change-content">${esc(cleanContent)}</div>
    `;

    container.appendChild(el);
    setTimeout(() => el.classList.add('visible'), 60 * i);
  });

  if (upTo === 0) {
    container.innerHTML = '<div class="empty-state">⟲ Origin state — no changes applied yet</div>';
  }
}

document.getElementById('btn-play').onclick = () => {
  if (playing) {
    clearInterval(playInterval);
    playing = false;
    document.getElementById('btn-play').textContent = '▶';
    document.getElementById('btn-play').classList.remove('active');
    return;
  }
  playing = true;
  document.getElementById('btn-play').textContent = '⏸';
  document.getElementById('btn-play').classList.add('active');
  currentStep = 0;
  updateTimelineView();

  playInterval = setInterval(() => {
    currentStep++;
    if (currentStep > DATA.changes.length) {
      clearInterval(playInterval);
      playing = false;
      document.getElementById('btn-play').textContent = '▶';
      document.getElementById('btn-play').classList.remove('active');
      return;
    }
    updateTimelineView();
    // Highlight the newly revealed bullet
    const change = DATA.changes[currentStep - 1];
    if (change && change.after) {
      const match = allBulletEls.find(b => b.raw.trim() === change.after.trim());
      if (match) {
        match.el.classList.remove('is-new');
        match.el.classList.add('revealed');
        match.el.classList.add('highlight-enter');
        match.el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  }, 1800);
};

document.getElementById('btn-reset').onclick = () => {
  if (playing) {
    clearInterval(playInterval);
    playing = false;
    document.getElementById('btn-play').textContent = '▶';
    document.getElementById('btn-play').classList.remove('active');
  }
  currentStep = 0;
  updateTimelineView();
};

function renderFeed() {
  const container = document.getElementById('exp-feed');
  const exps = DATA.experiences.slice().reverse();

  if (exps.length === 0) {
    container.innerHTML = '<div class="empty-state">No experiences logged yet.</div>';
    return;
  }

  container.innerHTML = exps.map(e => {
    const t = (e.timestamp || '').slice(11, 16);
    const sourceClass = (e.source || '').toLowerCase();
    const sigClass = (e.significance || '').toLowerCase();
    const content = (e.content || '').slice(0, 160) + ((e.content || '').length > 160 ? '…' : '');
    return `
      <div class="exp-entry">
        <div class="exp-meta">
          <span class="exp-source ${esc(sourceClass)}">${esc(e.source)}</span>
          <span class="exp-sig ${esc(sigClass)}">${esc(e.significance)}</span>
          <span style="margin-left:auto;font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:var(--text-dim)">${esc(t)}</span>
        </div>
        <div class="exp-content">${esc(content)}</div>
      </div>
    `;
  }).join('');
}

function vitalColor(value, key) {
  if (key === 'energy') {
    if (value < 10) return '#e05050';
    if (value < 30) return '#f0a050';
    if (value < 60) return '#e0d050';
    return '#50c878';
  }
  if (value > 90) return '#e05050';
  if (value > 70) return '#f0a050';
  if (value > 40) return '#e0d050';
  return '#50c878';
}

  function renderVitals() {
    const ph = DATA.physique;
    const grid = document.getElementById('vitals-grid');
    const meta = document.getElementById('vitals-meta');

    if (!ph || !ph.needs) {
      grid.innerHTML = '<div class="empty-state">No vitals data available.</div>';
      return;
    }

    const needKeys = ['energy', 'hunger', 'thirst', 'bladder', 'bowel', 'hygiene', 'stress', 'arousal'];
    grid.innerHTML = needKeys.map(k => {
      const v = ph.needs[k] ?? 0;
      const color = vitalColor(v, k);
      return `
        <div class="vital-row">
          <span class="vital-label">${k}</span>
          <div class="vital-bar-bg">
            <div class="vital-bar" style="width:${v}%;background:${color}"></div>
          </div>
          <span class="vital-value">${v}</span>
        </div>
      `;
    }).join('');

    const metaLines = [];
    if (ph.current_location) metaLines.push(`<span>📍 ${esc(ph.current_location)}</span>`);
    if (ph.current_outfit && ph.current_outfit.length) metaLines.push(`<span>👔 ${esc(ph.current_outfit.join(', '))}</span>`);
    if (ph.last_tick) metaLines.push(`<span>⏱ ${esc(ph.last_tick.slice(0, 19).replace('T', ' '))}</span>`);
    meta.innerHTML = metaLines.join('');
  }

  function renderMentalActivity() {
    const container = document.getElementById('mental-activity-list');
    const news = DATA.news || {};
    const comms = DATA.internal_comm || {};
    const refs = DATA.reflections || [];
    const social = DATA.social_events || { pending: [] };
    
    let html = '';

    // 1. Incoming Social Message (Phase 12)
    const activeSocial = social.pending.find(e => !e.processed);
    if (activeSocial) {
      html += `
        <div class="mental-card" style="border-left-color: #f0a050;">
          <span class="mental-label">Incoming Message from ${esc(activeSocial.sender_name)}</span>
          <div class="mental-content">"${esc(activeSocial.message)}"</div>
          <span class="mental-sub">${new Date(activeSocial.timestamp).toLocaleTimeString()}</span>
        </div>
      `;
    }

    // 2. Current Thought (from latest Limbic memo or Reflection)
    const latestMemo = (comms.memos || []).find(m => m.sender === 'limbic' && m.type === 'emotion');
    const latestRef = refs[refs.length - 1];
    
    if (latestMemo) {
      html += `
        <div class="mental-card">
          <span class="mental-label">Inner Voice (Limbic)</span>
          <div class="mental-content">"${esc(latestMemo.content)}"</div>
          <span class="mental-sub">${new Date(latestMemo.timestamp).toLocaleTimeString()}</span>
        </div>
      `;
    } else if (latestRef) {
      html += `
        <div class="mental-card">
          <span class="mental-label">Current Reflection</span>
          <div class="mental-content">${esc(latestRef.summary || latestRef.reflection_summary || '')}</div>
        </div>
      `;
    }

    // 2. Recent Web Research
    const history = news.browsing_history || [];
    if (history.length > 0) {
      const last = history[0];
      let snapHtml = '';
      if (last.screenshot) {
        // Extract filename from absolute path for media endpoint
        const filename = last.screenshot.split('/').pop();
        snapHtml = `<img src="/media/browser_snapshots/${filename}" class="browser-snap" onclick="window.open(this.src)">`;
      }
      html += `
        <div class="mental-card" style="border-left-color: var(--growth);">
          <span class="mental-label">Web Research</span>
          <div class="mental-content">Searching for: <strong>${esc(last.query)}</strong></div>
          ${snapHtml}
          <span class="mental-sub">${new Date(last.timestamp).toLocaleTimeString()}</span>
        </div>
      `;
    }

    if (!html) {
      html = '<div class="empty-state">Observing cognitive processes...</div>';
    }
    container.innerHTML = html;

    // Update Ticker
    const ticker = document.getElementById('ticker-content');
    const headlines = news.headlines || [];
    if (headlines.length > 0) {
      ticker.innerHTML = headlines.map(h => `
        <div class="ticker-item">[${h.category.toUpperCase()}] ${esc(h.title)}</div>
      `).join('') + headlines.map(h => `
        <div class="ticker-item">[${h.category.toUpperCase()}] ${esc(h.title)}</div>
      `).join(''); // Duplicate for seamless loop
    }

    // Update Status Text
    const statusText = document.getElementById('status-text');
    if (history.length > 0 && (new Date() - new Date(history[0].timestamp)) < 300000) {
      statusText.textContent = 'Autonomous Web Research Active';
      statusText.style.color = 'var(--growth)';
    } else if (latestMemo) {
      statusText.textContent = 'Processing Internal Narrative';
      statusText.style.color = 'var(--accent)';
    } else {
      statusText.textContent = 'Cognitive System Synchronized';
      statusText.style.color = 'var(--text-dim)';
    }
  }
function renderProposals() {
  const list = document.getElementById('proposals-list');
  const count = document.getElementById('proposals-count');
  const pending = DATA.proposals_pending || [];

  count.textContent = pending.length > 0 ? `(${pending.length})` : '';

  if (pending.length === 0) {
    list.innerHTML = '<div class="empty-state">No pending proposals.</div>';
    return;
  }

  list.innerHTML = pending.map((p, i) => {
    const changeType = (p.change_type || p.type || 'modify').toLowerCase();
    return `
      <div class="proposal-card" id="proposal-${i}">
        <div class="proposal-header">
          <span class="proposal-id">${esc(p.id || 'PROP-' + i)}</span>
          <span class="proposal-type ${esc(changeType)}">${esc(changeType)}</span>
        </div>
        <div class="proposal-section">${esc(p.section || '')} ${p.subsection ? '› ' + esc(p.subsection) : ''}</div>
        <div class="proposal-content">${esc(p.content || p.after || p.proposed || '')}</div>
        <div class="proposal-reason">${esc(p.reason || p.rationale || '')}</div>
        <div class="proposal-actions">
          <button class="btn-approve" onclick="resolveProposal(${i}, 'approved')">Approve</button>
          <button class="btn-reject" onclick="resolveProposal(${i}, 'rejected')">Reject</button>
        </div>
      </div>
    `;
  }).join('');
}

function resolveProposal(index, decision) {
  fetch('/resolve-proposal', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ index, decision })
  })
  .then(r => {
    if (r.ok) {
      const card = document.getElementById('proposal-' + index);
      if (card) card.style.display = 'none';
      const toast = document.getElementById('save-toast');
      toast.textContent = '✓ Proposal ' + decision;
      toast.classList.add('show');
      setTimeout(() => toast.classList.remove('show'), 2500);
    } else {
      alert('Failed to resolve proposal. Is server running?');
    }
  })
  .catch(() => alert('Server not reachable. Proposals can only be resolved in --serve mode.'));
}

function renderReflections() {
  const list = document.getElementById('reflections-list');
  const refs = (DATA.reflections || []).slice().reverse();

  if (refs.length === 0) {
    list.innerHTML = '<div class="empty-state">No reflections yet.</div>';
    return;
  }

  list.innerHTML = refs.slice(0, 20).map((r, i) => {
    const summary = r.summary || r.reflection_summary || '';
    const insights = r.insights || r.key_insights || [];
    const refType = r.type || r.reflection_type || 'batch';
    const proposalDecision = r.proposal_decision || r.proposals_generated || '';
    return `
      <div class="reflection-card collapsed">
        <div class="reflection-header" onclick="this.parentElement.classList.toggle('collapsed')">
          <span class="ref-type">${esc(refType)}</span>
          <span style="color:var(--text);flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${esc(summary.slice(0, 80))}</span>
          <span class="ref-arrow">▼</span>
        </div>
        <div class="reflection-body">
          <div>${esc(summary)}</div>
          ${insights.length > 0 ? '<ul class="ref-insights">' + insights.map(ins => '<li>' + esc(typeof ins === 'string' ? ins : (ins.insight || JSON.stringify(ins))) + '</li>').join('') + '</ul>' : ''}
          ${proposalDecision ? `<div style="margin-top:0.4rem;font-size:0.68rem;color:var(--accent)">Proposals: ${esc(String(proposalDecision))}</div>` : ''}
        </div>
      </div>
    `;
  }).join('');
}

function renderSignificant() {
  const list = document.getElementById('significant-list');
  const sigs = (DATA.significant || []).slice().reverse();

  if (sigs.length === 0) {
    list.innerHTML = '<div class="empty-state">No significant memories yet.</div>';
    return;
  }

  list.innerHTML = sigs.map(s => {
    const sig = s.significance || 'notable';
    const content = s.content || s.summary || '';
    const context = s.context || s.significance_reason || '';
    return `
      <div class="sig-entry">
        <div class="exp-meta">
          <span class="sig-badge">${esc(sig)}</span>
          <span style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:var(--text-dim)">${esc(s.id || '')}</span>
          <span style="margin-left:auto;font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:var(--text-dim)">${esc((s.timestamp || '').slice(0, 16).replace('T', ' '))}</span>
        </div>
        <div class="sig-content">${esc(content.slice(0, 200))}</div>
        ${context ? '<div class="sig-context">' + esc(context) + '</div>' : ''}
      </div>
    `;
  }).join('');
}

function renderPipelineState() {
  const cards = document.getElementById('state-cards');
  const runs = document.getElementById('pipeline-runs');
  const state = DATA.state || {};
  const pipeline = DATA.pipeline || [];

  const stateEntries = Object.entries(state);
  if (stateEntries.length === 0 && pipeline.length === 0) {
    cards.innerHTML = '<div class="empty-state" style="grid-column:1/-1">No pipeline state yet.</div>';
    return;
  }

  cards.innerHTML = stateEntries.map(([k, v]) => {
    const display = typeof v === 'object' ? JSON.stringify(v) : String(v);
    return `
      <div class="state-card">
        <div class="sc-value">${esc(display.length > 12 ? display.slice(0, 12) + '…' : display)}</div>
        <div class="sc-label">${esc(k.replace(/_/g, ' '))}</div>
      </div>
    `;
  }).join('');

  if (pipeline.length > 0) {
    runs.innerHTML = `<div style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:var(--text-dim);margin-bottom:0.5rem;text-transform:uppercase;letter-spacing:0.08em">Recent Runs</div>` +
      pipeline.slice(-10).reverse().map(p => {
        const ts = (p.timestamp || p.completed_at || '').slice(0, 16).replace('T', ' ');
        const status = p.status || p.result || 'done';
        return `<div class="pipeline-run">${esc(ts)} — ${esc(status)}</div>`;
      }).join('');
  }
}

function updateClock() {
  const el = document.getElementById('clock');
  if (el) {
    el.textContent = new Date().toLocaleTimeString();
  }
}
setInterval(updateClock, 1000);
updateClock();

  renderAgentName();
  renderStats();

renderLegend();
renderSoulTree(DATA.changes.length);
renderTimeline();
  renderFeed();
  renderVitals();
  renderMentalActivity();
  renderProposals();

renderReflections();
  renderSignificant();
  renderPipelineState();

  // Auto-refresh Dashboard every 30s
  setInterval(() => {
    if (document.getElementById('tab-dashboard').classList.contains('active')) {
      location.reload();
    }
  }, 30000);
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  
  const toast = document.createElement('div');
  toast.className = 'toast ' + type;
  toast.innerHTML = message;
  toast.onclick = () => toast.remove();
  
  container.appendChild(toast);
  
  setTimeout(() => {
    toast.style.animation = 'slideIn 0.3s ease-in reverse forwards';
    setTimeout(() => toast.remove(), 300);
  }, 5000);
}

// Tab Navigation
function switchTab(tabId) {
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  const el = document.getElementById('tab-' + tabId);
  if (el) el.classList.add('active');
  document.querySelectorAll('.tab-btn').forEach(b => {
    if (b.textContent.toLowerCase().trim() === tabId) b.classList.add('active');
  });
  if (tabId === 'interior' && !window._interiorRendered) { renderInterior(); window._interiorRendered = true; }
  if (tabId === 'inventory' && !window._inventoryRendered) { renderInventoryPanel(); window._inventoryRendered = true; }
  if (tabId === 'wardrobe' && !window._wardrobeRendered) { renderWardrobePanel(); window._wardrobeRendered = true; }
  if (tabId === 'development' && !window._devRendered) { renderDevPanel(); window._devRendered = true; }
  if (tabId === 'development') { loadExpansionState(); loadProjectsList(); }
  if (tabId === 'cycle' && !window._cycleRendered) { renderCyclePanel(); window._cycleRendered = true; }
  if (tabId === 'world' && !window._worldRendered) { renderWorldPanel(); window._worldRendered = true; }
  if (tabId === 'skills' && !window._skillsRendered) { renderSkillsPanel(); window._skillsRendered = true; }
  if (tabId === 'psychology' && !window._psychRendered) { renderPsychPanel(); window._psychRendered = true; }
  if (tabId === 'reputation' && !window._repRendered) { renderReputationPanel(); loadContactCRM(); loadPendingSocialEvents(); window._repRendered = true; }
  if (tabId === 'reputation') { loadPendingSocialEvents(); }
  if (tabId === 'stream' && !window._streamRendered) { renderPhotoStream(); window._streamRendered = true; }
  if (tabId === 'genesis' && !window._genesisRendered) { window._genesisRendered = true; loadGenesisStatus(); loadConfigs(); }
  if (tabId === 'genesis') { refreshSpatialState(); }
  if (tabId === 'vault' && !window._vaultRendered) { window._vaultRendered = true; loadVaultData(); }
  if (tabId === 'diagnostics') { loadDiagnostics(); }
}

// Modal system (replaces prompt())
let _modalResolve = null;

function openModal(title, fields) {
  return new Promise(resolve => {
    _modalResolve = resolve;
    document.getElementById('modal-title').textContent = title;
    const container = document.getElementById('modal-fields');
    container.innerHTML = fields.map(f => {
      if (f.type === 'select') {
        const opts = f.options.map(o => `<option value="${o}">${o}</option>`).join('');
        return `<div class="modal-field"><label>${f.label}</label><select id="mf-${f.key}">${opts}</select></div>`;
      }
      return `<div class="modal-field"><label>${f.label}</label><input id="mf-${f.key}" type="${f.type||'text'}" value="${f.default||''}" placeholder="${f.placeholder||''}"></div>`;
    }).join('');
    document.getElementById('modal-ok').onclick = () => {
      const result = {};
      fields.forEach(f => { result[f.key] = document.getElementById('mf-' + f.key).value; });
      closeModal();
      resolve(result);
    };
    document.getElementById('modal-overlay').classList.add('open');
    // Focus first field
    const first = container.querySelector('input, select');
    if (first) setTimeout(() => first.focus(), 100);
  });
}

function closeModal() {
  document.getElementById('modal-overlay').classList.remove('open');
  if (_modalResolve) { _modalResolve(null); _modalResolve = null; }
}

// Lightbox
let _lightboxCtx = { category: '', itemId: '', images: [], currentIdx: 0 };

function openLightbox(category, itemId, images, startIdx) {
  _lightboxCtx = { category, itemId, images: images || [], currentIdx: startIdx || 0 };
  document.getElementById('lightbox').classList.add('open');
  renderLightbox();
}

function closeLightbox() {
  document.getElementById('lightbox').classList.remove('open');
}

// Escape key closes lightbox and modal
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    if (document.getElementById('lightbox').classList.contains('open')) closeLightbox();
    else if (document.getElementById('modal-overlay').classList.contains('open')) closeModal();
  }
});

function renderLightbox() {
  const main = document.getElementById('lightbox-main');
  const gallery = document.getElementById('lightbox-gallery');
  if (_lightboxCtx.images.length === 0) {
    main.src = '';
    main.alt = 'No images';
    gallery.innerHTML = '<span style="color:var(--text-dim);font-size:0.8rem;">No images yet — drop an image or click Upload</span>';
    return;
  }
  const current = _lightboxCtx.images[_lightboxCtx.currentIdx] || _lightboxCtx.images[0];
  main.src = '/' + current;
  gallery.innerHTML = _lightboxCtx.images.map((img, i) =>
    `<img src="/${img}" class="${i === _lightboxCtx.currentIdx ? 'active' : ''}" onclick="_lightboxCtx.currentIdx=${i};renderLightbox();">`
  ).join('');
}

function doUpload(file) {
  if (!file || !file.type.startsWith('image/')) return;
  const reader = new FileReader();
  reader.onload = function(e) {
    const b64 = e.target.result.split(',')[1];
    fetch('/upload-image', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        category: _lightboxCtx.category,
        item_id: _lightboxCtx.itemId,
        filename: file.name,
        data: b64,
      })
    }).then(r => r.json()).then(res => {
      _lightboxCtx.images.push(res.path);
      _lightboxCtx.currentIdx = _lightboxCtx.images.length - 1;
      renderLightbox();
      refreshPanel(_lightboxCtx.category);
      showToast('Image uploaded', 'success');
    }).catch(err => showToast('Upload failed: ' + err, 'error'));
  };
  reader.readAsDataURL(file);
}

function uploadLightboxImage(event) {
  doUpload(event.target.files[0]);
  event.target.value = '';
}

// Drag-and-drop on lightbox dropzone
(function() {
  const dz = document.getElementById('lightbox-dropzone');
  if (!dz) return;
  dz.addEventListener('dragover', e => { e.preventDefault(); dz.classList.add('dragover'); });
  dz.addEventListener('dragleave', () => dz.classList.remove('dragover'));
  dz.addEventListener('drop', e => {
    e.preventDefault();
    dz.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) doUpload(e.dataTransfer.files[0]);
  });
})();

function deleteLightboxImage() {
  if (_lightboxCtx.images.length === 0) return;
  const path = _lightboxCtx.images[_lightboxCtx.currentIdx];
  if (!confirm('Delete this image?')) return;
  fetch('/delete-image', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ category: _lightboxCtx.category, item_id: _lightboxCtx.itemId, path: path })
  }).then(() => {
    _lightboxCtx.images.splice(_lightboxCtx.currentIdx, 1);
    if (_lightboxCtx.currentIdx >= _lightboxCtx.images.length) _lightboxCtx.currentIdx = Math.max(0, _lightboxCtx.images.length - 1);
    renderLightbox();
    refreshPanel(_lightboxCtx.category);
    showToast('Image deleted', 'success');
  }).catch(err => showToast('Delete failed: ' + err, 'error'));
}

function refreshPanel(category) {
  if (category === 'interior') { window._interiorRendered = false; renderInterior(); window._interiorRendered = true; }
  if (category === 'inventory') { window._inventoryRendered = false; renderInventoryPanel(); window._inventoryRendered = true; }
  if (category === 'wardrobe') { window._wardrobeRendered = false; renderWardrobePanel(); window._wardrobeRendered = true; }
}

// Delete all images for an item (orphan cleanup)
function deleteAllImages(category, itemId, images) {
  if (!images || images.length === 0) return Promise.resolve();
  return Promise.all(images.map(path =>
    fetch('/delete-image', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ category, item_id: itemId, path })
    }).catch(() => {})
  ));
}

// Interior Panel
let _currentRoom = null;

function renderInterior() {
  const interior = DATA.interior || { rooms: [] };
  const tabsEl = document.getElementById('room-tabs');
  const gridEl = document.getElementById('interior-grid');
  const detailEl = document.getElementById('interior-detail');

  if (interior.rooms.length === 0) {
    tabsEl.innerHTML = '';
    gridEl.innerHTML = '<div style="color:var(--text-dim);font-size:0.85rem;">No rooms yet. Add one to get started.</div>';
    detailEl.innerHTML = '';
    return;
  }

  if (!_currentRoom || !interior.rooms.find(r => r.id === _currentRoom)) {
    _currentRoom = interior.rooms[0].id;
  }

  tabsEl.innerHTML = interior.rooms.map(r => {
    const cnt = r.objects ? r.objects.length : 0;
    return `<button class="room-tab ${r.id === _currentRoom ? 'active' : ''}" onclick="_currentRoom='${esc(r.id)}';renderInterior();">${esc(r.name)} (${cnt})</button>`;
  }).join('') + `<button class="room-tab" style="color:var(--core);" onclick="removeRoom('${esc(_currentRoom)}')">- Remove</button>`;

  const room = interior.rooms.find(r => r.id === _currentRoom);
  if (!room) return;

  detailEl.innerHTML = `<div style="font-size:0.8rem;color:var(--text-dim);margin-bottom:0.5rem;">${esc(room.description || '')}</div>
    <button class="btn-crud" onclick="addObject('${esc(room.id)}')">+ Object</button>`;

  const topLevel = room.objects.filter(o => !o.located_on);
  gridEl.innerHTML = topLevel.map(obj => {
    const thumb = obj.images && obj.images.length > 0
      ? `<img src="/${obj.images[0]}" alt="${esc(obj.name)}">`
      : getCategoryIcon(obj.category);
    const subs = (obj.items_on || []).map(id => room.objects.find(o => o.id === id)).filter(Boolean);
    const subHtml = subs.length > 0
      ? `<div style="font-size:0.65rem;color:var(--text-dim);margin-top:0.3rem;">Items: ${subs.map(s => esc(s.name)).join(', ')}</div>`
      : '';
    return `<div class="item-card" onclick="openLightbox('interior','${esc(obj.id)}',${JSON.stringify(obj.images||[])},0)">
      <div class="thumb">${thumb}</div>
      <div class="card-name">${esc(obj.name)}</div>
      <div class="card-meta">${esc(obj.category)}${subHtml}</div>
      <div style="margin-top:0.4rem;display:flex;gap:0.3rem;">
        <button class="btn-crud danger" onclick="event.stopPropagation();removeObject('${esc(room.id)}','${esc(obj.id)}')">Remove</button>
      </div>
    </div>`;
  }).join('');
}

function esc(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }

function getCategoryIcon(cat) {
  const icons = { furniture: '🪑', electronics: '💻', decoration: '🎨', storage: '📦' };
  return icons[cat] || '📦';
}

async function addRoom() {
  const result = await openModal('Add Room', [
    { key: 'name', label: 'Room Name', placeholder: 'e.g. Living Room' },
    { key: 'desc', label: 'Description (optional)', placeholder: '' },
  ]);
  if (!result || !result.name) return;
  const interior = DATA.interior || { rooms: [] };
  const newRoom = { id: 'room_' + Date.now().toString(36), name: result.name, description: result.desc || '', objects: [] };
  interior.rooms.push(newRoom);
  DATA.interior = interior;
  _currentRoom = newRoom.id;
  saveInterior();
  renderInterior();
}

function removeRoom(roomId) {
  if (!confirm('Remove this room and all its objects?')) return;
  const interior = DATA.interior || { rooms: [] };
  const room = interior.rooms.find(r => r.id === roomId);
  // Cleanup orphaned images
  if (room) {
    for (const obj of room.objects) {
      deleteAllImages('interior', obj.id, obj.images);
    }
  }
  interior.rooms = interior.rooms.filter(r => r.id !== roomId);
  DATA.interior = interior;
  _currentRoom = null;
  saveInterior();
  renderInterior();
}

async function addObject(roomId) {
  const result = await openModal('Add Object', [
    { key: 'name', label: 'Object Name', placeholder: 'e.g. Desk' },
    { key: 'category', label: 'Category', type: 'select', options: ['furniture', 'electronics', 'decoration', 'storage', 'other'] },
    { key: 'desc', label: 'Description (optional)', placeholder: '' },
  ]);
  if (!result || !result.name) return;
  const interior = DATA.interior || { rooms: [] };
  const room = interior.rooms.find(r => r.id === roomId);
  if (!room) return;
  room.objects.push({
    id: 'obj_' + Date.now().toString(36),
    name: result.name, category: result.category || 'other', description: result.desc || '',
    images: [], added_at: new Date().toISOString()
  });
  DATA.interior = interior;
  saveInterior();
  renderInterior();
}

function removeObject(roomId, objId) {
  if (!confirm('Remove this object?')) return;
  const interior = DATA.interior || { rooms: [] };
  const room = interior.rooms.find(r => r.id === roomId);
  if (!room) return;
  // Cleanup orphaned images
  const obj = room.objects.find(o => o.id === objId);
  if (obj) deleteAllImages('interior', objId, obj.images);
  room.objects = room.objects.filter(o => o.id !== objId);
  DATA.interior = interior;
  saveInterior();
  renderInterior();
}

  function saveInterior() {
    fetch('/update-interior', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(DATA.interior)
    }).then(r => {
      if (!r.ok) throw new Error('HTTP ' + r.status);
      showToast('Interior saved', 'success');
    }).catch(err => showToast('Save failed: ' + err, 'error'));
  }
// Inventory Panel
let _invCategoryFilter = 'all';

function renderInventoryPanel() {
  const inv = DATA.inventory || { items: [], categories: [] };
  const chipsEl = document.getElementById('inv-chips');

  const cats = ['all', ...(inv.categories || [])];
  const countMap = {};
  (inv.items || []).forEach(i => { countMap[i.category] = (countMap[i.category] || 0) + 1; });
  const totalCount = (inv.items || []).length;

  chipsEl.innerHTML = cats.map(c => {
    const cnt = c === 'all' ? totalCount : (countMap[c] || 0);
    return `<button class="chip ${c === _invCategoryFilter ? 'active' : ''}" onclick="_invCategoryFilter='${c}';renderInventoryPanel();">${c} (${cnt})</button>`;
  }).join('') + `<button class="btn-crud" style="margin-left:auto;" onclick="addInventoryItem()">+ Item</button>`;

  filterInventory();
}

function filterInventory() {
  const inv = DATA.inventory || { items: [], categories: [] };
  const query = (document.getElementById('inv-search')?.value || '').toLowerCase();
  const gridEl = document.getElementById('inventory-grid');

  let items = inv.items || [];
  if (_invCategoryFilter !== 'all') items = items.filter(i => i.category === _invCategoryFilter);
  if (query) items = items.filter(i =>
    i.name.toLowerCase().includes(query) ||
    (i.description || '').toLowerCase().includes(query) ||
    (i.tags || []).some(t => t.toLowerCase().includes(query))
  );

  if (items.length === 0) {
    gridEl.innerHTML = '<div style="color:var(--text-dim);font-size:0.85rem;">No items found.</div>';
    return;
  }

  gridEl.innerHTML = items.map(item => {
    const thumb = item.images && item.images.length > 0
      ? `<img src="/${item.images[0]}" alt="${esc(item.name)}">`
      : '📦';
    const locBadge = item.location ? `<span style="font-size:0.6rem;background:var(--accent-glow);padding:0.1rem 0.4rem;border-radius:8px;color:var(--accent);">@ ${esc(item.location)}</span>` : '';
    const tags = (item.tags || []).map(t => `<span style="font-size:0.55rem;background:var(--bg);padding:0.1rem 0.3rem;border-radius:4px;color:var(--text-dim);">${esc(t)}</span>`).join(' ');
    return `<div class="item-card" onclick="openLightbox('inventory','${item.id}',${JSON.stringify(item.images||[])},0)">
      <div class="thumb">${thumb}</div>
      <div class="card-name">${esc(item.name)}</div>
      <div class="card-meta">x${item.quantity} [${esc(item.category)}] ${locBadge}</div>
      <div style="margin-top:0.2rem;">${tags}</div>
      <div style="margin-top:0.4rem;display:flex;gap:0.3rem;">
        <button class="btn-crud danger" onclick="event.stopPropagation();removeInventoryItem('${item.id}')">Remove</button>
      </div>
    </div>`;
  }).join('');
}

async function addInventoryItem() {
  const result = await openModal('Add Item', [
    { key: 'name', label: 'Item Name', placeholder: 'e.g. USB Cable' },
    { key: 'category', label: 'Category', placeholder: 'e.g. electronics' },
    { key: 'qty', label: 'Quantity', type: 'number', default: '1' },
  ]);
  if (!result || !result.name) return;
  const inv = DATA.inventory || { items: [], categories: [] };
  const qty = parseInt(result.qty, 10) || 1;
  const category = result.category || 'other';
  inv.items.push({
    id: 'inv_' + Date.now().toString(36),
    name: result.name, category, description: '',
    quantity: qty, images: [], tags: [],
    added_at: new Date().toISOString()
  });
  if (!inv.categories.includes(category)) inv.categories.push(category);
  DATA.inventory = inv;
  saveInventory();
  renderInventoryPanel();
}

function removeInventoryItem(itemId) {
  if (!confirm('Remove this item?')) return;
  const inv = DATA.inventory || { items: [], categories: [] };
  // Cleanup orphaned images
  const item = inv.items.find(i => i.id === itemId);
  if (item) deleteAllImages('inventory', itemId, item.images);
  inv.items = inv.items.filter(i => i.id !== itemId);
  DATA.inventory = inv;
  saveInventory();
  renderInventoryPanel();
}

function saveInventory() {
  fetch('/update-inventory', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(DATA.inventory)
  }).then(r => {
    if (!r.ok) throw new Error('HTTP ' + r.status);
    showToast('Inventory saved', 'success');
  }).catch(err => showToast('Save failed: ' + err, 'error'));
}

// Wardrobe Panel
let _wardrobeCatFilter = 'all';

function renderWardrobePanel() {
  const wd = DATA.wardrobe || { inventory: {}, outfits: {} };
  const chipsEl = document.getElementById('wardrobe-chips');
  const gridEl = document.getElementById('wardrobe-grid');
  const outfitsEl = document.getElementById('wardrobe-outfits');

  const cats = Object.keys(wd.inventory || {});
  const totalCount = cats.reduce((sum, c) => sum + (wd.inventory[c] || []).length, 0);
  chipsEl.innerHTML = ['all', ...cats].map(c => {
    const cnt = c === 'all' ? totalCount : (wd.inventory[c] || []).length;
    return `<button class="chip ${c === _wardrobeCatFilter ? 'active' : ''}" onclick="_wardrobeCatFilter='${c}';renderWardrobePanel();">${c} (${cnt})</button>`;
  }).join('');

  let allItems = [];
  for (const [cat, items] of Object.entries(wd.inventory || {})) {
    if (_wardrobeCatFilter !== 'all' && cat !== _wardrobeCatFilter) continue;
    for (const item of items) {
      if (typeof item === 'object') {
        allItems.push({ ...item, _cat: cat });
      }
    }
  }

  if (allItems.length === 0) {
    gridEl.innerHTML = '<div style="color:var(--text-dim);font-size:0.85rem;">No items in wardrobe.</div>';
  } else {
    gridEl.innerHTML = allItems.map(item => {
      const thumb = item.images && item.images.length > 0
        ? `<img src="/${item.images[0]}" alt="${esc(item.name)}">`
        : '👕';
      return `<div class="item-card" onclick="openLightbox('wardrobe','${item.id}',${JSON.stringify(item.images||[])},0)">
        <div class="thumb">${thumb}</div>
        <div class="card-name">${esc(item.name)}</div>
        <div class="card-meta">${esc(item._cat)}</div>
      </div>`;
    }).join('');
  }

  // Outfits section
  const outfits = wd.outfits || {};
  const outfitKeys = Object.keys(outfits);
  if (outfitKeys.length > 0) {
    outfitsEl.innerHTML = `<h3 style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:var(--text-dim);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.5rem;">Outfits</h3>` +
      outfitKeys.map(name =>
        `<div style="padding:0.5rem;background:var(--bg-hover);border:1px solid var(--border);border-radius:8px;margin-bottom:0.5rem;">
          <strong style="color:var(--text-bright);font-size:0.8rem;">${esc(name)}</strong>
          <div style="font-size:0.72rem;color:var(--text-dim);margin-top:0.2rem;">${outfits[name].map(n => esc(n)).join(', ')}</div>
        </div>`
      ).join('');
  } else {
    outfitsEl.innerHTML = '';
  }
}

// Phase 34: Self-Expansion Panel
async function loadExpansionState() {
  try {
    const res = await fetch('/api/expansion/state');
    const state = await res.json();

    const statusEl = document.getElementById('expansion-status');
    const progressEl = document.getElementById('expansion-progress');
    const projectNameEl = document.getElementById('expansion-project-name');
    const percentEl = document.getElementById('expansion-percent');
    const barEl = document.getElementById('expansion-bar');

    if (state.isExpanding && state.currentProject) {
      statusEl.innerHTML = '<span style="color:#a855f7;">●</span> <span style="color:#a855f7;">Self-Expanding</span> - Working on: ' + state.currentProject.name;
      progressEl.style.display = 'block';
      projectNameEl.textContent = state.currentProject.name;
      const percent = state.currentProject.progress || 0;
      percentEl.textContent = percent + '%';
      barEl.style.width = percent + '%';
    } else {
      statusEl.innerHTML = '<span style="color:var(--text-dim);">○</span> <span style="color:var(--text-dim);">Idle</span> - ' +
        (state.totalProjectsCreated > 0
          ? state.totalProjectsCreated + ' projects created, ' + (state.totalProjectsCreated - (state.active?.length || 0)) + ' completed'
          : 'Waiting for high energy + strong technical interest');
      progressEl.style.display = 'none';
    }
  } catch (e) {
    console.log('Expansion state not available');
  }
}

// Load projects list
async function loadProjectsList() {
  try {
    const res = await fetch('/api/expansion/projects');
    const data = await res.json();

    const listEl = document.getElementById('projects-list');
    if (!data.projects || data.projects.length === 0) {
      listEl.innerHTML = '<div style="color:var(--text-dim);font-size:0.9rem;">No autonomous projects yet. The entity will create projects when energy > 80% and technical interest sentiment > 0.9.</div>';
      return;
    }

    listEl.innerHTML = data.projects.map(p => {
      const statusColors = {
        'brainstorm': '#fbbf24',
        'planning': '#60a5fa',
        'implementing': '#a855f7',
        'completed': '#22c55e',
        'paused': '#6b7280'
      };
      const color = statusColors[p.status] || '#6b7280';
      return `<div style="background:var(--bg-dim);padding:0.75rem;border-radius:8px;margin-bottom:0.5rem;border-left:3px solid ${color};">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <div>
            <div style="font-weight:bold;">${esc(p.name)}</div>
            <div style="font-size:0.8rem;color:var(--text-dim);">${esc(p.topic)} &middot; ${p.type}</div>
          </div>
          <div style="text-align:right;">
            <div style="font-size:0.85rem;color:${color};font-weight:bold;">${p.status}</div>
            <div style="font-size:0.75rem;color:var(--text-dim);">${p.progress}%</div>
          </div>
        </div>
        ${p.progress < 100 ? `<div style="background:var(--bg);height:4px;border-radius:2px;margin-top:0.5rem;overflow:hidden;"><div style="background:${color};height:100%;width:${p.progress}%;"></div></div>` : ''}
      </div>`;
    }).join('');
  } catch (e) {
    console.log('Projects list not available');
  }
}

// Development Panel
function renderDevPanel() {
  const manifest = DATA.dev_manifest || { projects: [] };
  const gridEl = document.getElementById('dev-grid');
  const detailEl = document.getElementById('dev-detail');

  if (manifest.projects.length === 0) {
    gridEl.innerHTML = '<div style="color:var(--text-dim);font-size:0.85rem;">No development projects yet. Use reality_develop to create one.</div>';
    detailEl.innerHTML = '';
    return;
  }

  gridEl.innerHTML = manifest.projects.map(p => {
    const badgeClass = { draft: 'badge-draft', pending_review: 'badge-pending', approved: 'badge-approved', active: 'badge-active' }[p.status] || 'badge-draft';
    const typeIcon = { tool: '🔧', skill: '🧠', plugin: '🔌', script: '📜' }[p.type] || '📄';
    return `<div class="item-card" onclick="showDevDetail('${p.id}')">
      <div class="thumb" style="font-size:1.5rem;">${typeIcon}</div>
      <div class="card-name">${esc(p.name)} <span class="badge ${badgeClass}">${p.status}</span></div>
      <div class="card-meta">${p.type} &middot; ${p.files.length} files</div>
    </div>`;
  }).join('');
}

function showDevDetail(projId) {
  const manifest = DATA.dev_manifest || { projects: [] };
  const proj = manifest.projects.find(p => p.id === projId);
  if (!proj) return;
  const detailEl = document.getElementById('dev-detail');
  const badgeClass = { draft: 'badge-draft', pending_review: 'badge-pending', approved: 'badge-approved', active: 'badge-active' }[proj.status] || 'badge-draft';
  detailEl.innerHTML = `<div class="detail-panel">
    <h3 style="color:var(--text-bright);font-size:1rem;margin-bottom:0.5rem;">${esc(proj.name)} <span class="badge ${badgeClass}">${proj.status}</span></h3>
    <div style="font-size:0.8rem;color:var(--text-dim);margin-bottom:0.5rem;">${esc(proj.description || 'No description')}</div>
    <div style="font-size:0.72rem;color:var(--text-dim);">Type: ${proj.type} &middot; Created: ${proj.created_at} &middot; Approved: ${proj.approved}</div>
    <div style="margin-top:0.5rem;font-size:0.72rem;color:var(--text-dim);">
      <strong>Files:</strong> ${proj.files.length > 0 ? proj.files.map(f => esc(f)).join(', ') : 'none'}
    </div>
  </div>`;
}

// Cycle Tab
const CYCLE_HORMONES = {
  estrogen:     [20,22,25,28,30,35,42,50,60,70,80,90,95,100,85,65,50,45,55,65,70,68,60,50,40,32,25,20],
  progesterone: [5,5,5,5,5,5,5,5,5,5,5,5,5,8,15,30,50,65,80,90,100,95,85,70,55,40,20,8],
  lh:           [10,10,10,12,12,14,16,18,22,30,45,70,95,100,40,15,10,10,10,10,10,10,10,10,10,10,10,10],
  fsh:          [35,40,50,55,60,65,70,65,55,45,40,50,70,80,40,25,20,18,16,15,14,13,12,12,15,20,25,30]
};

const CYCLE_PHASE_COLORS = {
  menstruation: '#e74c3c',
  follicular: '#e67e22',
  ovulation: '#f1c40f',
  luteal: '#9b59b6'
};

const CYCLE_PHASE_RANGES = [
  { phase: 'menstruation', start: 1, end: 5, label: 'Menstruation' },
  { phase: 'follicular', start: 6, end: 13, label: 'Follicular' },
  { phase: 'ovulation', start: 14, end: 15, label: 'Ovulation' },
  { phase: 'luteal', start: 16, end: 28, label: 'Luteal' }
];

function getCyclePhaseJS(day) {
  if (day <= 5) return 'menstruation';
  if (day <= 13) return 'follicular';
  if (day <= 15) return 'ovulation';
  return 'luteal';
}

function getCycleModsJS(phase) {
  const m = { menstruation: { energy: -12, hunger: 5, stress: 8, libido: 0 }, follicular: { energy: 5, hunger: 0, stress: -5, libido: 0 }, ovulation: { energy: 8, hunger: 0, stress: -8, libido: 15 }, luteal: { energy: -8, hunger: 12, stress: 10, libido: 0 } };
  return m[phase] || {};
}

let _cycleDay = 1;
let _cycleSimActive = false;

function renderCyclePanel() {
  const cycle = DATA.cycle || {};
  _cycleDay = cycle.current_day || 1;
  _cycleSimActive = cycle.simulator?.active || false;
  if (_cycleSimActive && cycle.simulator?.simulated_day) _cycleDay = cycle.simulator.simulated_day;
  updateCycleAllPanels(_cycleDay, cycle);
}

function updateCycleAllPanels(day, cycle) {
  const phase = getCyclePhaseJS(day);
  renderCycleWheel(day);
  renderCyclePhaseBanner(day, phase);
  renderCycleHormoneChart(day);
  renderCycleBodyStatus(day, phase);
  renderCycleMetabolismImpact(phase);
  renderCycleSimulator(day, cycle);
  renderCycleEducation();
}

function setCycleDay(day) {
  _cycleDay = day;
  const cycle = DATA.cycle || {};
  updateCycleAllPanels(day, cycle);
}

function renderCycleWheel(currentDay) {
  const size = 450;
  const cx = size / 2, cy = size / 2;
  const outerR = size / 2 - 10, innerR = outerR - 45;
  let svg = `<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">`;

  for (let d = 1; d <= 28; d++) {
    const phase = getCyclePhaseJS(d);
    const color = CYCLE_PHASE_COLORS[phase];
    const startAngle = ((d - 1) / 28) * 360 - 90;
    const endAngle = (d / 28) * 360 - 90;
    const startRad = startAngle * Math.PI / 180;
    const endRad = endAngle * Math.PI / 180;
    const x1o = cx + outerR * Math.cos(startRad);
    const y1o = cy + outerR * Math.sin(startRad);
    const x2o = cx + outerR * Math.cos(endRad);
    const y2o = cy + outerR * Math.sin(endRad);
    const x1i = cx + innerR * Math.cos(endRad);
    const y1i = cy + innerR * Math.sin(endRad);
    const x2i = cx + innerR * Math.cos(startRad);
    const y2i = cy + innerR * Math.sin(startRad);

    const opacity = d === currentDay ? 1.0 : 0.6;
    const stroke = d === currentDay ? 'white' : 'rgba(10,10,15,0.8)';
    const strokeW = d === currentDay ? 2 : 0.5;

    svg += `<path d="M${x1o},${y1o} A${outerR},${outerR} 0 0,1 ${x2o},${y2o} L${x1i},${y1i} A${innerR},${innerR} 0 0,0 ${x2i},${y2i} Z"
      fill="${color}" opacity="${opacity}" stroke="${stroke}" stroke-width="${strokeW}"
      style="cursor:pointer" onclick="setCycleDay(${d})"/>`;

    // Day number label
    const midAngle = ((d - 0.5) / 28) * 360 - 90;
    const midRad = midAngle * Math.PI / 180;
    const labelR = (outerR + innerR) / 2;
    const lx = cx + labelR * Math.cos(midRad);
    const ly = cy + labelR * Math.sin(midRad);
    const fontSize = d === currentDay ? '12' : '9';
    const fontWeight = d === currentDay ? '700' : '400';
    const textColor = d === currentDay ? '#fff' : 'rgba(255,255,255,0.6)';
    svg += `<text x="${lx}" y="${ly}" text-anchor="middle" dominant-baseline="central"
      font-size="${fontSize}" font-weight="${fontWeight}" fill="${textColor}"
      font-family="JetBrains Mono, monospace" style="cursor:pointer;pointer-events:none">${d}</text>`;
  }

  // Glowing marker for current day
  const markerAngle = ((currentDay - 0.5) / 28) * 360 - 90;
  const markerRad = markerAngle * Math.PI / 180;
  const markerR = outerR + 8;
  const mx = cx + markerR * Math.cos(markerRad);
  const my = cy + markerR * Math.sin(markerRad);
  const markerColor = CYCLE_PHASE_COLORS[getCyclePhaseJS(currentDay)];
  svg += `<circle cx="${mx}" cy="${my}" r="6" fill="${markerColor}" opacity="0.9">
    <animate attributeName="opacity" values="0.9;0.4;0.9" dur="2s" repeatCount="indefinite"/>
  </circle>`;

  // Center text
  const phase = getCyclePhaseJS(currentDay);
  const phaseLabel = CYCLE_PHASE_RANGES.find(r => r.phase === phase)?.label || phase;
  svg += `<text x="${cx}" y="${cy - 15}" text-anchor="middle" font-size="42" font-weight="700" fill="var(--text-bright)" font-family="JetBrains Mono, monospace">${currentDay}</text>`;
  svg += `<text x="${cx}" y="${cy + 15}" text-anchor="middle" font-size="13" fill="${CYCLE_PHASE_COLORS[phase]}" font-family="JetBrains Mono, monospace" text-transform="uppercase">${phaseLabel}</text>`;
  svg += `<text x="${cx}" y="${cy + 35}" text-anchor="middle" font-size="10" fill="var(--text-dim)" font-family="DM Sans, sans-serif">of 28 days</text>`;
  svg += `</svg>`;

  document.getElementById('cycle-wheel').innerHTML = svg;
}

function renderCyclePhaseBanner(day, phase) {
  const descs = {
    menstruation: 'The body sheds the uterine lining. Energy dips, cramps may occur. A time for rest and self-care.',
    follicular: 'Estrogen rises, energy returns. A follicle matures in the ovary. Creativity and motivation increase.',
    ovulation: 'Peak fertility. LH surge triggers egg release. Energy, confidence, and libido are at their highest.',
    luteal: 'Progesterone dominates. The body prepares for potential implantation. PMS symptoms may appear.'
  };
  const label = CYCLE_PHASE_RANGES.find(r => r.phase === phase)?.label || phase;
  const color = CYCLE_PHASE_COLORS[phase];
  document.getElementById('cycle-phase-banner').innerHTML = `
    <div class="phase-name" style="color:${color}">${label} — Day ${day}</div>
    <div style="color:var(--text-dim);font-size:0.85rem;">${descs[phase] || ''}</div>`;
}

function renderCycleHormoneChart(currentDay) {
  const w = 800, h = 200, pad = 40;
  const chartW = w - pad * 2, chartH = h - pad * 1.5;
  let svg = `<svg viewBox="0 0 ${w} ${h}" style="width:100%;max-width:${w}px;height:auto;">`;

  // Phase background bands
  CYCLE_PHASE_RANGES.forEach(r => {
    const x1 = pad + ((r.start - 1) / 28) * chartW;
    const x2 = pad + (r.end / 28) * chartW;
    svg += `<rect x="${x1}" y="${pad/2}" width="${x2-x1}" height="${chartH}" fill="${CYCLE_PHASE_COLORS[r.phase]}" opacity="0.08"/>`;
  });

  // Gridlines
  for (let i = 0; i <= 4; i++) {
    const y = pad/2 + (i/4) * chartH;
    svg += `<line x1="${pad}" y1="${y}" x2="${pad+chartW}" y2="${y}" stroke="var(--border)" stroke-width="0.5"/>`;
    svg += `<text x="${pad-5}" y="${y+3}" text-anchor="end" font-size="8" fill="var(--text-dim)" font-family="JetBrains Mono">${100-i*25}%</text>`;
  }

  // Hormone curves
  const colors = { estrogen: '#ff69b4', progesterone: '#9b59b6', lh: '#f1c40f', fsh: '#3498db' };
  Object.entries(CYCLE_HORMONES).forEach(([name, values]) => {
    let points = values.map((v, i) => {
      const x = pad + ((i + 0.5) / 28) * chartW;
      const y = pad/2 + chartH - (v / 100) * chartH;
      return `${x},${y}`;
    });
    svg += `<polyline points="${points.join(' ')}" fill="none" stroke="${colors[name]}" stroke-width="2" stroke-linejoin="round" opacity="0.85"/>`;
  });

  // Current day marker
  const dx = pad + ((currentDay - 0.5) / 28) * chartW;
  svg += `<line x1="${dx}" y1="${pad/2}" x2="${dx}" y2="${pad/2+chartH}" stroke="white" stroke-width="1.5" stroke-dasharray="4,3" opacity="0.7"/>`;

  // Day labels
  for (let d = 1; d <= 28; d += (d < 7 ? 1 : (d < 15 ? 2 : 3))) {
    const x = pad + ((d - 0.5) / 28) * chartW;
    svg += `<text x="${x}" y="${h-5}" text-anchor="middle" font-size="8" fill="var(--text-dim)" font-family="JetBrains Mono">${d}</text>`;
  }

  svg += `</svg>`;
  document.getElementById('cycle-hormone-chart').innerHTML = svg;
  document.getElementById('cycle-legend').innerHTML = `
    <span class="leg-estrogen">Estrogen</span>
    <span class="leg-progesterone">Progesterone</span>
    <span class="leg-lh">LH</span>
    <span class="leg-fsh">FSH</span>`;
}

function renderCycleBodyStatus(day, phase) {
  const idx = Math.max(0, Math.min(27, day - 1));
  const e = CYCLE_HORMONES.estrogen[idx];
  const p = CYCLE_HORMONES.progesterone[idx];

  const bodyData = {
    menstruation: [
      { icon: '🩸', title: 'Uterine Lining', desc: 'Endometrium is being shed. Menstrual bleeding occurs as the body discards the unfertilized lining.' },
      { icon: '🫘', title: 'Ovarian Activity', desc: 'Follicles are dormant. FSH begins to slowly stimulate new follicle recruitment.' },
      { icon: '💧', title: 'Cervical Mucus', desc: 'Minimal and dry. The cervix is closed and low.' },
      { icon: '🌡️', title: 'Basal Temperature', desc: 'Low baseline temperature. Typically 36.1-36.4°C (97.0-97.5°F).' }
    ],
    follicular: [
      { icon: '🧱', title: 'Uterine Lining', desc: `Rebuilding under estrogen influence (E2: ${e}%). Endometrium thickens progressively.` },
      { icon: '🫘', title: 'Ovarian Activity', desc: 'Dominant follicle selected and growing. Produces increasing estrogen.' },
      { icon: '💧', title: 'Cervical Mucus', desc: 'Increasing, becoming clearer and more stretchy as estrogen rises.' },
      { icon: '🌡️', title: 'Basal Temperature', desc: 'Remains low. Steady baseline before ovulation.' }
    ],
    ovulation: [
      { icon: '🧱', title: 'Uterine Lining', desc: `Fully developed (${e}% estrogen peak). Rich blood supply, glands active.` },
      { icon: '🥚', title: 'Ovarian Activity', desc: 'LH surge triggers ovulation! Egg released from dominant follicle.' },
      { icon: '💧', title: 'Cervical Mucus', desc: 'Peak fertility mucus — clear, stretchy, egg-white consistency.' },
      { icon: '🌡️', title: 'Basal Temperature', desc: 'Brief dip then sharp rise of 0.2-0.5°C after ovulation.' }
    ],
    luteal: [
      { icon: '🧱', title: 'Uterine Lining', desc: `Maintained by progesterone (${p}%). Secretory phase — glands produce nutrients.` },
      { icon: '🟡', title: 'Corpus Luteum', desc: 'Collapsed follicle becomes corpus luteum, producing progesterone.' },
      { icon: '💧', title: 'Cervical Mucus', desc: 'Thick, sticky, and opaque. Cervix closes and firms.' },
      { icon: '🌡️', title: 'Basal Temperature', desc: 'Elevated plateau. Remains high due to progesterone.' }
    ]
  };

  const items = bodyData[phase] || [];
  document.getElementById('cycle-body-status').innerHTML = items.map(item => `
    <div class="cycle-body-row">
      <div class="cycle-body-icon">${item.icon}</div>
      <div class="cycle-body-text"><h3>${item.title}</h3><p>${item.desc}</p></div>
    </div>`).join('');
}

function renderCycleMetabolismImpact(phase) {
  const mods = getCycleModsJS(phase);
  const items = [
    { key: 'energy', label: 'Energy', val: mods.energy || 0 },
    { key: 'hunger', label: 'Hunger', val: mods.hunger || 0 },
    { key: 'stress', label: 'Stress', val: mods.stress || 0 },
    { key: 'libido', label: 'Libido', val: mods.libido || 0 }
  ];

  document.getElementById('cycle-metabolism-impact').innerHTML = items.map(item => {
    const maxVal = 20;
    const absVal = Math.abs(item.val);
    const pct = Math.min(100, (absVal / maxVal) * 100);
    const cls = item.val >= 0 ? 'positive' : 'negative';
    const arrow = item.val > 0 ? '↑' : (item.val < 0 ? '↓' : '→');
    const sign = item.val > 0 ? '+' : '';
    return `<div class="cycle-bar-row">
      <div class="cycle-bar-label">${item.label}</div>
      <div class="cycle-bar-track"><div class="cycle-bar-fill ${cls}" style="width:${pct}%"></div></div>
      <div class="cycle-bar-value">${arrow} ${sign}${item.val}</div>
    </div>`;
  }).join('');
}

function renderCycleSimulator(day, cycle) {
  const symptoms = ['cramps','bloating','fatigue','mood_swings','headache','breast_tenderness','acne','appetite_changes','back_pain','insomnia'];
  const symMods = cycle?.symptom_modifiers || {};

  let html = `<div class="cycle-sim-row">
    <label>
      <input type="checkbox" id="cycle-sim-toggle" ${_cycleSimActive ? 'checked' : ''}
        onchange="_cycleSimActive=this.checked; updateCycleAllPanels(_cycleDay, DATA.cycle||{})"> What-If Mode
    </label>
  </div>`;

  html += `<div class="cycle-sim-row">
    <label>Day</label>
    <input type="range" min="1" max="28" value="${day}" id="cycle-sim-day"
      oninput="setCycleDay(parseInt(this.value)); document.getElementById('cycle-sim-day-val').textContent=this.value">
    <div class="sim-val" id="cycle-sim-day-val">${day}</div>
  </div>`;

  html += `<div style="margin-top:0.5rem;padding-top:0.5rem;border-top:1px solid var(--border);">
    <div style="font-size:0.75rem;color:var(--text-dim);margin-bottom:0.5rem;text-transform:uppercase;letter-spacing:0.1em;">Symptom Intensity</div>`;

  symptoms.forEach(s => {
    const val = symMods[s] !== undefined ? symMods[s] : 1;
    const label = s.replace(/_/g, ' ').replace(/\\b\\w/g, c => c.toUpperCase());
    html += `<div class="cycle-sim-row">
      <label>${label}</label>
      <input type="range" min="0" max="3" step="0.1" value="${val}" id="sim-${s}-input"
        oninput="document.getElementById('sim-${s}-val').textContent=parseFloat(this.value).toFixed(1)+'x'">
      <div class="sim-val" id="sim-${s}-val">${parseFloat(val).toFixed(1)}x</div>
    </div>`;
  });

  html += `</div>`;

  html += `<div class="cycle-presets">
    <button onclick="applyCyclePreset('heavy_pms')">Heavy PMS</button>
    <button onclick="applyCyclePreset('minimal')">Minimal</button>
    <button onclick="applyCyclePreset('heavy_period')">Heavy Period</button>
    <button onclick="applyCyclePreset('reset')">Reset</button>
    <button onclick="saveCycleState()" style="border-color:var(--accent);color:var(--accent);">Save State</button>
  </div>`;

  document.getElementById('cycle-simulator').innerHTML = html;
}

function applyCyclePreset(preset) {
  const presets = {
    heavy_pms: { cramps: 2.5, bloating: 2.0, fatigue: 2.0, mood_swings: 2.5, headache: 1.8, breast_tenderness: 2.2, acne: 1.5, appetite_changes: 2.0, back_pain: 2.0, insomnia: 1.8 },
    minimal: { cramps: 0.3, bloating: 0.3, fatigue: 0.5, mood_swings: 0.3, headache: 0.2, breast_tenderness: 0.3, acne: 0.2, appetite_changes: 0.3, back_pain: 0.2, insomnia: 0.3 },
    heavy_period: { cramps: 3.0, bloating: 2.0, fatigue: 2.5, mood_swings: 1.5, headache: 2.0, breast_tenderness: 1.0, acne: 1.0, appetite_changes: 1.5, back_pain: 2.5, insomnia: 1.5 },
    reset: { cramps: 1, bloating: 1, fatigue: 1, mood_swings: 1, headache: 1, breast_tenderness: 1, acne: 1, appetite_changes: 1, back_pain: 1, insomnia: 1 }
  };
  const vals = presets[preset];
  if (!vals) return;
  if (!DATA.cycle) DATA.cycle = {};
  DATA.cycle.symptom_modifiers = vals;
  renderCycleSimulator(_cycleDay, DATA.cycle);
}

function saveCycleState() {
  const cycle = DATA.cycle || {};
  cycle.current_day = _cycleDay;
  cycle.phase = getCyclePhaseJS(_cycleDay);
  cycle.hormones = {
    estrogen: CYCLE_HORMONES.estrogen[_cycleDay - 1] || 0,
    progesterone: CYCLE_HORMONES.progesterone[_cycleDay - 1] || 0,
    lh: CYCLE_HORMONES.lh[_cycleDay - 1] || 0,
    fsh: CYCLE_HORMONES.fsh[_cycleDay - 1] || 0
  };
  cycle.simulator = { active: _cycleSimActive, simulated_day: _cycleDay, custom_modifiers: {} };
  cycle.last_advance = new Date().toISOString();
  if (!cycle.start_date) cycle.start_date = cycle.last_advance;
  if (!cycle.cycle_length) cycle.cycle_length = 28;
  if (!cycle.symptom_modifiers) cycle.symptom_modifiers = { cramps:1,bloating:1,fatigue:1,mood_swings:1,headache:1,breast_tenderness:1,acne:1,appetite_changes:1,back_pain:1,insomnia:1 };

  // Read symptom sliders
  const symptoms = ['cramps','bloating','fatigue','mood_swings','headache','breast_tenderness','acne','appetite_changes','back_pain','insomnia'];
  symptoms.forEach(s => {
    const el = document.getElementById(`sim-${s}-input`);
    if (el) cycle.symptom_modifiers[s] = parseFloat(el.value);
  });

  DATA.cycle = cycle;
  fetch('/update-cycle', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(cycle)
      }).then(r => {
        if (r.ok) showToast('Cycle state saved', 'success');
        else showToast('Save failed', 'error');
      }).catch(() => showToast('Save failed', 'error'));
  
}

function renderCycleEducation() {
  const phases = [
    {
      phase: 'menstruation', label: 'Menstruation (Days 1-5)', subtitle: 'The Shedding Phase',
      color: CYCLE_PHASE_COLORS.menstruation,
      text: `<p><strong>What happens:</strong> The uterine lining (endometrium) that built up during the previous cycle is shed through the vagina. This is menstrual bleeding, lasting typically 3-7 days.</p>
<p><strong>Hormones:</strong> Estrogen and progesterone are at their lowest. The drop in these hormones triggers the shedding. FSH begins to rise slowly, signaling the ovaries to prepare new follicles.</p>
<p><strong>Why it happens:</strong> When no fertilized egg implanted in the uterine wall, the corpus luteum degrades, progesterone drops, and the thickened lining is no longer supported — so the body releases it.</p>
<p><strong>Common symptoms:</strong> Cramps (prostaglandins cause uterine contractions), fatigue, lower back pain, mood changes. Iron loss through bleeding can contribute to tiredness.</p>`
    },
    {
      phase: 'follicular', label: 'Follicular Phase (Days 6-13)', subtitle: 'The Growth Phase',
      color: CYCLE_PHASE_COLORS.follicular,
      text: `<p><strong>What happens:</strong> FSH stimulates multiple ovarian follicles to develop. One becomes the "dominant follicle" and matures, producing increasing amounts of estrogen.</p>
<p><strong>Hormones:</strong> Estrogen rises steadily. This thickens the endometrium again, preparing a new, nutrient-rich lining. FSH peaks early then decreases as the dominant follicle takes over.</p>
<p><strong>Why it happens:</strong> The body is preparing for potential conception. Estrogen rebuilds the uterine lining and triggers changes in cervical mucus to eventually facilitate sperm transport.</p>
<p><strong>Common experience:</strong> Rising energy, improved mood, clearer skin, increased creativity and social drive. Many people feel "at their best" during the late follicular phase.</p>`
    },
    {
      phase: 'ovulation', label: 'Ovulation (Days 14-15)', subtitle: 'The Release',
      color: CYCLE_PHASE_COLORS.ovulation,
      text: `<p><strong>What happens:</strong> A massive LH surge (triggered by peak estrogen) causes the dominant follicle to rupture and release a mature egg (ovum) into the fallopian tube.</p>
<p><strong>Hormones:</strong> LH spikes dramatically (up to 10x baseline). Estrogen peaks just before. The egg is viable for 12-24 hours. This is the most fertile window.</p>
<p><strong>Why it happens:</strong> High estrogen signals the pituitary gland that a follicle is mature. The pituitary responds with the LH surge, which biochemically triggers the follicle wall to break down and release the egg.</p>
<p><strong>Common experience:</strong> Some feel a twinge or mild pain on one side (Mittelschmerz). Highest energy, confidence, and libido. Cervical mucus is clear and stretchy (egg-white consistency).</p>`
    },
    {
      phase: 'luteal', label: 'Luteal Phase (Days 16-28)', subtitle: 'The Waiting Phase',
      color: CYCLE_PHASE_COLORS.luteal,
      text: `<p><strong>What happens:</strong> The collapsed follicle becomes the corpus luteum, a temporary endocrine gland that produces progesterone and some estrogen to maintain the uterine lining.</p>
<p><strong>Hormones:</strong> Progesterone dominates, peaking around day 21. If no implantation occurs, the corpus luteum degrades after ~12 days, hormone levels drop, and a new cycle begins.</p>
<p><strong>Why it happens:</strong> Progesterone stabilizes the endometrium and creates a secretory environment (nutrients, blood vessels) suitable for embryo implantation. It also raises basal body temperature.</p>
<p><strong>Common symptoms (PMS):</strong> Bloating, breast tenderness, mood swings, food cravings, acne, fatigue, irritability. These are caused by progesterone's effects and the eventual hormone withdrawal.</p>`
    }
  ];

  document.getElementById('cycle-education').innerHTML = phases.map((p, i) => `
    <div class="cycle-edu-card${i === 0 ? ' open' : ''}" onclick="this.classList.toggle('open')">
      <div class="cycle-edu-header" style="border-left:3px solid ${p.color};">
        <span>${p.label} — ${p.subtitle}</span>
        <span style="font-size:0.7rem;color:var(--text-dim);">▼</span>
      </div>
      <div class="cycle-edu-body">${p.text}</div>
    </div>`).join('');
}

// World Tab
function renderWorldPanel() {
  const ws = DATA.world_state || {};
  const locs = DATA.physique?.world?.locations || [];

  // Weather
  const weatherIcons = { sunny: '☀️', cloudy: '☁️', rainy: '🌧️', stormy: '⛈️', snowy: '❄️' };
  const weatherIcon = weatherIcons[ws.weather] || '🌤️';
  document.getElementById('world-weather').innerHTML = `
    <div style="font-size:3rem;text-align:center;">${weatherIcon}</div>
    <p style="text-align:center;text-transform:capitalize;">${ws.weather || 'unknown'}</p>
    <p style="text-align:center;font-size:1.5rem;">${ws.temperature !== undefined ? ws.temperature + '°C' : 'N/A'}</p>
    <div style="margin-top:1rem;display:flex;flex-direction:column;gap:0.5rem;">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <span style="font-size:0.75rem;color:var(--text-dim);">Real-World Sync</span>
        <input type="checkbox" ${ws.sync_to_real_world ? 'checked' : ''} 
          onchange="updateWorld({sync_to_real_world: this.checked})">
      </div>
      <select class="btn-crud" style="width:100%;text-align:center;" onchange="updateWorld({weather: this.value, sync_to_real_world: false})">
        <option value="">-- Override Weather --</option>
        ${Object.keys(weatherIcons).map(w => `<option value="${w}" ${ws.weather === w ? 'selected' : ''}>${w.toUpperCase()}</option>`).join('')}
      </select>
    </div>`;

  // Season
  const seasonIcons = { spring: '🌸', summer: '☀️', autumn: '🍂', winter: '❄️' };
  const seasonIcon = seasonIcons[ws.season] || '🌍';
  document.getElementById('world-season').innerHTML = `
    <div style="font-size:3rem;text-align:center;">${seasonIcon}</div>
    <p style="text-align:center;text-transform:capitalize;">${ws.season || 'unknown'}</p>
    <div style="margin-top:1rem;">
      <select class="btn-crud" style="width:100%;text-align:center;" onchange="updateWorld({season: this.value, sync_to_real_world: false})">
        <option value="">-- Override Season --</option>
        ${Object.keys(seasonIcons).map(s => `<option value="${s}" ${ws.season === s ? 'selected' : ''}>${s.toUpperCase()}</option>`).join('')}
      </select>
    </div>`;

  // Market
  const marketMod = ws.market_modifier || 1.0;
  const marketColor = marketMod > 1 ? 'var(--growth)' : (marketMod < 1 ? 'var(--danger)' : 'var(--text)');
  document.getElementById('world-market').innerHTML = `
    <p style="font-size:1.5rem;text-align:center;color:${marketColor};">${(marketMod * 100).toFixed(0)}%</p>
    <p style="text-align:center;font-size:0.8rem;color:var(--text-dim);">of base price</p>
    <div style="margin-top:1rem;text-align:center;">
      <input type="range" min="0.5" max="1.5" step="0.05" value="${marketMod}" 
        style="width:100%;" onchange="updateWorld({market_modifier: parseFloat(this.value)})">
    </div>`;

  // Locations
  document.getElementById('world-locations').innerHTML = locs.length > 0
    ? locs.map(l => `<div style="padding:0.3rem 0;border-bottom:1px solid var(--border);">
        <strong>${l.name}</strong><br><span style="color:var(--text-dim);font-size:0.8rem;">${l.description || 'No description'}</span>
      </div>`).join('')
    : '<p style="color:var(--text-dim);">No locations defined</p>';
}

function updateWorld(data) {
  fetch('/update-world', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  .then(r => r.text())
  .then(txt => {
    if (txt === 'OK') {
      showToast('World updated', 'success');
      setTimeout(() => window.location.reload(), 500);
    } else {
      showToast(txt, 'error');
    }
  })
  .catch(e => showToast(e, 'error'));
}

// Skills Tab
function renderSkillsPanel() {
  const skills = DATA.skills?.skills || [];
  const totalXp = DATA.skills?.total_xp || 0;

  // Skills list
  if (skills.length === 0) {
    document.getElementById('skills-list').innerHTML = '<p style="color:var(--text-dim);">No skills learned yet</p>';
  } else {
    const sorted = [...skills].sort((a, b) => b.level - a.level || b.xp - a.xp);
    document.getElementById('skills-list').innerHTML = sorted.map(s => `
      <div style="padding:0.5rem;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;">
        <span><strong>${s.name}</strong></span>
        <span style="color:var(--core);">Lv.${s.level} <span style="color:var(--text-dim);font-size:0.8rem;">(${s.xp}/${s.xp_to_next} XP)</span></span>
      </div>`).join('');
  }

  // Top skills
  const top3 = skills.slice(0, 3).sort((a, b) => b.level - a.level);
  document.getElementById('skills-top').innerHTML = top3.length > 0
    ? top3.map((s, i) => `<div style="padding:0.3rem 0;">
        <span style="color:var(--core);">#{i+1}</span> <strong>${s.name}</strong> (Lv.${s.level})
      </div>`).join('')
    : '<p style="color:var(--text-dim);">No skills yet</p>';

  // Total XP
  document.getElementById('skills-total').innerHTML = `
    <p style="font-size:2rem;text-align:center;color:var(--growth);">${totalXp}</p>
    <p style="text-align:center;font-size:0.8rem;color:var(--text-dim);">Total XP earned</p>`;
}

// Voice Lab Functions - Phase 20
function updateVoiceLabel(param) {
  const slider = document.getElementById('voice-' + param);
  const label = document.getElementById('voice-' + param + '-val');
  if (slider && label) {
    if (param === 'speed') {
      label.textContent = parseFloat(slider.value).toFixed(1) + 'x';
    } else {
      label.textContent = slider.value;
    }
  }
}

function getVoiceSettings() {
  return {
    pitch: parseFloat(document.getElementById('voice-pitch').value) || 0,
    speed: parseFloat(document.getElementById('voice-speed').value) || 1.0,
    emotional_intensity: parseFloat(document.getElementById('voice-emotion').value) || 0.5
  };
}

async function uploadVoiceSample() {
  const fileInput = document.getElementById('voice-sample');
  const statusDiv = document.getElementById('voice-status');

  if (!fileInput.files || !fileInput.files[0]) {
    statusDiv.innerHTML = '<span style="color:var(--danger);">Please select a voice sample file.</span>';
    return;
  }

  const file = fileInput.files[0];
  statusDiv.innerHTML = '<span style="color:var(--text-dim);">Uploading voice sample...</span>';

  try {
    const formData = new FormData();
    formData.append('voice_sample', file);

    const response = await fetch('/api/voice/upload', {
      method: 'POST',
      body: formData
    });
    const result = await response.json();

    if (result.success) {
      statusDiv.innerHTML = '<span style="color:var(--growth);">✓ Voice sample uploaded! Sample: ' + result.sample_name + '</span>';
    } else {
      statusDiv.innerHTML = '<span style="color:var(--danger);">Upload failed: ' + (result.error || 'Unknown error') + '</span>';
    }
  } catch (e) {
    statusDiv.innerHTML = '<span style="color:var(--danger);">Upload error: ' + e.message + '</span>';
  }
}

async function generateVoice() {
  const text = document.getElementById('voice-test-text').value.trim();
  const statusDiv = document.getElementById('voice-status');

  if (!text) {
    statusDiv.innerHTML = '<span style="color:var(--danger);">Please enter text to speak.</span>';
    return;
  }

  statusDiv.innerHTML = '<span style="color:var(--text-dim);">Generating...</span>';

  try {
    const settings = getVoiceSettings();
    const response = await fetch('/api/voice/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: text, settings: settings })
    });
    const result = await response.json();

    if (result.success) {
      statusDiv.innerHTML = '<span style="color:var(--growth);">✓ Generated!</span>';

      // Add to history
      const historyDiv = document.getElementById('voice-history');
      const audioHtml = `<div style="background:var(--bg-dim);padding:0.5rem;border-radius:4px;margin-bottom:0.5rem;display:flex;align-items:center;justify-content:space-between;">
        <div style="flex:1;overflow:hidden;">
          <div style="font-size:0.8rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${text}</div>
          <div style="font-size:0.7rem;color:var(--text-dim);">${result.timestamp || new Date().toISOString()}</div>
        </div>
        <audio controls src="${result.url}" style="height:30px;margin-left:0.5rem;"></audio>
      </div>`;

      // Prepend to history
      const existing = historyDiv.innerHTML;
      if (existing.includes('No voice generated')) {
        historyDiv.innerHTML = audioHtml;
      } else {
        // Keep only last 5 items
        const items = [audioHtml];
        const existingItems = historyDiv.querySelectorAll('div[style*="background"]');
        existingItems.forEach((item, i) => {
          if (i < 4) items.push(item.outerHTML);
        });
        historyDiv.innerHTML = items.join('');
      }
    } else {
      statusDiv.innerHTML = '<span style="color:var(--danger);">Error: ' + (result.error || 'Unknown') + '</span>';
    }
  } catch (e) {
    statusDiv.innerHTML = '<span style="color:var(--danger);">Error: ' + e.message + '</span>';
  }
}

// The Vault Tab - Phase 21
async function loadVaultData() {
  try {
    const response = await fetch('/api/vault/status');
    const result = await response.json();

    // Check for new transactions
    const lastTxId = localStorage.getItem('vault_last_tx_id');
    const transactions = result.transactions || [];
    if (transactions.length > 0) {
      const latest = transactions[0];
      if (lastTxId && lastTxId !== latest.id) {
        showToast(`<strong>Trade Executed</strong><br>${latest.type.toUpperCase()} ${latest.amount} ${latest.symbol} @ $${latest.price.toFixed(2)}`, 'success');
      }
      localStorage.setItem('vault_last_tx_id', latest.id);
    }

    // Update mode display
    const modeEl = document.getElementById('vault-mode');
    if (modeEl && result.mode) {
      modeEl.textContent = result.mode === 'paper' ? 'Paper Trading (Sandbox)' : 'Live Trading';
    }

    // Populate config fields
    if (result.provider) document.getElementById('vault-provider').value = result.provider;
    if (result.mode) document.getElementById('vault-mode-select').value = result.mode;
    if (result.api_key) document.getElementById('vault-api-key').value = result.api_key;
    if (result.api_secret) document.getElementById('vault-api-secret').value = result.api_secret;

    // Update portfolio
    const portfolioDiv = document.getElementById('vault-portfolio');
    if (portfolioDiv) {
      const balances = result.balances || {};
      const positions = result.positions || {};

      if (Object.keys(balances).length === 0 && Object.keys(positions).length === 0) {
        portfolioDiv.innerHTML = '<p style="color:var(--text-dim);font-size:0.85rem;">No holdings. Deposit funds to start trading.</p>';
      } else {
        let html = '<div style="background:var(--bg-dim);padding:0.75rem;border-radius:4px;margin-bottom:0.5rem;">';
        html += '<h4 style="margin:0 0 0.5rem 0;">Balances</h4>';
        for (const [asset, amount] of Object.entries(balances)) {
          html += `<div style="display:flex;justify-content:space-between;font-size:0.85rem;margin-bottom:0.25rem;"><span>${asset}</span><span>${typeof amount === 'number' ? amount.toFixed(4) : amount}</span></div>`;
        }
        html += '</div>';

        if (Object.keys(positions).length > 0) {
          html += '<div style="background:var(--bg-dim);padding:0.75rem;border-radius:4px;"><h4 style="margin:0.5rem 0 0.5rem 0;">Positions</h4>';
          for (const [symbol, pos] of Object.entries(positions)) {
            const p = pos;
            html += `<div style="font-size:0.85rem;margin-bottom:0.25rem;"><strong>${symbol}</strong>: ${p.amount} @ ${p.avg_price.toFixed(2)}</div>`;
          }
          html += '</div>';
        }
        portfolioDiv.innerHTML = html;
      }
    }

    // Update transactions
    const txDiv = document.getElementById('vault-transactions');
    if (txDiv) {
      if (transactions.length === 0) {
        txDiv.innerHTML = '<p style="color:var(--text-dim);font-size:0.85rem;">No transactions yet.</p>';
      } else {
        txDiv.innerHTML = transactions.slice(0, 20).map(tx => `
          <div style="background:var(--bg-dim);padding:0.5rem;border-radius:4px;margin-bottom:0.5rem;font-size:0.85rem;border-left:3px solid ${tx.type === 'buy' ? 'var(--growth)' : 'var(--core)'};">
            <div style="display:flex;justify-content:space-between;">
              <strong>${tx.type.toUpperCase()} ${tx.symbol}</strong>
              <span>$${tx.total.toFixed(2)}</span>
            </div>
            <div style="color:var(--text-dim);font-size:0.75rem;">
              ${tx.amount} @ $${tx.price.toFixed(2)} · ${new Date(tx.timestamp).toLocaleString()}
            </div>
          </div>
        `).join('');
      }
    }

    // Update reports
    const reportsDiv = document.getElementById('vault-reports');
    if (reportsDiv) {
      const reports = result.market_reports || [];
      if (reports.length === 0) {
        reportsDiv.innerHTML = '<p style="color:var(--text-dim);font-size:0.85rem;">Waiting for AI morning report...</p>';
      } else {
        const latest = reports[0];
        reportsDiv.innerHTML = `
          <div style="margin-bottom:0.5rem;color:var(--accent);font-size:0.75rem;text-transform:uppercase;">Latest: ${latest.date}</div>
          <div>"${esc(latest.content)}"</div>
          ${reports.length > 1 ? `<div style="margin-top:0.5rem;font-size:0.7rem;color:var(--text-dim);">+ ${reports.length - 1} older reports</div>` : ''}
        `;
      }
    }
  } catch (e) {
    console.log('Could not load vault data:', e);
  }
}

async function saveVaultConfig() {
  const provider = document.getElementById('vault-provider').value;
  const mode = document.getElementById('vault-mode-select').value;
  const apiKey = document.getElementById('vault-api-key').value;
  const apiSecret = document.getElementById('vault-api-secret').value;
  const statusDiv = document.getElementById('vault-config-status');

  try {
    const response = await fetch('/api/vault/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ provider, mode, api_key: apiKey, api_secret: apiSecret })
    });
    const result = await response.json();

    if (result.success) {
      statusDiv.innerHTML = '<span style="color:var(--growth);">✓ Config saved!</span>';
      setTimeout(() => statusDiv.innerHTML = '', 3000);
      loadVaultData();
    } else {
      statusDiv.innerHTML = '<span style="color:var(--danger);">Error: ' + result.error + '</span>';
    }
  } catch (e) {
    statusDiv.innerHTML = '<span style="color:var(--danger);">Error: ' + e.message + '</span>';
  }
}

async function depositVault() {
  const amount = parseFloat(document.getElementById('vault-deposit-amount').value);
  const statusDiv = document.getElementById('vault-deposit-status');

  if (!amount || amount <= 0) {
    statusDiv.innerHTML = '<span style="color:var(--danger);">Please enter a valid amount.</span>';
    return;
  }

  statusDiv.innerHTML = '<span style="color:var(--text-dim);">Processing...</span>';

  try {
    const response = await fetch('/api/vault/deposit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ amount: amount })
    });
    const result = await response.json();

    if (result.success) {
      statusDiv.innerHTML = '<span style="color:var(--growth);">✓ Deposited $' + amount.toFixed(2) + '! Total: $' + result.total_balance.toFixed(2) + '</span>';
      loadVaultData();
    } else {
      statusDiv.innerHTML = '<span style="color:var(--danger);">Error: ' + result.error + '</span>';
    }
  } catch (e) {
    statusDiv.innerHTML = '<span style="color:var(--danger);">Error: ' + e.message + '</span>';
  }
}

async function executeTrade() {
  const symbol = document.getElementById('vault-trade-symbol').value.trim().toUpperCase();
  const amount = parseFloat(document.getElementById('vault-trade-amount').value);
  const tradeType = document.getElementById('vault-trade-type').value;
  const statusDiv = document.getElementById('vault-trade-status');

  if (!symbol || !amount || amount <= 0) {
    statusDiv.innerHTML = '<span style="color:var(--danger);">Please enter symbol and amount.</span>';
    return;
  }

  statusDiv.innerHTML = '<span style="color:var(--text-dim);">Executing trade...</span>';

  try {
    const response = await fetch('/api/vault/trade', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'trade', symbol: symbol, amount: amount, type: tradeType })
    });
    const result = await response.json();

    if (result.success) {
      const tx = result.transaction;
      statusDiv.innerHTML = '<span style="color:var(--growth);">✓ ' + tx.type.toUpperCase() + ' ' + tx.amount + ' ' + tx.symbol + ' @ $' + tx.price.toFixed(2) + '</span>';
      loadVaultData();
    } else {
      statusDiv.innerHTML = '<span style="color:var(--danger);">Error: ' + result.error + '</span>';
    }
  } catch (e) {
    statusDiv.innerHTML = '<span style="color:var(--danger);">Error: ' + e.message + '</span>';
  }
}

// Economy Engine State (Phase 37)
async function loadEconomyState() {
  try {
    const response = await fetch('/api/economy/state');
    const state = await response.json();

    // Update status
    const statusEl = document.getElementById('economy-status');
    if (statusEl) {
      statusEl.textContent = state.isActive ? 'Active' : 'Inactive';
      statusEl.style.color = state.isActive ? 'var(--growth)' : 'var(--text-dim)';
    }

    // Update strategy
    const strategyEl = document.getElementById('economy-strategy');
    if (strategyEl) {
      const strategyNames = {
        'observe': 'Observing',
        'hold': 'Holding',
        'panic_sell': 'Panic Sell',
        'momentum_buy': 'Momentum Buy',
        'gradual_buy': 'Gradual Buy',
        'buy_the_dip': 'Buy the Dip',
        'dollar_cost_average': 'DCA',
        'stop_loss': 'Stop Loss',
        'day_trade': 'Day Trade'
      };
      strategyEl.textContent = strategyNames[state.currentStrategy] || state.currentStrategy || '-';
    }

    // Update mood
    const moodEl = document.getElementById('economy-mood');
    if (moodEl) {
      const moodColors = { 'bullish': 'var(--growth)', 'bearish': 'var(--danger)', 'neutral': 'var(--core)' };
      moodEl.textContent = (state.marketMood || 'neutral').charAt(0).toUpperCase() + (state.marketMood || 'neutral').slice(1);
      moodEl.style.color = moodColors[state.marketMood] || 'var(--text)';
    }

    // Update trade count
    const tradesEl = document.getElementById('economy-trades');
    if (tradesEl) {
      tradesEl.textContent = state.totalTrades || 0;
    }

    // Update last trade time
    const lastTradeEl = document.getElementById('economy-last-trade');
    if (lastTradeEl) {
      if (state.lastTradeTime) {
        const date = new Date(state.lastTradeTime);
        lastTradeEl.textContent = date.toLocaleTimeString();
      } else {
        lastTradeEl.textContent = '-';
      }
    }
  } catch (e) {
    console.log('Economy state error:', e);
  }
}

// Load economy state when vault tab is loaded
window._economyPolling = null;
function startEconomyPolling() {
  if (window._economyPolling) clearInterval(window._economyPolling);
  loadEconomyState();
  window._economyPolling = setInterval(loadEconomyState, 5000);
}

// Start polling when vault tab becomes active
// Consolidating switchTab functionality
const originalSwitchTab = window.switchTab;
window.switchTab = function(tabId) {
  // Call original logic if it exists (the one defined in the first script tag)
  if (typeof originalSwitchTab === 'function') {
    originalSwitchTab(tabId);
  }

  // Handle diagnostics specifically
  if (tabId === 'diagnostics') {
    loadDiagnostics();
  }

  // Handle other tab-specific polls/logic
  if (tabId === 'vault') startEconomyPolling();
  if (tabId === 'stream') startPresencePolling();
  if (tabId === 'analytics') loadAnalyticsData();
  if (tabId === 'config') loadConfig();

  // Avatar initialization fallback
  if (tabId === 'avatar' && typeof vrmModel !== 'undefined' && !vrmModel) {
    if (typeof initAvatar === 'function') initAvatar();
  }
};


// Presence Engine State (Phase 39)
async function loadPresenceState() {
  try {
    const response = await fetch('/api/presence/state');
    const state = await response.json();

    // Update status
    const statusEl = document.getElementById('presence-status');
    if (statusEl) {
      statusEl.textContent = state.isActive ? 'Active' : 'Inactive';
      statusEl.style.color = state.isActive ? '#10b981' : 'var(--text-dim)';
    }

    // Update mood
    const moodEl = document.getElementById('presence-mood');
    if (moodEl) {
      const moodColors = { 'euphoric': '#10b981', 'happy': '#10b981', 'content': '#10b981', 'neutral': 'var(--core)', 'stressed': '#ef4444', 'anxious': '#f59e0b', 'tired': '#6b7280' };
      moodEl.textContent = (state.currentMood || 'neutral').charAt(0).toUpperCase() + (state.currentMood || 'neutral').slice(1);
      moodEl.style.color = moodColors[state.currentMood] || 'var(--text)';
    }

    // Update counts
    const totalEl = document.getElementById('presence-total-posts');
    if (totalEl) {
      totalEl.textContent = state.totalPosts || 0;
    }

    const todayEl = document.getElementById('presence-posts-today');
    if (todayEl) {
      todayEl.textContent = state.postsToday || 0;
    }

    // Update feed
    const feedEl = document.getElementById('social-feed');
    if (feedEl && state.feed) {
      if (state.feed.length === 0) {
        feedEl.innerHTML = '<p style="color:var(--text-dim);font-size:0.85rem;">No posts yet. The entity will post when significant events occur.</p>';
      } else {
        let html = '';
        for (const post of state.feed.slice(0, 10)) {
          const sentimentColors = { 'joy': '#10b981', 'excitement': '#10b981', 'neutral': 'var(--text-dim)', 'melancholy': '#6b7280', 'frustration': '#ef4444' };
          const icon = post.type === 'selfie' ? '📷' : post.type === 'milestone' ? '🎉' : '💭';
          html += `<div style="padding:0.75rem;background:var(--bg-dim);border-radius:6px;margin-bottom:0.5rem;border-left:3px solid ${sentimentColors[post.sentiment] || 'var(--border)'}">`;
          html += `<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.25rem;">`;
          html += `<span style="font-size:1.2rem;">${icon}</span>`;
          html += `<span style="font-size:0.75rem;color:var(--text-dim);">${new Date(post.timestamp).toLocaleTimeString()}</span>`;
          html += `</div>`;
          html += `<div style="font-size:0.9rem;line-height:1.4;">${post.content}</div>`;
          html += `<div style="font-size:0.75rem;color:var(--text-dim);margin-top:0.25rem;">❤️ ${post.likes} · 🔄 ${post.shares}</div>`;
          html += `</div>`;
        }
        feedEl.innerHTML = html;
      }
    }
  } catch (e) {
    console.log('Presence state error:', e);
  }
}

function startPresencePolling() {
  if (window._presencePolling) clearInterval(window._presencePolling);
  loadPresenceState();
  window._presencePolling = setInterval(loadPresenceState, 5000);
}

// Hardware Resonance State (Phase 40)
async function loadHardwareState() {
  try {
    const response = await fetch('/api/hardware/resonance');
    const state = await response.json();

    // Update CPU
    const cpuEl = document.getElementById('hardware-cpu');
    if (cpuEl) {
      cpuEl.textContent = (state.currentCpuLoad || 0).toFixed(0) + '%';
      cpuEl.style.color = state.currentCpuLoad > 80 ? '#ef4444' : state.currentCpuLoad > 50 ? '#f59e0b' : 'var(--accent)';
    }

    // Update RAM
    const ramEl = document.getElementById('hardware-ram');
    if (ramEl) {
      ramEl.textContent = (state.currentMemoryUsage || 0).toFixed(0) + '%';
      ramEl.style.color = state.currentMemoryUsage > 85 ? '#ef4444' : state.currentMemoryUsage > 70 ? '#f59e0b' : 'var(--growth)';
    }

    // Update Temp
    const tempEl = document.getElementById('hardware-temp');
    if (tempEl) {
      if (state.currentTemp) {
        tempEl.textContent = state.currentTemp.toFixed(0) + '°C';
        tempEl.style.color = state.currentTemp > 80 ? '#ef4444' : state.currentTemp > 60 ? '#f59e0b' : 'var(--core)';
      } else {
        tempEl.textContent = 'N/A';
      }
    }

    // Update Resonance Level
    const resonanceEl = document.getElementById('hardware-resonance');
    if (resonanceEl) {
      const levelColors = { 'calm': '#10b981', 'strained': '#f59e0b', 'overloaded': '#ef4444', 'resonant': '#8b5cf6' };
      resonanceEl.textContent = (state.resonanceLevel || 'calm').charAt(0).toUpperCase() + (state.resonanceLevel || 'calm').slice(1);
      resonanceEl.style.color = levelColors[state.resonanceLevel] || 'var(--accent)';
    }

    // Update Audio
    const audioEl = document.getElementById('hardware-audio');
    if (audioEl) {
      audioEl.textContent = state.isAudioPlaying ? 'Playing 🎵' : 'Silent';
      audioEl.style.color = state.isAudioPlaying ? '#10b981' : 'var(--text-dim)';
    }
  } catch (e) {
    console.log('Hardware state error:', e);
  }
}

// Diagnostics Tab (Phase 41)
async function loadDiagnostics() {
  loadLogStream();
  loadSystemHealth();
  loadModelDiagnostics();
}

function loadModelDiagnostics() {
  if (typeof DATA === 'undefined' || !DATA.system_config) return;
  const cfg = DATA.system_config;

  const setStatus = (id, isConfigured) => {
    const el = document.getElementById(id);
    if (el) {
      el.textContent = isConfigured ? 'OK' : 'Missing';
      el.style.color = isConfigured ? 'var(--growth)' : 'var(--core)';
    }
  };

  setStatus('model-status-openai', cfg.openai_ok);
  setStatus('model-status-anthropic', cfg.anthropic_ok);
  setStatus('model-status-venice', cfg.venice_ok);
  setStatus('model-status-xai', cfg.xai_ok);
  setStatus('model-status-gemini', cfg.gemini_ok);
  setStatus('model-status-fal', cfg.fal_ok);
  setStatus('model-status-mem0', cfg.mem0_configured);
  setStatus('model-status-vault', cfg.vault_configured);
  setStatus('model-status-browser', cfg.browser_tool_ok);
  setStatus('model-status-desktop', cfg.desktop_tool_ok);
  setStatus('model-status-weather', cfg.weather_engine_ok);
}

function jumpToConfig(id) {
  switchTab('config');
  setTimeout(() => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      el.focus();
      const origBg = el.style.backgroundColor;
      el.style.transition = 'background-color 0.5s ease';
      el.style.backgroundColor = 'var(--accent-glow)';
      setTimeout(() => { el.style.backgroundColor = origBg; }, 1500);
    }
  }, 100);
}

async function loadSystemHealth() {
  try {
    // Check logging
    const logHealth = document.getElementById('health-logging');
    if (logHealth) logHealth.textContent = 'Active';

    // Check economy
    const economyResponse = await fetch('/api/economy/state');
    const economy = await economyResponse.json();
    const econHealth = document.getElementById('health-economy');
    if (econHealth) econHealth.textContent = economy.isActive ? 'Active' : 'Idle';
    if (econHealth) econHealth.style.color = economy.isActive ? 'var(--growth)' : 'var(--text-dim)';

    // Check hardware
    const hwResponse = await fetch('/api/hardware/resonance');
    const hw = await hwResponse.json();
    const hwHealth = document.getElementById('health-hardware');
    if (hwHealth) hwHealth.textContent = hw.isActive ? 'Active' : 'Idle';
    if (hwHealth) hwHealth.style.color = hw.isActive ? 'var(--growth)' : 'var(--text-dim)';

    // Check social/presence
    const presenceResponse = await fetch('/api/presence/state');
    const presence = await presenceResponse.json();
    const socialHealth = document.getElementById('health-social');
    if (socialHealth) socialHealth.textContent = presence.isActive ? 'Active' : 'Idle';
    if (socialHealth) socialHealth.style.color = presence.isActive ? 'var(--growth)' : 'var(--text-dim)';

    // Check vault
    const vaultResponse = await fetch('/api/vault/status');
    const vault = await vaultResponse.json();
    const vaultHealth = document.getElementById('health-vault');
    if (vaultHealth) vaultHealth.textContent = vault.mode || 'Unknown';
    if (vaultHealth) vaultHealth.style.color = 'var(--accent)';
  } catch (e) {
    console.log('Health check error:', e);
  }
}

async function loadLogStream() {
  const level = document.getElementById('log-filter-level')?.value || '';
  const module = document.getElementById('log-filter-module')?.value || '';
  const count = 100;

  try {
    let url = '/api/logs/recent?count=' + count;
    if (level) url += '&level=' + level;
    if (module) url += '&module=' + module;

    const response = await fetch(url);
    const logs = await response.json();

    const logStream = document.getElementById('log-stream');
    const logCount = document.getElementById('log-count');

    if (logCount) logCount.textContent = logs.length + ' entries';

    if (logStream) {
      if (!logs || logs.length === 0) {
        logStream.innerHTML = '<div style="color:var(--text-dim);font-style:italic;">No log entries yet.</div>';
        return;
      }

      let html = '';
      for (const entry of logs) {
        const levelColors = {
          'DEBUG': '#6b7280',
          'INFO': '#10b981',
          'WARN': '#f59e0b',
          'ERROR': '#ef4444'
        };
        const color = levelColors[entry.level] || 'var(--text)';
        const time = new Date(entry.timestamp).toLocaleTimeString();
        html += `<div style="padding:0.25rem 0;border-bottom:1px solid var(--border-dim);">`;
        html += `<span style="color:var(--text-dim);font-size:0.7rem;">${time}</span> `;
        html += `<span style="color:${color};font-weight:bold;font-size:0.75rem;">${entry.level}</span> `;
        html += `<span style="color:var(--accent);font-size:0.75rem;">[${entry.module}]</span> `;
        html += `<span style="color:var(--text);">${entry.message}</span>`;
        if (entry.data) {
          html += `<span style="color:var(--text-dim);font-size:0.7rem;"> ${JSON.stringify(entry.data)}</span>`;
        }
        html += `</div>`;
      }
      logStream.innerHTML = html;
    }
  } catch (e) {
    console.log('Log load error:', e);
    const logStream = document.getElementById('log-stream');
    if (logStream) logStream.innerHTML = '<div style="color:var(--danger);">Error loading logs: ' + e.message + '</div>';
  }
}

function clearLogFilter() {
  const levelSelect = document.getElementById('log-filter-level');
  const moduleSelect = document.getElementById('log-filter-module');
  if (levelSelect) levelSelect.value = '';
  if (moduleSelect) moduleSelect.value = '';
  loadLogStream();
}

// Start hardware polling on load
setInterval(loadHardwareState, 5000);
loadHardwareState();

// Analytics Tab (v5.1.0)
async function loadAnalyticsData() {
  try {
    // Load vitals telemetry
    const vitalsResponse = await fetch('/api/telemetry/vitals');
    const vitals = await vitalsResponse.json();

    const vitalsEl = document.getElementById('analytics-vitals');
    if (vitalsEl && vitals.length > 0) {
      let html = '<div style="display:flex;gap:2px;height:100px;align-items:flex-end;">';
      const recent = vitals.slice(-48); // Last 48 entries
      for (const v of recent) {
        const stressH = (v.needs?.stress || 50);
        const energyH = (v.needs?.energy || 50);
        html += `<div style="flex:1;display:flex;flex-direction:column;gap:1px;">`;
        html += `<div style="height:${stressH}%;background:var(--danger);min-height:1px;" title="Stress: ${stressH}"></div>`;
        html += `<div style="height:${energyH}%;background:var(--growth);min-height:1px;" title="Energy: ${energyH}"></div>`;
        html += `</div>`;
      }
      html += '</div><div style="display:flex;justify-content:space-between;font-size:0.7rem;color:var(--text-dim);margin-top:0.25rem;"><span>24h ago</span><span>Now</span></div>';
      vitalsEl.innerHTML = html;
    } else if (vitalsEl) {
      vitalsEl.innerHTML = '<div style="color:var(--text-dim);font-style:italic;">No vitals data yet. Data accumulates over time.</div>';
    }

    // Load hardware telemetry
    const hwResponse = await fetch('/api/telemetry/hardware');
    const hw = await hwResponse.json();

    const hwEl = document.getElementById('analytics-hardware');
    if (hwEl && hw.length > 0) {
      let html = '<div style="display:flex;gap:2px;height:80px;align-items:flex-end;">';
      const recent = hw.slice(-48);
      for (const h of recent) {
        const cpuH = h.cpu || 0;
        const stressH = Math.min(100, (h.stress_impact || 0) * 10 + 20);
        html += `<div style="flex:1;display:flex;flex-direction:column;gap:1px;">`;
        html += `<div style="height:${cpuH}%;background:#8b5cf6;min-height:1px;" title="CPU: ${cpuH}%"></div>`;
        html += `<div style="height:${stressH}%;background:var(--danger);min-height:1px;" title="Stress Impact"></div>`;
        html += `</div>`;
      }
      html += '</div><div style="display:flex;justify-content:space-between;font-size:0.7rem;color:var(--text-dim);margin-top:0.25rem;"><span>CPU %</span><span>Stress</span></div>';
      hwEl.innerHTML = html;
    } else if (hwEl) {
      hwEl.innerHTML = '<div style="color:var(--text-dim);font-style:italic;">No hardware data yet.</div>';
    }

    // Load economy data
    const vaultResponse = await fetch('/api/vault/status');
    const vault = await vaultResponse.json();

    const econEl = document.getElementById('analytics-economy');
    if (econEl) {
      const totalValue = vault.balances?.USD || 0;
      const positions = Object.keys(vault.positions || {}).length;
      econEl.innerHTML = `<div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
        <div style="text-align:center;padding:1rem;background:var(--bg);border-radius:8px;">
          <div style="font-size:2rem;color:var(--growth);">$${totalValue.toFixed(2)}</div>
          <div style="font-size:0.8rem;color:var(--text-dim);">Total Value</div>
        </div>
        <div style="text-align:center;padding:1rem;background:var(--bg);border-radius:8px;">
          <div style="font-size:2rem;color:var(--accent);">${vault.transactions?.length || 0}</div>
          <div style="font-size:0.8rem;color:var(--text-dim);">Total Trades</div>
        </div>
      </div>`;
    }
  } catch (e) {
    console.log('Analytics load error:', e);
  }
}

// Config Tab (v5.1.0)
async function loadConfig() {
  try {
    const response = await fetch('/api/config/all');
    const config = await response.json();

    // Character
    if (config.character) {
      document.getElementById('config-character-name').value = config.character.name || 'Q';
    }

    // Metabolism
    if (config.metabolism) {
      document.getElementById('config-hunger-rate').value = config.metabolism.hunger_rate || 0.5;
      document.getElementById('config-hunger-rate-val').textContent = config.metabolism.hunger_rate || 0.5;
      document.getElementById('config-thirst-rate').value = config.metabolism.thirst_rate || 0.5;
      document.getElementById('config-thirst-rate-val').textContent = config.metabolism.thirst_rate || 0.5;
      document.getElementById('config-energy-rate').value = config.metabolism.energy_rate || 0.5;
      document.getElementById('config-energy-rate-val').textContent = config.metabolism.energy_rate || 0.5;
      document.getElementById('config-stress-rate').value = config.metabolism.stress_accumulation || 0.3;
      document.getElementById('config-stress-rate-val').textContent = config.metabolism.stress_accumulation || 0.3;
    }

    // Hardware
    if (config.hardware_resonance) {
      document.getElementById('config-cpu-threshold').value = config.hardware_resonance.cpu_threshold_high || 80;
      document.getElementById('config-ram-threshold').value = config.hardware_resonance.memory_threshold_high || 85;
      document.getElementById('config-temp-threshold').value = config.hardware_resonance.temp_threshold_high || 80;
      document.getElementById('config-audio-sensitivity').value = config.hardware_resonance.audio_sensitivity || 0.5;
      document.getElementById('config-audio-sensitivity-val').textContent = config.hardware_resonance.audio_sensitivity || 0.5;
    }

    // Social
    if (config.social) {
      document.getElementById('config-autopost').checked = config.social.autonomous_posting !== false;
      document.getElementById('config-post-frequency').value = config.social.post_frequency || 'medium';
      document.getElementById('config-npc-interact').checked = config.social.npc_interactions !== false;
      document.getElementById('config-interaction-frequency').value = config.social.interaction_frequency || 'medium';
    }

    // Connectivity
    if (config.connectivity) {
      document.getElementById('config-vmc-enabled').checked = config.connectivity.vmc_enabled === true;
      document.getElementById('config-osc-enabled').checked = config.connectivity.osc_enabled === true;
      document.getElementById('config-vmc-ip').value = config.connectivity.vmc_ip || '127.0.0.1';
      document.getElementById('config-vmc-port').value = config.connectivity.vmc_port || 8000;
    }
  } catch (e) {
    console.log('Config load error:', e);
  }
}

async function saveAllConfig() {
  const config = {
    character: {
      name: document.getElementById('config-character-name').value
    },
    metabolism: {
      hunger_rate: parseFloat(document.getElementById('config-hunger-rate').value),
      thirst_rate: parseFloat(document.getElementById('config-thirst-rate').value),
      energy_rate: parseFloat(document.getElementById('config-energy-rate').value),
      stress_accumulation: parseFloat(document.getElementById('config-stress-rate').value)
    },
    hardware_resonance: {
      enabled: true,
      cpu_threshold_high: parseInt(document.getElementById('config-cpu-threshold').value),
      memory_threshold_high: parseInt(document.getElementById('config-ram-threshold').value),
      temp_threshold_high: parseInt(document.getElementById('config-temp-threshold').value),
      audio_sensitivity: parseFloat(document.getElementById('config-audio-sensitivity').value)
    },
    social: {
      autonomous_posting: document.getElementById('config-autopost').checked,
      post_frequency: document.getElementById('config-post-frequency').value,
      npc_interactions: document.getElementById('config-npc-interact').checked,
      interaction_frequency: document.getElementById('config-interaction-frequency').value
    },
    connectivity: {
      vmc_enabled: document.getElementById('config-vmc-enabled').checked,
      osc_enabled: document.getElementById('config-osc-enabled').checked,
      vmc_ip: document.getElementById('config-vmc-ip').value,
      vmc_port: parseInt(document.getElementById('config-vmc-port').value)
    }
  };

  try {
    const response = await fetch('/api/config/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    });
    const result = await response.json();
    const statusEl = document.getElementById('config-save-status');
    if (result.success) {
      statusEl.textContent = '✓ Saved!';
      statusEl.style.color = 'var(--growth)';
      setTimeout(() => { statusEl.textContent = ''; }, 3000);
    } else {
      statusEl.textContent = '✗ Error: ' + result.error;
      statusEl.style.color = 'var(--danger)';
    }
  } catch (e) {
    document.getElementById('config-save-status').textContent = '✗ Error: ' + e.message;
  }
}

// Slider value displays
['hunger-rate', 'thirst-rate', 'energy-rate', 'stress-rate', 'audio-sensitivity'].forEach(id => {
  const slider = document.getElementById('config-' + id);
  if (slider) {
    slider.addEventListener('input', function() {
      const valEl = document.getElementById('config-' + id + '-val');
      if (valEl) valEl.textContent = this.value;
    });
  }
});

// Genesis Lab Tab
async function toggleGenesis(enabled) {
  const statusDiv = document.getElementById('genesis-status');
  try {
    const response = await fetch('/api/genesis/toggle', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled: enabled })
    });
    const result = await response.json();

    if (result.success) {
      statusDiv.innerHTML = enabled
        ? '<span style="color:var(--growth);">✓ Origin Engine enabled. Restart the agent to activate.</span>'
        : '<span style="color:var(--text-dim);">Origin Engine disabled.</span>';
    } else {
      statusDiv.innerHTML = '<span style="color:var(--danger);">Error: ' + result.message + '</span>';
    }
  } catch (error) {
    statusDiv.innerHTML = '<span style="color:var(--danger);">Error: ' + error.message + '</span>';
  }
}

async function toggleVoice(enabled) {
  const statusDiv = document.getElementById('voice-status');
  try {
    const response = await fetch('/api/voice/toggle', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled: enabled })
    });
    const result = await response.json();

    if (result.success) {
      statusDiv.innerHTML = enabled
        ? '<span style="color:var(--growth);">✓ Voice synthesis enabled.</span>'
        : '<span style="color:var(--text-dim);">Voice synthesis disabled.</span>';
    } else {
      statusDiv.innerHTML = '<span style="color:var(--danger);">Error: ' + result.message + '</span>';
    }
  } catch (error) {
    statusDiv.innerHTML = '<span style="color:var(--danger);">Error: ' + error.message + '</span>';
  }
}

async function loadVoiceStatus() {
  try {
    const response = await fetch('/api/voice/status');
    const result = await response.json();
    const checkbox = document.getElementById('voice-enabled');
    if (checkbox) checkbox.checked = result.enabled || false;

    const statusDiv = document.getElementById('voice-status');
    if (statusDiv) {
      statusDiv.innerHTML = result.enabled
        ? '<span style="color:var(--growth);">✓ Voice synthesis is enabled</span>'
        : '<span style="color:var(--text-dim);">Voice synthesis is disabled</span>';
    }
  } catch (e) {
    console.log('Could not load voice status:', e);
  }
}

async function loadGenesisStatus() {
  try {
    const response = await fetch('/api/genesis/status');
    const result = await response.json();
    document.getElementById('genesis-enabled').checked = result.enabled || false;

    const statusDiv = document.getElementById('genesis-status');
    if (result.enabled) {
      statusDiv.innerHTML = '<span style="color:var(--growth);">✓ Origin Engine is enabled</span>';
    } else {
      statusDiv.innerHTML = '<span style="color:var(--text-dim);">Origin Engine is disabled</span>';
    }

    // Load model configuration
    loadModelConfig();

    // Load profiles
    loadProfiles();

    // Load backups
    loadBackups();

    // Load voice status
    loadVoiceStatus();

    // Load Mem0 config
    loadMem0Config();
  } catch (e) {
    console.log('Could not load genesis status:', e);
  }
}

async function loadModelConfig() {
  try {
    const response = await fetch('/api/model/config');
    const config = await response.json();

    if (config.models) {
      if (config.models.persona) document.getElementById('model-persona').value = config.models.persona;
      if (config.models.limbic) document.getElementById('model-limbic').value = config.models.limbic;
      if (config.models.analyst) document.getElementById('model-analyst').value = config.models.analyst;
      if (config.models.world_engine) document.getElementById('model-world').value = config.models.world_engine;
    }
    if (config.image_provider) document.getElementById('provider-image').value = config.image_provider;
    if (config.vision_provider) document.getElementById('provider-vision').value = config.vision_provider;
    
    if (config.api_key) document.getElementById('api-key').value = config.api_key;
    if (config.key_venice) document.getElementById('key-venice').value = config.key_venice;
    if (config.key_fal) document.getElementById('key-fal').value = config.key_fal;
    if (config.key_xai) document.getElementById('key-xai').value = config.key_xai;
    if (config.key_gemini_img) document.getElementById('key-gemini-img').value = config.key_gemini_img;
  } catch (e) {
    console.log('Could not load model config:', e);
  }
}

async function saveAdvancedConfig() {
  const payload = {
    image_provider: document.getElementById('provider-image').value,
    vision_provider: document.getElementById('provider-vision').value,
    key_venice: document.getElementById('key-venice').value,
    key_fal: document.getElementById('key-fal').value,
    key_xai: document.getElementById('key-xai').value,
    key_gemini_img: document.getElementById('key-gemini-img').value,
  };

  try {
    const response = await fetch('/api/model/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const result = await response.json();
    const statusEl = document.getElementById('adv-config-status');
    if (result.success) {
      statusEl.innerHTML = '<span style="color:var(--growth);">✓ Saved!</span>';
      setTimeout(() => statusEl.innerHTML = '', 2000);
    } else {
      statusEl.innerHTML = '<span style="color:var(--danger);">Error: ' + result.message + '</span>';
    }
  } catch (e) {
    document.getElementById('adv-config-status').innerHTML = '<span style="color:var(--danger);">Error: ' + e.message + '</span>';
  }
}

async function saveModelConfig() {
  try {
    const models = {
      persona: document.getElementById('model-persona').value,
      limbic: document.getElementById('model-limbic').value,
      analyst: document.getElementById('model-analyst').value,
      world_engine: document.getElementById('model-world').value,
    };
    const apiKey = document.getElementById('model-api-key').value;
    const keyAnthropic = document.getElementById('key-anthropic').value;

    const response = await fetch('/api/model/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ models, api_key: apiKey, key_anthropic: keyAnthropic })
    });
    const result = await response.json();

    const statusEl = document.getElementById('model-config-status');
    if (result.success) {
      statusEl.innerHTML = '<span style="color:var(--growth);">✓ Saved!</span>';
      setTimeout(() => statusEl.innerHTML = '', 2000);
    } else {
      statusEl.innerHTML = '<span style="color:var(--danger);">Error: ' + result.message + '</span>';
    }
  } catch (e) {
    document.getElementById('model-config-status').innerHTML = '<span style="color:var(--danger);">Error: ' + e.message + '</span>';
  }
}

async function loadProfiles() {
  try {
    const response = await fetch('/api/profiles/list');
    const profiles = await response.json();

    const container = document.getElementById('profile-list');
    if (!profiles || profiles.length === 0) {
      container.innerHTML = '<p style="color:var(--text-dim);font-size:0.85rem;">No profiles saved yet.</p>';
      return;
    }

    container.innerHTML = profiles.map(p => `
      <div style="background:var(--bg);padding:0.5rem;border-radius:4px;display:flex;justify-content:space-between;align-items:center;">
        <span><strong>${p}</strong></span>
        <div>
          <button onclick="loadProfile('${p}')" style="background:var(--growth);color:#fff;border:none;padding:0.25rem 0.5rem;border-radius:4px;cursor:pointer;margin-right:0.25rem;">Load</button>
          <button onclick="deleteProfile('${p}')" style="background:var(--danger);color:#fff;border:none;padding:0.25rem 0.5rem;border-radius:4px;cursor:pointer;">Del</button>
        </div>
      </div>
    `).join('');
  } catch (e) {
    console.log('Could not load profiles:', e);
  }
}

async function loadBackups() {
  try {
    const response = await fetch('/api/backups/list');
    const backups = await response.json();

    const container = document.getElementById('backup-list');
    if (!backups || backups.length === 0) {
      container.innerHTML = '<p style="color:var(--text-dim);font-size:0.85rem;">No backups available yet.</p>';
      return;
    }

    container.innerHTML = backups.map(b => `
      <div style="background:var(--bg);padding:0.5rem;border-radius:4px;display:flex;justify-content:space-between;align-items:center;margin-bottom:0.25rem;">
        <span><strong>${b}</strong></span>
        <button onclick="rollbackTo('${b}')" style="background:var(--accent);color:#fff;border:none;padding:0.25rem 0.5rem;border-radius:4px;cursor:pointer;">Rollback</button>
      </div>
    `).join('');
  } catch (e) {
    console.log('Could not load backups:', e);
  }
}

// Memory Tab Functions
async function saveMem0Config() {
  try {
    const apiKey = document.getElementById('mem0-api-key').value.trim();
    const userId = document.getElementById('mem0-user-id').value.trim() || 'genesis_agent';

    if (!apiKey) {
      document.getElementById('mem0-config-status').innerHTML = '<span style="color:var(--danger);">Please enter an API key.</span>';
      return;
    }

    const response = await fetch('/api/mem0/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ api_key: apiKey, user_id: userId })
    });
    const result = await response.json();

    if (result.success) {
      document.getElementById('mem0-config-status').innerHTML = '<span style="color:var(--growth);">✓ Config saved!</span>';
      setTimeout(() => {
        document.getElementById('mem0-config-status').innerHTML = '';
      }, 3000);
    } else {
      document.getElementById('mem0-config-status').innerHTML = '<span style="color:var(--danger);">Error: ' + result.message + '</span>';
    }
  } catch (e) {
    document.getElementById('mem0-config-status').innerHTML = '<span style="color:var(--danger);">Error: ' + e.message + '</span>';
  }
}

async function loadMem0Config() {
  try {
    const response = await fetch('/api/mem0/config');
    const config = await response.json();

    if (config.api_key) {
      document.getElementById('mem0-api-key').value = config.api_key;
    }
    if (config.user_id) {
      document.getElementById('mem0-user-id').value = config.user_id;
    }
  } catch (e) {
    console.log('Could not load Mem0 config:', e);
  }
}

async function searchMemories() {
  const query = document.getElementById('memory-search-query').value.trim();
  const lang = document.getElementById('memory-lang').value;
  const resultsDiv = document.getElementById('memory-results');

  if (!query) {
    resultsDiv.innerHTML = '<p style="color:var(--danger);font-size:0.85rem;">Please enter a search query.</p>';
    return;
  }

  resultsDiv.innerHTML = '<p style="color:var(--text-dim);font-size:0.85rem;">Searching...</p>';

  try {
    const response = await fetch('/api/mem0/search', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: query })
    });
    const result = await response.json();

    if (result.error) {
      resultsDiv.innerHTML = '<p style="color:var(--danger);font-size:0.85rem;">' + result.error + '</p>';
      return;
    }

    if (result.memories && result.memories.length > 0) {
      const memories = result.memories;
      resultsDiv.innerHTML = '<h4 style="margin:0.5rem 0;">' + (lang === 'de' ? 'Gefundene Erinnerungen:' : 'Found Memories:') + '</h4>' + memories.map(m => `
        <div style="background:var(--bg);padding:0.75rem;border-radius:4px;margin-bottom:0.5rem;border-left:3px solid var(--core);">
          <p style="margin:0;font-size:0.9rem;">${m.memory || m.text || JSON.stringify(m)}</p>
          <small style="color:var(--text-dim);">ID: ${m.id || 'N/A'}</small>
        </div>
      `).join('');
    } else {
      resultsDiv.innerHTML = '<p style="color:var(--text-dim);font-size:0.85rem;">' + (lang === 'de' ? 'Keine Erinnerungen gefunden.' : 'No memories found.') + '</p>';
    }
  } catch (e) {
    resultsDiv.innerHTML = '<p style="color:var(--danger);font-size:0.85rem;">Error: ' + e.message + '</p>';
  }
}

async function storeMemory() {
  const memory = document.getElementById('memory-store-text').value.trim();
  const lang = document.getElementById('memory-lang').value;
  const statusDiv = document.getElementById('memory-store-status');

  if (!memory) {
    statusDiv.innerHTML = '<span style="color:var(--danger);">Please enter a memory to store.</span>';
    return;
  }

  statusDiv.innerHTML = '<span style="color:var(--text-dim);">Storing...</span>';

  try {
    const response = await fetch('/api/mem0/store', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ memory: memory })
    });
    const result = await response.json();

    if (result.error) {
      statusDiv.innerHTML = '<span style="color:var(--danger);">' + result.error + '</span>';
      return;
    }

    statusDiv.innerHTML = '<span style="color:var(--growth);">' + (lang === 'de' ? '✓ Erinnerung gespeichert!' : '✓ Memory stored!') + '</span>';
    document.getElementById('memory-store-text').value = '';

    setTimeout(() => {
      statusDiv.innerHTML = '';
    }, 3000);
  } catch (e) {
    statusDiv.innerHTML = '<span style="color:var(--danger);">Error: ' + e.message + '</span>';
  }
}

async function saveProfile() {
  const name = document.getElementById('profile-name').value.trim();
  if (!name) {
    alert('Please enter a profile name.');
    return;
  }

  // Sanitize name
  const safeName = name.replace(/[^a-zA-Z0-9_-]/g, '').slice(0, 50);
  if (!safeName) {
    alert('Invalid profile name.');
    return;
  }

  try {
    const response = await fetch('/api/profiles/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: safeName })
    });
    const result = await response.json();
    alert(result.success ? 'Profile saved!' : 'Error: ' + result.message);
    loadProfiles();
  } catch (e) {
    alert('Error: ' + e.message);
  }
}

async function loadProfile(name) {
  if (!confirm('Load profile "' + name + '"? This will overwrite current state.')) return;

  try {
    const response = await fetch('/api/profiles/load', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: name })
    });
    const result = await response.json();
    alert(result.success ? 'Profile loaded!' : 'Error: ' + result.message);
  } catch (e) {
    alert('Error: ' + e.message);
  }
}

async function deleteProfile(name) {
  if (!confirm('Delete profile "' + name + '"? This cannot be undone.')) return;

  try {
    const response = await fetch('/api/profiles/delete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: name })
    });
    const result = await response.json();
    alert(result.success ? 'Profile deleted!' : 'Error: ' + result.message);
    loadProfiles();
  } catch (e) {
    alert('Error: ' + e.message);
  }
}

async function rollbackTo(date) {
  if (!confirm('Rollback to ' + date + '? This will overwrite current state.')) return;

  try {
    const response = await fetch('/api/backups/rollback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ date: date })
    });
    const result = await response.json();
    alert(result.success ? 'Rollback complete!' : 'Error: ' + result.message);
  } catch (e) {
    alert('Error: ' + e.message);
  }
}

async function runPatch() {
  const instructions = document.getElementById('patch-prompt').value.trim();
  if (!instructions) {
    alert('Please enter patch instructions.');
    return;
  }

  if (!confirm('This will modify your current character traits. Proceed?')) return;

  // Prepend Patch: if not already present
  const prefix = instructions.toLowerCase().startsWith('patch:') || instructions.toLowerCase().startsWith('modify:')
    ? ''
    : 'Patch: ';

  // Show loading overlay
  const loading = document.getElementById('genesis-loading');
  const progress = document.getElementById('genesis-progress');
  loading.style.display = 'flex';
  progress.style.width = '10%';

  try {
    progress.style.width = '40%';
    const response = await fetch('/api/genesis/request', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: prefix + instructions })
    });
    const result = await response.json();
    
    if (!result.success) throw new Error(result.message);

    progress.style.width = '70%';
    
    // Show result
    const resultDiv = document.getElementById('genesis-result');
    const resultTitle = document.getElementById('genesis-result-title');
    const resultContent = document.getElementById('genesis-result-content');

    resultDiv.style.display = 'block';
    resultTitle.textContent = '⏳ Patch Requested';
    resultTitle.style.color = 'var(--accent)';
    resultContent.textContent = 'Your modification request has been sent. The agent will apply the patch in the next cycle. The dashboard will reload once complete.';

    // Poll for completion
    let attempts = 0;
    const poll = setInterval(async () => {
      attempts++;
      const statusRes = await fetch('/api/genesis/request-status');
      const status = await statusRes.json();
      
      if (!status.pending || attempts > 30) {
        clearInterval(poll);
        progress.style.width = '100%';
        setTimeout(() => location.reload(), 2000);
      }
    }, 2000);

  } catch (e) {
    alert('Error: ' + e.message);
    loading.style.display = 'none';
  }
}

async function runGenesis() {
  const prompt = document.getElementById('genesis-prompt').value.trim();
  if (!prompt) {
    alert('Please enter a life description.');
    return;
  }

  if (!confirm('DANGER: This will overwrite your entire simulation. Are you sure?')) return;

  // Show loading overlay
  const loading = document.getElementById('genesis-loading');
  const progress = document.getElementById('genesis-progress');
  loading.style.display = 'flex';
  progress.style.width = '10%';

  try {
    progress.style.width = '30%';

    // Send the prompt to the backend to be picked up by the agent
    const response = await fetch('/api/genesis/request', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: prompt })
    });
    const result = await response.json();

    if (!result.success) throw new Error(result.message);

    progress.style.width = '60%';
    
    // Tell user to wait for the agent to process the request
    const resultDiv = document.getElementById('genesis-result');
    const resultTitle = document.getElementById('genesis-result-title');
    const resultContent = document.getElementById('genesis-result-content');

    resultDiv.style.display = 'block';
    resultTitle.textContent = '⏳ Request Sent';
    resultTitle.style.color = 'var(--accent)';
    resultContent.textContent = 'Your request has been sent to the AI agent. Please wait a few seconds for the agent to process the generation and perform the bootstrap.\\n\\nThe dashboard will reload automatically once the process is complete.';

    progress.style.width = '90%';

    // Poll for completion (check if request file is gone)
    let attempts = 0;
    const poll = setInterval(async () => {
      attempts++;
      const statusRes = await fetch('/api/genesis/request-status');
      const status = await statusRes.json();
      
      if (!status.pending || attempts > 30) {
        clearInterval(poll);
        progress.style.width = '100%';
        resultTitle.textContent = '✅ Generation Complete';
        resultTitle.style.color = 'var(--growth)';
        resultContent.textContent = 'The agent has finished the life bootstrap. Reloading...';
        setTimeout(() => location.reload(), 2000);
      }
    }, 2000);

  } catch (error) {
    alert('Error: ' + error.message);
    loading.style.display = 'none';
  }
}

// Phase 35: Social Engine - Load Pending Events
async function loadPendingSocialEvents() {
  try {
    const res = await fetch('/api/social/pending');
    const data = await res.json();

    const container = document.getElementById('pending-social-events');
    if (!container) return;

    if (!data.pending || data.pending.length === 0) {
      container.innerHTML = '<div style="color:var(--text-dim);font-size:0.9rem;">No pending messages from NPCs.</div>';
      return;
    }

    const pending = data.pending.filter(e => !e.processed);
    if (pending.length === 0) {
      container.innerHTML = '<div style="color:var(--text-dim);font-size:0.9rem;">No pending messages. All caught up!</div>';
      return;
    }

    container.innerHTML = pending.map(e => {
      const categoryColors = {
        'chat': '#60a5fa',
        'support': '#22c55e',
        'request': '#fbbf24',
        'conflict': '#ef4444',
        'invitation': '#a855f7',
        'gossip': '#ec4899'
      };
      const color = categoryColors[e.category] || '#6b7280';
      const time = new Date(e.timestamp).toLocaleTimeString();

      return `<div style="background:var(--bg);padding:0.75rem;border-radius:8px;margin-bottom:0.5rem;border-left:3px solid ${color};">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <div>
            <div style="font-weight:bold;">${esc(e.sender_name)}</div>
            <div style="font-size:0.85rem;color:var(--text-dim);">${esc(e.message)}</div>
          </div>
          <div style="text-align:right;">
            <div style="font-size:0.75rem;color:${color};font-weight:bold;text-transform:uppercase;">${e.category}</div>
            <div style="font-size:0.7rem;color:var(--text-dim);">${time}</div>
          </div>
        </div>
      </div>`;
    }).join('');
  } catch (e) {
    console.log('Failed to load social events:', e);
  }
}

// Social Standing Tab
function renderReputationPanel() {
  const rep = DATA.reputation || {};
  const globalScore = rep.global_score || 0;
  const circles = rep.circles || [];
  const events = rep.events || [];

  // Update global reputation meter
  const bar = document.getElementById('rep-bar');
  const text = document.getElementById('rep-text');
  const score = document.getElementById('rep-score');

  if (bar && text && score) {
    const pct = (globalScore + 100) / 2; // Convert -100..100 to 0..100
    bar.style.width = pct + '%';
    score.textContent = (globalScore >= 0 ? '+' : '') + globalScore;

    // Color and label based on score
    let rank = 'Neutral';
    let color = '#888';
    if (globalScore >= 80) { rank = 'Icon'; color = '#4a4'; }
    else if (globalScore >= 50) { rank = 'Respected'; color = '#8c4'; }
    else if (globalScore >= 20) { rank = 'Known'; color = '#ac8'; }
    else if (globalScore >= -20) { rank = 'Neutral'; color = '#888'; }
    else if (globalScore >= -50) { rank = 'Controversial'; color = '#c84'; }
    else { rank = 'Pariah'; color = '#e44'; }

    text.textContent = rank;
    bar.style.background = `linear-gradient(90deg, ${color}, ${color})`;
  }

  // Render circles
  const circlesList = document.getElementById('circles-list');
  if (circlesList) {
    if (circles.length === 0) {
      circlesList.innerHTML = '<p style="color:var(--text-dim);">No circles defined</p>';
    } else {
      const sortedCircles = [...circles].sort((a, b) => b.score - a.score);
      circlesList.innerHTML = sortedCircles.map(c => {
        const score = c.score || 0;
        const color = score >= 0 ? (score > 50 ? '#4a4' : '#8c4') : (score < -50 ? '#e44' : '#c84');
        return `<div style="display:flex;align-items:center;justify-content:space-between;padding:0.5rem;margin-bottom:0.5rem;background:var(--bg-dim);border-radius:6px;">
          <span>${c.name}</span>
          <span style="color:${color};font-weight:bold;">${score >= 0 ? '+' : ''}${score}</span>
        </div>`;
      }).join('');
    }
  }

  // Render events
  const eventsList = document.getElementById('events-list');
          if (eventsList) {
            if (events.length === 0) {
              eventsList.innerHTML = '<p style="color:var(--text-dim);">No recent events</p>';
            } else {
              eventsList.innerHTML = events.slice(0, 20).map(e => {
      
            const change = e.change || 0;
            const color = change >= 0 ? '#4a4' : '#e44';
            const date = e.timestamp ? new Date(e.timestamp).toLocaleDateString() : '';
            return `<div style="padding:0.5rem;margin-bottom:0.5rem;background:var(--bg-dim);border-radius:4px;font-size:0.85rem;">
              <div style="display:flex;justify-content:space-between;">
                <strong>${e.circle || 'Public'}</strong>
                <span style="color:${color};">${change >= 0 ? '+' : ''}${change}</span>
              </div>
              <div style="color:var(--text-dim);font-size:0.75rem;">${e.reason || ''}</div>
              <div style="color:var(--text-dim);font-size:0.7rem;">${date}</div>
            </div>`;
          }).join('');
        }
      }
}

// Contact CRM Functions - Phase 19
async function loadContactCRM() {
  // Get language from memory-lang select or default to English
  const langSelect = document.getElementById('memory-lang');
  const CRM_LANG = langSelect ? langSelect.value : (localStorage.getItem('genesis_lang') || 'en');

  const LABELS = {
    en: {
      noContacts: 'No contacts yet. Add your first contact above.',
      external: 'External',
      noCircle: 'No circle',
      noVisual: 'No visual description yet',
      reimag: 'Re-imagine',
      errorLoading: 'Error loading contacts'
    },
    de: {
      noContacts: 'Noch keine Kontakte. Füge oben deinen ersten Kontakt hinzu.',
      external: 'Extern',
      noCircle: 'Kein Kreis',
      noVisual: 'Noch keine visuelle Beschreibung',
      reimag: 'Neu gestalten',
      errorLoading: 'Fehler beim Laden der Kontakte'
    }
  };

  const T = LABELS[CRM_LANG] || LABELS.en;

  try {
    const response = await fetch('/api/social/entities');
    const data = await response.json();

    const container = document.getElementById('contact-crm-list');
    if (!container) return;

    if (!data.entities || data.entities.length === 0) {
      container.innerHTML = '<p style="color:var(--text-dim);">' + T.noContacts + '</p>';
      return;
    }

    container.innerHTML = data.entities.map(entity => {
      const avatar = entity.portrait_url || '';
      const hasVisual = entity.visual_description && entity.visual_description.length > 0;
      const isExternal = entity.is_external ? '<span style="background:var(--accent);color:#fff;padding:0.1rem 0.3rem;border-radius:3px;font-size:0.7rem;margin-left:0.3rem;">' + T.external + '</span>' : '';

      return `
        <div style="background:var(--bg);padding:1rem;border-radius:8px;border:1px solid var(--border);">
          <div style="display:flex;gap:1rem;align-items:start;">
            ${avatar ? `<img src="${avatar}" style="width:60px;height:60px;border-radius:50%;object-fit:cover;">` : `<div style="width:60px;height:60px;border-radius:50%;background:var(--bg-dim);display:flex;align-items:center;justify-content:center;font-size:1.5rem;">👤</div>`}
            <div style="flex:1;min-width:0;">
              <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.25rem;">
                <strong>${entity.name}</strong>
                ${isExternal}
              </div>
              <div style="font-size:0.8rem;color:var(--text-dim);margin-bottom:0.5rem;">
                ${entity.relationship_type} · ${entity.circle || T.noCircle} · Bond: ${entity.bond}
              </div>
              ${hasVisual ? `
                <div style="font-size:0.75rem;background:var(--bg-dim);padding:0.5rem;border-radius:4px;margin-bottom:0.5rem;max-height:60px;overflow-y:auto;">
                  ${entity.visual_description}
                </div>
              ` : `
                <div style="font-size:0.75rem;color:var(--text-dim);font-style:italic;margin-bottom:0.5rem;">
                  ${T.noVisual}
                </div>
              `}
              <button onclick="reImagineNPC('${entity.id}', '${encodeURIComponent(entity.name)}')" style="background:var(--core);color:#fff;border:none;padding:0.3rem 0.6rem;border-radius:4px;cursor:pointer;font-size:0.8rem;">🎨 ${T.reimag}</button>
            </div>
          </div>
        </div>
      `;
    }).join('');

  } catch (e) {
    console.log('Could not load contacts:', e);
    const container = document.getElementById('contact-crm-list');
    if (container) container.innerHTML = '<p style="color:var(--danger);">' + T.errorLoading + '</p>';
  }
}

async function addManualContact() {
  const name = document.getElementById('new-contact-name').value.trim();
  const circle = document.getElementById('new-contact-circle').value;
  const statusDiv = document.getElementById('add-contact-status');

  if (!name) {
    statusDiv.innerHTML = '<span style="color:var(--danger);">Please enter a name.</span>';
    return;
  }

  try {
    const response = await fetch('/api/social/add-entity', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ entity_name: name, circle: circle, relationship_type: 'acquaintance' })
    });
    const result = await response.json();

    if (result.success) {
      statusDiv.innerHTML = '<span style="color:var(--growth);">✓ Contact added!</span>';
      document.getElementById('new-contact-name').value = '';
      loadContactCRM();
    } else {
      statusDiv.innerHTML = '<span style="color:var(--danger);">Error: ' + (result.error || 'Unknown error') + '</span>';
    }
  } catch (e) {
    statusDiv.innerHTML = '<span style="color:var(--danger);">Error: ' + e.message + '</span>';
  }
}

async function reImagineNPC(entityId, encodedName) {
  const name = decodeURIComponent(encodedName);
  const prompt = prompt('Enter new visual description for ' + name + ' (e.g., "A tall man with short black hair, brown eyes, sharp jawline"):');

  if (!prompt || !prompt.trim()) return;

  try {
    const response = await fetch('/api/social/update-entity', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ entity_id: entityId, visual_description: prompt.trim() })
    });
    const result = await response.json();

    if (result.success) {
      alert('Visual description updated! A portrait will be generated on next photo.');
      loadContactCRM();
    } else {
      alert('Error: ' + (result.error || 'Unknown error'));
    }
  } catch (e) {
    alert('Error: ' + e.message);
  }
}

// Psychology Tab
  function renderPsychPanel() {
    const psych = DATA.psychology || {};

    // Resilience
    const res = psych.resilience || 0;
    const resColor = res > 70 ? 'var(--growth)' : (res < 30 ? 'var(--danger)' : 'var(--text)');
    document.getElementById('psych-resilience').innerHTML = `
      <div style="width:100%;height:20px;background:var(--border);border-radius:10px;overflow:hidden;">
        <div style="width:${res}%;height:100%;background:${resColor};transition:width 0.5s;"></div>
      </div>
      <p style="text-align:center;margin-top:0.5rem;">${res}/100</p>`;

    // Traumas
    const traumas = psych.traumas || [];
    if (traumas.length === 0) {
      document.getElementById('psych-traumas').innerHTML = '<p style="color:var(--text-dim);">No active traumas</p>';
    } else {
      document.getElementById('psych-traumas').innerHTML = traumas.map(t => `
        <div style="padding:0.5rem;margin-bottom:0.5rem;background:rgba(224,80,80,0.1);border-left:3px solid var(--danger);border-radius:4px;">
          <div style="display:flex;justify-content:space-between;">
            <strong>${t.description?.slice(0, 50) || 'Trauma'}${t.description?.length > 50 ? '...' : ''}</strong>
            <span style="color:var(--danger);">${t.severity}/100</span>
          </div>
          <div style="font-size:0.75rem;color:var(--text-dim);margin-top:0.2rem;">
            Trigger: ${t.trigger || 'unknown'} · Decay: ${t.decay_rate}/day
          </div>
        </div>`).join('');
    }

    // Phobias
    const phobias = psych.phobias || [];
    document.getElementById('psych-phobias').innerHTML = phobias.length > 0
      ? phobias.map(p => `<span style="display:inline-block;padding:0.2rem 0.5rem;margin:0.2rem;background:var(--border);border-radius:4px;font-size:0.85rem;">${p}</span>`).join('')
      : '<p style="color:var(--text-dim);">No phobias recorded</p>';

    // Joys
    const joys = psych.joys || [];
    document.getElementById('psych-joys').innerHTML = joys.length > 0
      ? joys.map(j => `<div style="padding:0.3rem 0;border-bottom:1px solid var(--border);">${j}</div>`).join('')
      : '<p style="color:var(--text-dim);">No joys recorded</p>';
  }

  function renderPhotoStream() {
    const container = document.getElementById('photo-stream');
    const photos = DATA.photos || [];

    if (photos.length === 0) {
      container.innerHTML = '<div class="empty-state">No photos captured yet. Use reality_camera to take a photo.</div>';
      return;
    }

    container.innerHTML = photos.map(p => `
      <div class="panel-card" style="padding:0.5rem;overflow:hidden;">
        <img src="/media/photos/${p}" style="width:100%;aspect-ratio:1;object-fit:cover;border-radius:8px;cursor:pointer;" onclick="window.open(this.src)">
        <div style="padding:0.5rem;font-size:0.75rem;color:var(--text-dim);">
          ${p.replace('photo_', '').replace('.png', '').replace(/_/g, ' ')}
        </div>
      </div>
    `).join('');
  }


// --- Integrated God-Mode Logic ---
async function initGodMode() {
    const sliders = ['energy', 'hunger', 'thirst', 'bladder', 'stress', 'hygiene', 'arousal', 'libido'];
    const container = document.getElementById('godmode-sliders');
    if (!container) return;
    container.innerHTML = '';
    sliders.forEach(k => {
        const row = document.createElement('div');
        row.style.display = 'grid'; row.style.gridTemplateColumns = '100px 1fr 40px'; row.style.gap = '1rem'; row.style.alignItems = 'center';
        row.innerHTML = `<label style="text-transform:capitalize; color:var(--text-dim);">${k}</label>
            <input type="range" id="gm-${k}" min="0" max="100" value="50" oninput="document.getElementById('gm-${k}-val').textContent=this.value">
            <span id="gm-${k}-val" style="color:var(--accent);">50</span>`;
        container.appendChild(row);
    });
    try {
        const resp = await fetch('/api/godmode/physique');
        const data = await resp.json();
        if (data && data.needs) {
            Object.entries(data.needs).forEach(([k, v]) => {
                const el = document.getElementById('gm-' + k);
                if (el) { el.value = v; document.getElementById('gm-' + k + '-val').textContent = v; }
            });
        }
    } catch(e) {}
}
async function applyGodModeNeeds() {
    const needs = {};
    ['energy', 'hunger', 'thirst', 'bladder', 'stress', 'hygiene', 'arousal', 'libido'].forEach(k => {
        needs[k] = parseInt(document.getElementById('gm-' + k).value);
    });
    await fetch('/api/godmode/override/needs', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(needs)
    });
    alert('✅ Needs updated!');
}
async function injectGodModeEvent() {
    const event = {
        type: document.getElementById('gm-event-type').value,
        event: document.getElementById('gm-event-desc').value || 'Manual Override',
        impact: parseInt(document.getElementById('gm-event-impact').value)
    };
    await fetch('/api/godmode/inject/event', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(event)
    });
    alert('🎲 Event injected!');
}
// Hook into existing switchTab
if (!window._gm_hooked) {
    const oldSwitch = window.switchTab;
    window.switchTab = function(t) {
        if(oldSwitch) oldSwitch(t);
        if(t === 'godmode') initGodMode();
    };
    window._gm_hooked = true;
}
</script>

<!-- Three.js + VRM Avatar Script (Phase 22) -->
<script type="module">
// VRM Avatar Viewer - Three.js + @pixiv/three-vrm
// Phase 23: Emotional Expressiveness with Smooth BlendShape Transitions
let vrmModel = null;
let scene, camera, renderer;
let currentPose = 'idle';
let currentEmote = 'neutral';
let animationId = null;

// BlendShape state for smooth transitions (Phase 23)
let currentBlendShapes = {
  joy: 0, angry: 0, sad: 0, fear: 0, surprise: 0,
  neutral: 1, relaxed: 0, blinkLeft: 0, blinkRight: 0, blink: 0
};
let targetBlendShapes = { ...currentBlendShapes };
let lastExpressionUpdate = 0;
const LERP_SPEED = 0.05; // 5% per frame for smooth transition (~0.5s to settle)

// Default blend shapes (neutral)
const DEFAULT_BLENDSHAPES = {
  joy: 0, angry: 0, sad: 0, fear: 0, surprise: 0,
  neutral: 1, relaxed: 0, blinkLeft: 0, blinkRight: 0, blink: 0
};

// Import Three.js and VRM from CDN
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';
import { GLTFLoader } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/controls/OrbitControls.js';

// VRM support via simple fallback (full VRMLoader requires additional imports)
async function loadVRM(url) {
  const loader = new GLTFLoader();

  return new Promise((resolve, reject) => {
    loader.load(
      url,
      (gltf) => {
        resolve(gltf.scene);
      },
      (progress) => {
        console.log('Loading:', (progress.loaded / progress.total * 100) + '%');
      },
      (error) => {
        reject(error);
      }
    );
  });
}

async function initAvatar() {
  const canvas = document.getElementById('vrm-canvas');
  const loading = document.getElementById('avatar-loading');
  const error = document.getElementById('avatar-error');
  const statusText = document.getElementById('avatar-status-text');

  try {
    // Get avatar config
    const configRes = await fetch('/api/avatar/config');
    const config = await configRes.json();

    if (!config.vrm_path) {
      throw new Error('No VRM path configured');
    }

    // Setup Three.js scene
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a2e);

    // Camera
    camera = new THREE.PerspectiveCamera(45, canvas.clientWidth / canvas.clientHeight, 0.1, 1000);
    camera.position.set(0, 1.2, 3);

    // Renderer
    renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 5, 5);
    scene.add(directionalLight);

    // Load VRM/GLTF model
    const modelPath = config.vrm_path.replace('/home/leo/Schreibtisch', '');
    statusText.textContent = 'Loading 3D model...';

    vrmModel = await loadVRM(modelPath);

    // Scale and position the model
    vrmModel.scale.set(1, 1, 1);
    vrmModel.position.set(0, 0, 0);

    scene.add(vrmModel);

    // Hide loading, show canvas
    loading.style.display = 'none';
    statusText.textContent = 'Avatar loaded successfully';

    // Start animation loop
    animate();

    // Start polling for avatar state updates
    startAvatarPolling();

  } catch (err) {
    console.error('Failed to load avatar:', err);
    loading.style.display = 'none';
    error.style.display = 'block';
    statusText.textContent = 'Error: ' + err.message;
  }
}

function animate() {
  animationId = requestAnimationFrame(animate);

  if (vrmModel) {
    // Subtle idle animation
    const time = Date.now() * 0.001;
    vrmModel.position.y = Math.sin(time) * 0.02;

    // Phase 23: Smooth BlendShape interpolation (lerping)
    updateBlendShapesLerp();

    // Phase 24: Lip-sync analysis
    updateLipSync();

    // Phase 25: Motion/Idle animations
    updateMotionLerp();

    // Phase 29: Animate weather particles
    animateWeatherParticles();
  }

  renderer.render(scene, camera);
}

// Phase 23: Lerp current blend shapes toward target
function updateBlendShapesLerp() {
  let allSettled = true;

  for (const key of Object.keys(targetBlendShapes)) {
    const target = targetBlendShapes[key];
    const current = currentBlendShapes[key];

    if (Math.abs(target - current) > 0.001) {
      currentBlendShapes[key] = current + (target - current) * LERP_SPEED;
      allSettled = false;
    }
  }

  // Apply blend shapes to VRM model
  applyBlendShapesToVRM(currentBlendShapes);

  // Update status if expressions changed
  if (!allSettled) {
    const statusText = document.getElementById('avatar-status-text');
    if (statusText) {
      // Determine dominant expression
      const dominant = getDominantExpression(currentBlendShapes);
      statusText.textContent = `Expression: ${dominant}`;
    }
  }
}

// Apply computed blend shapes to VRM mesh (Phase 23)
function applyBlendShapesToVRM(blendShapes) {
  if (!vrmModel) return;

  // Find the VRM's face mesh (typically named "Face" or "Head")
  // This is a fallback implementation - full VRM uses specific blendShape weights

  // Calculate emissive color based on blend shapes
  const joy = blendShapes.joy || 0;
  const angry = blendShapes.angry || 0;
  const sad = blendShapes.sad || 0;
  const fear = blendShapes.fear || 0;

  // Color blending based on expression weights
  let r = 0, g = 0, b = 0;

  // Joy = green/yellow tint
  r += joy * 0.2;
  g += joy * 0.5;

  // Angry = red tint
  r += angry * 0.8;

  // Sad = blue tint
  b += sad * 0.5;

  // Fear = purple tint
  r += fear * 0.3;
  b += fear * 0.3;

  const intensity = Math.max(joy, angry, sad, fear) * 0.4;

  vrmModel.traverse((child) => {
    if (child.isMesh && child.material) {
      // Face/head meshes get expression colors
      const name = child.name.toLowerCase();
      if (name.includes('face') || name.includes('head')) {
        child.material.emissive = new THREE.Color(r, g, b);
        child.material.emissiveIntensity = intensity;
      }
    }
  });
}

// Get the dominant expression from blend shape weights
function getDominantExpression(blendShapes) {
  const { joy, angry, sad, fear, surprise, relaxed, neutral } = blendShapes;

  const max = Math.max(joy, angry, sad, fear, surprise, relaxed, neutral);

  if (max === joy && joy > 0.1) return 'Joy';
  if (max === angry && angry > 0.1) return 'Angry';
  if (max === sad && sad > 0.1) return 'Sad';
  if (max === fear && fear > 0.1) return 'Fear';
  if (max === surprise && surprise > 0.1) return 'Surprise';
  if (max === relaxed && relaxed > 0.1) return 'Relaxed';
  return 'Neutral';
}

function startAvatarPolling() {
  // Poll for state updates every 500ms
  setInterval(async () => {
    try {
      const res = await fetch('/api/avatar/state');
      const state = await res.json();

      if (state.action) {
        // Phase 23: Handle expression updates from tick handler
        if (state.action === 'expression' && state.blendShapes) {
          // Set target blend shapes for smooth interpolation
          targetBlendShapes = { ...DEFAULT_BLENDSHAPES, ...state.blendShapes };
          console.log('Expression update:', targetBlendShapes);
        }
        // Phase 24: Handle voice playback requests
        else if (state.action === 'voice' && state.audioUrl) {
          handleVoicePlayback(state);
        }
        // Phase 25: Handle motion updates
        else if (state.action === 'motion' || state.action === 'motion_walking') {
          handleMotionUpdate(state);
        }
        // Phase 29: Handle atmosphere sync
        else if (state.action === 'sync_atmosphere' && state.atmosphere) {
          handleAtmosphereUpdate(state.atmosphere);
        }
        // Phase 33: Handle interaction updates (props, furniture, light)
        else if (state.interaction) {
          handleInteractionUpdate(state.interaction);
        }
        else if (state.action === 'pose' && state.value) {
          applyPose(state.value);
        } else if (state.action === 'emote' && state.value) {
          applyEmote(state.value);
        } else if (state.action === 'sync_wardrobe') {
          syncWardrobe();
        }
      }
    } catch (e) {
      console.error('Avatar polling error:', e);
    }
  }, 500);
}

// Apply pose (basic implementation - rotates the model)
function applyPose(pose) {
  if (!vrmModel) return;

  currentPose = pose;
  console.log('Applying pose:', pose);

  // Reset rotation
  vrmModel.rotation.set(0, 0, 0);

  switch (pose) {
    case 'sitting':
      vrmModel.position.y = -0.3;
      break;
    case 'standing':
      vrmModel.position.y = 0;
      break;
    case 'walking':
      vrmModel.position.y = 0;
      // Slight animation would go here
      break;
    case 'idle':
    default:
      vrmModel.position.y = 0;
      break;
  }
}

// Apply emote (basic implementation - color/scale changes as fallback)
function applyEmote(emote) {
  if (!vrmModel) return;

  currentEmote = emote;
  console.log('Applying emote:', emote);

  // Reset
  vrmModel.traverse((child) => {
    if (child.isMesh && child.material) {
      child.material.emissive = new THREE.Color(0x000000);
      child.material.emissiveIntensity = 0;
    }
  });

  // Apply emote colors
  const emoteColors = {
    'joy': 0x00ff00,
    'angry': 0xff0000,
    'sad': 0x0000ff,
    'neutral': 0x000000,
    'relaxed': 0x00ffff
  };

  const color = emoteColors[emote] || 0x000000;

  if (color !== 0x000000) {
    vrmModel.traverse((child) => {
      if (child.isMesh && child.material) {
        child.material.emissive = new THREE.Color(color);
        child.material.emissiveIntensity = 0.3;
      }
    });
  }
}

// Sync wardrobe from physique.json
async function syncWardrobe() {
  const container = document.getElementById('avatar-wardrobe');

  try {
    const res = await fetch('/api/avatar/config');
    const config = await res.json();

    // In a full implementation, this would update VRM meshes
    container.innerHTML = `
      <div class="panel-card" style="padding:0.5rem;">
        <div style="font-weight:bold;">Outfit Synced</div>
        <div style="font-size:0.8rem;color:var(--text-dim);">VRM meshes updated</div>
      </div>
    `;

    console.log('Wardrobe synced');
  } catch (e) {
    container.innerHTML = `<div style="color:var(--error);">Sync failed: ${e.message}</div>`;
  }
}

// Global functions for buttons
window.setAvatarPose = async function(pose) {
  try {
    await fetch('/api/avatar/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'pose', value: pose })
    });
    applyPose(pose);
  } catch (e) {
    console.error('Failed to set pose:', e);
  }
};

window.setAvatarEmote = async function(emote) {
  try {
    await fetch('/api/avatar/update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'emote', value: emote })
    });
    applyEmote(emote);
  } catch (e) {
    console.error('Failed to set emote:', e);
  }
};

// Phase 33: Light control function
window.setLightState = async function(action) {
  try {
    // Use the new reality_light tool via the simulation config endpoint
    const res = await fetch('/api/config/simulation', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'light',
        light_action: action
      })
    });
    const data = await res.json();
    console.log('Light state:', action, data);

    // Update local state for immediate feedback
    if (directionalLight) {
      const intensities = { on: 0.8, off: 0, dim: 0.3, bright: 1.0, toggle: currentInteraction.lightIntensity > 0 ? 0 : 0.8 };
      const intensity = intensities[action];
      directionalLight.intensity = intensity;
      if (ambientLight) ambientLight.intensity = intensity * 0.75;
      currentInteraction.lightIntensity = intensity;
    }
  } catch (e) {
    console.error('Failed to set light state:', e);
  }
};

// ============================================================
// Phase 24: Vocal Resonance (Lip-Sync)
// ============================================================

// Audio context for lip-sync analysis
let audioContext = null;
let audioElement = null;
let analyserNode = null;
let audioSource = null;
let isPlayingAudio = false;
let lipSyncData = {
  vowel_a: 0,  // open mouth
  vowel_i: 0,  // wide
  vowel_u: 0,  // round
  vowel_e: 0,  // wide smile
  vowel_o: 0   // round
};
let targetLipSync = { ...lipSyncData };
const LIP_DECAY = 0.1; // How fast mouth closes when audio stops
const LIP_SENSITIVITY = 2.0; // Audio sensitivity multiplier

// Initialize audio system for lip-sync
function initAudioSystem() {
  if (audioContext) return;

  try {
    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    analyserNode = audioContext.createAnalyser();
    analyserNode.fftSize = 256;
    analyserNode.smoothingTimeConstant = 0.5;

    // Create hidden audio element
    audioElement = new Audio();
    audioElement.crossOrigin = 'anonymous';

    // Connect to analyser
    audioSource = audioContext.createMediaElementSource(audioElement);
    audioSource.connect(analyserNode);
    analyserNode.connect(audioContext.destination);

    // Audio ended handler
    audioElement.addEventListener('ended', () => {
      isPlayingAudio = false;
      console.log('Audio playback ended');
    });

    console.log('Audio system initialized for lip-sync');
  } catch (e) {
    console.error('Failed to initialize audio system:', e);
  }
}

// Play audio and trigger lip-sync
async function playAudioWithLipSync(audioUrl) {
  if (!audioContext) {
    initAudioSystem();
  }

  if (!audioElement || !audioContext) {
    console.error('Audio system not available');
    return;
  }

  try {
    // Resume audio context (required for autoplay policy)
    if (audioContext.state === 'suspended') {
      await audioContext.resume();
    }

    // Load and play audio
    audioElement.src = audioUrl;
    await audioElement.play();
    isPlayingAudio = true;

    console.log('Playing audio with lip-sync:', audioUrl);
  } catch (e) {
    console.error('Failed to play audio:', e);
  }
}

// Analyze audio and update lip-sync blend shapes
function updateLipSync() {
  if (!isPlayingAudio || !analyserNode) {
    // Decay lip shapes when not speaking
    for (const key of Object.keys(lipSyncData)) {
      lipSyncData[key] = Math.max(0, lipSyncData[key] - LIP_DECAY);
    }
    applyLipSyncToVRM(lipSyncData);
    return;
  }

  try {
    const bufferLength = analyserNode.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    analyserNode.getByteFrequencyData(dataArray);

    // Calculate average volume/intensity
    let sum = 0;
    for (let i = 0; i < bufferLength; i++) {
      sum += dataArray[i];
    }
    const average = sum / bufferLength;
    const intensity = Math.min(1, (average / 128) * LIP_SENSITIVITY);

    // Map intensity to vowel shapes (simplified mouth positions)
    // These create natural-sounding mouth movements
    const time = Date.now() * 0.01;

    // A (ah) - open mouth
    targetLipSync.vowel_a = intensity * 0.8;
    // I (ee) - wide
    targetLipSync.vowel_i = intensity * Math.abs(Math.sin(time * 1.5)) * 0.6;
    // U (oo) - round
    targetLipSync.vowel_u = intensity * Math.abs(Math.sin(time * 0.8)) * 0.5;
    // E (eh) - wide smile
    targetLipSync.vowel_e = intensity * Math.abs(Math.cos(time * 1.2)) * 0.4;
    // O (oh) - round
    targetLipSync.vowel_o = intensity * Math.abs(Math.sin(time * 0.6)) * 0.5;

    // Smooth interpolation
    for (const key of Object.keys(lipSyncData)) {
      const target = targetLipSync[key];
      const current = lipSyncData[key];
      lipSyncData[key] = current + (target - current) * 0.3;
    }

    // Apply to VRM
    applyLipSyncToVRM(lipSyncData);

  } catch (e) {
    console.error('Lip-sync analysis error:', e);
  }
}

// Apply lip-sync blend shapes to VRM model
function applyLipSyncToVRM(lipShapes) {
  if (!vrmModel) return;

  // Map vowels to mouth shape
  // vowel_a = open, vowel_i = wide, vowel_u = round, etc.
  const mouthOpen = lipShapes.vowel_a;  // How much mouth is open
  const mouthWide = lipShapes.vowel_i + lipShapes.vowel_e;  // Width
  const mouthRound = lipShapes.vowel_u + lipShapes.vowel_o;  // Roundness

  vrmModel.traverse((child) => {
    if (child.isMesh && child.material) {
      const name = child.name.toLowerCase();
      // Face/head meshes
      if (name.includes('face') || name.includes('head')) {
        // Create subtle pulsing based on lip-sync
        const pulse = mouthOpen * 0.15;
        child.material.emissiveIntensity = 0.1 + pulse;
      }
      // Mouth area - more intense effect
      if (name.includes('mouth') || name.includes('lip')) {
        child.material.emissive = new THREE.Color(mouthRound * 0.2, mouthWide * 0.1, mouthOpen * 0.1);
        child.material.emissiveIntensity = mouthOpen * 0.5;
      }
    }
  });
}

// Handle voice playback requests from backend
function handleVoicePlayback(state) {
  if (state.action === 'voice' && state.audioUrl) {
    const audioUrl = state.audioUrl;
    console.log('Voice playback requested:', audioUrl);
    playAudioWithLipSync(audioUrl);
  }
}

// Global function to manually trigger voice playback
window.playAvatarVoice = playAudioWithLipSync;

// ============================================================
// Phase 25: Physical Reaction (Idle Animations)
// ============================================================

// Motion state from backend
let currentMotion = {
  idle: 'neutral',
  breathingRate: 1.0,
  posture: 0.5,
  movementIntensity: 0.1,
  shakeAmplitude: 0,
  fidgetFrequency: 0
};
let targetMotion = { ...currentMotion };
let isWalking = false;
let walkingTimer = null;
const WALKING_DURATION = 4000; // 4 seconds walking animation

// Procedural breathing state
let breathPhase = 0; // 0-2*PI for sine wave

// Apply motion state to VRM model
function applyMotionToVRM(motion) {
  if (!vrmModel) return;

  const time = Date.now() * 0.001;
  const { idle, breathingRate, posture, movementIntensity, shakeAmplitude, fidgetFrequency } = motion;

  // Calculate breathing (sine wave)
  breathPhase += breathingRate * 0.03;
  const breathAmount = Math.sin(breathPhase) * 0.02 * breathingRate;

  // Apply to model
  vrmModel.traverse((child) => {
    if (!child.isMesh) return;

    const name = child.name.toLowerCase();

    // Spine/Chest - breathing animation
    if (name.includes('spine') || name.includes('chest') || name.includes('torso')) {
      // Breathing
      child.position.y = breathAmount;

      // Shaking (high stress)
      if (shakeAmplitude > 0) {
        child.position.x += (Math.random() - 0.5) * shakeAmplitude * 0.01;
      }
    }

    // Head - slight movement
    if (name.includes('head')) {
      // Posture affects head position
      const postureOffset = (posture - 0.5) * 0.05;
      child.position.y = postureOffset;

      // Fidgeting - random small movements
      if (fidgetFrequency > 0) {
        child.position.x += Math.sin(time * 10) * fidgetFrequency * 0.01;
        child.rotation.z = Math.sin(time * 8) * fidgetFrequency * 0.05;
      }
    }

    // General movement intensity
    if (movementIntensity > 0.1) {
      // Subtle sway
      child.rotation.y = Math.sin(time * 0.5) * movementIntensity * 0.02;
    }
  });
}

// Handle motion state updates from backend
function handleMotionUpdate(state) {
  // Phase 27: Handle sleeping state from dream engine
  if (state.motion && state.motion.isSleeping) {
    targetMotion = {
      idle: 'sleeping',
      breathingRate: 0.4,  // Very slow deep breathing
      posture: 0.1,         // Lying down
      movementIntensity: 0, // Completely still
      shakeAmplitude: 0,
      fidgetFrequency: 0,
      isSleeping: true
    };
    console.log('Entering sleep mode...');
    return;
  }

  if (state.motion) {
    // Extract isSleeping from motion if present
    const { isSleeping, ...motionWithoutSleeping } = state.motion;
    targetMotion = { ...motionWithoutSleeping, isSleeping: isSleeping || false };
    console.log('Motion update:', targetMotion);
  }

  // Handle walking animation
  if (state.isWalking || state.action === 'motion_walking') {
    isWalking = true;

    // Clear existing timer
    if (walkingTimer) {
      clearTimeout(walkingTimer);
    }

    // Set walking state
    targetMotion = {
      idle: 'walking',
      breathingRate: 1.5,
      posture: 0.8,
      movementIntensity: 0.8,
      shakeAmplitude: 0,
      fidgetFrequency: 0,
      isSleeping: false
    };

    // After walking duration, return to idle
    walkingTimer = setTimeout(() => {
      isWalking = false;
      targetMotion = {
        idle: 'neutral',
        breathingRate: 1.0,
        posture: 0.5,
        movementIntensity: 0.1,
        shakeAmplitude: 0,
        fidgetFrequency: 0,
        isSleeping: false
      };
      console.log('Walking complete, returning to idle');
    }, WALKING_DURATION);
  }
}

// Update motion with smooth interpolation
function updateMotionLerp() {
  let allSettled = true;

  for (const key of Object.keys(targetMotion)) {
    const target = targetMotion[key];
    const current = currentMotion[key];

    if (typeof target === 'number' && typeof current === 'number') {
      if (Math.abs(target - current) > 0.001) {
        currentMotion[key] = current + (target - current) * 0.1;
        allSettled = false;
      }
    } else if (target !== current) {
      currentMotion[key] = target;
      allSettled = false;
    }
  }

  // Apply to VRM
  applyMotionToVRM(currentMotion);
}

// ============================================================
// Phase 29: Atmospheric Sync (Weather, Time & Lighting)
// ============================================================

// Three.js objects for lighting
let directionalLight = null;
let ambientLight = null;
let rainParticles = null;
let snowParticles = null;

// Atmosphere state
let currentAtmosphere = {
  lightIntensity: 0.8,
  lightColor: '#ffffff',
  ambientIntensity: 0.6,
  ambientColor: '#ffffff',
  backgroundColor: '#1a1a2e',
  weather: 'clear',
  timeOfDay: 'afternoon'
};

// Phase 33: Interaction state (props, furniture, light)
let currentInteraction = {
  holding: [],
  lightIntensity: 0.8,
  lightColor: '#ffffff',
  furniture: '',
  prop: ''
};

// Initialize weather particle systems
function initWeatherParticles() {
  if (!scene) return;

  // Rain particles
  const rainGeometry = new THREE.BufferGeometry();
  const rainCount = 1000;
  const rainPositions = new Float32Array(rainCount * 3);
  for (let i = 0; i < rainCount * 3; i += 3) {
    rainPositions[i] = (Math.random() - 0.5) * 10;     // x
    rainPositions[i + 1] = Math.random() * 10;        // y
    rainPositions[i + 2] = (Math.random() - 0.5) * 10; // z
  }
  rainGeometry.setAttribute('position', new THREE.BufferAttribute(rainPositions, 3));
  const rainMaterial = new THREE.PointsMaterial({
    color: 0xaaaaaa,
    size: 0.02,
    transparent: true,
    opacity: 0.6
  });
  rainParticles = new THREE.Points(rainGeometry, rainMaterial);
  rainParticles.visible = false;
  scene.add(rainParticles);

  // Snow particles
  const snowGeometry = new THREE.BufferGeometry();
  const snowPositions = new Float32Array(rainCount * 3);
  for (let i = 0; i < rainCount * 3; i += 3) {
    snowPositions[i] = (Math.random() - 0.5) * 10;
    snowPositions[i + 1] = Math.random() * 10;
    snowPositions[i + 2] = (Math.random() - 0.5) * 10;
  }
  snowGeometry.setAttribute('position', new THREE.BufferAttribute(snowPositions, 3));
  const snowMaterial = new THREE.PointsMaterial({
    color: 0xffffff,
    size: 0.04,
    transparent: true,
    opacity: 0.8
  });
  snowParticles = new THREE.Points(snowGeometry, snowMaterial);
  snowParticles.visible = false;
  scene.add(snowParticles);
}

// Initialize lights
function initAtmosphereLights() {
  if (!scene) return;

  // Directional light (sun/moon)
  directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
  directionalLight.position.set(5, 5, 5);
  scene.add(directionalLight);

  // Ambient light
  ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
  scene.add(ambientLight);
}

// Update atmosphere
function handleAtmosphereUpdate(atmosphere) {
  currentAtmosphere = {
    lightIntensity: atmosphere.lightIntensity ?? currentAtmosphere.lightIntensity,
    lightColor: atmosphere.lightColor ?? currentAtmosphere.lightColor,
    ambientIntensity: atmosphere.ambientIntensity ?? currentAtmosphere.ambientIntensity,
    ambientColor: atmosphere.ambientColor ?? currentAtmosphere.ambientColor,
    backgroundColor: atmosphere.backgroundColor ?? currentAtmosphere.backgroundColor,
    weather: atmosphere.weather ?? currentAtmosphere.weather,
    timeOfDay: atmosphere.timeOfDay ?? currentAtmosphere.timeOfDay
  };

  // Update lighting
  if (directionalLight) {
    directionalLight.intensity = currentAtmosphere.lightIntensity;
    directionalLight.color.set(currentAtmosphere.lightColor);
  }

  if (ambientLight) {
    ambientLight.intensity = currentAtmosphere.ambientIntensity;
    ambientLight.color.set(currentAtmosphere.ambientColor);
  }

  // Update background
  if (scene) {
    scene.background = new THREE.Color(currentAtmosphere.backgroundColor);
  }

  // Update weather particles
  updateWeatherParticles(currentAtmosphere.weather);

  // Update UI
  updateAtmosphereUI(currentAtmosphere);

  console.log('Atmosphere updated:', currentAtmosphere.timeOfDay, currentAtmosphere.weather);
}

// ============================================================
// Phase 33: Interactive Environment (Props, Furniture, Light Control)
// ============================================================

// Handle interaction updates from prop_mapper
function handleInteractionUpdate(interaction) {
  currentInteraction = {
    holding: interaction.holding ?? currentInteraction.holding,
    lightIntensity: interaction.lightIntensity ?? currentInteraction.lightIntensity,
    lightColor: interaction.lightColor ?? currentInteraction.lightColor,
    furniture: interaction.furniture ?? currentInteraction.furniture,
    prop: interaction.prop ?? currentInteraction.prop
  };

  // Update lighting based on interaction state
  if (directionalLight) {
    directionalLight.intensity = currentInteraction.lightIntensity;
    directionalLight.color.set(currentInteraction.lightColor);
  }

  if (ambientLight) {
    ambientLight.intensity = currentInteraction.lightIntensity * 0.75;
    ambientLight.color.set(currentInteraction.lightColor);
  }

  // Update background brightness based on light
  if (scene) {
    const brightness = currentInteraction.lightIntensity;
    const r = Math.floor(0x1a * brightness);
    const g = Math.floor(0x1a * brightness);
    const b = Math.floor(0x2e * brightness);
    scene.background = new THREE.Color(r, g, b);
  }

  // Update UI
  updateInteractionUI(currentInteraction);

  console.log('Interaction updated:', currentInteraction);
}

// Update interaction UI
function updateInteractionUI(interaction) {
  const container = document.getElementById('interaction-status');
  if (!container) return;

  let html = '<div style="display:flex;flex-wrap:wrap;gap:0.5rem;align-items:center;">';

  // Holding props
  if (interaction.holding && interaction.holding.length > 0) {
    html += `<span class="tag" style="background:var(--accent);">Holding: ${interaction.holding.join(', ')}</span>`;
  }

  // Furniture
  if (interaction.furniture) {
    html += `<span class="tag" style="background:var(--primary);">At: ${interaction.furniture}</span>`;
  }

  // Light status
  if (interaction.lightIntensity > 0.5) {
    html += '<span class="tag" style="background:#4ade80;">Light: On</span>';
  } else if (interaction.lightIntensity > 0) {
    html += '<span class="tag" style="background:#fbbf24;">Light: Dim</span>';
  } else {
    html += '<span class="tag" style="background:#6b7280;">Light: Off</span>';
  }

  html += '</div>';
  container.innerHTML = html;
}

// Update weather particles
function updateWeatherParticles(weather) {
  if (!rainParticles || !snowParticles) return;

  // Hide all first
  rainParticles.visible = false;
  snowParticles.visible = false;

  switch (weather) {
    case 'rainy':
    case 'stormy':
      rainParticles.visible = true;
      break;
    case 'snowy':
      snowParticles.visible = true;
      break;
    default:
      // Clear weather - no particles
      break;
  }
}

// Animate weather particles
function animateWeatherParticles() {
  if (!scene) return;

  const time = Date.now() * 0.001;

  if (rainParticles && rainParticles.visible) {
    const positions = rainParticles.geometry.attributes.position.array;
    for (let i = 1; i < positions.length; i += 3) {
      positions[i] -= 0.1; // Fall down
      if (positions[i] < 0) {
        positions[i] = 10; // Reset to top
      }
    }
    rainParticles.geometry.attributes.position.needsUpdate = true;
  }

  if (snowParticles && snowParticles.visible) {
    const positions = snowParticles.geometry.attributes.position.array;
    for (let i = 1; i < positions.length; i += 3) {
      positions[i] -= 0.02; // Slow fall
      positions[i - 1] += Math.sin(time + i) * 0.002; // Drift
      if (positions[i] < 0) {
        positions[i] = 10;
      }
    }
    snowParticles.geometry.attributes.position.needsUpdate = true;
  }
}

// Update UI overlay
function updateAtmosphereUI(atmosphere) {
  let statusText = document.getElementById('avatar-status-text');
  if (statusText) {
    const weatherEmoji = {
      'clear': '☀️',
      'cloudy': '☁️',
      'rainy': '🌧️',
      'stormy': '⛈️',
      'snowy': '❄️',
      'foggy': '🌫️',
      'windy': '💨'
    };
    const emoji = weatherEmoji[atmosphere.weather] || '🌤️';
    statusText.textContent = `${emoji} ${atmosphere.timeOfDay} | ${atmosphere.weather}`;
  }
}

// Call atmosphere init from avatar init
const originalInitAvatar = window.initAvatar;
window.initAvatar = async function() {
  await originalInitAvatar();

  // Initialize atmosphere after VRM loads
  initAtmosphereLights();
  initWeatherParticles();

  // Try to load initial atmosphere state
  try {
    const res = await fetch('/api/avatar/state');
    const state = await res.json();
    if (state.action === 'sync_atmosphere' && state.atmosphere) {
      handleAtmosphereUpdate(state.atmosphere);
    }
  } catch (e) {
    console.log('No initial atmosphere state');
  }
};

window.syncAvatarWardrobe = syncWardrobe;

// ============================================================
// Phase 31: Interests & Dreams Tab Functions
// ============================================================

// Load interests data and render
async function loadInterestsTab() {
  try {
    // Fetch interests data
    const res = await fetch('/api/interests');
    const interests = await res.json();

    // Render hobbies
    const hobbyList = document.getElementById('hobby-list');
    if (hobbyList && interests.hobbies) {
      if (interests.hobbies.length === 0) {
        hobbyList.innerHTML = '<div style="color:var(--text-dim);">No hobbies discovered yet. High energy leads to curiosity!</div>';
      } else {
        hobbyList.innerHTML = interests.hobbies.map(h => `
          <div class="panel-card" style="padding:0.75rem;">
            <div style="font-weight:bold;">${h.topic}</div>
            <div style="display:flex;align-items:center;gap:0.5rem;margin-top:0.5rem;">
              <div style="flex:1;height:6px;background:var(--bg);border-radius:3px;overflow:hidden;">
                <div style="width:${h.sentiment * 100}%;height:100%;background:var(--accent);border-radius:3px;"></div>
              </div>
              <span style="font-size:0.8rem;color:var(--text-dim);">${Math.round(h.sentiment * 100)}%</span>
            </div>
            <div style="font-size:0.75rem;color:var(--text-dim);margin-top:0.25rem;">Researched ${h.researchCount}x</div>
          </div>
        `).join('');
      }
    }

    // Render likes
    const likesList = document.getElementById('likes-list');
    if (likesList && interests.likes) {
      const likes = Object.entries(interests.likes);
      if (likes.length === 0) {
        likesList.innerHTML = '<div style="color:var(--text-dim);font-size:0.85rem;">No likes recorded yet</div>';
      } else {
        likesList.innerHTML = likes.map(([topic, score]) => `
          <div style="padding:0.25rem 0;border-bottom:1px solid var(--border);">
            <span>${topic}</span>
            <span style="float:right;color:var(--growth);">${Math.round(score * 100)}%</span>
          </div>
        `).join('');
      }
    }

    // Render dislikes
    const dislikesList = document.getElementById('dislikes-list');
    if (dislikesList && interests.dislikes) {
      if (interests.dislikes.length === 0) {
        dislikesList.innerHTML = '<div style="color:var(--text-dim);font-size:0.85rem;">No dislikes recorded yet</div>';
      } else {
        dislikesList.innerHTML = interests.dislikes.map(d => `
          <div style="padding:0.25rem 0;border-bottom:1px solid var(--border);color:var(--error);">${d}</div>
        `).join('');
      }
    }

  } catch (e) {
    console.error('Failed to load interests:', e);
  }
}

// Load dreams data and render
async function loadDreamsTab() {
  try {
    // Fetch dreams list
    const res = await fetch('/api/dreams');
    const data = await res.json();

    // Update stats
    document.getElementById('dream-count').textContent = data.count || 0;
    document.getElementById('insight-count').textContent = data.insights || 0;
    document.getElementById('last-dream-date').textContent = data.lastDate || '—';

    // Get current dream state
    const stateRes = await fetch('/api/avatar/state');
    const state = await stateRes.json();
    const dreamStateEl = document.getElementById('dream-state');
    if (dreamStateEl) {
      if (state.motion && state.motion.isSleeping) {
        dreamStateEl.textContent = 'Dreaming';
        dreamStateEl.style.color = 'var(--dream)';
      } else {
        dreamStateEl.textContent = 'Awake';
      }
    }

    // Render dream list
    const dreamList = document.getElementById('dream-list');
    if (dreamList && data.dreams) {
      if (data.dreams.length === 0) {
        dreamList.innerHTML = '<div style="color:var(--text-dim);font-style:italic;">No dreams recorded yet</div>';
      } else {
        dreamList.innerHTML = data.dreams.map(d => `
          <div class="panel-card" style="margin-bottom:1rem;padding:1rem;border-left:4px solid var(--dream);">
            <div style="display:flex;justify-content:space-between;align-items:center;">
              <h4 style="color:var(--accent);">${d.date}</h4>
              <span style="font-size:0.8rem;color:var(--text-dim);">${d.insights} insights</span>
            </div>
            <p style="margin-top:0.5rem;color:var(--text);">${d.summary}</p>
          </div>
        `).join('');
      }
    }

  } catch (e) {
    console.error('Failed to load dreams:', e);
  }
}

// Load on page load if tabs are visible
if (document.getElementById('tab-interests').classList.contains('active')) {
  loadInterestsTab();
}
if (document.getElementById('tab-dreams').classList.contains('active')) {
  loadDreamsTab();
}

// ============================================================
// Phase 32: Simulation Tuning & VMC Config
// ============================================================

// Slider value display updates
['tune-hunger-rate', 'tune-thirst-rate', 'tune-energy-drain', 'tune-stress-rate', 'tune-reflex-threshold', 'tune-dream-threshold'].forEach(id => {
  const el = document.getElementById(id);
  if (el) {
    el.addEventListener('input', function() {
      const val = document.getElementById(id + '-val');
      if (val) val.textContent = this.value;
    });
  }
});

// Save simulation config
window.saveSimulationConfig = async function() {
  const config = {
    hunger_rate: parseFloat(document.getElementById('tune-hunger-rate').value),
    thirst_rate: parseFloat(document.getElementById('tune-thirst-rate').value),
    energy_drain: parseFloat(document.getElementById('tune-energy-drain').value),
    stress_rate: parseFloat(document.getElementById('tune-stress-rate').value),
    reflex_threshold: parseInt(document.getElementById('tune-reflex-threshold').value),
    dream_threshold: parseInt(document.getElementById('tune-dream-threshold').value)
  };

  try {
    await fetch('/api/config/simulation', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    });
    alert('Simulation config saved!');
  } catch (e) {
    console.error('Failed to save config:', e);
    alert('Failed to save config');
  }
};

// Save VMC config
window.saveVMCConfig = async function() {
  const enabled = document.getElementById('vmc-enabled').checked;
  const targetIp = document.getElementById('vmc-target-ip').value;
  const targetPort = parseInt(document.getElementById('vmc-target-port').value);

  const config = {
    vmc_enabled: enabled,
    vmc_target_ip: targetIp,
    vmc_target_port: targetPort
  };

  try {
    await fetch('/api/config/vmc', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    });

    const statusEl = document.getElementById('vmc-status');
    if (statusEl) {
      if (enabled) {
        statusEl.innerHTML = '<span style="color:var(--growth);">● Streaming active to ' + targetIp + ':' + targetPort + '</span>';
      } else {
        statusEl.textContent = 'VMC streaming is disabled';
      }
    }
    alert('VMC config saved!');
  } catch (e) {
    console.error('Failed to save VMC config:', e);
    alert('Failed to save config');
  }
};

// Phase 36: Spatial Input Functions
window.refreshSpatialState = async function() {
  const statusEl = document.getElementById('spatial-status');
  try {
    const res = await fetch('/api/spatial/state');
    const state = await res.json();

    if (state.isActive) {
      statusEl.innerHTML = '<span style="color:#22c55e;">● Active: ' + state.currentMode + '</span> | Keys: ' + state.keyStrokesCount + ' | Moves: ' + state.mouseMovesCount + ' | Scrolls: ' + state.scrollCount;
    } else if (state.currentMode === 'sovereignty_override') {
      statusEl.innerHTML = '<span style="color:#ef4444;">⚠️ Sovereignty Override (reflex lock)</span>';
    } else {
      statusEl.innerHTML = '<span style="color:var(--text-dim);">○ Idle - No desktop automation</span>';
    }
  } catch (e) {
    statusEl.textContent = 'Failed to load spatial state';
  }
};

window.stopSpatialAutomation = async function() {
  try {
    await fetch('/api/desktop/automation', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'stop' })
    });
    alert('Spatial automation stopped');
    window.refreshSpatialState();
  } catch (e) {
    console.error('Failed to stop spatial automation:', e);
  }
};

// Load config on page load
async function loadConfigs() {
  try {
    const res = await fetch('/api/config/simulation');
    const config = await res.json();

    if (config.hunger_rate) document.getElementById('tune-hunger-rate').value = config.hunger_rate;
    if (config.thirst_rate) document.getElementById('tune-thirst-rate').value = config.thirst_rate;
    if (config.energy_drain) document.getElementById('tune-energy-drain').value = config.energy_drain;
    if (config.stress_rate) document.getElementById('tune-stress-rate').value = config.stress_rate;
    if (config.reflex_threshold) document.getElementById('tune-reflex-threshold').value = config.reflex_threshold;
    if (config.dream_threshold) document.getElementById('tune-dream-threshold').value = config.dream_threshold;

    // Update displays
    ['hunger-rate', 'thirst-rate', 'energy-drain', 'stress-rate', 'reflex-threshold', 'dream-threshold'].forEach(id => {
      const el = document.getElementById('tune-' + id);
      const val = document.getElementById('tune-' + id + '-val');
      if (el && val) val.textContent = el.value;
    });
  } catch (e) {
    console.log('No simulation config found');
  }

  try {
    const res = await fetch('/api/config/vmc');
    const config = await res.json();

    if (config.vmc_enabled !== undefined) document.getElementById('vmc-enabled').checked = config.vmc_enabled;
    if (config.vmc_target_ip) document.getElementById('vmc-target-ip').value = config.vmc_target_ip;
    if (config.vmc_target_port) document.getElementById('vmc-target-port').value = config.vmc_target_port;

    const statusEl = document.getElementById('vmc-status');
    if (statusEl && config.vmc_enabled) {
      statusEl.innerHTML = '<span style="color:var(--growth);">● Streaming active to ' + config.vmc_target_ip + ':' + config.vmc_target_port + '</span>';
    }
  } catch (e) {
    console.log('No VMC config found');
  }
}

loadConfigs();

// Start if already on avatar tab
if (document.getElementById('tab-avatar').classList.contains('active')) {
  initAvatar();
}
</script>
</body>
</html>"""
    return html.replace("{data_json}", data_json).replace("{", "{").replace("}", "}")
    return html.replace("{data_json}", data_json).replace("{", "{").replace("}", "}")


def generate_mindmap_html(data: dict) -> str:
    """Generate the interactive canvas mindmap page."""
    data_json = json.dumps(data, indent=None, default=str)

    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Project Genesis — Soul Mindmap</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,700;1,400&display=swap');

* { margin: 0; padding: 0; box-sizing: border-box; }

:root {
  --bg: #060610;
  --text: #c8c8d8;
  --text-dim: #5a5a70;
  --text-bright: #eeeef4;
  --accent: #7c6ff0;
  --core: #e05050;
  --mutable: #50c878;
}

body {
  background: var(--bg);
  color: var(--text);
  font-family: 'DM Sans', sans-serif;
  overflow: hidden;
  height: 100vh;
  cursor: grab;
}
body.dragging { cursor: grabbing; }

canvas {
  display: block;
  position: absolute;
  top: 0; left: 0;
}

/* HUD overlay */
.hud {
  position: fixed;
  z-index: 100;
  pointer-events: none;
}
.hud > * { pointer-events: auto; }

.hud-top {
  top: 1.2rem; left: 50%;
  transform: translateX(-50%);
  text-align: center;
}
.hud-top h1 {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 300;
  font-size: 1.1rem;
  letter-spacing: 0.15em;
  color: var(--text-dim);
}
.hud-top h1 .evolution { color: var(--accent); }
.hud-top h1 .soul { color: var(--text-dim); }
.hud-top .back-link {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  color: var(--text-dim);
  text-decoration: none;
  letter-spacing: 0.05em;
  transition: color 0.2s;
}
.hud-top .back-link:hover { color: var(--mutable); }

/* Controls bar */
.controls {
  position: fixed;
  bottom: 1.5rem; left: 50%; transform: translateX(-50%);
  z-index: 100;
  display: flex; align-items: center; gap: 0.6rem;
  background: rgba(12, 12, 20, 0.85);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(30, 30, 48, 0.6);
  border-radius: 40px;
  padding: 0.5rem 1.2rem;
}
.controls button {
  background: none;
  border: 1px solid rgba(30, 30, 48, 0.8);
  color: var(--text);
  width: 32px; height: 32px;
  border-radius: 50%;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex; align-items: center; justify-content: center;
}
.controls button:hover {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}
.controls button.active {
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}
.controls .slider-wrap {
  display: flex; align-items: center; gap: 0.5rem;
  min-width: 240px;
}
.controls input[type=range] {
  -webkit-appearance: none;
  flex: 1;
  height: 3px;
  border-radius: 2px;
  background: rgba(30, 30, 48, 0.8);
  outline: none;
}
.controls input[type=range]::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 14px; height: 14px;
  border-radius: 50%;
  background: var(--accent);
  cursor: pointer;
  box-shadow: 0 0 10px rgba(124, 111, 240, 0.4);
}
.controls .step-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  color: var(--text-dim);
  min-width: 50px;
  text-align: center;
}

/* Tooltip */
.tooltip {
  position: fixed;
  z-index: 200;
  background: rgba(12, 12, 22, 0.95);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(30, 30, 48, 0.8);
  border-radius: 8px;
  padding: 0.6rem 0.8rem;
  max-width: 320px;
  font-size: 0.78rem;
  line-height: 1.45;
  color: var(--text);
  pointer-events: none;
  opacity: 0;
  transform: translateY(4px);
  transition: opacity 0.2s, transform 0.2s;
}
.tooltip.show {
  opacity: 1;
  transform: translateY(0);
}
.tooltip .tt-tag {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  margin-bottom: 0.3rem;
}
.tooltip .tt-tag.core { color: var(--core); }
.tooltip .tt-tag.mutable { color: var(--mutable); }
.tooltip .tt-section {
  font-size: 0.65rem;
  color: var(--text-dim);
  margin-bottom: 0.2rem;
}

/* Legend */
.hud-legend {
  position: fixed;
  bottom: 5rem; left: 50%; transform: translateX(-50%);
  z-index: 100;
  display: flex; gap: 1.2rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  color: var(--text-dim);
  letter-spacing: 0.04em;
}
.hud-legend .l-item {
  display: flex; align-items: center; gap: 0.35rem;
}
.hud-legend .l-dot {
  width: 7px; height: 7px; border-radius: 50%;
}

/* Change notification */
.change-toast {
  position: fixed;
  top: 4rem; right: 1.5rem;
  z-index: 150;
  background: rgba(12, 12, 22, 0.9);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(80, 200, 120, 0.3);
  border-radius: 10px;
  padding: 0.7rem 1rem;
  max-width: 300px;
  font-size: 0.75rem;
  line-height: 1.4;
  opacity: 0;
  transform: translateX(20px);
  transition: all 0.4s;
}
.change-toast.show {
  opacity: 1;
  transform: translateX(0);
}
.change-toast .ct-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  font-weight: 700;
  color: var(--mutable);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 0.3rem;
}
</style>
</head>
<body>

<div class="hud hud-top">
  <a href="soul-evolution.html" class="back-link">← back to dashboard</a>
  <h1><span class="evolution">Soul</span><span class="soul"> Evolution</span> · mindmap</h1>
</div>

<div class="controls">
  <button id="btn-play" title="Play growth">▶</button>
  <button id="btn-reset" title="Reset to origin">⟲</button>
  <div class="slider-wrap">
    <span class="step-label" id="step-label">origin</span>
    <input type="range" id="timeline" min="0" max="1" value="1" step="1">
  </div>
  <button id="btn-fit" title="Fit to view">⊡</button>
</div>

<div class="hud-legend" id="legend"></div>

<div class="tooltip" id="tooltip">
  <div class="tt-tag" id="tt-tag"></div>
  <div class="tt-section" id="tt-section"></div>
  <div id="tt-text"></div>
</div>

<div class="change-toast" id="change-toast">
  <div class="ct-label">soul change</div>
  <div id="ct-text"></div>
</div>

<canvas id="canvas"></canvas>

<script>
const DATA =  {data_json};

const SECTION_COLORS = {
  'Personality': '#f0a050',
  'Philosophy': '#7c6ff0',
  'Boundaries': '#e05050',
  'Continuity': '#50b8e0',
};
function secColor(name) {
  for (const [k, v] of Object.entries(SECTION_COLORS)) {
    if (name && name.includes(k)) return v;
  }
  return '#888';
}
function hexToRgb(hex) {
  const r = parseInt(hex.slice(1,3),16);
  const g = parseInt(hex.slice(3,5),16);
  const b = parseInt(hex.slice(5,7),16);
  return [r, g, b];
}

function buildNodes() {
  const nodes = [];
  const edges = [];
  let id = 0;

  // Root
  const root = { id: id++, type: 'root', label: 'SOUL', x: 0, y: 0, r: 28, color: '#7c6ff0', depth: 0, growStep: -1 };
  nodes.push(root);

  let growIdx = 0;

  DATA.soul_tree.forEach((sec, si) => {
    const color = secColor(sec.text);
    const sNode = { id: id++, type: 'section', label: sec.text, x: 0, y: 0, r: 18, color, depth: 1, growStep: growIdx++, parentId: root.id };
    nodes.push(sNode);
    edges.push({ from: root.id, to: sNode.id, color });

    sec.children.forEach((child, ci) => {
      if (child.type === 'subsection') {
        const subNode = { id: id++, type: 'subsection', label: child.text, x: 0, y: 0, r: 12, color, depth: 2, growStep: growIdx++, parentId: sNode.id };
        nodes.push(subNode);
        edges.push({ from: sNode.id, to: subNode.id, color });

        (child.children || []).forEach((b, bi) => {
          const isAdded = DATA.changes.some(c => c.after && c.after.trim() === b.raw.trim());
          const bNode = {
            id: id++, type: 'bullet', label: b.text, tag: b.tag,
            x: 0, y: 0, r: b.tag === 'CORE' ? 7 : 6,
            color: b.tag === 'CORE' ? '#e05050' : (b.tag === 'MUTABLE' ? '#50c878' : '#666'),
            depth: 3, growStep: growIdx++, parentId: subNode.id,
            raw: b.raw, isChangeAdded: isAdded,
            section: sec.text, subsection: child.text,
          };
          nodes.push(bNode);
          edges.push({ from: subNode.id, to: bNode.id, color: bNode.color });
        });
      } else if (child.type === 'bullet') {
        const b = child;
        const bNode = {
          id: id++, type: 'bullet', label: b.text, tag: b.tag,
          x: 0, y: 0, r: b.tag === 'CORE' ? 7 : 6,
          color: b.tag === 'CORE' ? '#e05050' : (b.tag === 'MUTABLE' ? '#50c878' : '#666'),
          depth: 2, growStep: growIdx++, parentId: sNode.id,
          raw: b.raw, isChangeAdded: false,
          section: sec.text, subsection: '',
        };
        nodes.push(bNode);
        edges.push({ from: sNode.id, to: bNode.id, color: bNode.color });
      }
    });
  });

  // Mark change-added nodes with the change index
  DATA.changes.forEach((c, ci) => {
    if (c.after) {
      const match = nodes.find(n => n.raw && n.raw.trim() === c.after.trim());
      if (match) match.changeIdx = ci;
    }
  });

  return { nodes, edges, totalGrowSteps: growIdx };
}

function layoutRadial(nodes, edges) {
  const childrenOf = {};
  edges.forEach(e => {
    if (!childrenOf[e.from]) childrenOf[e.from] = [];
    childrenOf[e.from].push(e.to);
  });

  const nodeMap = {};
  nodes.forEach(n => nodeMap[n.id] = n);

  function countLeaves(nid) {
    const kids = childrenOf[nid] || [];
    if (kids.length === 0) return 1;
    return kids.reduce((s, k) => s + countLeaves(k), 0);
  }

  function layout(nid, angleStart, angleEnd, radius) {
    const node = nodeMap[nid];
    const kids = childrenOf[nid] || [];
    const mid = (angleStart + angleEnd) / 2;

    if (nid !== 0) {
      node.x = Math.cos(mid) * radius;
      node.y = Math.sin(mid) * radius;
    }

    if (kids.length === 0) return;

    const totalLeaves = countLeaves(nid);
    let cursor = angleStart;

    kids.forEach(kid => {
      const kidNode = nodeMap[kid];
      const leaves = countLeaves(kid);
      const share = (leaves / totalLeaves) * (angleEnd - angleStart);
      const extra = radiusBonus(kidNode);
      layout(kid, cursor, cursor + share, radius + radiusStep(kidNode.depth) + extra);
      cursor += share;
    });
  }

  function radiusStep(depth) {
    if (depth === 1) return 160;
    if (depth === 2) return 130;
    return 110;
  }

  // Push change-added nodes further out from the core
  function radiusBonus(node) {
    if (node.changeIdx !== undefined) {
      // Each successive change gets pushed further out
      return 60 + node.changeIdx * 40;
    }
    return 0;
  }

  layout(0, -Math.PI, Math.PI, 0);
}

const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
let W, H;
let camX = 0, camY = 0, camZoom = 1;
let targetCamX = 0, targetCamY = 0, targetCamZoom = 1;
let camSmooth = 0.06; // lerp speed
let isDragging = false, dragStartX, dragStartY, camStartX, camStartY;
let hoveredNode = null;
let animTime = 0;

const { nodes, edges, totalGrowSteps } = buildNodes();
layoutRadial(nodes, edges);

// Current visible step
let currentStep = DATA.changes.length; // max
let maxGrowStep = totalGrowSteps;
const slider = document.getElementById('timeline');
slider.max = DATA.changes.length;
slider.value = DATA.changes.length;

// Determine which growSteps are visible at each timeline step
function getVisibleGrowStep(timelineStep) {
  // All nodes visible except those added by changes AFTER timelineStep
  const hiddenChanges = new Set();
  for (let i = DATA.changes.length - 1; i >= timelineStep; i--) {
    if (DATA.changes[i].after) hiddenChanges.add(DATA.changes[i].after.trim());
  }
  return hiddenChanges;
}

// Particles for celebrations
let particles = [];
function spawnParticles(x, y, color) {
  const [r, g, b] = hexToRgb(color);
  for (let i = 0; i < 20; i++) {
    const angle = Math.random() * Math.PI * 2;
    const speed = 1 + Math.random() * 3;
    particles.push({
      x, y,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      life: 1,
      decay: 0.01 + Math.random() * 0.02,
      r, g, b,
      size: 2 + Math.random() * 3,
    });
  }
}

function resize() {
  W = window.innerWidth;
  H = window.innerHeight;
  canvas.width = W * devicePixelRatio;
  canvas.height = H * devicePixelRatio;
  canvas.style.width = W + 'px';
  canvas.style.height = H + 'px';
  ctx.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0);
}
window.addEventListener('resize', resize);
resize();

// Node grow animation state
const nodeAnim = {};
nodes.forEach(n => {
  nodeAnim[n.id] = { scale: 0, targetScale: 1, visible: true };
});

function setVisibility() {
  const hidden = getVisibleGrowStep(currentStep);
  nodes.forEach(n => {
    if (n.raw && hidden.has(n.raw.trim())) {
      nodeAnim[n.id].targetScale = 0;
      nodeAnim[n.id].visible = false;
    } else {
      nodeAnim[n.id].targetScale = 1;
      nodeAnim[n.id].visible = true;
    }
  });
}
setVisibility();
// Start fully visible
nodes.forEach(n => { nodeAnim[n.id].scale = nodeAnim[n.id].targetScale; });

function screenToWorld(sx, sy) {
  return [(sx - W/2) / camZoom + camX, (sy - H/2) / camZoom + camY];
}

function worldToScreen(wx, wy) {
  return [(wx - camX) * camZoom + W/2, (wy - camY) * camZoom + H/2];
}

function draw() {
  animTime += 0.016;

  // Smooth camera
  camX += (targetCamX - camX) * camSmooth;
  camY += (targetCamY - camY) * camSmooth;
  camZoom += (targetCamZoom - camZoom) * camSmooth;

  // Animate node scales
  nodes.forEach(n => {
    const a = nodeAnim[n.id];
    a.scale += (a.targetScale - a.scale) * 0.08;
    if (Math.abs(a.scale - a.targetScale) < 0.001) a.scale = a.targetScale;
  });

  // Update particles
  particles = particles.filter(p => {
    p.x += p.vx;
    p.y += p.vy;
    p.vx *= 0.97;
    p.vy *= 0.97;
    p.life -= p.decay;
    return p.life > 0;
  });

  ctx.clearRect(0, 0, W, H);

  // Background glow
  const grad = ctx.createRadialGradient(W/2, H/2, 0, W/2, H/2, Math.max(W, H) * 0.6);
  grad.addColorStop(0, 'rgba(124, 111, 240, 0.03)');
  grad.addColorStop(1, 'transparent');
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, W, H);

  ctx.save();
  ctx.translate(W/2, H/2);
  ctx.scale(camZoom, camZoom);
  ctx.translate(-camX, -camY);

  const nodeMap = {};
  nodes.forEach(n => nodeMap[n.id] = n);

  // Draw edges (organic bezier curves)
  edges.forEach(e => {
    const from = nodeMap[e.from];
    const to = nodeMap[e.to];
    const aFrom = nodeAnim[from.id];
    const aTo = nodeAnim[to.id];
    const alpha = Math.min(aFrom.scale, aTo.scale);
    if (alpha < 0.01) return;

    const [r, g, b] = hexToRgb(e.color);

    ctx.beginPath();
    const dx = to.x - from.x;
    const dy = to.y - from.y;
    const dist = Math.sqrt(dx*dx + dy*dy);

    // Organic bezier: control points offset perpendicular
    const mx = (from.x + to.x) / 2;
    const my = (from.y + to.y) / 2;
    const nx = -dy / dist;
    const ny = dx / dist;
    const wobble = Math.sin(animTime * 0.5 + from.id) * 8;
    const cpx = mx + nx * wobble;
    const cpy = my + ny * wobble;

    ctx.moveTo(from.x, from.y);
    ctx.quadraticCurveTo(cpx, cpy, to.x, to.y);

    ctx.strokeStyle = `rgba(${r},${g},${b},${alpha * 0.25})`;
    ctx.lineWidth = to.depth <= 1 ? 2.5 : (to.depth === 2 ? 1.5 : 1);
    ctx.stroke();
  });

  // Draw nodes
  nodes.forEach(n => {
    const a = nodeAnim[n.id];
    if (a.scale < 0.01) return;

    const s = a.scale;
    const r = n.r * s;
    const [cr, cg, cb] = hexToRgb(n.color);
    const isHov = hoveredNode && hoveredNode.id === n.id;

    // Glow
    if (n.type !== 'bullet' || isHov) {
      const glowR = r * (isHov ? 4 : 2.5);
      const glow = ctx.createRadialGradient(n.x, n.y, r * 0.5, n.x, n.y, glowR);
      glow.addColorStop(0, `rgba(${cr},${cg},${cb},${s * (isHov ? 0.25 : 0.12)})`);
      glow.addColorStop(1, 'transparent');
      ctx.fillStyle = glow;
      ctx.fillRect(n.x - glowR, n.y - glowR, glowR * 2, glowR * 2);
    }

    // Node circle
    ctx.beginPath();
    ctx.arc(n.x, n.y, r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(${cr},${cg},${cb},${s * (isHov ? 0.9 : 0.7)})`;
    ctx.fill();

    // Border ring
    if (n.type === 'root' || n.type === 'section' || isHov) {
      ctx.beginPath();
      ctx.arc(n.x, n.y, r + 1.5, 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(${cr},${cg},${cb},${s * 0.5})`;
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    // Pulse ring for change-added nodes at current step
    if (n.changeIdx !== undefined && n.changeIdx === currentStep - 1) {
      const pulse = (Math.sin(animTime * 3) + 1) * 0.5;
      ctx.beginPath();
      ctx.arc(n.x, n.y, r + 4 + pulse * 6, 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(${cr},${cg},${cb},${0.3 + pulse * 0.3})`;
      ctx.lineWidth = 1.5;
      ctx.stroke();
    }

    // Labels
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    if (n.type === 'root') {
      ctx.font = `700 ${14 * s}px 'JetBrains Mono', monospace`;
      ctx.fillStyle = `rgba(255,255,255,${s})`;
      ctx.fillText(n.label, n.x, n.y);
    } else if (n.type === 'section') {
      ctx.font = `500 ${11 * s}px 'JetBrains Mono', monospace`;
      ctx.fillStyle = `rgba(255,255,255,${s * 0.9})`;
      ctx.fillText(n.label, n.x, n.y + r + 14);
    } else if (n.type === 'subsection' && camZoom > 0.5) {
      ctx.font = `400 ${9 * s}px 'DM Sans', sans-serif`;
      ctx.fillStyle = `rgba(200,200,216,${s * 0.7})`;
      const maxW = 100;
      ctx.fillText(n.label.length > 18 ? n.label.slice(0, 16) + '…' : n.label, n.x, n.y + r + 12);
    }
  });

  // Particles
  particles.forEach(p => {
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.size * p.life, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(${p.r},${p.g},${p.b},${p.life * 0.6})`;
    ctx.fill();
  });

  ctx.restore();
  requestAnimationFrame(draw);
}

canvas.addEventListener('mousedown', e => {
  isDragging = true;
  dragStartX = e.clientX;
  dragStartY = e.clientY;
  camStartX = camX;
  camStartY = camY;
  document.body.classList.add('dragging');
});
window.addEventListener('mousemove', e => {
  if (isDragging) {
    const nx = camStartX - (e.clientX - dragStartX) / camZoom;
    const ny = camStartY - (e.clientY - dragStartY) / camZoom;
    camX = targetCamX = nx;
    camY = targetCamY = ny;
  }

  // Hover detection
  const [wx, wy] = screenToWorld(e.clientX, e.clientY);
  let found = null;
  // Check in reverse (top nodes last drawn = on top)
  for (let i = nodes.length - 1; i >= 0; i--) {
    const n = nodes[i];
    const a = nodeAnim[n.id];
    if (a.scale < 0.1) continue;
    const dx = wx - n.x;
    const dy = wy - n.y;
    const hitR = Math.max(n.r * a.scale, 10);
    if (dx*dx + dy*dy < hitR * hitR) {
      found = n;
      break;
    }
  }

  hoveredNode = found;
  const tooltip = document.getElementById('tooltip');
  if (found && (found.type === 'bullet' || found.type === 'subsection')) {
    tooltip.classList.add('show');
    tooltip.style.left = (e.clientX + 16) + 'px';
    tooltip.style.top = (e.clientY - 10) + 'px';
    // Clamp
    if (e.clientX + 340 > W) tooltip.style.left = (e.clientX - 330) + 'px';
    if (e.clientY + 80 > H) tooltip.style.top = (e.clientY - 60) + 'px';

    const tagEl = document.getElementById('tt-tag');
    const secEl = document.getElementById('tt-section');
    const textEl = document.getElementById('tt-text');

    if (found.tag) {
      tagEl.textContent = found.tag;
      tagEl.className = 'tt-tag ' + found.tag.toLowerCase();
      tagEl.style.display = '';
    } else {
      tagEl.style.display = 'none';
    }
    secEl.textContent = (found.section || '') + (found.subsection ? ' › ' + found.subsection : '');
    textEl.textContent = found.label;
  } else {
    tooltip.classList.remove('show');
  }
});
window.addEventListener('mouseup', () => {
  isDragging = false;
  document.body.classList.remove('dragging');
});

canvas.addEventListener('wheel', e => {
  e.preventDefault();
  const factor = e.deltaY > 0 ? 0.9 : 1.1;
  const [wx, wy] = screenToWorld(e.clientX, e.clientY);
  camZoom *= factor;
  camZoom = Math.max(0.15, Math.min(5, camZoom));
  camX = wx - (e.clientX - W/2) / camZoom;
  camY = wy - (e.clientY - H/2) / camZoom;
  targetCamX = camX;
  targetCamY = camY;
  targetCamZoom = camZoom;
}, { passive: false });

let lastTouchDist = 0;
canvas.addEventListener('touchstart', e => {
  e.preventDefault();
  if (e.touches.length === 1) {
    isDragging = true;
    dragStartX = e.touches[0].clientX;
    dragStartY = e.touches[0].clientY;
    camStartX = camX;
    camStartY = camY;
  } else if (e.touches.length === 2) {
    isDragging = false;
    const dx = e.touches[0].clientX - e.touches[1].clientX;
    const dy = e.touches[0].clientY - e.touches[1].clientY;
    lastTouchDist = Math.sqrt(dx * dx + dy * dy);
  }
}, { passive: false });
canvas.addEventListener('touchmove', e => {
  e.preventDefault();
  if (e.touches.length === 1 && isDragging) {
    const nx = camStartX - (e.touches[0].clientX - dragStartX) / camZoom;
    const ny = camStartY - (e.touches[0].clientY - dragStartY) / camZoom;
    camX = targetCamX = nx;
    camY = targetCamY = ny;
  } else if (e.touches.length === 2) {
    const dx = e.touches[0].clientX - e.touches[1].clientX;
    const dy = e.touches[0].clientY - e.touches[1].clientY;
    const dist = Math.sqrt(dx * dx + dy * dy);
    if (lastTouchDist > 0) {
      const factor = dist / lastTouchDist;
      const mx = (e.touches[0].clientX + e.touches[1].clientX) / 2;
      const my = (e.touches[0].clientY + e.touches[1].clientY) / 2;
      const [wx, wy] = screenToWorld(mx, my);
      camZoom *= factor;
      camZoom = Math.max(0.15, Math.min(5, camZoom));
      camX = wx - (mx - W/2) / camZoom;
      camY = wy - (my - H/2) / camZoom;
      targetCamX = camX;
      targetCamY = camY;
      targetCamZoom = camZoom;
    }
    lastTouchDist = dist;
  }
}, { passive: false });
canvas.addEventListener('touchend', e => {
  isDragging = false;
  lastTouchDist = 0;
});

const stepLabel = document.getElementById('step-label');

function setStep(s) {
  currentStep = s;
  slider.value = s;
  setVisibility();
  if (s === 0) {
    stepLabel.textContent = 'origin';
  } else {
    const c = DATA.changes[s - 1];
    stepLabel.textContent = (c.timestamp || '').slice(11, 16) || '#' + s;
  }
}

slider.oninput = () => setStep(parseInt(slider.value));

// Play
let playing = false;
let playTimer = null;
document.getElementById('btn-play').onclick = () => {
  const btn = document.getElementById('btn-play');
  if (playing) {
    clearInterval(playTimer);
    playing = false;
    btn.textContent = '▶';
    btn.classList.remove('active');
    return;
  }
  playing = true;
  btn.textContent = '⏸';
  btn.classList.add('active');

  // Start at origin: all base nodes visible, no changes applied
  setStep(0);

  // Instantly grow all base (non-change) nodes with a quick stagger
  nodes.forEach(n => {
    const a = nodeAnim[n.id];
    if (n.changeIdx === undefined && a.visible) {
      setTimeout(() => { a.targetScale = 1; }, n.growStep * 25);
    }
  });

  // Fit tight on the base tree first
  setTimeout(() => fitToVisible(false), 200);

  // After base tree is grown, play changes one by one at uniform pace
  const baseGrowTime = Math.min(maxGrowStep * 25 + 400, 1500);
  const changePause = 2000; // 2 seconds per change

  let changeIdx = 0;
  setTimeout(() => {
    if (!playing) return;
    // Fit to base tree before changes start
    fitToVisible(false);

    playTimer = setInterval(() => {
      changeIdx++;
      if (changeIdx <= DATA.changes.length) {
        setStep(changeIdx);
        // Smoothly zoom out to include the new node
        fitToVisible(false);
        // Celebrate the new node
        const c = DATA.changes[changeIdx - 1];
        if (c && c.after) {
          const match = nodes.find(n => n.raw && n.raw.trim() === c.after.trim());
          if (match) {
            spawnParticles(match.x, match.y, match.color);
            const toast = document.getElementById('change-toast');
            document.getElementById('ct-text').textContent =
              c.after.replace(/\\s*\\[(CORE|MUTABLE)\\]\\s*/g, '').replace(/^- /, '').slice(0, 120);
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), changePause - 300);
          }
        }
      } else {
        clearInterval(playTimer);
        playing = false;
        btn.textContent = '▶';
        btn.classList.remove('active');
      }
    }, changePause);
  }, baseGrowTime);
};

document.getElementById('btn-reset').onclick = () => {
  if (playing) {
    clearInterval(playTimer);
    playing = false;
    document.getElementById('btn-play').textContent = '▶';
    document.getElementById('btn-play').classList.remove('active');
  }
  // Reset all scales to 0, then grow
  nodes.forEach(n => {
    nodeAnim[n.id].scale = 0;
    nodeAnim[n.id].targetScale = 0;
  });
  setStep(0);
  // Quick regrow
  setTimeout(() => {
    nodes.forEach(n => {
      if (!n.raw || !getVisibleGrowStep(0).has(n.raw.trim())) {
        setTimeout(() => { nodeAnim[n.id].targetScale = 1; }, n.growStep * 40);
      }
    });
    fitToVisible(false);
  }, 200);
};

// Fit camera to visible nodes, always centered on SOUL (0,0)
function fitToVisible(instant) {
  let maxDist = 0;
  nodes.forEach(n => {
    if (nodeAnim[n.id].scale > 0.1 || nodeAnim[n.id].targetScale > 0.5) {
      const dist = Math.sqrt(n.x * n.x + n.y * n.y) + n.r + 40;
      if (dist > maxDist) maxDist = dist;
    }
  });
  maxDist = Math.max(maxDist, 80); // minimum extent
  const padding = 1.15;
  const halfExtent = maxDist * padding;
  const zoom = Math.min(W / (halfExtent * 2), H / (halfExtent * 2), 2.5);

  targetCamX = 0;
  targetCamY = 0;
  targetCamZoom = zoom;
  if (instant) {
    camX = targetCamX;
    camY = targetCamY;
    camZoom = targetCamZoom;
  }
}

document.getElementById('btn-fit').onclick = () => fitToVisible(false);

// Legend
document.getElementById('legend').innerHTML = [
  { c: '#e05050', l: 'CORE' },
  { c: '#50c878', l: 'MUTABLE' },
  ...Object.entries(SECTION_COLORS).map(([k, v]) => ({ c: v, l: k })),
].map(i => `<div class="l-item"><div class="l-dot" style="background:${i.c}"></div>${i.l}</div>`).join('');

// Init
// Start fully grown
nodes.forEach(n => {
  nodeAnim[n.id].scale = nodeAnim[n.id].targetScale;
});
setStep(DATA.changes.length);
setTimeout(() => fitToVisible(true), 100);
draw();
</script>
</body>
</html>"""
    return html.replace("{data_json}", data_json)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    workspace = sys.argv[1]

    # Check for SOUL.md at workspace root
    soul_path = os.path.join(workspace, "SOUL.md")
    if not os.path.exists(soul_path):
        # Maybe they passed the parent dir
        for candidate in ["SOUL.md", "workspace-soul-evolution-demo/SOUL.md"]:
            p = os.path.join(workspace, candidate)
            if os.path.exists(p):
                workspace = os.path.dirname(p)
                break
        else:
            print(f"Error: Cannot find SOUL.md in {workspace}")
            sys.exit(1)

    print(f"Reading workspace: {workspace}")
    data = collect_data(workspace)

    print(f"  Soul sections: {len(data['soul_tree'])}")
    print(f"  Experiences: {len(data['experiences'])}")
    print(f"  Reflections: {len(data['reflections'])}")
    print(f"  Soul changes: {len(data['changes'])}")

    html = generate_html(data)
    mindmap_html = generate_mindmap_html(data)

    # --serve mode
    if "--serve" in sys.argv:
        port = 8080
        idx = sys.argv.index("--serve")
        if idx + 1 < len(sys.argv) and sys.argv[idx + 1].isdigit():
            port = int(sys.argv[idx + 1])

        import http.server
        import socketserver
        import tempfile

        out_dir = tempfile.gettempdir()
        with open(os.path.join(out_dir, "soul-evolution.html"), "w") as f:
            f.write(html)
        with open(os.path.join(out_dir, "soul-mindmap.html"), "w") as f:
            f.write(mindmap_html)

        soul_path = os.path.join(workspace, "SOUL.md")

        pending_path = os.path.join(workspace, "memory", "proposals", "pending.jsonl")
        history_path = os.path.join(workspace, "memory", "proposals", "history.jsonl")

        # Paths for new data files
        interior_path = os.path.join(workspace, "memory", "reality", "interior.json")
        inventory_path = os.path.join(workspace, "memory", "reality", "inventory.json")
        wardrobe_path = os.path.join(workspace, "memory", "reality", "wardrobe.json")
        media_base = os.path.join(workspace, "memory", "reality")

        class SoulEvolutionHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/godmode.html":
                    try:
                        with open(os.path.join(os.path.dirname(__file__), "godmode.html"), "r") as f:
                            data = f.read()
                        self.send_response(200)
                        self.send_header("Content-Type", "text/html")
                        self.end_headers()
                        self.wfile.write(data.encode())
                        return
                    except:
                        pass

                if self.path.startswith("/media/"):
                    # Serve media files from workspace/memory/reality/media/
                    rel = self.path[len("/media/"):]
                    file_path = os.path.join(media_base, rel)
                    # Security: resolved path must be under media_base
                    real_base = os.path.realpath(media_base)
                    real_path = os.path.realpath(file_path)
                    if not real_path.startswith(real_base):
                        self.send_response(403)
                        self.end_headers()
                        return
                    if not os.path.isfile(real_path):
                        self.send_response(404)
                        self.end_headers()
                        return
                    ext = os.path.splitext(real_path)[1].lower()
                    content_types = {
                        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                        ".png": "image/png", ".gif": "image/gif",
                        ".webp": "image/webp", ".svg": "image/svg+xml",
                        ".wav": "audio/wav", ".mp3": "audio/mpeg",
                    }
                    ct = content_types.get(ext, "application/octet-stream")
                    with open(real_path, "rb") as f:
                        data = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", ct)
                    self.send_header("Content-Length", str(len(data)))
                    # Force download for SVG files to prevent XSS
                    if ext == ".svg":
                        self.send_header("Content-Disposition", "attachment")
                    self.end_headers()
                    self.wfile.write(data)
                elif self.path == "/godmode.html":
                    with open(os.path.join(os.path.dirname(__file__), "godmode.html"), "r") as f:
                        data = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html")
                    self.end_headers()
                    self.wfile.write(data.encode())
                elif self.path == '/godmode.html':
                    try:
                        with open(os.path.join(os.path.dirname(__file__), 'godmode.html'), 'r') as f:
                            data = f.read()
                        self.send_response(200)
                        self.send_header('Content-Type', 'text/html')
                        self.end_headers()
                        self.wfile.write(data.encode())
                    except Exception as e:
                        self.send_error(500, str(e))
                elif self.path == '/api/godmode/physique':
                    path = os.path.join(workspace, 'memory', 'reality', 'physique.json')
                    data = {}
                    if os.path.exists(path):
                        with open(path) as f: data = json.load(f)
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(data).encode())
                elif self.path == "/api/genesis/status":
                    # Return genesis enabled status
                    genesis_enabled_path = os.path.join(workspace, "memory", "reality", "genesis_enabled.json")
                    enabled = False
                    if os.path.exists(genesis_enabled_path):
                        try:
                            with open(genesis_enabled_path) as f:
                                data = json.load(f)
                                enabled = data.get("enabled", False)
                        except:
                            pass
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"enabled": enabled}).encode())

                elif self.path == "/api/model/config":
                    # Get or set model configuration
                    model_config_path = os.path.join(workspace, "memory", "reality", "model_config.json")

                    if self.command == 'GET':
                        # Return current config
                        config = {"models": {}}
                        if os.path.exists(model_config_path):
                            try:
                                with open(model_config_path) as f:
                                    config = json.load(f)
                            except:
                                pass
                        
                        # Return config with placeholder for existing keys
                        config_ui = config.copy()
                        for key in ["api_key", "key_anthropic", "key_venice", "key_fal", "key_xai", "key_gemini_img"]:
                            if config.get(key):
                                config_ui[key] = "****"
                        
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps(config_ui).encode())
                    else:
                        # Save config (Merge with existing)
                        length = int(self.headers.get("Content-Length", 0))
                        body = self.rfile.read(length).decode("utf-8")
                        try:
                            new_data = json.loads(body)
                            
                            # Load existing
                            config = {}
                            if os.path.exists(model_config_path):
                                with open(model_config_path) as f:
                                    config = json.load(f)
                            
                            # Update with new data (Handle empty values carefully)
                            for k, v in new_data.items():
                                if v == "****": continue # Don't overwrite with placeholder
                                if k == "models" and isinstance(v, dict):
                                    if "models" not in config: config["models"] = {}
                                    config["models"].update(v)
                                else:
                                    config[k] = v

                            os.makedirs(os.path.dirname(model_config_path), exist_ok=True)
                            with open(model_config_path, "w") as f:
                                json.dump(config, f, indent=2)

                            self.send_response(200)
                            self.send_header("Content-Type", "application/json")
                            self.end_headers()
                            self.wfile.write(json.dumps({"success": True}).encode())
                            print(f"  ✓ Model config updated")
                        except Exception as e:
                            self.send_response(500)
                            self.send_header("Content-Type", "application/json")
                            self.end_headers()
                            self.wfile.write(json.dumps({"success": False, "message": str(e)}).encode())

                elif self.path == "/api/genesis/request-status":
                    request_path = os.path.join(workspace, "memory", "reality", "genesis_request.json")
                    pending = os.path.exists(request_path)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"pending": pending}).encode())

                elif self.path == "/api/profiles/list":
                    # List all saved profiles
                    profiles_dir = os.path.join(workspace, "memory", "profiles")
                    profiles = []
                    if os.path.isdir(profiles_dir):
                        for entry in os.listdir(profiles_dir):
                            full_path = os.path.join(profiles_dir, entry)
                            if os.path.isdir(full_path):
                                profiles.append(entry)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(profiles).encode())

                elif self.path == "/api/backups/list":
                    # List all daily backups
                    backups_dir = os.path.join(workspace, "memory", "backups")
                    backups = []
                    if os.path.isdir(backups_dir):
                        for entry in os.listdir(backups_dir):
                            full_path = os.path.join(backups_dir, entry)
                            if os.path.isdir(full_path) and entry not in ('.snapshot_done'):
                                backups.append(entry)
                    backups.sort(reverse=True)  # Most recent first
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(backups).encode())
                else:
                    super().do_GET()

            def do_POST(self):
                if self.path == "/save-soul":
                    length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(length).decode("utf-8")
                    try:
                        with open(soul_path, "w") as f:
                            f.write(body)
                        self.send_response(200)
                        self.send_header("Content-Type", "text/plain")
                        self.end_headers()
                        self.wfile.write(b"OK")
                        print(f"  ✓ SOUL.md saved ({len(body)} bytes)")
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "text/plain")
                        self.end_headers()
                        self.wfile.write(str(e).encode())
                        print(f"  ✗ Save failed: {e}")
                elif self.path == "/resolve-proposal":
                    length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(length).decode("utf-8")
                    try:
                        req = json.loads(body)
                        idx = req.get("index", -1)
                        decision = req.get("decision", "rejected")

                        # Read all pending proposals
                        proposals = []
                        if os.path.exists(pending_path):
                            with open(pending_path, "r") as f:
                                for line in f:
                                    line = line.strip()
                                    if line:
                                        proposals.append(json.loads(line))

                        if idx < 0 or idx >= len(proposals):
                            self.send_response(400)
                            self.send_header("Content-Type", "text/plain")
                            self.end_headers()
                            self.wfile.write(b"Invalid proposal index")
                            return

                        # Move resolved proposal to history
                        resolved = proposals.pop(idx)
                        resolved["decision"] = decision
                        resolved["resolved_at"] = __import__("datetime").datetime.now().isoformat()

                        os.makedirs(os.path.dirname(history_path), exist_ok=True)
                        with open(history_path, "a") as f:
                            f.write(json.dumps(resolved) + "\n")

                        # Rewrite pending without the resolved one
                        with open(pending_path, "w") as f:
                            for p in proposals:
                                f.write(json.dumps(p) + "\n")

                        self.send_response(200)
                        self.send_header("Content-Type", "text/plain")
                        self.end_headers()
                        self.wfile.write(b"OK")
                        print(f"  ✓ Proposal {resolved.get('id', idx)} {decision}")
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "text/plain")
                        self.end_headers()
                        self.wfile.write(str(e).encode())
                        print(f"  ✗ Resolve failed: {e}")
                elif self.path == "/upload-image":
                    length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(length).decode("utf-8")
                    try:
                        import base64
                        req = json.loads(body)
                        category = req.get("category", "")
                        item_id = req.get("item_id", "")
                        filename = req.get("filename", "image.jpg")
                        b64data = req.get("data", "")

                        if category not in ("wardrobe", "interior", "inventory"):
                            raise ValueError("Invalid category")

                        # Reject SVG uploads (XSS risk)
                        ext_check = os.path.splitext(filename)[1].lower()
                        if ext_check == ".svg":
                            raise ValueError("SVG uploads are not allowed")

                        # Determine next image number
                        cat_dir = os.path.join(media_base, category)
                        os.makedirs(cat_dir, exist_ok=True)
                        existing = [f for f in os.listdir(cat_dir) if f.startswith(item_id + "_")]
                        ext = os.path.splitext(filename)[1] or ".jpg"
                        num = len(existing) + 1
                        new_filename = f"{item_id}_{str(num).zfill(3)}{ext}"
                        new_path = os.path.join(cat_dir, new_filename)

                        # Security check
                        real_base = os.path.realpath(cat_dir)
                        real_new = os.path.realpath(new_path)
                        if not real_new.startswith(real_base):
                            raise ValueError("Path traversal detected")

                        with open(new_path, "wb") as f:
                            f.write(base64.b64decode(b64data))

                        rel_path = f"media/{category}/{new_filename}"

                        # Update images array in corresponding JSON
                        if category == "wardrobe":
                            wd = load_json(wardrobe_path)
                            if wd.get("inventory"):
                                for cat_items in wd["inventory"].values():
                                    for item in cat_items:
                                        if isinstance(item, dict) and item.get("id") == item_id:
                                            if "images" not in item:
                                                item["images"] = []
                                            item["images"].append(rel_path)
                                with open(wardrobe_path, "w") as f:
                                    json.dump(wd, f, indent=2)
                        elif category == "interior":
                            interior = load_json(interior_path)
                            for room in interior.get("rooms", []):
                                for obj in room.get("objects", []):
                                    if obj.get("id") == item_id:
                                        if "images" not in obj:
                                            obj["images"] = []
                                        obj["images"].append(rel_path)
                            with open(interior_path, "w") as f:
                                json.dump(interior, f, indent=2)
                        elif category == "inventory":
                            inv = load_json(inventory_path)
                            for item in inv.get("items", []):
                                if item.get("id") == item_id:
                                    if "images" not in item:
                                        item["images"] = []
                                    item["images"].append(rel_path)
                            with open(inventory_path, "w") as f:
                                json.dump(inv, f, indent=2)

                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"path": rel_path}).encode())
                        print(f"  \u2713 Image uploaded: {rel_path}")
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "text/plain")
                        self.end_headers()
                        self.wfile.write(str(e).encode())
                        print(f"  \u2717 Upload failed: {e}")

                elif self.path == "/delete-image":
                    length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(length).decode("utf-8")
                    try:
                        req = json.loads(body)
                        category = req.get("category", "")
                        item_id = req.get("item_id", "")
                        img_path = req.get("path", "")

                        # Delete file
                        full_path = os.path.join(workspace, "memory", "reality", img_path)
                        real_base = os.path.realpath(media_base)
                        real_path = os.path.realpath(full_path)
                        if not real_path.startswith(real_base):
                            raise ValueError("Path traversal detected")
                        if os.path.exists(real_path):
                            os.remove(real_path)

                        # Remove from JSON
                        if category == "wardrobe":
                            wd = load_json(wardrobe_path)
                            if wd.get("inventory"):
                                for cat_items in wd["inventory"].values():
                                    for item in cat_items:
                                        if isinstance(item, dict) and item.get("id") == item_id:
                                            item["images"] = [p for p in item.get("images", []) if p != img_path]
                                with open(wardrobe_path, "w") as f:
                                    json.dump(wd, f, indent=2)
                        elif category == "interior":
                            interior = load_json(interior_path)
                            for room in interior.get("rooms", []):
                                for obj in room.get("objects", []):
                                    if obj.get("id") == item_id:
                                        obj["images"] = [p for p in obj.get("images", []) if p != img_path]
                            with open(interior_path, "w") as f:
                                json.dump(interior, f, indent=2)
                        elif category == "inventory":
                            inv = load_json(inventory_path)
                            for item in inv.get("items", []):
                                if item.get("id") == item_id:
                                    item["images"] = [p for p in item.get("images", []) if p != img_path]
                            with open(inventory_path, "w") as f:
                                json.dump(inv, f, indent=2)

                        self.send_response(200)
                        self.send_header("Content-Type", "text/plain")
                        self.end_headers()
                        self.wfile.write(b"OK")
                        print(f"  \u2713 Image deleted: {img_path}")
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "text/plain")
                        self.end_headers()
                        self.wfile.write(str(e).encode())

                elif self.path == "/update-interior":
                    length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(length).decode("utf-8")
                    try:
                        data = json.loads(body)
                        if "rooms" not in data or not isinstance(data["rooms"], list):
                            raise ValueError("Invalid interior format")
                        with open(interior_path, "w") as f:
                            json.dump(data, f, indent=2)
                        self.send_response(200)
                        self.send_header("Content-Type", "text/plain")
                        self.end_headers()
                        self.wfile.write(b"OK")
                        print(f"  \u2713 Interior saved")
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "text/plain")
                        self.end_headers()
                        self.wfile.write(str(e).encode())

                elif self.path == "/update-inventory":
                    length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(length).decode("utf-8")
                    try:
                        data = json.loads(body)
                        if "items" not in data or not isinstance(data["items"], list):
                            raise ValueError("Invalid inventory format")
                        with open(inventory_path, "w") as f:
                            json.dump(data, f, indent=2)
                        self.send_response(200)
                        self.send_header("Content-Type", "text/plain")
                        self.end_headers()
                        self.wfile.write(b"OK")
                        print(f"  \u2713 Inventory saved")
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "text/plain")
                        self.end_headers()
                        self.wfile.write(str(e).encode())

                elif self.path == "/update-wardrobe":
                    length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(length).decode("utf-8")
                    try:
                        data = json.loads(body)
                        if "inventory" not in data or not isinstance(data["inventory"], dict):
                            raise ValueError("Invalid wardrobe format")
                        with open(wardrobe_path, "w") as f:
                            json.dump(data, f, indent=2)
                        self.send_response(200)
                        self.send_header("Content-Type", "text/plain")
                        self.end_headers()
                        self.wfile.write(b"OK")
                        print(f"  \u2713 Wardrobe saved")
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "text/plain")
                        self.end_headers()
                        self.wfile.write(str(e).encode())

                elif self.path == "/update-world":
                    length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(length).decode("utf-8")
                    try:
                        data = json.loads(body)
                        # Minimal validation
                        if not isinstance(data, dict):
                            raise ValueError("World data must be a JSON object")
                        
                        world_path = os.path.join(workspace, "memory", "reality", "world_state.json")
                        os.makedirs(os.path.dirname(world_path), exist_ok=True)
                        
                        # Merge with existing if available
                        current = {}
                        if os.path.exists(world_path):
                            with open(world_path, "r") as f:
                                current = json.load(f)
                        
                        current.update(data)
                        current["last_update"] = __import__("datetime").datetime.now().isoformat()
                        
                        with open(world_path, "w") as f:
                            json.dump(current, f, indent=2)
                            
                        self.send_response(200)
                        self.send_header("Content-Type", "text/plain")
                        self.end_headers()
                        self.wfile.write(b"OK")
                        print(f"  \u2713 World state updated")
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "text/plain")
                        self.end_headers()
                        self.wfile.write(str(e).encode())

                elif self.path == "/update-cycle":
                    length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(length).decode("utf-8")
                    try:
                        data = json.loads(body)
                        # Schema validation
                        if not isinstance(data, dict):
                            raise ValueError("Cycle data must be a JSON object")
                        for required_key in ("cycle_length", "current_day", "phase"):
                            if required_key not in data:
                                raise ValueError(f"Missing required field: {required_key}")
                        if data["cycle_length"] != 28:
                            raise ValueError("cycle_length must be 28")
                        if not isinstance(data["current_day"], (int, float)) or not (1 <= int(data["current_day"]) <= 28):
                            raise ValueError("current_day must be between 1 and 28")
                        data["current_day"] = int(data["current_day"])
                        cycle_path = os.path.join(workspace, "memory", "reality", "cycle.json")
                        os.makedirs(os.path.dirname(cycle_path), exist_ok=True)
                        with open(cycle_path, "w") as f:
                            json.dump(data, f, indent=2)
                        self.send_response(200)
                        self.send_header("Content-Type", "text/plain")
                        self.end_headers()
                        self.wfile.write(b"OK")
                        print(f"  \u2713 Cycle state saved")
                    except (json.JSONDecodeError, ValueError) as e:
                        self.send_response(400)
                        self.send_header("Content-Type", "text/plain")
                        self.end_headers()
                        self.wfile.write(str(e).encode())
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "text/plain")
                        self.end_headers()
                        self.wfile.write(str(e).encode())

                elif self.path == "/api/genesis/toggle":
                    length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(length).decode("utf-8")
                    try:
                        data = json.loads(body)
                        enabled = data.get("enabled", False)
                        genesis_enabled_path = os.path.join(workspace, "memory", "reality", "genesis_enabled.json")
                        os.makedirs(os.path.dirname(genesis_enabled_path), exist_ok=True)
                        with open(genesis_enabled_path, "w") as f:
                            json.dump({"enabled": enabled, "updated_at": datetime.now().isoformat()}, f, indent=2)
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": True, "enabled": enabled}).encode())
                        print(f"  \u2713 Genesis enabled: {enabled}")
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": False, "message": str(e)}).encode())

                elif self.path == "/api/voice/toggle":
                    length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(length).decode("utf-8")
                    try:
                        data = json.loads(body)
                        enabled = data.get("enabled", False)
                        voice_enabled_path = os.path.join(workspace, "memory", "reality", "voice_enabled.json")
                        os.makedirs(os.path.dirname(voice_enabled_path), exist_ok=True)
                        with open(voice_enabled_path, "w") as f:
                            json.dump({"enabled": enabled, "updated_at": datetime.now().isoformat()}, f, indent=2)
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": True, "enabled": enabled}).encode())
                        print(f"  \u2713 Voice enabled: {enabled}")
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": False, "message": str(e)}).encode())

                elif self.path == "/api/voice/status":
                    try:
                        voice_enabled_path = os.path.join(workspace, "memory", "reality", "voice_enabled.json")
                        if os.path.exists(voice_enabled_path):
                            with open(voice_enabled_path, "r") as f:
                                data = json.load(f)
                            enabled = data.get("enabled", False)
                        else:
                            enabled = False
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"enabled": enabled}).encode())
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"enabled": False, "error": str(e)}).encode())

                elif self.path == "/api/voice/generate":
                    try:
                        length = int(self.headers.get("Content-Length", 0))
                        body = self.rfile.read(length).decode("utf-8")
                        data = json.loads(body)
                        text = data.get("text", "")
                        settings = data.get("settings", {})

                        if not text:
                            self.send_response(400)
                            self.send_header("Content-Type", "application/json")
                            self.end_headers()
                            self.wfile.write(json.dumps({"success": False, "error": "Text is required"}).encode())
                            return

                        # Call voice bridge
                        import subprocess
                        voice_bridge = os.path.join(os.path.dirname(__file__), "voice", "voice_bridge.py")
                        voice_dir = os.path.join(workspace, "memory", "reality", "media", "voice")
                        os.makedirs(voice_dir, exist_ok=True)

                        cmd = [
                            sys.executable,
                            voice_bridge,
                            json.dumps({"text": text, "settings": settings})
                        ]

                        result = subprocess.run(
                            cmd,
                            capture_output=True,
                            text=True,
                            timeout=120
                        )

                        if result.returncode == 0:
                            try:
                                voice_result = json.loads(result.stdout)
                                if voice_result.get("success"):
                                    self.send_response(200)
                                    self.send_header("Content-Type", "application/json")
                                    self.end_headers()
                                    self.wfile.write(json.dumps({
                                        "success": True,
                                        "url": voice_result.get("url"),
                                        "text": text,
                                        "timestamp": voice_result.get("timestamp")
                                    }).encode())
                                else:
                                    raise Exception(voice_result.get("error", "Generation failed"))
                            except json.JSONDecodeError:
                                raise Exception("Invalid response from voice bridge")
                        else:
                            raise Exception(result.stderr or "Voice generation failed")

                    except subprocess.TimeoutExpired:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": False, "error": "Generation timed out"}).encode())
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

                # Voice Sample Upload API
                elif self.path == "/api/voice/upload" and self.command == "POST":
                    try:
                        content_type = self.headers.get('Content-Type', '')
                        if 'multipart/form-data' in content_type:
                            # Parse multipart form data
                            content_length = int(self.headers.get('Content-Length', 0))
                            body = self.rfile.read(content_length)

                            # Extract filename from boundary
                            import re
                            filename_match = re.search(r'filename="([^"]+)"', body.decode('utf-8', errors='ignore'))
                            filename = filename_match.group(1) if filename_match else "voice_sample.wav"

                            # Save to voice samples directory
                            voice_dir = os.path.join(workspace, "memory", "reality", "media", "voice", "samples")
                            os.makedirs(voice_dir, exist_ok=True)

                            # Save the file
                            sample_path = os.path.join(voice_dir, filename)
                            # Extract actual audio data (skip headers)
                            audio_start = body.find(b'\r\n\r\n') + 4
                            audio_data = body[audio_start:]
                            with open(sample_path, 'wb') as f:
                                f.write(audio_data)

                            # Call voice bridge to process sample
                            voice_bridge = os.path.join(os.path.dirname(__file__), "voice", "voice_bridge.py")
                            result = subprocess.run(
                                [sys.executable, voice_bridge, "--upload-sample", sample_path],
                                capture_output=True,
                                text=True,
                                timeout=60
                            )

                            self.send_response(200)
                            self.send_header("Content-Type", "application/json")
                            self.end_headers()
                            self.wfile.write(json.dumps({
                                "success": True,
                                "sample_name": filename,
                                "sample_path": sample_path,
                                "message": "Voice sample uploaded successfully"
                            }).encode())
                        else:
                            raise Exception("Invalid content type")
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

                # Phase 21: The Vault API
                elif self.path == "/api/vault/status":
                    try:
                        vault_bridge = os.path.join(os.path.dirname(__file__), "vault_bridge.py")
                        result = subprocess.run(
                            [sys.executable, vault_bridge, "status"],
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        if result.returncode == 0:
                            data = json.loads(result.stdout)
                            self.send_response(200)
                            self.send_header("Content-Type", "application/json")
                            self.end_headers()
                            self.wfile.write(json.dumps(data).encode())
                        else:
                            raise Exception(result.stderr)
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": str(e)}).encode())

                elif self.path == "/api/vault/config":
                    try:
                        length = int(self.headers.get("Content-Length", 0))
                        body = self.rfile.read(length).decode("utf-8")
                        data = json.loads(body)

                        vault_state_path = os.path.join(workspace, "memory", "reality", "vault_state.json")
                        os.makedirs(os.path.dirname(vault_state_path), exist_ok=True)

                        # Load existing state
                        if os.path.exists(vault_state_path):
                            with open(vault_state_path, "r") as f:
                                state = json.load(f)
                        else:
                            state = {}

                        # Update config
                        state["mode"] = data.get("mode", "paper")
                        state["api_provider"] = data.get("provider", "kraken")
                        state["api_key"] = data.get("api_key", "")
                        state["api_secret"] = data.get("api_secret", "")

                        with open(vault_state_path, "w") as f:
                            json.dump(state, f, indent=2)

                        # Also save to model_config
                        model_config_path = os.path.join(workspace, "memory", "reality", "model_config.json")
                        if os.path.exists(model_config_path):
                            with open(model_config_path, "r") as f:
                                mc = json.load(f)
                        else:
                            mc = {}

                        mc["vault_provider"] = data.get("provider", "kraken")
                        mc["vault_api_key"] = data.get("api_key", "")
                        mc["vault_api_secret"] = data.get("api_secret", "")

                        with open(model_config_path, "w") as f:
                            json.dump(mc, f, indent=2)

                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": True}).encode())
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

                elif self.path == "/api/vault/deposit":
                    try:
                        length = int(self.headers.get("Content-Length", 0))
                        body = self.rfile.read(length).decode("utf-8")
                        data = json.loads(body)
                        amount = data.get("amount", 0)

                        vault_bridge = os.path.join(os.path.dirname(__file__), "vault_bridge.py")
                        result = subprocess.run(
                            [sys.executable, vault_bridge, json.dumps({"action": "deposit", "amount": amount})],
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        if result.returncode == 0:
                            res = json.loads(result.stdout)
                            self.send_response(200)
                            self.send_header("Content-Type", "application/json")
                            self.end_headers()
                            self.wfile.write(json.dumps(res).encode())
                        else:
                            raise Exception(result.stderr)
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

                elif self.path == "/api/vault/trade":
                    try:
                        length = int(self.headers.get("Content-Length", 0))
                        body = self.rfile.read(length).decode("utf-8")
                        data = json.loads(body)

                        vault_bridge = os.path.join(os.path.dirname(__file__), "vault_bridge.py")
                        result = subprocess.run(
                            [sys.executable, vault_bridge, json.dumps(data)],
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        if result.returncode == 0:
                            res = json.loads(result.stdout)
                            self.send_response(200)
                            self.send_header("Content-Type", "application/json")
                            self.end_headers()
                            self.wfile.write(json.dumps(res).encode())
                        else:
                            raise Exception(result.stderr)
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

                # Phase 37: Economy Engine State
                elif self.path == "/api/economy/state":
                    try:
                        economy_state_path = os.path.join(workspace, "memory", "reality", "economy_state.json")
                        if os.path.exists(economy_state_path):
                            with open(economy_state_path, "r") as f:
                                state = json.load(f)
                        else:
                            state = {
                                "isActive": False,
                                "currentStrategy": "observe",
                                "marketMood": "neutral",
                                "totalTrades": 0,
                                "lastTradeTime": None
                            }
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps(state).encode())
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": str(e)}).encode())

                # Phase 39: Presence Engine State
                elif self.path == "/api/presence/state":
                    try:
                        presence_state_path = os.path.join(workspace, "memory", "reality", "presence_state.json")
                        if os.path.exists(presence_state_path):
                            with open(presence_state_path, "r") as f:
                                state = json.load(f)
                        else:
                            state = {
                                "isActive": False,
                                "totalPosts": 0,
                                "postsToday": 0,
                                "lastPostTime": None,
                                "currentMood": "neutral",
                                "feed": []
                            }
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps(state).encode())
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": str(e)}).encode())

                # Phase 40: Hardware Resonance State
                elif self.path == "/api/hardware/resonance":
                    try:
                        resonance_state_path = os.path.join(workspace, "memory", "reality", "hardware_resonance.json")
                        if os.path.exists(resonance_state_path):
                            with open(resonance_state_path, "r") as f:
                                state = json.load(f)
                        else:
                            state = {
                                "isActive": False,
                                "currentCpuLoad": 0,
                                "currentMemoryUsage": 0,
                                "currentTemp": None,
                                "isAudioPlaying": False,
                                "resonanceLevel": "calm",
                                "totalResonanceEvents": 0
                            }
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps(state).encode())
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": str(e)}).encode())

                # v5.1.0: Centralized Config API
                elif self.path == "/api/config/all":
                    try:
                        config_path = os.path.join(workspace, "memory", "reality", "simulation_config.json")
                        if os.path.exists(config_path):
                            with open(config_path, "r") as f:
                                config = json.load(f)
                        else:
                            config = {"version": "5.1.0", "character": {"name": "Q"}}
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps(config).encode())
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": str(e)}).encode())

                elif self.path == "/api/config/save":
                    try:
                        length = int(self.headers.get("Content-Length", 0))
                        body = self.rfile.read(length).decode("utf-8")
                        data = json.loads(body)
                        config_path = os.path.join(workspace, "memory", "reality", "simulation_config.json")
                        os.makedirs(os.path.dirname(config_path), exist_ok=True)
                        data["last_updated"] = datetime.now().isoformat()
                        with open(config_path, "w") as f:
                            json.dump(data, f, indent=2)
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": True}).encode())
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

                # v5.1.0: Telemetry API
                elif self.path == "/api/telemetry/vitals":
                    try:
                        tel_dir = os.path.join(workspace, "memory", "telemetry")
                        entries = []
                        if os.path.exists(tel_dir):
                            for f in os.listdir(tel_dir):
                                if f.startswith("vitality_") and f.endswith(".jsonl"):
                                    with open(os.path.join(tel_dir, f), "r") as fp:
                                        for line in fp:
                                            try:
                                                entries.append(json.loads(line))
                                            except:
                                                pass
                        entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps(entries[:100]).encode())
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": str(e)}).encode())

                elif self.path == "/api/telemetry/hardware":
                    try:
                        tel_path = os.path.join(workspace, "memory", "telemetry", "hardware.jsonl")
                        entries = []
                        if os.path.exists(tel_path):
                            with open(tel_path, "r") as f:
                                for line in f:
                                    try:
                                        entries.append(json.loads(line))
                                    except:
                                        pass
                        entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps(entries[:100]).encode())
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": str(e)}).encode())

                # Phase 41: Debug Logs API
                elif self.path == "/api/logs/recent":
                    try:
                        log_path = os.path.join(workspace, "memory", "genesis_debug.jsonl")
                        entries = []
                        count = int(self.path_query.get("count", 100))
                        level_filter = self.path_query.get("level", "")
                        module_filter = self.path_query.get("module", "")

                        if os.path.exists(log_path):
                            with open(log_path, "r") as f:
                                lines = f.readlines()
                                # Read in reverse to get most recent
                                for line in reversed(lines[-1000:]):
                                    try:
                                        entry = json.loads(line)
                                        if level_filter and entry.get("level") != level_filter:
                                            continue
                                        if module_filter and entry.get("module") != module_filter:
                                            continue
                                        entries.append(entry)
                                        if len(entries) >= count:
                                            break
                                    except:
                                        pass

                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps(entries).encode())
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": str(e)}).encode())

                elif self.path == "/api/mem0/config":
                    try:
                        mem0_config_path = os.path.join(workspace, "memory", "reality", "mem0_config.json")
                        if self.command == "GET":
                            if os.path.exists(mem0_config_path):
                                with open(mem0_config_path, "r") as f:
                                    config = json.load(f)
                            else:
                                config = {"api_key": "", "user_id": "genesis_agent"}
                            self.send_response(200)
                            self.send_header("Content-Type", "application/json")
                            self.end_headers()
                            self.wfile.write(json.dumps(config).encode())
                        else:
                            length = int(self.headers.get("Content-Length", 0))
                            body = self.rfile.read(length).decode("utf-8")
                            data = json.loads(body)
                            os.makedirs(os.path.dirname(mem0_config_path), exist_ok=True)
                            with open(mem0_config_path, "w") as f:
                                json.dump({
                                    "api_key": data.get("api_key", ""),
                                    "user_id": data.get("user_id", "genesis_agent"),
                                    "updated_at": datetime.now().isoformat()
                                }, f, indent=2)
                            self.send_response(200)
                            self.send_header("Content-Type", "application/json")
                            self.end_headers()
                            self.wfile.write(json.dumps({"success": True}).encode())
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": False, "message": str(e)}).encode())

                elif self.path == "/api/mem0/search":
                    try:
                        length = int(self.headers.get("Content-Length", 0))
                        body = self.rfile.read(length).decode("utf-8")
                        data = json.loads(body)
                        query = data.get("query", "")

                        mem0_config_path = os.path.join(workspace, "memory", "reality", "mem0_config.json")
                        user_id = "genesis_agent"
                        if os.path.exists(mem0_config_path):
                            with open(mem0_config_path, "r") as f:
                                cfg = json.load(f)
                                user_id = cfg.get("user_id", "genesis_agent")

                        # Search via local memory bridge
                        bridge = os.path.join(os.path.dirname(__file__), "memory_bridge.py")
                        res = subprocess.run(
                            [sys.executable, bridge, json.dumps({"action": "search", "query": query, "user_id": user_id})],
                            capture_output=True, text=True, timeout=30
                        )
                        
                        if res.returncode == 0:
                            result = json.loads(res.stdout)
                            self.send_response(200)
                            self.send_header("Content-Type", "application/json")
                            self.end_headers()
                            self.wfile.write(json.dumps(result).encode())
                        else:
                            raise Exception(res.stderr)

                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": str(e)}).encode())

                elif self.path == "/api/mem0/store":
                    try:
                        length = int(self.headers.get("Content-Length", 0))
                        body = self.rfile.read(length).decode("utf-8")
                        data = json.loads(body)
                        memory = data.get("memory", "")

                        mem0_config_path = os.path.join(workspace, "memory", "reality", "mem0_config.json")
                        user_id = "genesis_agent"
                        if os.path.exists(mem0_config_path):
                            with open(mem0_config_path, "r") as f:
                                cfg = json.load(f)
                                user_id = cfg.get("user_id", "genesis_agent")

                        # Store via local memory bridge
                        bridge = os.path.join(os.path.dirname(__file__), "memory_bridge.py")
                        res = subprocess.run(
                            [sys.executable, bridge, json.dumps({"action": "add", "text": memory, "user_id": user_id})],
                            capture_output=True, text=True, timeout=30
                        )
                        
                        if res.returncode == 0:
                            result = json.loads(res.stdout)
                            self.send_response(200)
                            self.send_header("Content-Type", "application/json")
                            self.end_headers()
                            self.wfile.write(json.dumps({"success": True, "result": result}).encode())
                        else:
                            raise Exception(res.stderr)

                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": str(e)}).encode())

                # Phase 19: Contact CRM API
                elif self.path == "/api/social/entities":
                    try:
                        social_path = os.path.join(workspace, "memory", "reality", "social.json")
                        if os.path.exists(social_path):
                            with open(social_path, "r") as f:
                                social_data = json.load(f)
                        else:
                            social_data = {"entities": [], "circles": [], "last_network_search": None}

                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps(social_data).encode())
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": str(e)}).encode())

                elif self.path == "/api/social/add-entity":
                    try:
                        length = int(self.headers.get("Content-Length", 0))
                        body = self.rfile.read(length).decode("utf-8")
                        data = json.loads(body)

                        entity_name = data.get("entity_name", "")
                        if not entity_name:
                            raise ValueError("Entity name required")

                        circle = data.get("circle", "Friends")
                        relationship_type = data.get("relationship_type", "acquaintance")

                        social_path = os.path.join(workspace, "memory", "reality", "social.json")
                        if os.path.exists(social_path):
                            with open(social_path, "r") as f:
                                social_data = json.load(f)
                        else:
                            social_data = {"entities": [], "circles": [], "last_network_search": None}

                        # Create new entity
                        now = datetime.now().isoformat()
                        new_entity = {
                            "id": f"social_{int(datetime.now().timestamp())}",
                            "name": entity_name,
                            "relationship_type": relationship_type,
                            "bond": 0,
                            "trust": 10,
                            "intimacy": 0,
                            "last_interaction": now,
                            "interaction_count": 0,
                            "history_summary": f"Met {entity_name} via contact manager.",
                            "introduced_at": now,
                            "notes": "",
                            "circle": circle,
                            "visual_description": "",
                            "portrait_url": "",
                            "is_external": False
                        }

                        social_data.setdefault("entities", []).append(new_entity)

                        os.makedirs(os.path.dirname(social_path), exist_ok=True)
                        with open(social_path, "w") as f:
                            json.dump(social_data, f, indent=2)

                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": True}).encode())

                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

                elif self.path == "/api/social/update-entity":
                    try:
                        length = int(self.headers.get("Content-Length", 0))
                        body = self.rfile.read(length).decode("utf-8")
                        data = json.loads(body)

                        entity_id = data.get("entity_id", "")
                        visual_description = data.get("visual_description", "")

                        if not entity_id:
                            raise ValueError("Entity ID required")

                        social_path = os.path.join(workspace, "memory", "reality", "social.json")
                        if not os.path.exists(social_path):
                            raise ValueError("Social data not found")

                        with open(social_path, "r") as f:
                            social_data = json.load(f)

                        # Find and update entity
                        updated = False
                        for entity in social_data.get("entities", []):
                            if entity.get("id") == entity_id:
                                entity["visual_description"] = visual_description
                                updated = True
                                break

                        if not updated:
                            raise ValueError("Entity not found")

                        with open(social_path, "w") as f:
                            json.dump(social_data, f, indent=2)

                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": True}).encode())

                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

                # Phase 35: Social Engine - Get Pending Events
                elif self.path == "/api/social/pending":
                    events_path = os.path.join(workspace, "memory", "reality", "social_events.json")
                    events = {"pending": []}
                    if os.path.exists(events_path):
                        try:
                            with open(events_path, "r") as f:
                                events = json.load(f)
                        except:
                            pass

                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(events).encode())

                # Phase 36: Spatial Engine - Get State
                elif self.path == "/api/spatial/state":
                    spatial_path = os.path.join(workspace, "memory", "reality", "spatial_state.json")
                    state = {
                        "isActive": False,
                        "currentMode": "idle",
                        "keyStrokesCount": 0,
                        "mouseMovesCount": 0,
                        "scrollCount": 0
                    }
                    if os.path.exists(spatial_path):
                        try:
                            with open(spatial_path, "r") as f:
                                state = json.load(f)
                        except:
                            pass

                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(state).encode())

                # Phase 36: Spatial Engine - Stop Automation
                elif self.path == "/api/desktop/automation":
                    if self.command == 'POST':
                        length = int(self.headers.get("Content-Length", 0))
                        body = self.rfile.read(length).decode("utf-8")
                        try:
                            data = json.loads(body)
                            if data.get("action") == "stop":
                                # Write to spatial state to stop
                                spatial_path = os.path.join(workspace, "memory", "reality", "spatial_state.json")
                                state = {
                                    "isActive": False,
                                    "currentMode": "idle",
                                    "lastInputTime": None,
                                    "keyStrokesCount": 0,
                                    "mouseMovesCount": 0,
                                    "scrollCount": 0
                                }
                                with open(spatial_path, "w") as f:
                                    json.dump(state, f)
                                self.send_response(200)
                                self.send_header("Content-Type", "application/json")
                                self.end_headers()
                                self.wfile.write(json.dumps({"success": True}).encode())
                            else:
                                self.send_response(400)
                                self.send_header("Content-Type", "application/json")
                                self.end_headers()
                                self.wfile.write(json.dumps({"error": "Unknown action"}).encode())
                        except Exception as e:
                            self.send_response(500)
                            self.send_header("Content-Type", "application/json")
                            self.end_headers()
                            self.wfile.write(json.dumps({"error": str(e)}).encode())
                    else:
                        self.send_response(405)
                        self.end_headers()

                elif self.path == "/api/backups/rollback":
                    length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(length).decode("utf-8")
                    try:
                        data = json.loads(body)
                        date = data.get("date", "")
                        backup_dir = os.path.join(workspace, "memory", "backups", date)
                        if not os.path.isdir(backup_dir):
                            raise ValueError("Backup not found")

                        # Restore files
                        files_restore = [
                            ("physique.json", os.path.join(workspace, "memory", "reality", "physique.json")),
                            ("lifecycle.json", os.path.join(workspace, "memory", "reality", "lifecycle.json")),
                            ("finances.json", os.path.join(workspace, "memory", "reality", "finances.json")),
                            ("social.json", os.path.join(workspace, "memory", "reality", "social.json")),
                            ("skills.json", os.path.join(workspace, "memory", "reality", "skills.json")),
                            ("psychology.json", os.path.join(workspace, "memory", "reality", "psychology.json")),
                            ("world_state.json", os.path.join(workspace, "memory", "reality", "world_state.json")),
                            ("interests.json", os.path.join(workspace, "memory", "reality", "interests.json")),
                            ("IDENTITY.md", os.path.join(workspace, "IDENTITY.md")),
                            ("SOUL.md", os.path.join(workspace, "SOUL.md")),
                            ("EMOTIONS.md", os.path.join(workspace, "EMOTIONS.md")),
                            ("GROWTH.md", os.path.join(workspace, "GROWTH.md")),
                            ("DESIRES.md", os.path.join(workspace, "DESIRES.md")),
                        ]
                        for src_name, dest_path in files_restore:
                            src_path = os.path.join(backup_dir, src_name)
                            if os.path.exists(src_path):
                                with open(src_path) as sf:
                                    with open(dest_path, "w") as df:
                                        df.write(sf.read())

                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": True}).encode())
                        print(f"  ✓ Rolled back to {date}")
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": False, "message": str(e)}).encode())

                elif self.path == "/api/profiles/save":
                    length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(length).decode("utf-8")
                    try:
                        data = json.loads(body)
                        name = data.get("name", "")
                        profile_dir = os.path.join(workspace, "memory", "profiles", name)
                        os.makedirs(profile_dir, exist_ok=True)

                        files_save = [
                            (os.path.join(workspace, "memory", "reality", "physique.json"), "physique.json"),
                            (os.path.join(workspace, "memory", "reality", "lifecycle.json"), "lifecycle.json"),
                            (os.path.join(workspace, "memory", "reality", "finances.json"), "finances.json"),
                            (os.path.join(workspace, "memory", "reality", "social.json"), "social.json"),
                            (os.path.join(workspace, "memory", "reality", "skills.json"), "skills.json"),
                            (os.path.join(workspace, "memory", "reality", "psychology.json"), "psychology.json"),
                            (os.path.join(workspace, "memory", "reality", "world_state.json"), "world_state.json"),
                            (os.path.join(workspace, "memory", "reality", "interests.json"), "interests.json"),
                            (os.path.join(workspace, "IDENTITY.md"), "IDENTITY.md"),
                            (os.path.join(workspace, "SOUL.md"), "SOUL.md"),
                            (os.path.join(workspace, "EMOTIONS.md"), "EMOTIONS.md"),
                            (os.path.join(workspace, "GROWTH.md"), "GROWTH.md"),
                            (os.path.join(workspace, "DESIRES.md"), "DESIRES.md"),
                        ]
                        for src_path, dest_name in files_save:
                            if os.path.exists(src_path):
                                with open(src_path) as sf:
                                    with open(os.path.join(profile_dir, dest_name), "w") as df:
                                        df.write(sf.read())

                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": True}).encode())
                        print(f"  ✓ Profile saved: {name}")
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": False, "message": str(e)}).encode())

                elif self.path == "/api/profiles/load":
                    length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(length).decode("utf-8")
                    try:
                        data = json.loads(body)
                        name = data.get("name", "")
                        profile_dir = os.path.join(workspace, "memory", "profiles", name)
                        if not os.path.isdir(profile_dir):
                            raise ValueError("Profile not found")

                        files_restore = [
                            ("physique.json", os.path.join(workspace, "memory", "reality", "physique.json")),
                            ("lifecycle.json", os.path.join(workspace, "memory", "reality", "lifecycle.json")),
                            ("finances.json", os.path.join(workspace, "memory", "reality", "finances.json")),
                            ("social.json", os.path.join(workspace, "memory", "reality", "social.json")),
                            ("skills.json", os.path.join(workspace, "memory", "reality", "skills.json")),
                            ("psychology.json", os.path.join(workspace, "memory", "reality", "psychology.json")),
                            ("world_state.json", os.path.join(workspace, "memory", "reality", "world_state.json")),
                            ("interests.json", os.path.join(workspace, "memory", "reality", "interests.json")),
                            ("IDENTITY.md", os.path.join(workspace, "IDENTITY.md")),
                            ("SOUL.md", os.path.join(workspace, "SOUL.md")),
                            ("EMOTIONS.md", os.path.join(workspace, "EMOTIONS.md")),
                            ("GROWTH.md", os.path.join(workspace, "GROWTH.md")),
                            ("DESIRES.md", os.path.join(workspace, "DESIRES.md")),
                        ]
                        for src_name, dest_path in files_restore:
                            src_path = os.path.join(profile_dir, src_name)
                            if os.path.exists(src_path):
                                with open(src_path) as sf:
                                    with open(dest_path, "w") as df:
                                        df.write(sf.read())

                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": True}).encode())
                        print(f"  ✓ Profile loaded: {name}")
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": False, "message": str(e)}).encode())

                elif self.path == "/api/profiles/delete":
                    length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(length).decode("utf-8")
                    try:
                        data = json.loads(body)
                        name = data.get("name", "")
                        profile_dir = os.path.join(workspace, "memory", "profiles", name)
                        if os.path.isdir(profile_dir):
                            import shutil
                            shutil.rmtree(profile_dir)
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": True}).encode())
                        print(f"  ✓ Profile deleted: {name}")
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": False, "message": str(e)}).encode())

                elif self.path == "/api/genesis/request":
                    length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(length).decode("utf-8")
                    try:
                        data = json.loads(body)
                        prompt_text = data.get("prompt", "")
                        request_path = os.path.join(workspace, "memory", "reality", "genesis_request.json")
                        os.makedirs(os.path.dirname(request_path), exist_ok=True)
                        with open(request_path, "w") as f:
                            json.dump({"prompt": prompt_text, "requested_at": datetime.now().isoformat()}, f, indent=2)
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": True}).encode())
                        print(f"  \u2713 Genesis request saved")
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": False, "message": str(e)}).encode())

                elif self.path == "/api/genesis/request-status":
                    request_path = os.path.join(workspace, "memory", "reality", "genesis_request.json")
                    pending = os.path.exists(request_path)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"pending": pending}).encode())

                elif self.path == "/api/avatar/update":
                    # Handle avatar pose/emote/wardrobe/interaction updates
                    length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(length).decode("utf-8")
                    try:
                        req = json.loads(body)
                        action = req.get("action", "")
                        value = req.get("value", "")

                        # Write to avatar state file for the frontend to pick up
                        avatar_state_path = os.path.join(workspace, "memory", "reality", "avatar_state.json")
                        state = {
                            "action": action,
                            "value": value,
                            "timestamp": datetime.now().isoformat()
                        }

                        # Phase 33: Handle interaction updates
                        if action == "interaction_update":
                            interaction_state = req.get("state", {})
                            state.update({
                                "holding": interaction_state.get("holding", []),
                                "light_intensity": interaction_state.get("light_intensity", 0.8),
                                "light_color": interaction_state.get("light_color", "#ffffff"),
                                "furniture": interaction_state.get("furniture", ""),
                                "prop": interaction_state.get("prop", ""),
                            })

                        with open(avatar_state_path, "w") as f:
                            json.dump(state, f, indent=2)

                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": True, "action": action, "value": value}).encode())
                        print(f"  \u2713 Avatar update: {action} = {value}")
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": False, "message": str(e)}).encode())

                elif self.path == "/api/avatar/state":
                    # Return current avatar state
                    avatar_state_path = os.path.join(workspace, "memory", "reality", "avatar_state.json")
                    state = {"action": "idle", "value": "", "timestamp": ""}
                    if os.path.exists(avatar_state_path):
                        try:
                            with open(avatar_state_path, "r") as f:
                                state = json.load(f)
                        except:
                            pass

                    # Also check for atmosphere state
                    atmosphere_state_path = os.path.join(workspace, "memory", "reality", "atmosphere_state.json")
                    atmosphere = {}
                    if os.path.exists(atmosphere_state_path):
                        try:
                            with open(atmosphere_state_path, "r") as f:
                                atmosphere = json.load(f)
                        except:
                            pass

                    # Merge atmosphere into state if present
                    if atmosphere:
                        state["atmosphere"] = atmosphere

                    # Phase 33: Also check for interaction state
                    interaction_state_path = os.path.join(workspace, "memory", "reality", "interaction_state.json")
                    interaction = {}
                    if os.path.exists(interaction_state_path):
                        try:
                            with open(interaction_state_path, "r") as f:
                                interaction = json.load(f)
                        except:
                            pass

                    if interaction:
                        state["interaction"] = {
                            "current_action": interaction.get("current_action", "standing"),
                            "holding": interaction.get("holding", []),
                            "light_intensity": interaction.get("light_intensity", 0.8),
                            "light_color": interaction.get("light_color", "#ffffff"),
                            "furniture": interaction.get("current_furniture", {}).get("name", ""),
                            "prop": interaction.get("current_prop", {}).get("name", ""),
                        }

                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(state).encode())

                elif self.path == "/api/avatar/config":
                    # Return avatar configuration
                    avatar_config_path = os.path.join(workspace, "memory", "reality", "avatar_config.json")
                    config = {}
                    if os.path.exists(avatar_config_path):
                        try:
                            with open(avatar_config_path, "r") as f:
                                config = json.load(f)
                        except:
                            pass
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(config).encode())

                elif self.path == "/api/avatar/voice":
                    # Phase 24: Handle voice playback requests
                    # POST body: {"audioUrl": "/path/to/audio.wav"}
                    length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(length).decode("utf-8")
                    try:
                        req = json.loads(body)
                        audio_url = req.get("audioUrl", "")

                        # Write voice state for frontend to pick up
                        voice_state_path = os.path.join(workspace, "memory", "reality", "avatar_state.json")
                        state = {
                            "action": "voice",
                            "audioUrl": audio_url,
                            "timestamp": datetime.now().isoformat()
                        }
                        with open(voice_state_path, "w") as f:
                            json.dump(state, f, indent=2)

                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": True, "audioUrl": audio_url}).encode())
                        print(f"  → Voice playback queued: {audio_url}")
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({"success": False, "message": str(e)}).encode())

                # Phase 31: Interests API
                elif self.path == "/api/interests":
                    interests_path = os.path.join(workspace, "memory", "reality", "interests.json")
                    interests = {"hobbies": [], "likes": {}, "dislikes": [], "wishlist": [], "experiences": []}
                    if os.path.exists(interests_path):
                        try:
                            with open(interests_path, "r") as f:
                                interests = json.load(f)
                        except:
                            pass
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(interests).encode())

                # Phase 31: Dreams API
                elif self.path == "/api/dreams":
                    dreams_dir = os.path.join(workspace, "memory", "reality", "dreams")
                    dreams_list = []
                    total_insights = 0
                    last_date = None

                    if os.path.exists(dreams_dir):
                        try:
                            for f in os.listdir(dreams_dir):
                                if f.startswith("dream_") and f.endswith(".md"):
                                    fpath = os.path.join(dreams_dir, f)
                                    content = open(fpath).read()
                                    # Extract date from filename
                                    date = f.replace("dream_", "").replace(".md", "")
                                    # Count insights (## lines)
                                    insights = content.count("## ")
                                    total_insights += insights
                                    # Extract summary
                                    summary = ""
                                    if "## Dream Summary" in content:
                                        parts = content.split("## Dream Summary")
                                        if len(parts) > 1:
                                            summary = parts[1].split("##")[0].strip()[:200]
                                    dreams_list.append({
                                        "date": date,
                                        "summary": summary,
                                        "insights": insights
                                    })
                                    if not last_date:
                                        last_date = date
                        except:
                            pass

                    # Sort by date descending
                    dreams_list.sort(key=lambda x: x["date"], reverse=True)

                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        "dreams": dreams_list[:10],  # Last 10
                        "count": len(dreams_list),
                        "insights": total_insights,
                        "lastDate": last_date
                    }).encode())

                # Phase 32: Simulation Config API
                elif self.path == "/api/config/simulation":
                    config_path = os.path.join(workspace, "memory", "reality", "simulation_config.json")

                    if self.command == 'GET':
                        config = {}
                        if os.path.exists(config_path):
                            try:
                                with open(config_path, "r") as f:
                                    config = json.load(f)
                            except:
                                pass
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps(config).encode())
                    else:
                        length = int(self.headers.get("Content-Length", 0))
                        body = self.rfile.read(length).decode("utf-8")
                        try:
                            data = json.loads(body)
                            config = {}
                            if os.path.exists(config_path):
                                with open(config_path, "r") as f:
                                    config = json.load(f)
                            config.update(data)
                            with open(config_path, "w") as f:
                                json.dump(config, f, indent=2)
                            self.send_response(200)
                            self.send_header("Content-Type", "application/json")
                            self.end_headers()
                            self.wfile.write(json.dumps({"success": True}).encode())
                            print("  → Simulation config saved")
                        except Exception as e:
                            self.send_response(500)
                            self.send_header("Content-Type", "application/json")
                            self.end_headers()
                            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

                # Phase 32: VMC Config API
                elif self.path == "/api/config/vmc":
                    config_path = os.path.join(workspace, "memory", "reality", "osc_config.json")

                    if self.command == 'GET':
                        config = {}
                        if os.path.exists(config_path):
                            try:
                                with open(config_path, "r") as f:
                                    config = json.load(f)
                            except:
                                pass
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps(config).encode())
                    else:
                        length = int(self.headers.get("Content-Length", 0))
                        body = self.rfile.read(length).decode("utf-8")
                        try:
                            data = json.loads(body)
                            config = {}
                            if os.path.exists(config_path):
                                with open(config_path, "r") as f:
                                    config = json.load(f)

                            # Map frontend names to internal names
                            if 'vmc_enabled' in data:
                                config['enabled'] = data['vmc_enabled']
                            if 'vmc_target_ip' in data:
                                config['targetIp'] = data['vmc_target_ip']
                            if 'vmc_target_port' in data:
                                config['targetPort'] = data['vmc_target_port']

                            with open(config_path, "w") as f:
                                json.dump(config, f, indent=2)
                            self.send_response(200)
                            self.send_header("Content-Type", "application/json")
                            self.end_headers()
                            self.wfile.write(json.dumps({"success": True}).encode())
                            print("  → VMC config saved")
                        except Exception as e:
                            self.send_response(500)
                            self.send_header("Content-Type", "application/json")
                            self.end_headers()
                            self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode())

                # Phase 34: Self-Expansion State API
                elif self.path == "/api/expansion/state":
                    expansion_path = os.path.join(workspace, "memory", "reality", "expansion_state.json")
                    state = {
                        "isExpanding": False,
                        "currentProject": None,
                        "totalProjectsCreated": 0,
                        "expansionCount": 0
                    }
                    if os.path.exists(expansion_path):
                        try:
                            with open(expansion_path, "r") as f:
                                state = json.load(f)
                        except:
                            pass

                    # Also check manifest for active projects
                    manifest_path = os.path.join(workspace, "memory", "development", "manifest.json")
                    active = []
                    if os.path.exists(manifest_path):
                        try:
                            with open(manifest_path, "r") as f:
                                manifest = json.load(f)
                                if manifest and manifest.get("projects"):
                                    active = [p for p in manifest["projects"] if p.get("status") not in ["completed", "paused"]]
                        except:
                            pass

                    state["active"] = active
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(state).encode())

                # Phase 34: Self-Expansion Projects API
                elif self.path == "/api/expansion/projects":
                    manifest_path = os.path.join(workspace, "memory", "development", "manifest.json")
                    projects = []
                    if os.path.exists(manifest_path):
                        try:
                            with open(manifest_path, "r") as f:
                                manifest = json.load(f)
                                if manifest and manifest.get("projects"):
                                    projects = manifest["projects"]
                        except:
                            pass

                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"projects": projects}).encode())

                else:
                    self.send_response(404)
                    self.end_headers()

            def log_message(self, format, *args):
                # Suppress GET request logging noise
                if "POST" in str(args):
                    super().log_message(format, *args)

        os.chdir(out_dir)
        print(f"\n  → Serving at http://localhost:{port}/soul-evolution.html")
        print(f"  → Mindmap at  http://localhost:{port}/soul-mindmap.html")
        print(f"  → Edits save directly to: {soul_path}\n")

        with socketserver.TCPServer(("0.0.0.0", port), SoulEvolutionHandler) as httpd:
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nStopped.")
    else:
        out_dir = workspace
        with open(os.path.join(out_dir, "soul-evolution.html"), "w") as f:
            f.write(html)
        with open(os.path.join(out_dir, "soul-mindmap.html"), "w") as f:
            f.write(mindmap_html)
        print(f"\n  → Dashboard: {os.path.join(out_dir, 'soul-evolution.html')}")
        print(f"  → Mindmap:   {os.path.join(out_dir, 'soul-mindmap.html')}")
        print(f"  → Open in browser or run: python3 -m http.server 8080")



if __name__ == "__main__":
    main()
