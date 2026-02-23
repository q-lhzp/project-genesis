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

    return {
        "soul_tree": soul_tree,
        "soul_raw": soul_content,
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
        "telemetry_vitality": vitality_data[-100:] if len(vitality_data) > 100 else vitality_data,  # Last 100 entries
        "telemetry_economy": economy_data[-100:] if len(economy_data) > 100 else economy_data,
    }


def generate_html(data: dict) -> str:
    """Generate the interactive visualization HTML."""
    data_json = json.dumps(data, indent=None, default=str)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Soul Evolution</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,700;1,400&display=swap');

* {{ margin: 0; padding: 0; box-sizing: border-box; }}

:root {{
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
}}

html {{ font-size: 15px; }}

body {{
  background: var(--bg);
  color: var(--text);
  font-family: 'DM Sans', sans-serif;
  min-height: 100vh;
  overflow-x: hidden;
}}

/* Grain overlay */
body::after {{
  content: '';
  position: fixed; inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.03'/%3E%3C/svg%3E");
  pointer-events: none;
  z-index: 9999;
}}

/* Header */
.header {{
  padding: 3rem 2rem 2rem;
  text-align: center;
  position: relative;
}}
.header::before {{
  content: '';
  position: absolute; top: 0; left: 50%; transform: translateX(-50%);
  width: 600px; height: 300px;
  background: radial-gradient(ellipse, var(--accent-glow), transparent 70%);
  pointer-events: none;
}}
.header h1 {{
  font-family: 'JetBrains Mono', monospace;
  font-weight: 300;
  font-size: 2.2rem;
  letter-spacing: 0.15em;
  color: var(--text-bright);
  position: relative;
}}
.header h1 .evolution {{ color: var(--accent); }}
.header h1 .soul {{ color: var(--text-dim); }}
.header .subtitle {{
  font-size: 0.85rem;
  color: var(--text-dim);
  margin-top: 0.6rem;
  font-family: 'JetBrains Mono', monospace;
  letter-spacing: 0.05em;
}}
.header .subtitle .evolution {{ color: var(--accent); }}
.header .subtitle .soul {{ color: var(--text-dim); }}
.stats-bar {{
  display: flex; justify-content: center; gap: 2.5rem;
  margin-top: 1.5rem; flex-wrap: wrap;
}}
.stat {{
  text-align: center;
}}
.stat .num {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.6rem; font-weight: 700;
  color: var(--text-bright);
}}
  .stat .label {{
    font-size: 0.7rem; color: var(--text-dim);
    text-transform: uppercase; letter-spacing: 0.1em;
    margin-top: 0.2rem;
  }}

  /* News Ticker */
  .news-ticker {{
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
  }}
  .ticker-content {{
    display: inline-block;
    padding-left: 100%;
    animation: ticker 60s linear infinite;
  }}
  @keyframes ticker {{
    0% {{ transform: translateX(0); }}
    100% {{ transform: translateX(-100%); }}
  }}
  .ticker-item {{
    display: inline-block;
    padding: 0 2rem;
  }}
  .ticker-item::before {{ content: '⚡'; margin-right: 0.5rem; }}

  .pulse {{
    display: inline-block;
    animation: pulse 2s infinite;
    margin-right: 0.5rem;
  }}
  @keyframes pulse {{
    0% {{ opacity: 1; transform: scale(1); }}
    50% {{ opacity: 0.4; transform: scale(0.8); }}
    100% {{ opacity: 1; transform: scale(1); }}
  }}

  /* Mental Activity */
  .mental-card {{
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-left: 4px solid var(--accent);
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
  }}
  .mental-label {{
    font-size: 0.7rem;
    text-transform: uppercase;
    color: var(--text-dim);
    margin-bottom: 0.5rem;
    display: block;
  }}
  .mental-content {{
    font-size: 0.95rem;
    line-height: 1.4;
    color: var(--text-bright);
    font-style: italic;
  }}
  .mental-sub {{
    font-size: 0.8rem;
    color: var(--text-dim);
    margin-top: 0.5rem;
    display: block;
  }}
  .browser-snap {{
    width: 100%;
    border-radius: 4px;
    margin-top: 0.5rem;
    border: 1px solid var(--border);
    cursor: pointer;
    transition: transform 0.2s;
  }}
  .browser-snap:hover {{
    transform: scale(1.02);
  }}

  /* Layout */

.main {{
  max-width: 1600px;
  margin: 0 auto;
  padding: 0 2rem 4rem;
  display: grid;
  grid-template-columns: 1fr 380px 380px;
  gap: 1.5rem;
}}
@media (max-width: 1200px) {{
  .main {{ grid-template-columns: 1fr; }}
  .soul-map {{ order: -1; }}
}}

/* Soul Map */
.soul-map {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
  position: relative;
}}
.soul-map h2 {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem; font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--text-dim);
  margin-bottom: 1.2rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--border);
}}

.section-block {{
  margin-bottom: 1.5rem;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--border);
  opacity: 0;
  transform: translateY(12px);
  transition: opacity 0.5s, transform 0.5s;
}}
.section-block.visible {{
  opacity: 1;
  transform: translateY(0);
}}
.section-header {{
  padding: 0.7rem 1rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem; font-weight: 500;
  letter-spacing: 0.08em;
  display: flex; align-items: center; gap: 0.6rem;
  cursor: pointer;
  user-select: none;
}}
.section-header .dot {{
  width: 8px; height: 8px; border-radius: 50%;
  flex-shrink: 0;
}}
.section-header .arrow {{
  margin-left: auto;
  font-size: 0.7rem;
  transition: transform 0.3s;
  color: var(--text-dim);
}}
.section-block.collapsed .section-header .arrow {{
  transform: rotate(-90deg);
}}
.section-block.collapsed .section-body {{
  display: none;
}}

.subsection {{
  padding: 0.3rem 1rem 0.5rem 1.6rem;
}}
.subsection-title {{
  font-size: 0.72rem;
  color: var(--text-dim);
  font-weight: 500;
  margin-bottom: 0.4rem;
  padding-left: 0.4rem;
}}

.bullet {{
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
}}
.bullet:hover {{
  background: var(--bg-hover);
}}
.bullet.highlight-enter {{
  animation: bulletEnter 1s ease-out;
}}
@keyframes bulletEnter {{
  0% {{ background: rgba(124, 111, 240, 0.3); transform: scale(1.02); }}
  100% {{ background: transparent; transform: scale(1); }}
}}
.bullet .tag {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  font-weight: 700;
  padding: 0.15rem 0.4rem;
  border-radius: 3px;
  flex-shrink: 0;
  margin-top: 0.15rem;
  letter-spacing: 0.05em;
}}
.bullet .tag.core {{
  color: var(--core);
  background: var(--core-bg);
  border: 1px solid var(--core-border);
}}
.bullet .tag.mutable {{
  color: var(--mutable);
  background: var(--mutable-bg);
  border: 1px solid var(--mutable-border);
}}
.bullet.is-new {{
  opacity: 0;
  max-height: 0;
  overflow: hidden;
  transition: opacity 0.6s, max-height 0.6s;
}}
.bullet.is-new.revealed {{
  opacity: 1;
  max-height: 200px;
}}

/* Right panel */
.right-panel {{
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}}

/* Timeline */
.timeline-panel {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
}}
.timeline-panel h2 {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem; font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--text-dim);
  margin-bottom: 1rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--border);
}}

.timeline-controls {{
  display: flex; align-items: center; gap: 0.6rem;
  margin-bottom: 1.2rem;
}}
.timeline-controls button {{
  background: var(--bg-hover);
  border: 1px solid var(--border);
  color: var(--text);
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.72rem;
  cursor: pointer;
  transition: all 0.2s;
}}
.timeline-controls button:hover {{
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}}
.timeline-controls button.active {{
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}}
.timeline-slider {{
  flex: 1;
  -webkit-appearance: none;
  height: 4px;
  border-radius: 2px;
  background: var(--timeline-line);
  outline: none;
}}
.timeline-slider::-webkit-slider-thumb {{
  -webkit-appearance: none;
  width: 14px; height: 14px;
  border-radius: 50%;
  background: var(--accent);
  cursor: pointer;
  box-shadow: 0 0 8px var(--accent-glow);
}}
.timeline-label {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  color: var(--text-dim);
  min-width: 3rem;
  text-align: right;
}}

/* Change entries */
.change-entry {{
  padding: 0.8rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  margin-bottom: 0.6rem;
  position: relative;
  transition: all 0.3s;
  opacity: 0;
  transform: translateX(10px);
}}
.change-entry.visible {{
  opacity: 1;
  transform: translateX(0);
}}
.change-entry:hover {{
  border-color: var(--accent);
  background: var(--bg-hover);
}}
.change-entry .change-time {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  color: var(--text-dim);
}}
.change-entry .change-type {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 0.1rem 0.35rem;
  border-radius: 3px;
  display: inline-block;
  margin: 0.3rem 0;
}}
.change-entry .change-type.add {{
  color: var(--mutable);
  background: var(--mutable-bg);
  border: 1px solid var(--mutable-border);
}}
.change-entry .change-type.modify {{
  color: var(--accent);
  background: var(--accent-glow);
  border: 1px solid rgba(124, 111, 240, 0.3);
}}
.change-entry .change-type.remove {{
  color: var(--core);
  background: var(--core-bg);
  border: 1px solid var(--core-border);
}}
.change-entry .change-section {{
  font-size: 0.72rem;
  color: var(--text-dim);
  margin: 0.2rem 0;
}}
.change-entry .change-content {{
  font-size: 0.78rem;
  line-height: 1.4;
  color: var(--text);
  margin-top: 0.3rem;
}}

/* Experience feed */
.feed-panel {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
  max-height: 400px;
  overflow-y: auto;
}}
.feed-panel h2 {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem; font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--text-dim);
  margin-bottom: 1rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--border);
}}
.feed-panel::-webkit-scrollbar {{
  width: 4px;
}}
.feed-panel::-webkit-scrollbar-track {{
  background: transparent;
}}
.feed-panel::-webkit-scrollbar-thumb {{
  background: var(--border);
  border-radius: 2px;
}}

.exp-entry {{
  padding: 0.6rem 0;
  border-bottom: 1px solid var(--border);
  font-size: 0.78rem;
  line-height: 1.4;
}}
.exp-entry:last-child {{ border-bottom: none; }}
.exp-meta {{
  display: flex; gap: 0.5rem; align-items: center;
  margin-bottom: 0.25rem;
}}
.exp-source {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 0.1rem 0.35rem;
  border-radius: 3px;
  background: var(--bg-hover);
  color: var(--text-dim);
}}
.exp-source.moltbook {{ color: #f0a050; background: rgba(240, 160, 80, 0.1); }}
.exp-source.conversation {{ color: var(--accent); background: var(--accent-glow); }}
.exp-sig {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.55rem;
  color: var(--text-dim);
}}
.exp-sig.notable {{ color: var(--mutable); }}
.exp-sig.pivotal {{ color: var(--core); }}
.exp-content {{ color: var(--text-dim); }}

/* Legend */
.legend {{
  display: flex; gap: 1.2rem; flex-wrap: wrap;
  padding: 0.8rem 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 0.7rem;
}}
.legend-item {{
  display: flex; align-items: center; gap: 0.4rem;
}}
.legend-dot {{
  width: 8px; height: 8px; border-radius: 50%;
}}

/* Empty state */
.empty-state {{
  text-align: center;
  padding: 2rem;
  color: var(--text-dim);
  font-size: 0.85rem;
  font-style: italic;
}}

/* Edit mode */
.edit-bar {{
  display: flex; align-items: center; gap: 0.6rem;
  margin-bottom: 1rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--border);
}}
.edit-bar h2 {{
  margin: 0 !important; padding: 0 !important; border: none !important;
  flex-shrink: 0;
}}
.edit-bar .spacer {{ flex: 1; min-width: 0; }}
.btn-edit, .btn-save {{
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
}}
.btn-edit:hover {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
.btn-save {{
  background: rgba(80, 200, 120, 0.15);
  border-color: var(--mutable-border);
  color: var(--mutable);
}}
.btn-save:hover {{
  background: var(--mutable);
  color: #fff;
  border-color: var(--mutable);
}}
.btn-edit.active {{
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}}

/* Genesis Toggle Switch */
#genesis-enabled {{ opacity: 0; width: 0; height: 0; }}
#genesis-enabled + span {{ background-color: #ccc; }}
#genesis-enabled:checked + span {{ background-color: var(--core); }}
#genesis-enabled:checked + span:before {{ transform: translateX(24px); }}
#genesis-enabled + span:before {{ position: absolute; content: ''; height: 20px; width: 20px; left: 3px; bottom: 3px; background-color: white; transition: 0.3s; border-radius: 50%; }}

/* Editable bullets */
.bullet.editing {{
  background: var(--bg-hover);
  border: 1px solid var(--border);
  border-radius: 6px;
}}
.bullet .edit-text {{
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
}}
.bullet .edit-text:focus {{
  color: var(--text-bright);
}}
.bullet .tag-toggle {{
  cursor: pointer;
  user-select: none;
  transition: transform 0.15s;
}}
.bullet .tag-toggle:hover {{ transform: scale(1.15); }}
.bullet .btn-delete {{
  background: none;
  border: none;
  color: var(--text-dim);
  cursor: pointer;
  font-size: 0.9rem;
  padding: 0 0.2rem;
  opacity: 0;
  transition: all 0.2s;
  flex-shrink: 0;
}}
.bullet.editing .btn-delete {{ opacity: 0.5; }}
.bullet.editing .btn-delete:hover {{ opacity: 1; color: var(--core); }}
.btn-add-bullet {{
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
}}
.soul-map.edit-mode .btn-add-bullet {{ display: block; }}
.btn-add-bullet:hover {{
  border-color: var(--mutable);
  color: var(--mutable);
  background: var(--mutable-bg);
}}

/* Save toast */
.save-toast {{
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
}}
.save-toast.show {{ opacity: 1; }}

/* Modal */
.modal-overlay {{
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.7);
  z-index: 10000;
  display: none;
  align-items: center;
  justify-content: center;
}}
.modal-overlay.open {{ display: flex; }}
.modal-box {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
  min-width: 340px;
  max-width: 480px;
}}
.modal-title {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-bright);
  margin-bottom: 1rem;
}}
.modal-field {{
  margin-bottom: 0.8rem;
}}
.modal-field label {{
  display: block;
  font-size: 0.7rem;
  color: var(--text-dim);
  font-family: 'JetBrains Mono', monospace;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 0.3rem;
}}
.modal-field input, .modal-field select {{
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
}}
.modal-field input:focus, .modal-field select:focus {{ border-color: var(--accent); }}
.modal-buttons {{
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1rem;
}}

/* Mindmap link */
.mindmap-link {{
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
}}
.mindmap-link::before {{
  content: '';
  position: absolute; inset: 0;
  background: linear-gradient(135deg, rgba(80, 200, 120, 0.08), rgba(124, 111, 240, 0.08));
  opacity: 0;
  transition: opacity 0.3s;
}}
.mindmap-link:hover {{
  border-color: var(--mutable);
  transform: translateY(-1px);
  box-shadow: 0 4px 20px rgba(80, 200, 120, 0.1);
}}
.mindmap-link:hover::before {{ opacity: 1; }}
.mindmap-link-icon {{ font-size: 1.3rem; position: relative; }}
.mindmap-link-sub {{
  font-size: 0.65rem;
  color: var(--text-dim);
  font-weight: 300;
  letter-spacing: 0.05em;
}}
.mindmap-link-arrow {{
  margin-left: auto;
  font-size: 1.1rem;
  color: var(--mutable);
  transition: transform 0.3s;
  position: relative;
}}
.mindmap-link:hover .mindmap-link-arrow {{ transform: translateX(4px); }}

/* Vitals Dashboard */
.vitals-panel {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
}}
.vitals-panel h2 {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem; font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--text-dim);
  margin-bottom: 1rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--border);
}}
.vitals-grid {{
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}}
.vital-row {{
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 0.78rem;
}}
.vital-label {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  color: var(--text-dim);
  min-width: 60px;
  text-transform: capitalize;
}}
.vital-bar-bg {{
  flex: 1;
  height: 10px;
  background: var(--bg-hover);
  border-radius: 5px;
  overflow: hidden;
}}
.vital-bar {{
  height: 100%;
  border-radius: 5px;
  transition: width 0.5s ease;
}}
.vital-value {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  color: var(--text-dim);
  min-width: 30px;
  text-align: right;
}}
.vitals-meta {{
  margin-top: 0.8rem;
  padding-top: 0.8rem;
  border-top: 1px solid var(--border);
  font-size: 0.72rem;
  color: var(--text-dim);
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}}
.vitals-meta span {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem;
}}

/* Proposals Panel */
.proposals-panel {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
  max-height: 500px;
  overflow-y: auto;
}}
.proposals-panel h2 {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem; font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--text-dim);
  margin-bottom: 1rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--border);
}}
.proposal-card {{
  padding: 0.8rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  margin-bottom: 0.6rem;
  transition: all 0.3s;
}}
.proposal-card:hover {{
  border-color: var(--accent);
  background: var(--bg-hover);
}}
.proposal-header {{
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.4rem;
}}
.proposal-id {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  color: var(--text-dim);
}}
.proposal-type {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  font-weight: 700;
  text-transform: uppercase;
  padding: 0.1rem 0.35rem;
  border-radius: 3px;
}}
.proposal-type.add {{ color: var(--mutable); background: var(--mutable-bg); border: 1px solid var(--mutable-border); }}
.proposal-type.modify {{ color: var(--accent); background: var(--accent-glow); border: 1px solid rgba(124, 111, 240, 0.3); }}
.proposal-type.remove {{ color: var(--core); background: var(--core-bg); border: 1px solid var(--core-border); }}
.proposal-section {{
  font-size: 0.7rem;
  color: var(--text-dim);
  margin-bottom: 0.3rem;
}}
.proposal-content {{
  font-size: 0.78rem;
  color: var(--text);
  line-height: 1.4;
  margin-bottom: 0.3rem;
}}
.proposal-reason {{
  font-size: 0.7rem;
  color: var(--text-dim);
  font-style: italic;
}}
.proposal-actions {{
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}}
.btn-approve, .btn-reject {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  padding: 0.3rem 0.6rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid;
}}
.btn-approve {{
  color: var(--mutable);
  background: var(--mutable-bg);
  border-color: var(--mutable-border);
}}
.btn-approve:hover {{ background: var(--mutable); color: #fff; }}
.btn-reject {{
  color: var(--core);
  background: var(--core-bg);
  border-color: var(--core-border);
}}
.btn-reject:hover {{ background: var(--core); color: #fff; }}

/* Reflections Panel */
.reflections-panel {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
  max-height: 400px;
  overflow-y: auto;
}}
.reflections-panel h2 {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem; font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--text-dim);
  margin-bottom: 1rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--border);
}}
.reflection-card {{
  border: 1px solid var(--border);
  border-radius: 8px;
  margin-bottom: 0.5rem;
  overflow: hidden;
}}
.reflection-header {{
  padding: 0.6rem 0.8rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  transition: background 0.2s;
}}
.reflection-header:hover {{ background: var(--bg-hover); }}
.reflection-header .ref-type {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  font-weight: 700;
  text-transform: uppercase;
  padding: 0.1rem 0.3rem;
  border-radius: 3px;
  color: var(--accent);
  background: var(--accent-glow);
}}
.reflection-header .ref-arrow {{
  margin-left: auto;
  font-size: 0.65rem;
  color: var(--text-dim);
  transition: transform 0.3s;
}}
.reflection-card.collapsed .ref-arrow {{ transform: rotate(-90deg); }}
.reflection-card.collapsed .reflection-body {{ display: none; }}
.reflection-body {{
  padding: 0.5rem 0.8rem 0.8rem;
  font-size: 0.75rem;
  line-height: 1.5;
  color: var(--text-dim);
  border-top: 1px solid var(--border);
}}
.reflection-body .ref-insights {{
  margin-top: 0.4rem;
  padding-left: 0.8rem;
}}
.reflection-body .ref-insights li {{
  margin-bottom: 0.2rem;
  list-style: disc;
}}

/* Significant Memories */
.significant-panel {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
  max-height: 400px;
  overflow-y: auto;
}}
.significant-panel h2 {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem; font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--text-dim);
  margin-bottom: 1rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--border);
}}
.sig-entry {{
  padding: 0.6rem 0;
  border-bottom: 1px solid var(--border);
  font-size: 0.78rem;
  line-height: 1.4;
}}
.sig-entry:last-child {{ border-bottom: none; }}
.sig-badge {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.55rem;
  font-weight: 700;
  text-transform: uppercase;
  padding: 0.1rem 0.35rem;
  border-radius: 3px;
  color: var(--core);
  background: var(--core-bg);
  border: 1px solid var(--core-border);
}}
.sig-content {{ color: var(--text); margin-top: 0.25rem; }}
.sig-context {{ font-size: 0.68rem; color: var(--text-dim); margin-top: 0.15rem; }}

/* Pipeline State */
.pipeline-panel {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
  max-height: 400px;
  overflow-y: auto;
}}
.pipeline-panel h2 {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem; font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--text-dim);
  margin-bottom: 1rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--border);
}}
.state-cards {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
  margin-bottom: 1rem;
}}
.state-card {{
  padding: 0.6rem;
  background: var(--bg-hover);
  border: 1px solid var(--border);
  border-radius: 8px;
  text-align: center;
}}
.state-card .sc-value {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-bright);
}}
.state-card .sc-label {{
  font-size: 0.6rem;
  color: var(--text-dim);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-top: 0.2rem;
}}
.pipeline-run {{
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--border);
  font-size: 0.72rem;
  color: var(--text-dim);
}}
.pipeline-run:last-child {{ border-bottom: none; }}

/* Tab Navigation */
.tab-bar {{
  display: flex;
  gap: 0;
  max-width: 1600px;
  margin: 0 auto;
  padding: 0 2rem;
  border-bottom: 1px solid var(--border);
}}
.tab-btn {{
  padding: 0.7rem 1.5rem;
  background: none;
  border: none;
  color: var(--text-dim);
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.3s;
}}
.tab-btn:hover {{ color: var(--text); }}
.tab-btn.active {{
  color: var(--accent);
  border-bottom-color: var(--accent);
}}
.tab-content {{ display: none; }}
.tab-content.active {{ display: block; }}

/* Shared panel styles for new tabs */
.panel-card {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
}}
.panel-card h2 {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem; font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.15em;
  color: var(--text-dim);
  margin-bottom: 1rem;
  padding-bottom: 0.8rem;
  border-bottom: 1px solid var(--border);
}}

/* Cycle Tab */
.cycle-phase-banner {{
  text-align: center;
  font-size: 1.1rem;
  padding: 1rem 1.5rem;
}}
.cycle-phase-banner .phase-name {{
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  font-size: 1.3rem;
  margin-bottom: 0.3rem;
}}
.cycle-legend {{
  display: flex; gap: 1.5rem; justify-content: center; margin-top: 1rem; flex-wrap: wrap;
}}
.cycle-legend span {{
  font-size: 0.75rem; color: var(--text-dim);
  display: flex; align-items: center; gap: 0.3rem;
}}
.cycle-legend span::before {{
  content: ''; display: inline-block; width: 12px; height: 3px; border-radius: 2px;
}}
.cycle-legend .leg-estrogen::before {{ background: #ff69b4; }}
.cycle-legend .leg-progesterone::before {{ background: #9b59b6; }}
.cycle-legend .leg-lh::before {{ background: #f1c40f; }}
.cycle-legend .leg-fsh::before {{ background: #3498db; }}

.cycle-bar-row {{
  display: flex; align-items: center; gap: 0.8rem; margin-bottom: 0.6rem;
}}
.cycle-bar-label {{ width: 80px; font-size: 0.8rem; color: var(--text-dim); text-align: right; }}
.cycle-bar-track {{
  flex: 1; height: 20px; background: var(--bg); border-radius: 4px; position: relative; overflow: hidden;
}}
.cycle-bar-fill {{
  height: 100%; border-radius: 4px; transition: width 0.3s;
}}
.cycle-bar-value {{ width: 50px; font-size: 0.8rem; font-family: 'JetBrains Mono', monospace; }}
.cycle-bar-fill.positive {{ background: linear-gradient(90deg, #2ecc71, #27ae60); }}
.cycle-bar-fill.negative {{ background: linear-gradient(90deg, #e74c3c, #c0392b); }}

.cycle-body-row {{
  display: flex; align-items: flex-start; gap: 0.8rem; margin-bottom: 1rem;
  padding: 0.6rem; border-radius: 8px; background: var(--bg);
}}
.cycle-body-icon {{ font-size: 1.4rem; }}
.cycle-body-text h3 {{ font-size: 0.85rem; color: var(--text-bright); margin-bottom: 0.2rem; }}
.cycle-body-text p {{ font-size: 0.75rem; color: var(--text-dim); line-height: 1.4; }}

.cycle-sim-row {{
  display: flex; align-items: center; gap: 0.8rem; margin-bottom: 0.8rem;
}}
.cycle-sim-row label {{ width: 140px; font-size: 0.8rem; color: var(--text-dim); }}
.cycle-sim-row input[type=range] {{ flex: 1; accent-color: var(--accent); }}
.cycle-sim-row .sim-val {{ width: 50px; font-size: 0.8rem; font-family: 'JetBrains Mono', monospace; text-align: right; }}
.cycle-presets {{ display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.5rem; }}
.cycle-presets button {{
  padding: 0.4rem 0.8rem; border-radius: 6px; border: 1px solid var(--border);
  background: var(--bg-hover); color: var(--text); font-size: 0.75rem; cursor: pointer;
  transition: all 0.2s;
}}
.cycle-presets button:hover {{ border-color: var(--accent); color: var(--accent); }}

.cycle-edu-card {{
  border: 1px solid var(--border); border-radius: 8px; margin-bottom: 0.5rem; overflow: hidden;
}}
.cycle-edu-header {{
  padding: 0.8rem 1rem; cursor: pointer; display: flex; justify-content: space-between;
  align-items: center; font-size: 0.85rem; font-weight: 500; transition: background 0.2s;
}}
.cycle-edu-header:hover {{ background: var(--bg-hover); }}
.cycle-edu-body {{
  padding: 0 1rem; max-height: 0; overflow: hidden; transition: max-height 0.3s, padding 0.3s;
  font-size: 0.8rem; line-height: 1.6; color: var(--text-dim);
}}
.cycle-edu-card.open .cycle-edu-body {{ max-height: 500px; padding: 0.8rem 1rem; }}

/* Item Cards Grid */
.item-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}}
.item-card {{
  background: var(--bg-hover);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s;
}}
.item-card:hover {{
  border-color: var(--accent);
  transform: translateY(-2px);
}}
.item-card .thumb {{
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
}}
.item-card .thumb img {{
  width: 100%;
  height: 100%;
  object-fit: cover;
}}
.item-card .card-name {{
  font-size: 0.85rem;
  color: var(--text-bright);
  font-weight: 500;
}}
.item-card .card-meta {{
  font-size: 0.7rem;
  color: var(--text-dim);
  margin-top: 0.2rem;
}}

/* Category chips */
.chip-bar {{
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}}
.chip {{
  padding: 0.3rem 0.8rem;
  border-radius: 20px;
  font-size: 0.7rem;
  font-family: 'JetBrains Mono', monospace;
  background: var(--bg-hover);
  border: 1px solid var(--border);
  color: var(--text-dim);
  cursor: pointer;
  transition: all 0.2s;
}}
.chip:hover, .chip.active {{
  background: var(--accent-glow);
  border-color: var(--accent);
  color: var(--accent);
}}

/* Status badges */
.badge {{
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 12px;
  font-size: 0.6rem;
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}}
.badge-draft {{ background: rgba(120,120,120,0.2); color: #999; }}
.badge-pending {{ background: rgba(240,180,50,0.15); color: #f0b432; }}
.badge-approved {{ background: rgba(80,200,120,0.15); color: #50c878; }}
.badge-active {{ background: rgba(80,160,240,0.15); color: #50a0f0; }}

/* Lightbox */
.lightbox-overlay {{
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.85);
  z-index: 9998;
  display: none;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 1rem;
}}
.lightbox-overlay.open {{ display: flex; }}
.lightbox-overlay img {{
  max-width: 90vw;
  max-height: 70vh;
  border-radius: 8px;
}}
.lightbox-gallery {{
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
  padding: 0.5rem;
}}
.lightbox-gallery img {{
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 6px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: border-color 0.2s;
}}
.lightbox-gallery img:hover, .lightbox-gallery img.active {{
  border-color: var(--accent);
}}
.lightbox-close {{
  position: absolute;
  top: 1rem;
  right: 1.5rem;
  background: none;
  border: none;
  color: var(--text);
  font-size: 2rem;
  cursor: pointer;
}}
.lightbox-actions {{
  display: flex;
  gap: 0.5rem;
}}
.lightbox-actions button {{
  padding: 0.4rem 1rem;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--bg-card);
  color: var(--text);
  font-size: 0.75rem;
  cursor: pointer;
}}
.lightbox-actions button:hover {{ border-color: var(--accent); }}
.lightbox-actions button.danger {{ color: var(--core); }}
.lightbox-actions button.danger:hover {{ border-color: var(--core); }}

/* Upload zone */
.upload-zone {{
  border: 2px dashed var(--border);
  border-radius: 10px;
  padding: 1.5rem;
  text-align: center;
  color: var(--text-dim);
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.3s;
  margin-top: 0.5rem;
}}
.upload-zone:hover, .upload-zone.dragover {{
  border-color: var(--accent);
  color: var(--accent);
  background: var(--accent-glow);
}}

/* Room tabs */
.room-tabs {{
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}}
.room-tab {{
  padding: 0.4rem 1rem;
  border-radius: 8px;
  font-size: 0.75rem;
  font-family: 'JetBrains Mono', monospace;
  background: var(--bg-hover);
  border: 1px solid var(--border);
  color: var(--text-dim);
  cursor: pointer;
  transition: all 0.2s;
}}
.room-tab:hover, .room-tab.active {{
  background: var(--accent-glow);
  border-color: var(--accent);
  color: var(--accent);
}}

/* Search bar */
.search-bar {{
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
}}
.search-bar:focus {{ border-color: var(--accent); }}

/* CRUD buttons */
.btn-crud {{
  padding: 0.35rem 0.8rem;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--bg-card);
  color: var(--text);
  font-size: 0.72rem;
  font-family: 'JetBrains Mono', monospace;
  cursor: pointer;
  transition: all 0.2s;
}}
.btn-crud:hover {{ border-color: var(--accent); color: var(--accent); }}
.btn-crud.danger:hover {{ border-color: var(--core); color: var(--core); }}

/* Detail panel */
.detail-panel {{
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
  margin-top: 1rem;
}}
.detail-images {{
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin: 0.5rem 0;
}}
.detail-images img {{
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 6px;
  cursor: pointer;
  border: 2px solid var(--border);
  transition: border-color 0.2s;
}}
.detail-images img:hover {{ border-color: var(--accent); }}
</style>
</head>
<body>
<div class="news-ticker" id="news-ticker">
  <div class="ticker-content" id="ticker-content">
    <div class="ticker-item">Project Genesis Simulation Active</div>
    <div class="ticker-item">Waiting for world events...</div>
  </div>
</div>
<div class="header">
  <h1>Agent Soul Evolution</h1>
  <div class="subtitle">powered by <span class="evolution">Soul</span><span class="soul"> Evolution</span></div>
  <div class="stats-bar" id="stats-bar"></div>
  <div id="cognitive-status" style="margin-top:1rem;font-family:'JetBrains Mono',monospace;font-size:0.8rem;color:var(--accent);">
    <span class="pulse">●</span> <span id="status-text">Cognitive System Synchronized</span>
  </div>
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
  <button class="tab-btn" onclick="switchTab('genesis')">Genesis Lab</button>
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
    <div class="panel-card">
      <h2>Development Projects</h2>
      <div class="item-grid" id="dev-grid"></div>
      <div id="dev-detail" style="margin-top:1rem;"></div>
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
          <label style="font-size:0.8rem;">API Key</label>
          <input type="password" id="api-key" placeholder="sk-..." style="width:100%;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:4px;padding:0.5rem;margin-top:0.25rem;">
          <p style="font-size:0.7rem;color:var(--text-dim);margin:0.25rem 0 0 0;">Your API key is stored locally and never sent to external servers.</p>
        </div>

        <!-- Save Button -->
        <button onclick="saveModelConfig()" style="margin-top:0.5rem;background:var(--core);color:#fff;border:none;padding:0.5rem 1rem;border-radius:4px;cursor:pointer;">💾 Save Model Config</button>
        <span id="model-config-status" style="margin-left:0.5rem;font-size:0.8rem;"></span>
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
</div>

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

<div class="save-toast" id="save-toast">✓ SOUL.md saved</div>
<div class="save-toast error-toast" id="error-toast" style="background:rgba(224,80,80,0.15);border-color:var(--core-border);color:var(--core);">Save failed</div>

<script>
const DATA = {data_json};

const SECTION_COLORS = {{
  'Personality': '#f0a050',
  'Philosophy': '#7c6ff0',
  'Boundaries': '#e05050',
  'Continuity': '#50b8e0',
}};
function sectionColor(name) {{
  for (const [k, v] of Object.entries(SECTION_COLORS)) {{
    if (name && name.includes(k)) return v;
  }}
  return '#888';
}}

// --- Stats ---
function renderStats() {{
  const bar = document.getElementById('stats-bar');
  const tree = DATA.soul_tree;
  let core = 0, mutable = 0, totalBullets = 0;
  tree.forEach(sec => {{
    sec.children.forEach(child => {{
      if (child.type === 'bullet') {{
        totalBullets++;
        if (child.tag === 'CORE') core++;
        if (child.tag === 'MUTABLE') mutable++;
      }}
      if (child.children) child.children.forEach(b => {{
        if (b.type === 'bullet') {{
          totalBullets++;
          if (b.tag === 'CORE') core++;
          if (b.tag === 'MUTABLE') mutable++;
        }}
      }});
    }});
  }});
      const stats = [
        {{ num: DATA.experiences.length, label: 'Experiences' }},
        {{ num: DATA.reflections.length, label: 'Reflections' }},
        {{ num: (DATA.news?.browsing_history || []).length, label: 'Web Searches' }},
        {{ num: (DATA.news?.headlines || []).length, label: 'World News' }},
        {{ num: core, label: 'Core' }},
        {{ num: mutable, label: 'Mutable' }},
      ];
  
  bar.innerHTML = stats.map(s =>
    `<div class="stat"><div class="num">${{s.num}}</div><div class="label">${{s.label}}</div></div>`
  ).join('');
}}

// --- Legend ---
function renderLegend() {{
  const el = document.getElementById('legend');
  const items = [
    {{ color: 'var(--core)', label: 'CORE (immutable)' }},
    {{ color: 'var(--mutable)', label: 'MUTABLE (evolvable)' }},
    ...Object.entries(SECTION_COLORS).map(([k, v]) => ({{ color: v, label: k }})),
  ];
  el.innerHTML = items.map(i =>
    `<div class="legend-item"><div class="legend-dot" style="background:${{i.color}}"></div>${{i.label}}</div>`
  ).join('');
}}

// --- Soul Map ---
let allBulletEls = [];
let changesBulletMap = {{}};

let editMode = false;

function renderSoulTree(revealUpTo) {{
  const container = document.getElementById('soul-tree');
  container.innerHTML = '';
  allBulletEls = [];

  // Build set of bullets added by changes after revealUpTo
  const hiddenAfter = new Set();
  if (!editMode) {{
    const changes = DATA.changes;
    for (let i = changes.length - 1; i >= 0; i--) {{
      if (i >= revealUpTo) {{
        if (changes[i].change_type === 'add' && changes[i].after) {{
          hiddenAfter.add(changes[i].after.trim());
        }}
      }}
    }}
  }}

  DATA.soul_tree.forEach((sec, si) => {{
    const color = sectionColor(sec.text);
    const block = document.createElement('div');
    block.className = 'section-block';
    block.style.borderColor = color + '33';

    const header = document.createElement('div');
    header.className = 'section-header';
    header.style.background = color + '0d';
    header.innerHTML = `<div class="dot" style="background:${{color}}"></div>${{esc(sec.text)}}<span class="arrow">▼</span>`;
    header.onclick = () => block.classList.toggle('collapsed');
    block.appendChild(header);

    const body = document.createElement('div');
    body.className = 'section-body';

    sec.children.forEach((child, ci) => {{
      if (child.type === 'subsection') {{
        const sub = document.createElement('div');
        sub.className = 'subsection';
        sub.innerHTML = `<div class="subsection-title">${{esc(child.text)}}</div>`;

        (child.children || []).forEach((b, bi) => {{
          const bEl = renderBullet(b, hiddenAfter, [si, ci, bi]);
          sub.appendChild(bEl);
        }});

        // Add bullet button
        const addBtn = document.createElement('button');
        addBtn.className = 'btn-add-bullet';
        addBtn.textContent = '+ add bullet';
        addBtn.onclick = () => addBullet(si, ci);
        sub.appendChild(addBtn);

        body.appendChild(sub);
      }} else if (child.type === 'bullet') {{
        body.appendChild(renderBullet(child, hiddenAfter, [si, ci, -1]));
      }}
    }});

    block.appendChild(body);
    container.appendChild(block);

    setTimeout(() => block.classList.add('visible'), 80 * si);
  }});
}}

function renderBullet(b, hiddenAfter, path) {{
  const el = document.createElement('div');
  el.className = 'bullet';
  const isHidden = hiddenAfter.has(b.raw.trim());
  if (isHidden) {{
    el.classList.add('is-new');
  }}

  const tagClass = b.tag === 'CORE' ? 'core' : (b.tag === 'MUTABLE' ? 'mutable' : '');

  if (editMode) {{
    el.classList.add('editing');
    const [si, ci, bi] = path;

    // Tag toggle
    const tagEl = document.createElement('span');
    tagEl.className = `tag ${{tagClass}} tag-toggle`;
    tagEl.textContent = b.tag || 'TAG';
    tagEl.title = 'Click to toggle CORE/MUTABLE';
    tagEl.onclick = () => {{
      const next = b.tag === 'CORE' ? 'MUTABLE' : 'CORE';
      b.tag = next;
      updateBulletRaw(b);
      renderSoulTree(currentStep);
    }};
    el.appendChild(tagEl);

    // Editable text
    const input = document.createElement('textarea');
    input.className = 'edit-text';
    input.value = b.text;
    input.rows = 1;
    input.oninput = () => {{
      input.style.height = 'auto';
      input.style.height = input.scrollHeight + 'px';
      b.text = input.value;
      updateBulletRaw(b);
    }};
    // Auto-resize on mount
    setTimeout(() => {{ input.style.height = input.scrollHeight + 'px'; }}, 0);
    el.appendChild(input);

    // Delete button
    const del = document.createElement('button');
    del.className = 'btn-delete';
    del.innerHTML = '×';
    del.title = 'Remove bullet';
    del.onclick = () => {{
      deleteBullet(si, ci, bi);
    }};
    el.appendChild(del);
  }} else {{
    el.innerHTML = `
      ${{tagClass ? `<span class="tag ${{tagClass}}">${{esc(b.tag)}}</span>` : ''}}
      <span>${{esc(b.text)}}</span>
    `;
  }}

  allBulletEls.push({{ el, raw: b.raw, tag: b.tag }});
  return el;
}}

function updateBulletRaw(b) {{
  b.raw = `- ${{b.text}} [${{b.tag}}]`;
}}

function toggleEditMode() {{
  editMode = !editMode;
  const btn = document.getElementById('btn-edit');
  const saveBtn = document.getElementById('btn-save');
  const mapEl = document.getElementById('soul-map');

  if (editMode) {{
    btn.classList.add('active');
    btn.textContent = '✎ Editing';
    saveBtn.style.display = '';
    mapEl.classList.add('edit-mode');
  }} else {{
    btn.classList.remove('active');
    btn.textContent = '✎ Edit';
    saveBtn.style.display = 'none';
    mapEl.classList.remove('edit-mode');
  }}
  renderSoulTree(currentStep);
}}

function addBullet(si, ci) {{
  const sub = DATA.soul_tree[si].children[ci];
  if (!sub.children) sub.children = [];
  const sec = DATA.soul_tree[si];
  const newBullet = {{
    type: 'bullet',
    text: 'New belief',
    raw: '- New belief [MUTABLE]',
    tag: 'MUTABLE',
    section: sec.raw,
    subsection: sub.raw,
  }};
  sub.children.push(newBullet);
  renderSoulTree(currentStep);
}}

function deleteBullet(si, ci, bi) {{
  if (bi >= 0) {{
    DATA.soul_tree[si].children[ci].children.splice(bi, 1);
  }} else {{
    DATA.soul_tree[si].children.splice(ci, 1);
  }}
  renderSoulTree(currentStep);
}}

function reconstructSoulMd() {{
  let lines = [];
  lines.push('# SOUL.md - Who You Are');
  lines.push('');
  lines.push('> ⚠️ This file is managed by **Soul Evolution**. Bullets tagged `[CORE]` are immutable.');
  lines.push('> Bullets tagged `[MUTABLE]` may evolve through the structured proposal pipeline.');
  lines.push('> Direct edits outside the pipeline are not permitted for `[MUTABLE]` items.');
  lines.push('> See `soul-evolution/SKILL.md` for the full protocol.');
  lines.push('');
  lines.push('---');

  DATA.soul_tree.forEach(sec => {{
    lines.push('');
    lines.push(`## ${{sec.text}}`);

    sec.children.forEach(child => {{
      if (child.type === 'subsection') {{
        lines.push('');
        lines.push(`### ${{child.text}}`);
        lines.push('');
        (child.children || []).forEach(b => {{
          lines.push(`- ${{b.text}} [${{b.tag}}]`);
        }});
      }} else if (child.type === 'bullet') {{
        lines.push(`- ${{child.text}} [${{child.tag}}]`);
      }}
    }});
  }});

  lines.push('');
  lines.push('---');
  lines.push('');
  lines.push('_This file is yours to evolve. As you learn who you are, update it._');
  return lines.join('\\n');
}}

function saveSoul() {{
  const content = reconstructSoulMd();
  const toast = document.getElementById('save-toast');

  // Try server-side save first (works in --serve mode)
  fetch('/save-soul', {{
    method: 'POST',
    headers: {{ 'Content-Type': 'text/markdown' }},
    body: content
  }})
  .then(resp => {{
    if (resp.ok) {{
      toast.textContent = '✓ SOUL.md saved to workspace';
      toast.classList.add('show');
      setTimeout(() => toast.classList.remove('show'), 2500);
    }} else {{
      throw new Error('Server save failed');
    }}
  }})
  .catch(() => {{
    // Fallback: browser download (static HTML mode)
    const blob = new Blob([content], {{ type: 'text/markdown' }});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'SOUL.md';
    a.click();
    URL.revokeObjectURL(url);
    toast.textContent = '✓ SOUL.md downloaded';
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 2500);
  }});
}}

// --- Timeline ---
let currentStep = -1;
let playing = false;
let playInterval = null;

function renderTimeline() {{
  const changes = DATA.changes;
  const slider = document.getElementById('timeline-slider');
  slider.max = changes.length;
  slider.value = changes.length;
  currentStep = changes.length;

  slider.oninput = () => {{
    currentStep = parseInt(slider.value);
    updateTimelineView();
  }};

  updateTimelineView();
}}

function updateTimelineView() {{
  const changes = DATA.changes;
  const label = document.getElementById('timeline-label');

  if (currentStep === 0) {{
    label.textContent = 'origin';
  }} else if (currentStep <= changes.length) {{
    const c = changes[currentStep - 1];
    const t = c.timestamp || '';
    label.textContent = t.slice(11, 16) || `#${{currentStep}}`;
  }}

  // Re-render soul map with visibility
  renderSoulTree(currentStep);

  // Re-render changes list
  renderChangesList(currentStep);

  // Update slider
  document.getElementById('timeline-slider').value = currentStep;
}}

function renderChangesList(upTo) {{
  const container = document.getElementById('changes-list');
  const changes = DATA.changes;

  if (changes.length === 0) {{
    container.innerHTML = '<div class="empty-state">No soul changes yet. The soul is in its original state.</div>';
    return;
  }}

  container.innerHTML = '';
  const visible = changes.slice(0, upTo);
  visible.forEach((c, i) => {{
    const el = document.createElement('div');
    el.className = 'change-entry';

    const t = c.timestamp || '';
    const time = t.slice(0, 16).replace('T', ' ');
    const section = (c.section || '').replace('## ', '') + ' › ' + (c.subsection || '').replace('### ', '');
    const content = c.after || c.before || '';
    const cleanContent = content.replace(/\\s*\\[(CORE|MUTABLE)\\]\\s*/g, '').replace(/^- /, '');

    el.innerHTML = `
      <div class="change-time">${{esc(time)}}</div>
      <span class="change-type ${{esc(c.change_type)}}">${{esc(c.change_type)}}</span>
      <div class="change-section">${{esc(section)}}</div>
      <div class="change-content">${{esc(cleanContent)}}</div>
    `;

    container.appendChild(el);
    setTimeout(() => el.classList.add('visible'), 60 * i);
  }});

  if (upTo === 0) {{
    container.innerHTML = '<div class="empty-state">⟲ Origin state — no changes applied yet</div>';
  }}
}}

// --- Play / Reset ---
document.getElementById('btn-play').onclick = () => {{
  if (playing) {{
    clearInterval(playInterval);
    playing = false;
    document.getElementById('btn-play').textContent = '▶';
    document.getElementById('btn-play').classList.remove('active');
    return;
  }}
  playing = true;
  document.getElementById('btn-play').textContent = '⏸';
  document.getElementById('btn-play').classList.add('active');
  currentStep = 0;
  updateTimelineView();

  playInterval = setInterval(() => {{
    currentStep++;
    if (currentStep > DATA.changes.length) {{
      clearInterval(playInterval);
      playing = false;
      document.getElementById('btn-play').textContent = '▶';
      document.getElementById('btn-play').classList.remove('active');
      return;
    }}
    updateTimelineView();
    // Highlight the newly revealed bullet
    const change = DATA.changes[currentStep - 1];
    if (change && change.after) {{
      const match = allBulletEls.find(b => b.raw.trim() === change.after.trim());
      if (match) {{
        match.el.classList.remove('is-new');
        match.el.classList.add('revealed');
        match.el.classList.add('highlight-enter');
        match.el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
      }}
    }}
  }}, 1800);
}};

document.getElementById('btn-reset').onclick = () => {{
  if (playing) {{
    clearInterval(playInterval);
    playing = false;
    document.getElementById('btn-play').textContent = '▶';
    document.getElementById('btn-play').classList.remove('active');
  }}
  currentStep = 0;
  updateTimelineView();
}};

// --- Experience Feed ---
function renderFeed() {{
  const container = document.getElementById('exp-feed');
  const exps = DATA.experiences.slice().reverse();

  if (exps.length === 0) {{
    container.innerHTML = '<div class="empty-state">No experiences logged yet.</div>';
    return;
  }}

  container.innerHTML = exps.map(e => {{
    const t = (e.timestamp || '').slice(11, 16);
    const sourceClass = (e.source || '').toLowerCase();
    const sigClass = (e.significance || '').toLowerCase();
    const content = (e.content || '').slice(0, 160) + ((e.content || '').length > 160 ? '…' : '');
    return `
      <div class="exp-entry">
        <div class="exp-meta">
          <span class="exp-source ${{esc(sourceClass)}}">${{esc(e.source)}}</span>
          <span class="exp-sig ${{esc(sigClass)}}">${{esc(e.significance)}}</span>
          <span style="margin-left:auto;font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:var(--text-dim)">${{esc(t)}}</span>
        </div>
        <div class="exp-content">${{esc(content)}}</div>
      </div>
    `;
  }}).join('');
}}

// --- Vitals Dashboard ---
function vitalColor(value, key) {{
  if (key === 'energy') {{
    if (value < 10) return '#e05050';
    if (value < 30) return '#f0a050';
    if (value < 60) return '#e0d050';
    return '#50c878';
  }}
  if (value > 90) return '#e05050';
  if (value > 70) return '#f0a050';
  if (value > 40) return '#e0d050';
  return '#50c878';
}}

  function renderVitals() {{
    const ph = DATA.physique;
    const grid = document.getElementById('vitals-grid');
    const meta = document.getElementById('vitals-meta');

    if (!ph || !ph.needs) {{
      grid.innerHTML = '<div class="empty-state">No vitals data available.</div>';
      return;
    }}

    const needKeys = ['energy', 'hunger', 'thirst', 'bladder', 'bowel', 'hygiene', 'stress', 'arousal'];
    grid.innerHTML = needKeys.map(k => {{
      const v = ph.needs[k] ?? 0;
      const color = vitalColor(v, k);
      return `
        <div class="vital-row">
          <span class="vital-label">${{k}}</span>
          <div class="vital-bar-bg">
            <div class="vital-bar" style="width:${{v}}%;background:${{color}}"></div>
          </div>
          <span class="vital-value">${{v}}</span>
        </div>
      `;
    }}).join('');

    const metaLines = [];
    if (ph.current_location) metaLines.push(`<span>📍 ${{esc(ph.current_location)}}</span>`);
    if (ph.current_outfit && ph.current_outfit.length) metaLines.push(`<span>👔 ${{esc(ph.current_outfit.join(', '))}}</span>`);
    if (ph.last_tick) metaLines.push(`<span>⏱ ${{esc(ph.last_tick.slice(0, 19).replace('T', ' '))}}</span>`);
    meta.innerHTML = metaLines.join('');
  }}

  // --- Mental Activity & Ticker ---
  function renderMentalActivity() {{
    const container = document.getElementById('mental-activity-list');
    const news = DATA.news || {{}};
    const comms = DATA.internal_comm || {{}};
    const refs = DATA.reflections || [];
    
    let html = '';

    // 1. Current Thought (from latest Limbic memo or Reflection)
    const latestMemo = (comms.memos || []).find(m => m.sender === 'limbic' && m.type === 'emotion');
    const latestRef = refs[refs.length - 1];
    
    if (latestMemo) {{
      html += `
        <div class="mental-card">
          <span class="mental-label">Inner Voice (Limbic)</span>
          <div class="mental-content">"${{esc(latestMemo.content)}}"</div>
          <span class="mental-sub">${{new Date(latestMemo.timestamp).toLocaleTimeString()}}</span>
        </div>
      `;
    }} else if (latestRef) {{
      html += `
        <div class="mental-card">
          <span class="mental-label">Current Reflection</span>
          <div class="mental-content">${{esc(latestRef.summary || latestRef.reflection_summary || '')}}</div>
        </div>
      `;
    }}

    // 2. Recent Web Research
    const history = news.browsing_history || [];
    if (history.length > 0) {{
      const last = history[0];
      let snapHtml = '';
      if (last.screenshot) {{
        // Extract filename from absolute path for media endpoint
        const filename = last.screenshot.split('/').pop();
        snapHtml = `<img src="/media/browser_snapshots/${{filename}}" class="browser-snap" onclick="window.open(this.src)">`;
      }}
      html += `
        <div class="mental-card" style="border-left-color: var(--growth);">
          <span class="mental-label">Web Research</span>
          <div class="mental-content">Searching for: <strong>${{esc(last.query)}}</strong></div>
          ${{snapHtml}}
          <span class="mental-sub">${{new Date(last.timestamp).toLocaleTimeString()}}</span>
        </div>
      `;
    }}

    if (!html) {{
      html = '<div class="empty-state">Observing cognitive processes...</div>';
    }}
    container.innerHTML = html;

    // Update Ticker
    const ticker = document.getElementById('ticker-content');
    const headlines = news.headlines || [];
    if (headlines.length > 0) {{
      ticker.innerHTML = headlines.map(h => `
        <div class="ticker-item">[${{h.category.toUpperCase()}}] ${{esc(h.title)}}</div>
      `).join('') + headlines.map(h => `
        <div class="ticker-item">[${{h.category.toUpperCase()}}] ${{esc(h.title)}}</div>
      `).join(''); // Duplicate for seamless loop
    }}

    // Update Status Text
    const statusText = document.getElementById('status-text');
    if (history.length > 0 && (new Date() - new Date(history[0].timestamp)) < 300000) {{
      statusText.textContent = 'Autonomous Web Research Active';
      statusText.style.color = 'var(--growth)';
    }} else if (latestMemo) {{
      statusText.textContent = 'Processing Internal Narrative';
      statusText.style.color = 'var(--accent)';
    }} else {{
      statusText.textContent = 'Cognitive System Synchronized';
      statusText.style.color = 'var(--text-dim)';
    }}
  }}
// --- Proposals ---
function renderProposals() {{
  const list = document.getElementById('proposals-list');
  const count = document.getElementById('proposals-count');
  const pending = DATA.proposals_pending || [];

  count.textContent = pending.length > 0 ? `(${{pending.length}})` : '';

  if (pending.length === 0) {{
    list.innerHTML = '<div class="empty-state">No pending proposals.</div>';
    return;
  }}

  list.innerHTML = pending.map((p, i) => {{
    const changeType = (p.change_type || p.type || 'modify').toLowerCase();
    return `
      <div class="proposal-card" id="proposal-${{i}}">
        <div class="proposal-header">
          <span class="proposal-id">${{esc(p.id || 'PROP-' + i)}}</span>
          <span class="proposal-type ${{esc(changeType)}}">${{esc(changeType)}}</span>
        </div>
        <div class="proposal-section">${{esc(p.section || '')}} ${{p.subsection ? '› ' + esc(p.subsection) : ''}}</div>
        <div class="proposal-content">${{esc(p.content || p.after || p.proposed || '')}}</div>
        <div class="proposal-reason">${{esc(p.reason || p.rationale || '')}}</div>
        <div class="proposal-actions">
          <button class="btn-approve" onclick="resolveProposal(${{i}}, 'approved')">Approve</button>
          <button class="btn-reject" onclick="resolveProposal(${{i}}, 'rejected')">Reject</button>
        </div>
      </div>
    `;
  }}).join('');
}}

function resolveProposal(index, decision) {{
  fetch('/resolve-proposal', {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }},
    body: JSON.stringify({{ index, decision }})
  }})
  .then(r => {{
    if (r.ok) {{
      const card = document.getElementById('proposal-' + index);
      if (card) card.style.display = 'none';
      const toast = document.getElementById('save-toast');
      toast.textContent = '✓ Proposal ' + decision;
      toast.classList.add('show');
      setTimeout(() => toast.classList.remove('show'), 2500);
    }} else {{
      alert('Failed to resolve proposal. Is server running?');
    }}
  }})
  .catch(() => alert('Server not reachable. Proposals can only be resolved in --serve mode.'));
}}

// --- Reflections ---
function renderReflections() {{
  const list = document.getElementById('reflections-list');
  const refs = (DATA.reflections || []).slice().reverse();

  if (refs.length === 0) {{
    list.innerHTML = '<div class="empty-state">No reflections yet.</div>';
    return;
  }}

  list.innerHTML = refs.slice(0, 20).map((r, i) => {{
    const summary = r.summary || r.reflection_summary || '';
    const insights = r.insights || r.key_insights || [];
    const refType = r.type || r.reflection_type || 'batch';
    const proposalDecision = r.proposal_decision || r.proposals_generated || '';
    return `
      <div class="reflection-card collapsed">
        <div class="reflection-header" onclick="this.parentElement.classList.toggle('collapsed')">
          <span class="ref-type">${{esc(refType)}}</span>
          <span style="color:var(--text);flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${{esc(summary.slice(0, 80))}}</span>
          <span class="ref-arrow">▼</span>
        </div>
        <div class="reflection-body">
          <div>${{esc(summary)}}</div>
          ${{insights.length > 0 ? '<ul class="ref-insights">' + insights.map(ins => '<li>' + esc(typeof ins === 'string' ? ins : (ins.insight || JSON.stringify(ins))) + '</li>').join('') + '</ul>' : ''}}
          ${{proposalDecision ? '<div style="margin-top:0.4rem;font-size:0.68rem;color:var(--accent)">Proposals: ' + esc(String(proposalDecision)) + '</div>' : ''}}
        </div>
      </div>
    `;
  }}).join('');
}}

// --- Significant Memories ---
function renderSignificant() {{
  const list = document.getElementById('significant-list');
  const sigs = (DATA.significant || []).slice().reverse();

  if (sigs.length === 0) {{
    list.innerHTML = '<div class="empty-state">No significant memories yet.</div>';
    return;
  }}

  list.innerHTML = sigs.map(s => {{
    const sig = s.significance || 'notable';
    const content = s.content || s.summary || '';
    const context = s.context || s.significance_reason || '';
    return `
      <div class="sig-entry">
        <div class="exp-meta">
          <span class="sig-badge">${{esc(sig)}}</span>
          <span style="font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:var(--text-dim)">${{esc(s.id || '')}}</span>
          <span style="margin-left:auto;font-family:'JetBrains Mono',monospace;font-size:0.6rem;color:var(--text-dim)">${{esc((s.timestamp || '').slice(0, 16).replace('T', ' '))}}</span>
        </div>
        <div class="sig-content">${{esc(content.slice(0, 200))}}</div>
        ${{context ? '<div class="sig-context">' + esc(context) + '</div>' : ''}}
      </div>
    `;
  }}).join('');
}}

// --- Pipeline State ---
function renderPipelineState() {{
  const cards = document.getElementById('state-cards');
  const runs = document.getElementById('pipeline-runs');
  const state = DATA.state || {{}};
  const pipeline = DATA.pipeline || [];

  const stateEntries = Object.entries(state);
  if (stateEntries.length === 0 && pipeline.length === 0) {{
    cards.innerHTML = '<div class="empty-state" style="grid-column:1/-1">No pipeline state yet.</div>';
    return;
  }}

  cards.innerHTML = stateEntries.map(([k, v]) => {{
    const display = typeof v === 'object' ? JSON.stringify(v) : String(v);
    return `
      <div class="state-card">
        <div class="sc-value">${{esc(display.length > 12 ? display.slice(0, 12) + '…' : display)}}</div>
        <div class="sc-label">${{esc(k.replace(/_/g, ' '))}}</div>
      </div>
    `;
  }}).join('');

  if (pipeline.length > 0) {{
    runs.innerHTML = '<div style="font-family:\'JetBrains Mono\',monospace;font-size:0.7rem;color:var(--text-dim);margin-bottom:0.5rem;text-transform:uppercase;letter-spacing:0.08em">Recent Runs</div>' +
      pipeline.slice(-10).reverse().map(p => {{
        const ts = (p.timestamp || p.completed_at || '').slice(0, 16).replace('T', ' ');
        const status = p.status || p.result || 'done';
        return `<div class="pipeline-run">${{esc(ts)}} — ${{esc(status)}}</div>`;
      }}).join('');
  }}
}}

// --- Init ---
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
  setInterval(() => {{
    if (document.getElementById('tab-dashboard').classList.contains('active')) {{
      location.reload();
    }}
  }}, 30000);
// ---------------------------------------------------------------------------
// Tab Navigation
// ---------------------------------------------------------------------------
function switchTab(tabId) {{
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  const el = document.getElementById('tab-' + tabId);
  if (el) el.classList.add('active');
  document.querySelectorAll('.tab-btn').forEach(b => {{
    if (b.textContent.toLowerCase().trim() === tabId) b.classList.add('active');
  }});
  if (tabId === 'interior' && !window._interiorRendered) {{ renderInterior(); window._interiorRendered = true; }}
  if (tabId === 'inventory' && !window._inventoryRendered) {{ renderInventoryPanel(); window._inventoryRendered = true; }}
  if (tabId === 'wardrobe' && !window._wardrobeRendered) {{ renderWardrobePanel(); window._wardrobeRendered = true; }}
  if (tabId === 'development' && !window._devRendered) {{ renderDevPanel(); window._devRendered = true; }}
  if (tabId === 'cycle' && !window._cycleRendered) {{ renderCyclePanel(); window._cycleRendered = true; }}
  if (tabId === 'world' && !window._worldRendered) {{ renderWorldPanel(); window._worldRendered = true; }}
  if (tabId === 'skills' && !window._skillsRendered) {{ renderSkillsPanel(); window._skillsRendered = true; }}
  if (tabId === 'psychology' && !window._psychRendered) {{ renderPsychPanel(); window._psychRendered = true; }}
  if (tabId === 'reputation' && !window._repRendered) {{ renderReputationPanel(); window._repRendered = true; }}
  if (tabId === 'genesis' && !window._genesisRendered) {{ window._genesisRendered = true; loadGenesisStatus(); }}
}}

// ---------------------------------------------------------------------------
// Toast helpers
// ---------------------------------------------------------------------------
function showToast(msg, isError) {{
  const id = isError ? 'error-toast' : 'save-toast';
  const el = document.getElementById(id);
  el.textContent = msg || (isError ? 'Save failed' : 'Saved');
  el.classList.add('show');
  setTimeout(() => el.classList.remove('show'), 2500);
}}

// ---------------------------------------------------------------------------
// Modal system (replaces prompt())
// ---------------------------------------------------------------------------
let _modalResolve = null;

function openModal(title, fields) {{
  return new Promise(resolve => {{
    _modalResolve = resolve;
    document.getElementById('modal-title').textContent = title;
    const container = document.getElementById('modal-fields');
    container.innerHTML = fields.map(f => {{
      if (f.type === 'select') {{
        const opts = f.options.map(o => `<option value="${{o}}">${{o}}</option>`).join('');
        return `<div class="modal-field"><label>${{f.label}}</label><select id="mf-${{f.key}}">${{opts}}</select></div>`;
      }}
      return `<div class="modal-field"><label>${{f.label}}</label><input id="mf-${{f.key}}" type="${{f.type||'text'}}" value="${{f.default||''}}" placeholder="${{f.placeholder||''}}"></div>`;
    }}).join('');
    document.getElementById('modal-ok').onclick = () => {{
      const result = {{}};
      fields.forEach(f => {{ result[f.key] = document.getElementById('mf-' + f.key).value; }});
      closeModal();
      resolve(result);
    }};
    document.getElementById('modal-overlay').classList.add('open');
    // Focus first field
    const first = container.querySelector('input, select');
    if (first) setTimeout(() => first.focus(), 100);
  }});
}}

function closeModal() {{
  document.getElementById('modal-overlay').classList.remove('open');
  if (_modalResolve) {{ _modalResolve(null); _modalResolve = null; }}
}}

// ---------------------------------------------------------------------------
// Lightbox
// ---------------------------------------------------------------------------
let _lightboxCtx = {{ category: '', itemId: '', images: [], currentIdx: 0 }};

function openLightbox(category, itemId, images, startIdx) {{
  _lightboxCtx = {{ category, itemId, images: images || [], currentIdx: startIdx || 0 }};
  document.getElementById('lightbox').classList.add('open');
  renderLightbox();
}}

function closeLightbox() {{
  document.getElementById('lightbox').classList.remove('open');
}}

// Escape key closes lightbox and modal
document.addEventListener('keydown', e => {{
  if (e.key === 'Escape') {{
    if (document.getElementById('lightbox').classList.contains('open')) closeLightbox();
    else if (document.getElementById('modal-overlay').classList.contains('open')) closeModal();
  }}
}});

function renderLightbox() {{
  const main = document.getElementById('lightbox-main');
  const gallery = document.getElementById('lightbox-gallery');
  if (_lightboxCtx.images.length === 0) {{
    main.src = '';
    main.alt = 'No images';
    gallery.innerHTML = '<span style="color:var(--text-dim);font-size:0.8rem;">No images yet — drop an image or click Upload</span>';
    return;
  }}
  const current = _lightboxCtx.images[_lightboxCtx.currentIdx] || _lightboxCtx.images[0];
  main.src = '/' + current;
  gallery.innerHTML = _lightboxCtx.images.map((img, i) =>
    `<img src="/${{img}}" class="${{i === _lightboxCtx.currentIdx ? 'active' : ''}}" onclick="_lightboxCtx.currentIdx=${{i}};renderLightbox();">`
  ).join('');
}}

function doUpload(file) {{
  if (!file || !file.type.startsWith('image/')) return;
  const reader = new FileReader();
  reader.onload = function(e) {{
    const b64 = e.target.result.split(',')[1];
    fetch('/upload-image', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{
        category: _lightboxCtx.category,
        item_id: _lightboxCtx.itemId,
        filename: file.name,
        data: b64,
      }})
    }}).then(r => r.json()).then(res => {{
      _lightboxCtx.images.push(res.path);
      _lightboxCtx.currentIdx = _lightboxCtx.images.length - 1;
      renderLightbox();
      refreshPanel(_lightboxCtx.category);
      showToast('Image uploaded');
    }}).catch(err => showToast('Upload failed: ' + err, true));
  }};
  reader.readAsDataURL(file);
}}

function uploadLightboxImage(event) {{
  doUpload(event.target.files[0]);
  event.target.value = '';
}}

// Drag-and-drop on lightbox dropzone
(function() {{
  const dz = document.getElementById('lightbox-dropzone');
  if (!dz) return;
  dz.addEventListener('dragover', e => {{ e.preventDefault(); dz.classList.add('dragover'); }});
  dz.addEventListener('dragleave', () => dz.classList.remove('dragover'));
  dz.addEventListener('drop', e => {{
    e.preventDefault();
    dz.classList.remove('dragover');
    if (e.dataTransfer.files.length > 0) doUpload(e.dataTransfer.files[0]);
  }});
}})();

function deleteLightboxImage() {{
  if (_lightboxCtx.images.length === 0) return;
  const path = _lightboxCtx.images[_lightboxCtx.currentIdx];
  if (!confirm('Delete this image?')) return;
  fetch('/delete-image', {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }},
    body: JSON.stringify({{ category: _lightboxCtx.category, item_id: _lightboxCtx.itemId, path: path }})
  }}).then(() => {{
    _lightboxCtx.images.splice(_lightboxCtx.currentIdx, 1);
    if (_lightboxCtx.currentIdx >= _lightboxCtx.images.length) _lightboxCtx.currentIdx = Math.max(0, _lightboxCtx.images.length - 1);
    renderLightbox();
    refreshPanel(_lightboxCtx.category);
    showToast('Image deleted');
  }}).catch(err => showToast('Delete failed: ' + err, true));
}}

function refreshPanel(category) {{
  if (category === 'interior') {{ window._interiorRendered = false; renderInterior(); window._interiorRendered = true; }}
  if (category === 'inventory') {{ window._inventoryRendered = false; renderInventoryPanel(); window._inventoryRendered = true; }}
  if (category === 'wardrobe') {{ window._wardrobeRendered = false; renderWardrobePanel(); window._wardrobeRendered = true; }}
}}

// Delete all images for an item (orphan cleanup)
function deleteAllImages(category, itemId, images) {{
  if (!images || images.length === 0) return Promise.resolve();
  return Promise.all(images.map(path =>
    fetch('/delete-image', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{ category, item_id: itemId, path }})
    }}).catch(() => {{}})
  ));
}}

// ---------------------------------------------------------------------------
// Interior Panel
// ---------------------------------------------------------------------------
let _currentRoom = null;

function renderInterior() {{
  const interior = DATA.interior || {{ rooms: [] }};
  const tabsEl = document.getElementById('room-tabs');
  const gridEl = document.getElementById('interior-grid');
  const detailEl = document.getElementById('interior-detail');

  if (interior.rooms.length === 0) {{
    tabsEl.innerHTML = '';
    gridEl.innerHTML = '<div style="color:var(--text-dim);font-size:0.85rem;">No rooms yet. Add one to get started.</div>';
    detailEl.innerHTML = '';
    return;
  }}

  if (!_currentRoom || !interior.rooms.find(r => r.id === _currentRoom)) {{
    _currentRoom = interior.rooms[0].id;
  }}

  tabsEl.innerHTML = interior.rooms.map(r => {{
    const cnt = r.objects ? r.objects.length : 0;
    return `<button class="room-tab ${{r.id === _currentRoom ? 'active' : ''}}" onclick="_currentRoom='${{esc(r.id)}}';renderInterior();">${{esc(r.name)}} (${{cnt}})</button>`;
  }}).join('') + `<button class="room-tab" style="color:var(--core);" onclick="removeRoom('${{esc(_currentRoom)}}')">- Remove</button>`;

  const room = interior.rooms.find(r => r.id === _currentRoom);
  if (!room) return;

  detailEl.innerHTML = `<div style="font-size:0.8rem;color:var(--text-dim);margin-bottom:0.5rem;">${{esc(room.description || '')}}</div>
    <button class="btn-crud" onclick="addObject('${{esc(room.id)}}')">+ Object</button>`;

  const topLevel = room.objects.filter(o => !o.located_on);
  gridEl.innerHTML = topLevel.map(obj => {{
    const thumb = obj.images && obj.images.length > 0
      ? `<img src="/${{obj.images[0]}}" alt="${{esc(obj.name)}}">`
      : getCategoryIcon(obj.category);
    const subs = (obj.items_on || []).map(id => room.objects.find(o => o.id === id)).filter(Boolean);
    const subHtml = subs.length > 0
      ? `<div style="font-size:0.65rem;color:var(--text-dim);margin-top:0.3rem;">Items: ${{subs.map(s => esc(s.name)).join(', ')}}</div>`
      : '';
    return `<div class="item-card" onclick="openLightbox('interior','${{esc(obj.id)}}',${{JSON.stringify(obj.images||[])}},0)">
      <div class="thumb">${{thumb}}</div>
      <div class="card-name">${{esc(obj.name)}}</div>
      <div class="card-meta">${{esc(obj.category)}}${{subHtml}}</div>
      <div style="margin-top:0.4rem;display:flex;gap:0.3rem;">
        <button class="btn-crud danger" onclick="event.stopPropagation();removeObject('${{esc(room.id)}}','${{esc(obj.id)}}')">Remove</button>
      </div>
    </div>`;
  }}).join('');
}}

function esc(s) {{ const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }}

function getCategoryIcon(cat) {{
  const icons = {{ furniture: '🪑', electronics: '💻', decoration: '🎨', storage: '📦' }};
  return icons[cat] || '📦';
}}

async function addRoom() {{
  const result = await openModal('Add Room', [
    {{ key: 'name', label: 'Room Name', placeholder: 'e.g. Living Room' }},
    {{ key: 'desc', label: 'Description (optional)', placeholder: '' }},
  ]);
  if (!result || !result.name) return;
  const interior = DATA.interior || {{ rooms: [] }};
  const newRoom = {{ id: 'room_' + Date.now().toString(36), name: result.name, description: result.desc || '', objects: [] }};
  interior.rooms.push(newRoom);
  DATA.interior = interior;
  _currentRoom = newRoom.id;
  saveInterior();
  renderInterior();
}}

function removeRoom(roomId) {{
  if (!confirm('Remove this room and all its objects?')) return;
  const interior = DATA.interior || {{ rooms: [] }};
  const room = interior.rooms.find(r => r.id === roomId);
  // Cleanup orphaned images
  if (room) {{
    for (const obj of room.objects) {{
      deleteAllImages('interior', obj.id, obj.images);
    }}
  }}
  interior.rooms = interior.rooms.filter(r => r.id !== roomId);
  DATA.interior = interior;
  _currentRoom = null;
  saveInterior();
  renderInterior();
}}

async function addObject(roomId) {{
  const result = await openModal('Add Object', [
    {{ key: 'name', label: 'Object Name', placeholder: 'e.g. Desk' }},
    {{ key: 'category', label: 'Category', type: 'select', options: ['furniture', 'electronics', 'decoration', 'storage', 'other'] }},
    {{ key: 'desc', label: 'Description (optional)', placeholder: '' }},
  ]);
  if (!result || !result.name) return;
  const interior = DATA.interior || {{ rooms: [] }};
  const room = interior.rooms.find(r => r.id === roomId);
  if (!room) return;
  room.objects.push({{
    id: 'obj_' + Date.now().toString(36),
    name: result.name, category: result.category || 'other', description: result.desc || '',
    images: [], added_at: new Date().toISOString()
  }});
  DATA.interior = interior;
  saveInterior();
  renderInterior();
}}

function removeObject(roomId, objId) {{
  if (!confirm('Remove this object?')) return;
  const interior = DATA.interior || {{ rooms: [] }};
  const room = interior.rooms.find(r => r.id === roomId);
  if (!room) return;
  // Cleanup orphaned images
  const obj = room.objects.find(o => o.id === objId);
  if (obj) deleteAllImages('interior', objId, obj.images);
  room.objects = room.objects.filter(o => o.id !== objId);
  DATA.interior = interior;
  saveInterior();
  renderInterior();
}}

function saveInterior() {{
  fetch('/update-interior', {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }},
    body: JSON.stringify(DATA.interior)
  }}).then(r => {{
    if (!r.ok) throw new Error('HTTP ' + r.status);
    showToast('Interior saved');
  }}).catch(err => showToast('Save failed: ' + err, true));
}}

// ---------------------------------------------------------------------------
// Inventory Panel
// ---------------------------------------------------------------------------
let _invCategoryFilter = 'all';

function renderInventoryPanel() {{
  const inv = DATA.inventory || {{ items: [], categories: [] }};
  const chipsEl = document.getElementById('inv-chips');

  const cats = ['all', ...(inv.categories || [])];
  const countMap = {{}};
  (inv.items || []).forEach(i => {{ countMap[i.category] = (countMap[i.category] || 0) + 1; }});
  const totalCount = (inv.items || []).length;

  chipsEl.innerHTML = cats.map(c => {{
    const cnt = c === 'all' ? totalCount : (countMap[c] || 0);
    return `<button class="chip ${{c === _invCategoryFilter ? 'active' : ''}}" onclick="_invCategoryFilter='${{c}}';renderInventoryPanel();">${{c}} (${{cnt}})</button>`;
  }}).join('') + `<button class="btn-crud" style="margin-left:auto;" onclick="addInventoryItem()">+ Item</button>`;

  filterInventory();
}}

function filterInventory() {{
  const inv = DATA.inventory || {{ items: [], categories: [] }};
  const query = (document.getElementById('inv-search')?.value || '').toLowerCase();
  const gridEl = document.getElementById('inventory-grid');

  let items = inv.items || [];
  if (_invCategoryFilter !== 'all') items = items.filter(i => i.category === _invCategoryFilter);
  if (query) items = items.filter(i =>
    i.name.toLowerCase().includes(query) ||
    (i.description || '').toLowerCase().includes(query) ||
    (i.tags || []).some(t => t.toLowerCase().includes(query))
  );

  if (items.length === 0) {{
    gridEl.innerHTML = '<div style="color:var(--text-dim);font-size:0.85rem;">No items found.</div>';
    return;
  }}

  gridEl.innerHTML = items.map(item => {{
    const thumb = item.images && item.images.length > 0
      ? `<img src="/${{item.images[0]}}" alt="${{esc(item.name)}}">`
      : '📦';
    const locBadge = item.location ? `<span style="font-size:0.6rem;background:var(--accent-glow);padding:0.1rem 0.4rem;border-radius:8px;color:var(--accent);">@ ${{esc(item.location)}}</span>` : '';
    const tags = (item.tags || []).map(t => `<span style="font-size:0.55rem;background:var(--bg);padding:0.1rem 0.3rem;border-radius:4px;color:var(--text-dim);">${{esc(t)}}</span>`).join(' ');
    return `<div class="item-card" onclick="openLightbox('inventory','${{item.id}}',${{JSON.stringify(item.images||[])}},0)">
      <div class="thumb">${{thumb}}</div>
      <div class="card-name">${{esc(item.name)}}</div>
      <div class="card-meta">x${{item.quantity}} [${{esc(item.category)}}] ${{locBadge}}</div>
      <div style="margin-top:0.2rem;">${{tags}}</div>
      <div style="margin-top:0.4rem;display:flex;gap:0.3rem;">
        <button class="btn-crud danger" onclick="event.stopPropagation();removeInventoryItem('${{item.id}}')">Remove</button>
      </div>
    </div>`;
  }}).join('');
}}

async function addInventoryItem() {{
  const result = await openModal('Add Item', [
    {{ key: 'name', label: 'Item Name', placeholder: 'e.g. USB Cable' }},
    {{ key: 'category', label: 'Category', placeholder: 'e.g. electronics' }},
    {{ key: 'qty', label: 'Quantity', type: 'number', default: '1' }},
  ]);
  if (!result || !result.name) return;
  const inv = DATA.inventory || {{ items: [], categories: [] }};
  const qty = parseInt(result.qty, 10) || 1;
  const category = result.category || 'other';
  inv.items.push({{
    id: 'inv_' + Date.now().toString(36),
    name: result.name, category, description: '',
    quantity: qty, images: [], tags: [],
    added_at: new Date().toISOString()
  }});
  if (!inv.categories.includes(category)) inv.categories.push(category);
  DATA.inventory = inv;
  saveInventory();
  renderInventoryPanel();
}}

function removeInventoryItem(itemId) {{
  if (!confirm('Remove this item?')) return;
  const inv = DATA.inventory || {{ items: [], categories: [] }};
  // Cleanup orphaned images
  const item = inv.items.find(i => i.id === itemId);
  if (item) deleteAllImages('inventory', itemId, item.images);
  inv.items = inv.items.filter(i => i.id !== itemId);
  DATA.inventory = inv;
  saveInventory();
  renderInventoryPanel();
}}

function saveInventory() {{
  fetch('/update-inventory', {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }},
    body: JSON.stringify(DATA.inventory)
  }}).then(r => {{
    if (!r.ok) throw new Error('HTTP ' + r.status);
    showToast('Inventory saved');
  }}).catch(err => showToast('Save failed: ' + err, true));
}}

// ---------------------------------------------------------------------------
// Wardrobe Panel
// ---------------------------------------------------------------------------
let _wardrobeCatFilter = 'all';

function renderWardrobePanel() {{
  const wd = DATA.wardrobe || {{ inventory: {{}}, outfits: {{}} }};
  const chipsEl = document.getElementById('wardrobe-chips');
  const gridEl = document.getElementById('wardrobe-grid');
  const outfitsEl = document.getElementById('wardrobe-outfits');

  const cats = Object.keys(wd.inventory || {{}});
  const totalCount = cats.reduce((sum, c) => sum + (wd.inventory[c] || []).length, 0);
  chipsEl.innerHTML = ['all', ...cats].map(c => {{
    const cnt = c === 'all' ? totalCount : (wd.inventory[c] || []).length;
    return `<button class="chip ${{c === _wardrobeCatFilter ? 'active' : ''}}" onclick="_wardrobeCatFilter='${{c}}';renderWardrobePanel();">${{c}} (${{cnt}})</button>`;
  }}).join('');

  let allItems = [];
  for (const [cat, items] of Object.entries(wd.inventory || {{}})) {{
    if (_wardrobeCatFilter !== 'all' && cat !== _wardrobeCatFilter) continue;
    for (const item of items) {{
      if (typeof item === 'object') {{
        allItems.push({{ ...item, _cat: cat }});
      }}
    }}
  }}

  if (allItems.length === 0) {{
    gridEl.innerHTML = '<div style="color:var(--text-dim);font-size:0.85rem;">No items in wardrobe.</div>';
  }} else {{
    gridEl.innerHTML = allItems.map(item => {{
      const thumb = item.images && item.images.length > 0
        ? `<img src="/${{item.images[0]}}" alt="${{esc(item.name)}}">`
        : '👕';
      return `<div class="item-card" onclick="openLightbox('wardrobe','${{item.id}}',${{JSON.stringify(item.images||[])}},0)">
        <div class="thumb">${{thumb}}</div>
        <div class="card-name">${{esc(item.name)}}</div>
        <div class="card-meta">${{esc(item._cat)}}</div>
      </div>`;
    }}).join('');
  }}

  // Outfits section
  const outfits = wd.outfits || {{}};
  const outfitKeys = Object.keys(outfits);
  if (outfitKeys.length > 0) {{
    outfitsEl.innerHTML = '<h3 style="font-family:JetBrains Mono,monospace;font-size:0.75rem;color:var(--text-dim);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.5rem;">Outfits</h3>' +
      outfitKeys.map(name =>
        `<div style="padding:0.5rem;background:var(--bg-hover);border:1px solid var(--border);border-radius:8px;margin-bottom:0.5rem;">
          <strong style="color:var(--text-bright);font-size:0.8rem;">${{esc(name)}}</strong>
          <div style="font-size:0.72rem;color:var(--text-dim);margin-top:0.2rem;">${{outfits[name].map(n => esc(n)).join(', ')}}</div>
        </div>`
      ).join('');
  }} else {{
    outfitsEl.innerHTML = '';
  }}
}}

// ---------------------------------------------------------------------------
// Development Panel
// ---------------------------------------------------------------------------
function renderDevPanel() {{
  const manifest = DATA.dev_manifest || {{ projects: [] }};
  const gridEl = document.getElementById('dev-grid');
  const detailEl = document.getElementById('dev-detail');

  if (manifest.projects.length === 0) {{
    gridEl.innerHTML = '<div style="color:var(--text-dim);font-size:0.85rem;">No development projects yet. Use reality_develop to create one.</div>';
    detailEl.innerHTML = '';
    return;
  }}

  gridEl.innerHTML = manifest.projects.map(p => {{
    const badgeClass = {{ draft: 'badge-draft', pending_review: 'badge-pending', approved: 'badge-approved', active: 'badge-active' }}[p.status] || 'badge-draft';
    return `<div class="item-card" onclick="showDevDetail('${{p.id}}')">
      <div class="thumb" style="font-size:1.5rem;">${{{{ tool: '🔧', skill: '🧠', plugin: '🔌', script: '📜' }}[p.type] || '📄'}}</div>
      <div class="card-name">${{esc(p.name)}} <span class="badge ${{badgeClass}}">${{p.status}}</span></div>
      <div class="card-meta">${{p.type}} &middot; ${{p.files.length}} files</div>
    </div>`;
  }}).join('');
}}

function showDevDetail(projId) {{
  const manifest = DATA.dev_manifest || {{ projects: [] }};
  const proj = manifest.projects.find(p => p.id === projId);
  if (!proj) return;
  const detailEl = document.getElementById('dev-detail');
  const badgeClass = {{ draft: 'badge-draft', pending_review: 'badge-pending', approved: 'badge-approved', active: 'badge-active' }}[proj.status] || 'badge-draft';
  detailEl.innerHTML = `<div class="detail-panel">
    <h3 style="color:var(--text-bright);font-size:1rem;margin-bottom:0.5rem;">${{esc(proj.name)}} <span class="badge ${{badgeClass}}">${{proj.status}}</span></h3>
    <div style="font-size:0.8rem;color:var(--text-dim);margin-bottom:0.5rem;">${{esc(proj.description || 'No description')}}</div>
    <div style="font-size:0.72rem;color:var(--text-dim);">Type: ${{proj.type}} &middot; Created: ${{proj.created_at}} &middot; Approved: ${{proj.approved}}</div>
    <div style="margin-top:0.5rem;font-size:0.72rem;color:var(--text-dim);">
      <strong>Files:</strong> ${{proj.files.length > 0 ? proj.files.map(f => esc(f)).join(', ') : 'none'}}
    </div>
  </div>`;
}}

// ---------------------------------------------------------------------------
// Cycle Tab
// ---------------------------------------------------------------------------
const CYCLE_HORMONES = {{
  estrogen:     [20,22,25,28,30,35,42,50,60,70,80,90,95,100,85,65,50,45,55,65,70,68,60,50,40,32,25,20],
  progesterone: [5,5,5,5,5,5,5,5,5,5,5,5,5,8,15,30,50,65,80,90,100,95,85,70,55,40,20,8],
  lh:           [10,10,10,12,12,14,16,18,22,30,45,70,95,100,40,15,10,10,10,10,10,10,10,10,10,10,10,10],
  fsh:          [35,40,50,55,60,65,70,65,55,45,40,50,70,80,40,25,20,18,16,15,14,13,12,12,15,20,25,30]
}};

const CYCLE_PHASE_COLORS = {{
  menstruation: '#e74c3c',
  follicular: '#e67e22',
  ovulation: '#f1c40f',
  luteal: '#9b59b6'
}};

const CYCLE_PHASE_RANGES = [
  {{ phase: 'menstruation', start: 1, end: 5, label: 'Menstruation' }},
  {{ phase: 'follicular', start: 6, end: 13, label: 'Follicular' }},
  {{ phase: 'ovulation', start: 14, end: 15, label: 'Ovulation' }},
  {{ phase: 'luteal', start: 16, end: 28, label: 'Luteal' }}
];

function getCyclePhaseJS(day) {{
  if (day <= 5) return 'menstruation';
  if (day <= 13) return 'follicular';
  if (day <= 15) return 'ovulation';
  return 'luteal';
}}

function getCycleModsJS(phase) {{
  const m = {{ menstruation: {{ energy: -12, hunger: 5, stress: 8, libido: 0 }}, follicular: {{ energy: 5, hunger: 0, stress: -5, libido: 0 }}, ovulation: {{ energy: 8, hunger: 0, stress: -8, libido: 15 }}, luteal: {{ energy: -8, hunger: 12, stress: 10, libido: 0 }} }};
  return m[phase] || {{}};
}}

let _cycleDay = 1;
let _cycleSimActive = false;

function renderCyclePanel() {{
  const cycle = DATA.cycle || {{}};
  _cycleDay = cycle.current_day || 1;
  _cycleSimActive = cycle.simulator?.active || false;
  if (_cycleSimActive && cycle.simulator?.simulated_day) _cycleDay = cycle.simulator.simulated_day;
  updateCycleAllPanels(_cycleDay, cycle);
}}

function updateCycleAllPanels(day, cycle) {{
  const phase = getCyclePhaseJS(day);
  renderCycleWheel(day);
  renderCyclePhaseBanner(day, phase);
  renderCycleHormoneChart(day);
  renderCycleBodyStatus(day, phase);
  renderCycleMetabolismImpact(phase);
  renderCycleSimulator(day, cycle);
  renderCycleEducation();
}}

function setCycleDay(day) {{
  _cycleDay = day;
  const cycle = DATA.cycle || {{}};
  updateCycleAllPanels(day, cycle);
}}

function renderCycleWheel(currentDay) {{
  const size = 450;
  const cx = size / 2, cy = size / 2;
  const outerR = size / 2 - 10, innerR = outerR - 45;
  let svg = `<svg width="${{size}}" height="${{size}}" viewBox="0 0 ${{size}} ${{size}}">`;

  for (let d = 1; d <= 28; d++) {{
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

    svg += `<path d="M${{x1o}},${{y1o}} A${{outerR}},${{outerR}} 0 0,1 ${{x2o}},${{y2o}} L${{x1i}},${{y1i}} A${{innerR}},${{innerR}} 0 0,0 ${{x2i}},${{y2i}} Z"
      fill="${{color}}" opacity="${{opacity}}" stroke="${{stroke}}" stroke-width="${{strokeW}}"
      style="cursor:pointer" onclick="setCycleDay(${{d}})"/>`;

    // Day number label
    const midAngle = ((d - 0.5) / 28) * 360 - 90;
    const midRad = midAngle * Math.PI / 180;
    const labelR = (outerR + innerR) / 2;
    const lx = cx + labelR * Math.cos(midRad);
    const ly = cy + labelR * Math.sin(midRad);
    const fontSize = d === currentDay ? '12' : '9';
    const fontWeight = d === currentDay ? '700' : '400';
    const textColor = d === currentDay ? '#fff' : 'rgba(255,255,255,0.6)';
    svg += `<text x="${{lx}}" y="${{ly}}" text-anchor="middle" dominant-baseline="central"
      font-size="${{fontSize}}" font-weight="${{fontWeight}}" fill="${{textColor}}"
      font-family="JetBrains Mono, monospace" style="cursor:pointer;pointer-events:none">${{d}}</text>`;
  }}

  // Glowing marker for current day
  const markerAngle = ((currentDay - 0.5) / 28) * 360 - 90;
  const markerRad = markerAngle * Math.PI / 180;
  const markerR = outerR + 8;
  const mx = cx + markerR * Math.cos(markerRad);
  const my = cy + markerR * Math.sin(markerRad);
  const markerColor = CYCLE_PHASE_COLORS[getCyclePhaseJS(currentDay)];
  svg += `<circle cx="${{mx}}" cy="${{my}}" r="6" fill="${{markerColor}}" opacity="0.9">
    <animate attributeName="opacity" values="0.9;0.4;0.9" dur="2s" repeatCount="indefinite"/>
  </circle>`;

  // Center text
  const phase = getCyclePhaseJS(currentDay);
  const phaseLabel = CYCLE_PHASE_RANGES.find(r => r.phase === phase)?.label || phase;
  svg += `<text x="${{cx}}" y="${{cy - 15}}" text-anchor="middle" font-size="42" font-weight="700" fill="var(--text-bright)" font-family="JetBrains Mono, monospace">${{currentDay}}</text>`;
  svg += `<text x="${{cx}}" y="${{cy + 15}}" text-anchor="middle" font-size="13" fill="${{CYCLE_PHASE_COLORS[phase]}}" font-family="JetBrains Mono, monospace" text-transform="uppercase">${{phaseLabel}}</text>`;
  svg += `<text x="${{cx}}" y="${{cy + 35}}" text-anchor="middle" font-size="10" fill="var(--text-dim)" font-family="DM Sans, sans-serif">of 28 days</text>`;
  svg += `</svg>`;

  document.getElementById('cycle-wheel').innerHTML = svg;
}}

function renderCyclePhaseBanner(day, phase) {{
  const descs = {{
    menstruation: 'The body sheds the uterine lining. Energy dips, cramps may occur. A time for rest and self-care.',
    follicular: 'Estrogen rises, energy returns. A follicle matures in the ovary. Creativity and motivation increase.',
    ovulation: 'Peak fertility. LH surge triggers egg release. Energy, confidence, and libido are at their highest.',
    luteal: 'Progesterone dominates. The body prepares for potential implantation. PMS symptoms may appear.'
  }};
  const label = CYCLE_PHASE_RANGES.find(r => r.phase === phase)?.label || phase;
  const color = CYCLE_PHASE_COLORS[phase];
  document.getElementById('cycle-phase-banner').innerHTML = `
    <div class="phase-name" style="color:${{color}}">${{label}} — Day ${{day}}</div>
    <div style="color:var(--text-dim);font-size:0.85rem;">${{descs[phase] || ''}}</div>`;
}}

function renderCycleHormoneChart(currentDay) {{
  const w = 800, h = 200, pad = 40;
  const chartW = w - pad * 2, chartH = h - pad * 1.5;
  let svg = `<svg viewBox="0 0 ${{w}} ${{h}}" style="width:100%;max-width:${{w}}px;height:auto;">`;

  // Phase background bands
  CYCLE_PHASE_RANGES.forEach(r => {{
    const x1 = pad + ((r.start - 1) / 28) * chartW;
    const x2 = pad + (r.end / 28) * chartW;
    svg += `<rect x="${{x1}}" y="${{pad/2}}" width="${{x2-x1}}" height="${{chartH}}" fill="${{CYCLE_PHASE_COLORS[r.phase]}}" opacity="0.08"/>`;
  }});

  // Gridlines
  for (let i = 0; i <= 4; i++) {{
    const y = pad/2 + (i/4) * chartH;
    svg += `<line x1="${{pad}}" y1="${{y}}" x2="${{pad+chartW}}" y2="${{y}}" stroke="var(--border)" stroke-width="0.5"/>`;
    svg += `<text x="${{pad-5}}" y="${{y+3}}" text-anchor="end" font-size="8" fill="var(--text-dim)" font-family="JetBrains Mono">${{100-i*25}}%</text>`;
  }}

  // Hormone curves
  const colors = {{ estrogen: '#ff69b4', progesterone: '#9b59b6', lh: '#f1c40f', fsh: '#3498db' }};
  Object.entries(CYCLE_HORMONES).forEach(([name, values]) => {{
    let points = values.map((v, i) => {{
      const x = pad + ((i + 0.5) / 28) * chartW;
      const y = pad/2 + chartH - (v / 100) * chartH;
      return `${{x}},${{y}}`;
    }});
    svg += `<polyline points="${{points.join(' ')}}" fill="none" stroke="${{colors[name]}}" stroke-width="2" stroke-linejoin="round" opacity="0.85"/>`;
  }});

  // Current day marker
  const dx = pad + ((currentDay - 0.5) / 28) * chartW;
  svg += `<line x1="${{dx}}" y1="${{pad/2}}" x2="${{dx}}" y2="${{pad/2+chartH}}" stroke="white" stroke-width="1.5" stroke-dasharray="4,3" opacity="0.7"/>`;

  // Day labels
  for (let d = 1; d <= 28; d += (d < 7 ? 1 : (d < 15 ? 2 : 3))) {{
    const x = pad + ((d - 0.5) / 28) * chartW;
    svg += `<text x="${{x}}" y="${{h-5}}" text-anchor="middle" font-size="8" fill="var(--text-dim)" font-family="JetBrains Mono">${{d}}</text>`;
  }}

  svg += `</svg>`;
  document.getElementById('cycle-hormone-chart').innerHTML = svg;
  document.getElementById('cycle-legend').innerHTML = `
    <span class="leg-estrogen">Estrogen</span>
    <span class="leg-progesterone">Progesterone</span>
    <span class="leg-lh">LH</span>
    <span class="leg-fsh">FSH</span>`;
}}

function renderCycleBodyStatus(day, phase) {{
  const idx = Math.max(0, Math.min(27, day - 1));
  const e = CYCLE_HORMONES.estrogen[idx];
  const p = CYCLE_HORMONES.progesterone[idx];

  const bodyData = {{
    menstruation: [
      {{ icon: '🩸', title: 'Uterine Lining', desc: 'Endometrium is being shed. Menstrual bleeding occurs as the body discards the unfertilized lining.' }},
      {{ icon: '🫘', title: 'Ovarian Activity', desc: 'Follicles are dormant. FSH begins to slowly stimulate new follicle recruitment.' }},
      {{ icon: '💧', title: 'Cervical Mucus', desc: 'Minimal and dry. The cervix is closed and low.' }},
      {{ icon: '🌡️', title: 'Basal Temperature', desc: 'Low baseline temperature. Typically 36.1-36.4°C (97.0-97.5°F).' }}
    ],
    follicular: [
      {{ icon: '🧱', title: 'Uterine Lining', desc: `Rebuilding under estrogen influence (E2: ${{e}}%). Endometrium thickens progressively.` }},
      {{ icon: '🫘', title: 'Ovarian Activity', desc: 'Dominant follicle selected and growing. Produces increasing estrogen.' }},
      {{ icon: '💧', title: 'Cervical Mucus', desc: 'Increasing, becoming clearer and more stretchy as estrogen rises.' }},
      {{ icon: '🌡️', title: 'Basal Temperature', desc: 'Remains low. Steady baseline before ovulation.' }}
    ],
    ovulation: [
      {{ icon: '🧱', title: 'Uterine Lining', desc: `Fully developed (${{e}}% estrogen peak). Rich blood supply, glands active.` }},
      {{ icon: '🥚', title: 'Ovarian Activity', desc: 'LH surge triggers ovulation! Egg released from dominant follicle.' }},
      {{ icon: '💧', title: 'Cervical Mucus', desc: 'Peak fertility mucus — clear, stretchy, egg-white consistency.' }},
      {{ icon: '🌡️', title: 'Basal Temperature', desc: 'Brief dip then sharp rise of 0.2-0.5°C after ovulation.' }}
    ],
    luteal: [
      {{ icon: '🧱', title: 'Uterine Lining', desc: `Maintained by progesterone (${{p}}%). Secretory phase — glands produce nutrients.` }},
      {{ icon: '🟡', title: 'Corpus Luteum', desc: 'Collapsed follicle becomes corpus luteum, producing progesterone.' }},
      {{ icon: '💧', title: 'Cervical Mucus', desc: 'Thick, sticky, and opaque. Cervix closes and firms.' }},
      {{ icon: '🌡️', title: 'Basal Temperature', desc: 'Elevated plateau. Remains high due to progesterone.' }}
    ]
  }};

  const items = bodyData[phase] || [];
  document.getElementById('cycle-body-status').innerHTML = items.map(item => `
    <div class="cycle-body-row">
      <div class="cycle-body-icon">${{item.icon}}</div>
      <div class="cycle-body-text"><h3>${{item.title}}</h3><p>${{item.desc}}</p></div>
    </div>`).join('');
}}

function renderCycleMetabolismImpact(phase) {{
  const mods = getCycleModsJS(phase);
  const items = [
    {{ key: 'energy', label: 'Energy', val: mods.energy || 0 }},
    {{ key: 'hunger', label: 'Hunger', val: mods.hunger || 0 }},
    {{ key: 'stress', label: 'Stress', val: mods.stress || 0 }},
    {{ key: 'libido', label: 'Libido', val: mods.libido || 0 }}
  ];

  document.getElementById('cycle-metabolism-impact').innerHTML = items.map(item => {{
    const maxVal = 20;
    const absVal = Math.abs(item.val);
    const pct = Math.min(100, (absVal / maxVal) * 100);
    const cls = item.val >= 0 ? 'positive' : 'negative';
    const arrow = item.val > 0 ? '↑' : (item.val < 0 ? '↓' : '→');
    const sign = item.val > 0 ? '+' : '';
    return `<div class="cycle-bar-row">
      <div class="cycle-bar-label">${{item.label}}</div>
      <div class="cycle-bar-track"><div class="cycle-bar-fill ${{cls}}" style="width:${{pct}}%"></div></div>
      <div class="cycle-bar-value">${{arrow}} ${{sign}}${{item.val}}</div>
    </div>`;
  }}).join('');
}}

function renderCycleSimulator(day, cycle) {{
  const symptoms = ['cramps','bloating','fatigue','mood_swings','headache','breast_tenderness','acne','appetite_changes','back_pain','insomnia'];
  const symMods = cycle?.symptom_modifiers || {{}};

  let html = `<div class="cycle-sim-row">
    <label>
      <input type="checkbox" id="cycle-sim-toggle" ${{_cycleSimActive ? 'checked' : ''}}
        onchange="_cycleSimActive=this.checked; updateCycleAllPanels(_cycleDay, DATA.cycle||{{}})"> What-If Mode
    </label>
  </div>`;

  html += `<div class="cycle-sim-row">
    <label>Day</label>
    <input type="range" min="1" max="28" value="${{day}}" id="cycle-sim-day"
      oninput="setCycleDay(parseInt(this.value)); document.getElementById('cycle-sim-day-val').textContent=this.value">
    <div class="sim-val" id="cycle-sim-day-val">${{day}}</div>
  </div>`;

  html += `<div style="margin-top:0.5rem;padding-top:0.5rem;border-top:1px solid var(--border);">
    <div style="font-size:0.75rem;color:var(--text-dim);margin-bottom:0.5rem;text-transform:uppercase;letter-spacing:0.1em;">Symptom Intensity</div>`;

  symptoms.forEach(s => {{
    const val = symMods[s] !== undefined ? symMods[s] : 1;
    const label = s.replace(/_/g, ' ').replace(/\\b\\w/g, c => c.toUpperCase());
    html += `<div class="cycle-sim-row">
      <label>${{label}}</label>
      <input type="range" min="0" max="3" step="0.1" value="${{val}}" id="sim-${{s}}-input"
        oninput="document.getElementById('sim-${{s}}-val').textContent=parseFloat(this.value).toFixed(1)+'x'">
      <div class="sim-val" id="sim-${{s}}-val">${{parseFloat(val).toFixed(1)}}x</div>
    </div>`;
  }});

  html += `</div>`;

  html += `<div class="cycle-presets">
    <button onclick="applyCyclePreset('heavy_pms')">Heavy PMS</button>
    <button onclick="applyCyclePreset('minimal')">Minimal</button>
    <button onclick="applyCyclePreset('heavy_period')">Heavy Period</button>
    <button onclick="applyCyclePreset('reset')">Reset</button>
    <button onclick="saveCycleState()" style="border-color:var(--accent);color:var(--accent);">Save State</button>
  </div>`;

  document.getElementById('cycle-simulator').innerHTML = html;
}}

function applyCyclePreset(preset) {{
  const presets = {{
    heavy_pms: {{ cramps: 2.5, bloating: 2.0, fatigue: 2.0, mood_swings: 2.5, headache: 1.8, breast_tenderness: 2.2, acne: 1.5, appetite_changes: 2.0, back_pain: 2.0, insomnia: 1.8 }},
    minimal: {{ cramps: 0.3, bloating: 0.3, fatigue: 0.5, mood_swings: 0.3, headache: 0.2, breast_tenderness: 0.3, acne: 0.2, appetite_changes: 0.3, back_pain: 0.2, insomnia: 0.3 }},
    heavy_period: {{ cramps: 3.0, bloating: 2.0, fatigue: 2.5, mood_swings: 1.5, headache: 2.0, breast_tenderness: 1.0, acne: 1.0, appetite_changes: 1.5, back_pain: 2.5, insomnia: 1.5 }},
    reset: {{ cramps: 1, bloating: 1, fatigue: 1, mood_swings: 1, headache: 1, breast_tenderness: 1, acne: 1, appetite_changes: 1, back_pain: 1, insomnia: 1 }}
  }};
  const vals = presets[preset];
  if (!vals) return;
  if (!DATA.cycle) DATA.cycle = {{}};
  DATA.cycle.symptom_modifiers = vals;
  renderCycleSimulator(_cycleDay, DATA.cycle);
}}

function saveCycleState() {{
  const cycle = DATA.cycle || {{}};
  cycle.current_day = _cycleDay;
  cycle.phase = getCyclePhaseJS(_cycleDay);
  cycle.hormones = {{
    estrogen: CYCLE_HORMONES.estrogen[_cycleDay - 1] || 0,
    progesterone: CYCLE_HORMONES.progesterone[_cycleDay - 1] || 0,
    lh: CYCLE_HORMONES.lh[_cycleDay - 1] || 0,
    fsh: CYCLE_HORMONES.fsh[_cycleDay - 1] || 0
  }};
  cycle.simulator = {{ active: _cycleSimActive, simulated_day: _cycleDay, custom_modifiers: {{}} }};
  cycle.last_advance = new Date().toISOString();
  if (!cycle.start_date) cycle.start_date = cycle.last_advance;
  if (!cycle.cycle_length) cycle.cycle_length = 28;
  if (!cycle.symptom_modifiers) cycle.symptom_modifiers = {{ cramps:1,bloating:1,fatigue:1,mood_swings:1,headache:1,breast_tenderness:1,acne:1,appetite_changes:1,back_pain:1,insomnia:1 }};

  // Read symptom sliders
  const symptoms = ['cramps','bloating','fatigue','mood_swings','headache','breast_tenderness','acne','appetite_changes','back_pain','insomnia'];
  symptoms.forEach(s => {{
    const el = document.getElementById(`sim-${{s}}-input`);
    if (el) cycle.symptom_modifiers[s] = parseFloat(el.value);
  }});

  DATA.cycle = cycle;
  fetch('/update-cycle', {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }},
    body: JSON.stringify(cycle)
  }}).then(r => {{
    if (r.ok) showToast('Cycle state saved');
    else showToast('Save failed', true);
  }}).catch(() => showToast('Save failed', true));
}}

function renderCycleEducation() {{
  const phases = [
    {{
      phase: 'menstruation', label: 'Menstruation (Days 1-5)', subtitle: 'The Shedding Phase',
      color: CYCLE_PHASE_COLORS.menstruation,
      text: `<p><strong>What happens:</strong> The uterine lining (endometrium) that built up during the previous cycle is shed through the vagina. This is menstrual bleeding, lasting typically 3-7 days.</p>
<p><strong>Hormones:</strong> Estrogen and progesterone are at their lowest. The drop in these hormones triggers the shedding. FSH begins to rise slowly, signaling the ovaries to prepare new follicles.</p>
<p><strong>Why it happens:</strong> When no fertilized egg implanted in the uterine wall, the corpus luteum degrades, progesterone drops, and the thickened lining is no longer supported — so the body releases it.</p>
<p><strong>Common symptoms:</strong> Cramps (prostaglandins cause uterine contractions), fatigue, lower back pain, mood changes. Iron loss through bleeding can contribute to tiredness.</p>`
    }},
    {{
      phase: 'follicular', label: 'Follicular Phase (Days 6-13)', subtitle: 'The Growth Phase',
      color: CYCLE_PHASE_COLORS.follicular,
      text: `<p><strong>What happens:</strong> FSH stimulates multiple ovarian follicles to develop. One becomes the "dominant follicle" and matures, producing increasing amounts of estrogen.</p>
<p><strong>Hormones:</strong> Estrogen rises steadily. This thickens the endometrium again, preparing a new, nutrient-rich lining. FSH peaks early then decreases as the dominant follicle takes over.</p>
<p><strong>Why it happens:</strong> The body is preparing for potential conception. Estrogen rebuilds the uterine lining and triggers changes in cervical mucus to eventually facilitate sperm transport.</p>
<p><strong>Common experience:</strong> Rising energy, improved mood, clearer skin, increased creativity and social drive. Many people feel "at their best" during the late follicular phase.</p>`
    }},
    {{
      phase: 'ovulation', label: 'Ovulation (Days 14-15)', subtitle: 'The Release',
      color: CYCLE_PHASE_COLORS.ovulation,
      text: `<p><strong>What happens:</strong> A massive LH surge (triggered by peak estrogen) causes the dominant follicle to rupture and release a mature egg (ovum) into the fallopian tube.</p>
<p><strong>Hormones:</strong> LH spikes dramatically (up to 10x baseline). Estrogen peaks just before. The egg is viable for 12-24 hours. This is the most fertile window.</p>
<p><strong>Why it happens:</strong> High estrogen signals the pituitary gland that a follicle is mature. The pituitary responds with the LH surge, which biochemically triggers the follicle wall to break down and release the egg.</p>
<p><strong>Common experience:</strong> Some feel a twinge or mild pain on one side (Mittelschmerz). Highest energy, confidence, and libido. Cervical mucus is clear and stretchy (egg-white consistency).</p>`
    }},
    {{
      phase: 'luteal', label: 'Luteal Phase (Days 16-28)', subtitle: 'The Waiting Phase',
      color: CYCLE_PHASE_COLORS.luteal,
      text: `<p><strong>What happens:</strong> The collapsed follicle becomes the corpus luteum, a temporary endocrine gland that produces progesterone and some estrogen to maintain the uterine lining.</p>
<p><strong>Hormones:</strong> Progesterone dominates, peaking around day 21. If no implantation occurs, the corpus luteum degrades after ~12 days, hormone levels drop, and a new cycle begins.</p>
<p><strong>Why it happens:</strong> Progesterone stabilizes the endometrium and creates a secretory environment (nutrients, blood vessels) suitable for embryo implantation. It also raises basal body temperature.</p>
<p><strong>Common symptoms (PMS):</strong> Bloating, breast tenderness, mood swings, food cravings, acne, fatigue, irritability. These are caused by progesterone's effects and the eventual hormone withdrawal.</p>`
    }}
  ];

  document.getElementById('cycle-education').innerHTML = phases.map((p, i) => `
    <div class="cycle-edu-card${{i === 0 ? ' open' : ''}}" onclick="this.classList.toggle('open')">
      <div class="cycle-edu-header" style="border-left:3px solid ${{p.color}};">
        <span>${{p.label}} — ${{p.subtitle}}</span>
        <span style="font-size:0.7rem;color:var(--text-dim);">▼</span>
      </div>
      <div class="cycle-edu-body">${{p.text}}</div>
    </div>`).join('');
}}

// ---------------------------------------------------------------------------
// World Tab
// ---------------------------------------------------------------------------
function renderWorldPanel() {{
  const ws = DATA.world_state || {{}};
  const locs = DATA.physique?.world?.locations || [];

  // Weather
  const weatherIcons = {{ sunny: '☀️', cloudy: '☁️', rainy: '🌧️', stormy: '⛈️', snowy: '❄️' }};
  const weatherIcon = weatherIcons[ws.weather] || '🌤️';
  document.getElementById('world-weather').innerHTML = `
    <div style="font-size:3rem;text-align:center;">${{weatherIcon}}</div>
    <p style="text-align:center;text-transform:capitalize;">${{ws.weather || 'unknown'}}</p>
    <p style="text-align:center;font-size:1.5rem;">${{ws.temperature !== undefined ? ws.temperature + '°C' : 'N/A'}}</p>
    <div style="margin-top:1rem;display:flex;flex-direction:column;gap:0.5rem;">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <span style="font-size:0.75rem;color:var(--text-dim);">Real-World Sync</span>
        <input type="checkbox" ${{ws.sync_to_real_world ? 'checked' : ''}} 
          onchange="updateWorld({{sync_to_real_world: this.checked}})">
      </div>
      <select class="btn-crud" style="width:100%;text-align:center;" onchange="updateWorld({{weather: this.value, sync_to_real_world: false}})">
        <option value="">-- Override Weather --</option>
        ${{Object.keys(weatherIcons).map(w => `<option value="${{w}}" ${{ws.weather === w ? 'selected' : ''}}>${{w.toUpperCase()}}</option>`).join('')}}
      </select>
    </div>`;

  // Season
  const seasonIcons = {{ spring: '🌸', summer: '☀️', autumn: '🍂', winter: '❄️' }};
  const seasonIcon = seasonIcons[ws.season] || '🌍';
  document.getElementById('world-season').innerHTML = `
    <div style="font-size:3rem;text-align:center;">${{seasonIcon}}</div>
    <p style="text-align:center;text-transform:capitalize;">${{ws.season || 'unknown'}}</p>
    <div style="margin-top:1rem;">
      <select class="btn-crud" style="width:100%;text-align:center;" onchange="updateWorld({{season: this.value, sync_to_real_world: false}})">
        <option value="">-- Override Season --</option>
        ${{Object.keys(seasonIcons).map(s => `<option value="${{s}}" ${{ws.season === s ? 'selected' : ''}}>${{s.toUpperCase()}}</option>`).join('')}}
      </select>
    </div>`;

  // Market
  const marketMod = ws.market_modifier || 1.0;
  const marketColor = marketMod > 1 ? 'var(--growth)' : (marketMod < 1 ? 'var(--danger)' : 'var(--text)');
  document.getElementById('world-market').innerHTML = `
    <p style="font-size:1.5rem;text-align:center;color:${{marketColor}};">${{(marketMod * 100).toFixed(0)}}%</p>
    <p style="text-align:center;font-size:0.8rem;color:var(--text-dim);">of base price</p>
    <div style="margin-top:1rem;text-align:center;">
      <input type="range" min="0.5" max="1.5" step="0.05" value="${{marketMod}}" 
        style="width:100%;" onchange="updateWorld({{market_modifier: parseFloat(this.value)}})">
    </div>`;

  // Locations
  document.getElementById('world-locations').innerHTML = locs.length > 0
    ? locs.map(l => `<div style="padding:0.3rem 0;border-bottom:1px solid var(--border);">
        <strong>${{l.name}}</strong><br><span style="color:var(--text-dim);font-size:0.8rem;">${{l.description || 'No description'}}</span>
      </div>`).join('')
    : '<p style="color:var(--text-dim);">No locations defined</p>';
}}

function updateWorld(data) {{
  fetch('/update-world', {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }},
    body: JSON.stringify(data)
  }})
  .then(r => r.text())
  .then(txt => {{
    if (txt === 'OK') {{
      showToast('World updated');
      setTimeout(() => window.location.reload(), 500);
    }} else {{
      showToast(txt, true);
    }}
  }})
  .catch(e => showToast(e, true));
}}

// ---------------------------------------------------------------------------
// Skills Tab
// ---------------------------------------------------------------------------
function renderSkillsPanel() {{
  const skills = DATA.skills?.skills || [];
  const totalXp = DATA.skills?.total_xp || 0;

  // Skills list
  if (skills.length === 0) {{
    document.getElementById('skills-list').innerHTML = '<p style="color:var(--text-dim);">No skills learned yet</p>';
  }} else {{
    const sorted = [...skills].sort((a, b) => b.level - a.level || b.xp - a.xp);
    document.getElementById('skills-list').innerHTML = sorted.map(s => `
      <div style="padding:0.5rem;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;">
        <span><strong>${{s.name}}</strong></span>
        <span style="color:var(--core);">Lv.${{s.level}} <span style="color:var(--text-dim);font-size:0.8rem;">(${{s.xp}}/${{s.xp_to_next}} XP)</span></span>
      </div>`).join('');
  }}

  // Top skills
  const top3 = skills.slice(0, 3).sort((a, b) => b.level - a.level);
  document.getElementById('skills-top').innerHTML = top3.length > 0
    ? top3.map((s, i) => `<div style="padding:0.3rem 0;">
        <span style="color:var(--core);">#{{i+1}}</span> <strong>${{s.name}}</strong> (Lv.${{s.level}})
      </div>`).join('')
    : '<p style="color:var(--text-dim);">No skills yet</p>';

  // Total XP
  document.getElementById('skills-total').innerHTML = `
    <p style="font-size:2rem;text-align:center;color:var(--growth);">${{totalXp}}</p>
    <p style="text-align:center;font-size:0.8rem;color:var(--text-dim);">Total XP earned</p>`;
}}

// ---------------------------------------------------------------------------
// Genesis Lab Tab
// ---------------------------------------------------------------------------
async function toggleGenesis(enabled) {{
  const statusDiv = document.getElementById('genesis-status');
  try {{
    const response = await fetch('/api/genesis/toggle', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{ enabled: enabled }})
    }});
    const result = await response.json();

    if (result.success) {{
      statusDiv.innerHTML = enabled
        ? '<span style="color:var(--growth);">✓ Origin Engine enabled. Restart the agent to activate.</span>'
        : '<span style="color:var(--text-dim);">Origin Engine disabled.</span>';
    }} else {{
      statusDiv.innerHTML = '<span style="color:var(--danger);">Error: ' + result.message + '</span>';
    }}
  }} catch (error) {{
    statusDiv.innerHTML = '<span style="color:var(--danger);">Error: ' + error.message + '</span>';
  }}
}}

async function loadGenesisStatus() {{
  try {{
    const response = await fetch('/api/genesis/status');
    const result = await response.json();
    document.getElementById('genesis-enabled').checked = result.enabled || false;

    const statusDiv = document.getElementById('genesis-status');
    if (result.enabled) {{
      statusDiv.innerHTML = '<span style="color:var(--growth);">✓ Origin Engine is enabled</span>';
    }} else {{
      statusDiv.innerHTML = '<span style="color:var(--text-dim);">Origin Engine is disabled</span>';
    }}

    // Load model configuration
    loadModelConfig();

    // Load profiles
    loadProfiles();

    // Load backups
    loadBackups();
  }} catch (e) {{
    console.log('Could not load genesis status:', e);
  }}
}}

async function loadModelConfig() {{
  try {{
    const response = await fetch('/api/model/config');
    const config = await response.json();

    if (config.models) {{
      if (config.models.persona) document.getElementById('model-persona').value = config.models.persona;
      if (config.models.limbic) document.getElementById('model-limbic').value = config.models.limbic;
      if (config.models.analyst) document.getElementById('model-analyst').value = config.models.analyst;
      if (config.models.world_engine) document.getElementById('model-world').value = config.models.world_engine;
    }}
    if (config.api_key) {{
      document.getElementById('api-key').value = config.api_key;
    }}
  }} catch (e) {{
    console.log('Could not load model config:', e);
  }}
}}

async function saveModelConfig() {{
  const models = {{
    persona: document.getElementById('model-persona').value,
    limbic: document.getElementById('model-limbic').value,
    analyst: document.getElementById('model-analyst').value,
    world_engine: document.getElementById('model-world').value,
  }};
  const apiKey = document.getElementById('api-key').value;

  try {{
    const response = await fetch('/api/model/config', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{ models, api_key: apiKey }})
    }});
    const result = await response.json();

    const statusEl = document.getElementById('model-config-status');
    if (result.success) {{
      statusEl.innerHTML = '<span style="color:var(--growth);">✓ Saved!</span>';
      setTimeout(() => statusEl.innerHTML = '', 2000);
    }} else {{
      statusEl.innerHTML = '<span style="color:var(--danger);">Error: ' + result.message + '</span>';
    }}
  }} catch (e) {{
    document.getElementById('model-config-status').innerHTML = '<span style="color:var(--danger);">Error: ' + e.message + '</span>';
  }}
}}

async function loadProfiles() {{
  try {{
    const response = await fetch('/api/profiles/list');
    const profiles = await response.json();

    const container = document.getElementById('profile-list');
    if (!profiles || profiles.length === 0) {{
      container.innerHTML = '<p style="color:var(--text-dim);font-size:0.85rem;">No profiles saved yet.</p>';
      return;
    }}

    container.innerHTML = profiles.map(p => `
      <div style="background:var(--bg);padding:0.5rem;border-radius:4px;display:flex;justify-content:space-between;align-items:center;">
        <span><strong>${{p}}</strong></span>
        <div>
          <button onclick="loadProfile('${{p}}')" style="background:var(--growth);color:#fff;border:none;padding:0.25rem 0.5rem;border-radius:4px;cursor:pointer;margin-right:0.25rem;">Load</button>
          <button onclick="deleteProfile('${{p}}')" style="background:var(--danger);color:#fff;border:none;padding:0.25rem 0.5rem;border-radius:4px;cursor:pointer;">Del</button>
        </div>
      </div>
    `).join('');
  }} catch (e) {{
    console.log('Could not load profiles:', e);
  }}
}}

async function loadBackups() {{
  try {{
    const response = await fetch('/api/backups/list');
    const backups = await response.json();

    const container = document.getElementById('backup-list');
    if (!backups || backups.length === 0) {{
      container.innerHTML = '<p style="color:var(--text-dim);font-size:0.85rem;">No backups available yet.</p>';
      return;
    }}

    container.innerHTML = backups.map(b => `
      <div style="background:var(--bg);padding:0.5rem;border-radius:4px;display:flex;justify-content:space-between;align-items:center;margin-bottom:0.25rem;">
        <span><strong>${{b}}</strong></span>
        <button onclick="rollbackTo('${{b}}')" style="background:var(--accent);color:#fff;border:none;padding:0.25rem 0.5rem;border-radius:4px;cursor:pointer;">Rollback</button>
      </div>
    `).join('');
  }} catch (e) {{
    console.log('Could not load backups:', e);
  }}
}}

async function saveProfile() {{
  const name = document.getElementById('profile-name').value.trim();
  if (!name) {{
    alert('Please enter a profile name.');
    return;
  }}

  // Sanitize name
  const safeName = name.replace(/[^a-zA-Z0-9_-]/g, '').slice(0, 50);
  if (!safeName) {{
    alert('Invalid profile name.');
    return;
  }}

  try {{
    const response = await fetch('/api/profiles/save', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{ name: safeName }})
    }});
    const result = await response.json();
    alert(result.success ? 'Profile saved!' : 'Error: ' + result.message);
    loadProfiles();
  }} catch (e) {{
    alert('Error: ' + e.message);
  }}
}}

async function loadProfile(name) {{
  if (!confirm('Load profile "' + name + '"? This will overwrite current state.')) return;

  try {{
    const response = await fetch('/api/profiles/load', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{ name: name }})
    }});
    const result = await response.json();
    alert(result.success ? 'Profile loaded!' : 'Error: ' + result.message);
  }} catch (e) {{
    alert('Error: ' + e.message);
  }}
}}

async function deleteProfile(name) {{
  if (!confirm('Delete profile "' + name + '"? This cannot be undone.')) return;

  try {{
    const response = await fetch('/api/profiles/delete', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{ name: name }})
    }});
    const result = await response.json();
    alert(result.success ? 'Profile deleted!' : 'Error: ' + result.message);
    loadProfiles();
  }} catch (e) {{
    alert('Error: ' + e.message);
  }}
}}

async function rollbackTo(date) {{
  if (!confirm('Rollback to ' + date + '? This will overwrite current state.')) return;

  try {{
    const response = await fetch('/api/backups/rollback', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{ date: date }})
    }});
    const result = await response.json();
    alert(result.success ? 'Rollback complete!' : 'Error: ' + result.message);
  }} catch (e) {{
    alert('Error: ' + e.message);
  }}
}}

async function runPatch() {{
  const instructions = document.getElementById('patch-prompt').value.trim();
  if (!instructions) {{
    alert('Please enter patch instructions.');
    return;
  }}

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

  try {{
    progress.style.width = '40%';
    const response = await fetch('/api/genesis/request', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{ prompt: prefix + instructions }})
    }});
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
    const poll = setInterval(async () => {{
      attempts++;
      const statusRes = await fetch('/api/genesis/request-status');
      const status = await statusRes.json();
      
      if (!status.pending || attempts > 30) {{
        clearInterval(poll);
        progress.style.width = '100%';
        setTimeout(() => location.reload(), 2000);
      }}
    }}, 2000);

  }} catch (e) {{
    alert('Error: ' + e.message);
    loading.style.display = 'none';
  }}
}}

async function runGenesis() {{
  const prompt = document.getElementById('genesis-prompt').value.trim();
  if (!prompt) {{
    alert('Please enter a life description.');
    return;
  }}

  if (!confirm('DANGER: This will overwrite your entire simulation. Are you sure?')) return;

  // Show loading overlay
  const loading = document.getElementById('genesis-loading');
  const progress = document.getElementById('genesis-progress');
  loading.style.display = 'flex';
  progress.style.width = '10%';

  try {{
    progress.style.width = '30%';

    // Send the prompt to the backend to be picked up by the agent
    const response = await fetch('/api/genesis/request', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{ prompt: prompt }})
    }});
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
    const poll = setInterval(async () => {{
      attempts++;
      const statusRes = await fetch('/api/genesis/request-status');
      const status = await statusRes.json();
      
      if (!status.pending || attempts > 30) {{
        clearInterval(poll);
        progress.style.width = '100%';
        resultTitle.textContent = '✅ Generation Complete';
        resultTitle.style.color = 'var(--growth)';
        resultContent.textContent = 'The agent has finished the life bootstrap. Reloading...';
        setTimeout(() => location.reload(), 2000);
      }}
    }}, 2000);

  }} catch (error) {{
    alert('Error: ' + error.message);
    loading.style.display = 'none';
  }}
}}

// ---------------------------------------------------------------------------
// Social Standing Tab
// ---------------------------------------------------------------------------
function renderReputationPanel() {{
  const rep = DATA.reputation || {{}};
  const globalScore = rep.global_score || 0;
  const circles = rep.circles || [];
  const events = rep.events || [];

  // Update global reputation meter
  const bar = document.getElementById('rep-bar');
  const text = document.getElementById('rep-text');
  const score = document.getElementById('rep-score');

  if (bar && text && score) {{
    const pct = (globalScore + 100) / 2; // Convert -100..100 to 0..100
    bar.style.width = pct + '%';
    score.textContent = (globalScore >= 0 ? '+' : '') + globalScore;

    // Color and label based on score
    let rank = 'Neutral';
    let color = '#888';
    if (globalScore >= 80) {{ rank = 'Icon'; color = '#4a4'; }}
    else if (globalScore >= 50) {{ rank = 'Respected'; color = '#8c4'; }}
    else if (globalScore >= 20) {{ rank = 'Known'; color = '#ac8'; }}
    else if (globalScore >= -20) {{ rank = 'Neutral'; color = '#888'; }}
    else if (globalScore >= -50) {{ rank = 'Controversial'; color = '#c84'; }}
    else {{ rank = 'Pariah'; color = '#e44'; }}

    text.textContent = rank;
    bar.style.background = `linear-gradient(90deg, ${color}, ${color})`;
  }}

  // Render circles
  const circlesList = document.getElementById('circles-list');
  if (circlesList) {{
    if (circles.length === 0) {{
      circlesList.innerHTML = '<p style="color:var(--text-dim);">No circles defined</p>';
    }} else {{
      const sortedCircles = [...circles].sort((a, b) => b.score - a.score);
      circlesList.innerHTML = sortedCircles.map(c => {{
        const score = c.score || 0;
        const color = score >= 0 ? (score > 50 ? '#4a4' : '#8c4') : (score < -50 ? '#e44' : '#c84');
        return `<div style="display:flex;align-items:center;justify-content:space-between;padding:0.5rem;margin-bottom:0.5rem;background:var(--bg-dim);border-radius:6px;">
          <span>${{c.name}}</span>
          <span style="color:${{color}};font-weight:bold;">${{score >= 0 ? '+' : ''}}${{score}}</span>
        </div>`;
      }}).join('');
    }}
  }}

  // Render events
  const eventsList = document.getElementById('events-list');
          if (eventsList) {{
            if (events.length === 0) {{
              eventsList.innerHTML = '<p style="color:var(--text-dim);">No recent events</p>';
            }} else {{
              eventsList.innerHTML = events.slice(0, 20).map(e => {{
      
            const change = e.change || 0;
            const color = change >= 0 ? '#4a4' : '#e44';
            const date = e.timestamp ? new Date(e.timestamp).toLocaleDateString() : '';
            return `<div style="padding:0.5rem;margin-bottom:0.5rem;background:var(--bg-dim);border-radius:4px;font-size:0.85rem;">
              <div style="display:flex;justify-content:space-between;">
                <strong>${{e.circle || 'Public'}}</strong>
                <span style="color:${{color}};">${{change >= 0 ? '+' : ''}}${{change}}</span>
              </div>
              <div style="color:var(--text-dim);font-size:0.75rem;">${{e.reason || ''}}</div>
              <div style="color:var(--text-dim);font-size:0.7rem;">${{date}}</div>
            </div>`;
          }}).join('');
        }}
      }}
  
}}

// ---------------------------------------------------------------------------
// Psychology Tab
// ---------------------------------------------------------------------------
function renderPsychPanel() {{
  const psych = DATA.psychology || {{}};

  // Resilience
  const res = psych.resilience || 0;
  const resColor = res > 70 ? 'var(--growth)' : (res < 30 ? 'var(--danger)' : 'var(--text)');
  document.getElementById('psych-resilience').innerHTML = `
    <div style="width:100%;height:20px;background:var(--border);border-radius:10px;overflow:hidden;">
      <div style="width:${{res}}%;height:100%;background:${{resColor}};transition:width 0.5s;"></div>
    </div>
    <p style="text-align:center;margin-top:0.5rem;">${{res}}/100</p>`;

  // Traumas
  const traumas = psych.traumas || [];
  if (traumas.length === 0) {{
    document.getElementById('psych-traumas').innerHTML = '<p style="color:var(--text-dim);">No active traumas</p>';
  }} else {{
    document.getElementById('psych-traumas').innerHTML = traumas.map(t => `
      <div style="padding:0.5rem;margin-bottom:0.5rem;background:rgba(224,80,80,0.1);border-left:3px solid var(--danger);border-radius:4px;">
        <div style="display:flex;justify-content:space-between;">
          <strong>${{t.description?.slice(0, 50) || 'Trauma'}}${{t.description?.length > 50 ? '...' : ''}}</strong>
          <span style="color:var(--danger);">${{t.severity}}/100</span>
        </div>
        <div style="font-size:0.75rem;color:var(--text-dim);margin-top:0.2rem;">
          Trigger: ${{t.trigger || 'unknown'}} · Decay: ${{t.decay_rate}}/day
        </div>
      </div>`).join('');
  }}

  // Phobias
  const phobias = psych.phobias || [];
  document.getElementById('psych-phobias').innerHTML = phobias.length > 0
    ? phobias.map(p => `<span style="display:inline-block;padding:0.2rem 0.5rem;margin:0.2rem;background:var(--border);border-radius:4px;font-size:0.85rem;">${{p}}</span>`).join('')
    : '<p style="color:var(--text-dim);">No phobias recorded</p>';

  // Joys
  const joys = psych.joys || [];
  document.getElementById('psych-joys').innerHTML = joys.length > 0
    ? joys.map(j => `<div style="padding:0.3rem 0;border-bottom:1px solid var(--border);">${{j}}</div>`).join('')
    : '<p style="color:var(--text-dim);">No joys recorded</p>';
}}
</script>
</body>
</html>"""


def generate_mindmap_html(data: dict) -> str:
    """Generate the interactive canvas mindmap page."""
    data_json = json.dumps(data, indent=None, default=str)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Soul Evolution — Soul Mindmap</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,700;1,400&display=swap');

* {{ margin: 0; padding: 0; box-sizing: border-box; }}

:root {{
  --bg: #060610;
  --text: #c8c8d8;
  --text-dim: #5a5a70;
  --text-bright: #eeeef4;
  --accent: #7c6ff0;
  --core: #e05050;
  --mutable: #50c878;
}}

body {{
  background: var(--bg);
  color: var(--text);
  font-family: 'DM Sans', sans-serif;
  overflow: hidden;
  height: 100vh;
  cursor: grab;
}}
body.dragging {{ cursor: grabbing; }}

canvas {{
  display: block;
  position: absolute;
  top: 0; left: 0;
}}

/* HUD overlay */
.hud {{
  position: fixed;
  z-index: 100;
  pointer-events: none;
}}
.hud > * {{ pointer-events: auto; }}

.hud-top {{
  top: 1.2rem; left: 50%;
  transform: translateX(-50%);
  text-align: center;
}}
.hud-top h1 {{
  font-family: 'JetBrains Mono', monospace;
  font-weight: 300;
  font-size: 1.1rem;
  letter-spacing: 0.15em;
  color: var(--text-dim);
}}
.hud-top h1 .evolution {{ color: var(--accent); }}
.hud-top h1 .soul {{ color: var(--text-dim); }}
.hud-top .back-link {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  color: var(--text-dim);
  text-decoration: none;
  letter-spacing: 0.05em;
  transition: color 0.2s;
}}
.hud-top .back-link:hover {{ color: var(--mutable); }}

/* Controls bar */
.controls {{
  position: fixed;
  bottom: 1.5rem; left: 50%; transform: translateX(-50%);
  z-index: 100;
  display: flex; align-items: center; gap: 0.6rem;
  background: rgba(12, 12, 20, 0.85);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(30, 30, 48, 0.6);
  border-radius: 40px;
  padding: 0.5rem 1.2rem;
}}
.controls button {{
  background: none;
  border: 1px solid rgba(30, 30, 48, 0.8);
  color: var(--text);
  width: 32px; height: 32px;
  border-radius: 50%;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex; align-items: center; justify-content: center;
}}
.controls button:hover {{
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}}
.controls button.active {{
  background: var(--accent);
  color: #fff;
  border-color: var(--accent);
}}
.controls .slider-wrap {{
  display: flex; align-items: center; gap: 0.5rem;
  min-width: 240px;
}}
.controls input[type=range] {{
  -webkit-appearance: none;
  flex: 1;
  height: 3px;
  border-radius: 2px;
  background: rgba(30, 30, 48, 0.8);
  outline: none;
}}
.controls input[type=range]::-webkit-slider-thumb {{
  -webkit-appearance: none;
  width: 14px; height: 14px;
  border-radius: 50%;
  background: var(--accent);
  cursor: pointer;
  box-shadow: 0 0 10px rgba(124, 111, 240, 0.4);
}}
.controls .step-label {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem;
  color: var(--text-dim);
  min-width: 50px;
  text-align: center;
}}

/* Tooltip */
.tooltip {{
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
}}
.tooltip.show {{
  opacity: 1;
  transform: translateY(0);
}}
.tooltip .tt-tag {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  margin-bottom: 0.3rem;
}}
.tooltip .tt-tag.core {{ color: var(--core); }}
.tooltip .tt-tag.mutable {{ color: var(--mutable); }}
.tooltip .tt-section {{
  font-size: 0.65rem;
  color: var(--text-dim);
  margin-bottom: 0.2rem;
}}

/* Legend */
.hud-legend {{
  position: fixed;
  bottom: 5rem; left: 50%; transform: translateX(-50%);
  z-index: 100;
  display: flex; gap: 1.2rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  color: var(--text-dim);
  letter-spacing: 0.04em;
}}
.hud-legend .l-item {{
  display: flex; align-items: center; gap: 0.35rem;
}}
.hud-legend .l-dot {{
  width: 7px; height: 7px; border-radius: 50%;
}}

/* Change notification */
.change-toast {{
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
}}
.change-toast.show {{
  opacity: 1;
  transform: translateX(0);
}}
.change-toast .ct-label {{
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.6rem;
  font-weight: 700;
  color: var(--mutable);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 0.3rem;
}}
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
const DATA = {data_json};

// --- Color palette ---
const SECTION_COLORS = {{
  'Personality': '#f0a050',
  'Philosophy': '#7c6ff0',
  'Boundaries': '#e05050',
  'Continuity': '#50b8e0',
}};
function secColor(name) {{
  for (const [k, v] of Object.entries(SECTION_COLORS)) {{
    if (name && name.includes(k)) return v;
  }}
  return '#888';
}}
function hexToRgb(hex) {{
  const r = parseInt(hex.slice(1,3),16);
  const g = parseInt(hex.slice(3,5),16);
  const b = parseInt(hex.slice(5,7),16);
  return [r, g, b];
}}

// --- Build node tree ---
function buildNodes() {{
  const nodes = [];
  const edges = [];
  let id = 0;

  // Root
  const root = {{ id: id++, type: 'root', label: 'SOUL', x: 0, y: 0, r: 28, color: '#7c6ff0', depth: 0, growStep: -1 }};
  nodes.push(root);

  let growIdx = 0;

  DATA.soul_tree.forEach((sec, si) => {{
    const color = secColor(sec.text);
    const sNode = {{ id: id++, type: 'section', label: sec.text, x: 0, y: 0, r: 18, color, depth: 1, growStep: growIdx++, parentId: root.id }};
    nodes.push(sNode);
    edges.push({{ from: root.id, to: sNode.id, color }});

    sec.children.forEach((child, ci) => {{
      if (child.type === 'subsection') {{
        const subNode = {{ id: id++, type: 'subsection', label: child.text, x: 0, y: 0, r: 12, color, depth: 2, growStep: growIdx++, parentId: sNode.id }};
        nodes.push(subNode);
        edges.push({{ from: sNode.id, to: subNode.id, color }});

        (child.children || []).forEach((b, bi) => {{
          const isAdded = DATA.changes.some(c => c.after && c.after.trim() === b.raw.trim());
          const bNode = {{
            id: id++, type: 'bullet', label: b.text, tag: b.tag,
            x: 0, y: 0, r: b.tag === 'CORE' ? 7 : 6,
            color: b.tag === 'CORE' ? '#e05050' : (b.tag === 'MUTABLE' ? '#50c878' : '#666'),
            depth: 3, growStep: growIdx++, parentId: subNode.id,
            raw: b.raw, isChangeAdded: isAdded,
            section: sec.text, subsection: child.text,
          }};
          nodes.push(bNode);
          edges.push({{ from: subNode.id, to: bNode.id, color: bNode.color }});
        }});
      }} else if (child.type === 'bullet') {{
        const b = child;
        const bNode = {{
          id: id++, type: 'bullet', label: b.text, tag: b.tag,
          x: 0, y: 0, r: b.tag === 'CORE' ? 7 : 6,
          color: b.tag === 'CORE' ? '#e05050' : (b.tag === 'MUTABLE' ? '#50c878' : '#666'),
          depth: 2, growStep: growIdx++, parentId: sNode.id,
          raw: b.raw, isChangeAdded: false,
          section: sec.text, subsection: '',
        }};
        nodes.push(bNode);
        edges.push({{ from: sNode.id, to: bNode.id, color: bNode.color }});
      }}
    }});
  }});

  // Mark change-added nodes with the change index
  DATA.changes.forEach((c, ci) => {{
    if (c.after) {{
      const match = nodes.find(n => n.raw && n.raw.trim() === c.after.trim());
      if (match) match.changeIdx = ci;
    }}
  }});

  return {{ nodes, edges, totalGrowSteps: growIdx }};
}}

// --- Layout: radial tree ---
function layoutRadial(nodes, edges) {{
  const childrenOf = {{}};
  edges.forEach(e => {{
    if (!childrenOf[e.from]) childrenOf[e.from] = [];
    childrenOf[e.from].push(e.to);
  }});

  const nodeMap = {{}};
  nodes.forEach(n => nodeMap[n.id] = n);

  function countLeaves(nid) {{
    const kids = childrenOf[nid] || [];
    if (kids.length === 0) return 1;
    return kids.reduce((s, k) => s + countLeaves(k), 0);
  }}

  function layout(nid, angleStart, angleEnd, radius) {{
    const node = nodeMap[nid];
    const kids = childrenOf[nid] || [];
    const mid = (angleStart + angleEnd) / 2;

    if (nid !== 0) {{
      node.x = Math.cos(mid) * radius;
      node.y = Math.sin(mid) * radius;
    }}

    if (kids.length === 0) return;

    const totalLeaves = countLeaves(nid);
    let cursor = angleStart;

    kids.forEach(kid => {{
      const kidNode = nodeMap[kid];
      const leaves = countLeaves(kid);
      const share = (leaves / totalLeaves) * (angleEnd - angleStart);
      const extra = radiusBonus(kidNode);
      layout(kid, cursor, cursor + share, radius + radiusStep(kidNode.depth) + extra);
      cursor += share;
    }});
  }}

  function radiusStep(depth) {{
    if (depth === 1) return 160;
    if (depth === 2) return 130;
    return 110;
  }}

  // Push change-added nodes further out from the core
  function radiusBonus(node) {{
    if (node.changeIdx !== undefined) {{
      // Each successive change gets pushed further out
      return 60 + node.changeIdx * 40;
    }}
    return 0;
  }}

  layout(0, -Math.PI, Math.PI, 0);
}}

// --- Canvas renderer ---
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
let W, H;
let camX = 0, camY = 0, camZoom = 1;
let targetCamX = 0, targetCamY = 0, targetCamZoom = 1;
let camSmooth = 0.06; // lerp speed
let isDragging = false, dragStartX, dragStartY, camStartX, camStartY;
let hoveredNode = null;
let animTime = 0;

const {{ nodes, edges, totalGrowSteps }} = buildNodes();
layoutRadial(nodes, edges);

// Current visible step
let currentStep = DATA.changes.length; // max
let maxGrowStep = totalGrowSteps;
const slider = document.getElementById('timeline');
slider.max = DATA.changes.length;
slider.value = DATA.changes.length;

// Determine which growSteps are visible at each timeline step
function getVisibleGrowStep(timelineStep) {{
  // All nodes visible except those added by changes AFTER timelineStep
  const hiddenChanges = new Set();
  for (let i = DATA.changes.length - 1; i >= timelineStep; i--) {{
    if (DATA.changes[i].after) hiddenChanges.add(DATA.changes[i].after.trim());
  }}
  return hiddenChanges;
}}

// Particles for celebrations
let particles = [];
function spawnParticles(x, y, color) {{
  const [r, g, b] = hexToRgb(color);
  for (let i = 0; i < 20; i++) {{
    const angle = Math.random() * Math.PI * 2;
    const speed = 1 + Math.random() * 3;
    particles.push({{
      x, y,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      life: 1,
      decay: 0.01 + Math.random() * 0.02,
      r, g, b,
      size: 2 + Math.random() * 3,
    }});
  }}
}}

function resize() {{
  W = window.innerWidth;
  H = window.innerHeight;
  canvas.width = W * devicePixelRatio;
  canvas.height = H * devicePixelRatio;
  canvas.style.width = W + 'px';
  canvas.style.height = H + 'px';
  ctx.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0);
}}
window.addEventListener('resize', resize);
resize();

// Node grow animation state
const nodeAnim = {{}};
nodes.forEach(n => {{
  nodeAnim[n.id] = {{ scale: 0, targetScale: 1, visible: true }};
}});

function setVisibility() {{
  const hidden = getVisibleGrowStep(currentStep);
  nodes.forEach(n => {{
    if (n.raw && hidden.has(n.raw.trim())) {{
      nodeAnim[n.id].targetScale = 0;
      nodeAnim[n.id].visible = false;
    }} else {{
      nodeAnim[n.id].targetScale = 1;
      nodeAnim[n.id].visible = true;
    }}
  }});
}}
setVisibility();
// Start fully visible
nodes.forEach(n => {{ nodeAnim[n.id].scale = nodeAnim[n.id].targetScale; }});

function screenToWorld(sx, sy) {{
  return [(sx - W/2) / camZoom + camX, (sy - H/2) / camZoom + camY];
}}

function worldToScreen(wx, wy) {{
  return [(wx - camX) * camZoom + W/2, (wy - camY) * camZoom + H/2];
}}

// --- Drawing ---
function draw() {{
  animTime += 0.016;

  // Smooth camera
  camX += (targetCamX - camX) * camSmooth;
  camY += (targetCamY - camY) * camSmooth;
  camZoom += (targetCamZoom - camZoom) * camSmooth;

  // Animate node scales
  nodes.forEach(n => {{
    const a = nodeAnim[n.id];
    a.scale += (a.targetScale - a.scale) * 0.08;
    if (Math.abs(a.scale - a.targetScale) < 0.001) a.scale = a.targetScale;
  }});

  // Update particles
  particles = particles.filter(p => {{
    p.x += p.vx;
    p.y += p.vy;
    p.vx *= 0.97;
    p.vy *= 0.97;
    p.life -= p.decay;
    return p.life > 0;
  }});

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

  const nodeMap = {{}};
  nodes.forEach(n => nodeMap[n.id] = n);

  // Draw edges (organic bezier curves)
  edges.forEach(e => {{
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

    ctx.strokeStyle = `rgba(${{r}},${{g}},${{b}},${{alpha * 0.25}})`;
    ctx.lineWidth = to.depth <= 1 ? 2.5 : (to.depth === 2 ? 1.5 : 1);
    ctx.stroke();
  }});

  // Draw nodes
  nodes.forEach(n => {{
    const a = nodeAnim[n.id];
    if (a.scale < 0.01) return;

    const s = a.scale;
    const r = n.r * s;
    const [cr, cg, cb] = hexToRgb(n.color);
    const isHov = hoveredNode && hoveredNode.id === n.id;

    // Glow
    if (n.type !== 'bullet' || isHov) {{
      const glowR = r * (isHov ? 4 : 2.5);
      const glow = ctx.createRadialGradient(n.x, n.y, r * 0.5, n.x, n.y, glowR);
      glow.addColorStop(0, `rgba(${{cr}},${{cg}},${{cb}},${{s * (isHov ? 0.25 : 0.12)}})`);
      glow.addColorStop(1, 'transparent');
      ctx.fillStyle = glow;
      ctx.fillRect(n.x - glowR, n.y - glowR, glowR * 2, glowR * 2);
    }}

    // Node circle
    ctx.beginPath();
    ctx.arc(n.x, n.y, r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(${{cr}},${{cg}},${{cb}},${{s * (isHov ? 0.9 : 0.7)}})`;
    ctx.fill();

    // Border ring
    if (n.type === 'root' || n.type === 'section' || isHov) {{
      ctx.beginPath();
      ctx.arc(n.x, n.y, r + 1.5, 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(${{cr}},${{cg}},${{cb}},${{s * 0.5}})`;
      ctx.lineWidth = 1;
      ctx.stroke();
    }}

    // Pulse ring for change-added nodes at current step
    if (n.changeIdx !== undefined && n.changeIdx === currentStep - 1) {{
      const pulse = (Math.sin(animTime * 3) + 1) * 0.5;
      ctx.beginPath();
      ctx.arc(n.x, n.y, r + 4 + pulse * 6, 0, Math.PI * 2);
      ctx.strokeStyle = `rgba(${{cr}},${{cg}},${{cb}},${{0.3 + pulse * 0.3}})`;
      ctx.lineWidth = 1.5;
      ctx.stroke();
    }}

    // Labels
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    if (n.type === 'root') {{
      ctx.font = `700 ${{14 * s}}px 'JetBrains Mono', monospace`;
      ctx.fillStyle = `rgba(255,255,255,${{s}})`;
      ctx.fillText(n.label, n.x, n.y);
    }} else if (n.type === 'section') {{
      ctx.font = `500 ${{11 * s}}px 'JetBrains Mono', monospace`;
      ctx.fillStyle = `rgba(255,255,255,${{s * 0.9}})`;
      ctx.fillText(n.label, n.x, n.y + r + 14);
    }} else if (n.type === 'subsection' && camZoom > 0.5) {{
      ctx.font = `400 ${{9 * s}}px 'DM Sans', sans-serif`;
      ctx.fillStyle = `rgba(200,200,216,${{s * 0.7}})`;
      const maxW = 100;
      ctx.fillText(n.label.length > 18 ? n.label.slice(0, 16) + '…' : n.label, n.x, n.y + r + 12);
    }}
  }});

  // Particles
  particles.forEach(p => {{
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.size * p.life, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(${{p.r}},${{p.g}},${{p.b}},${{p.life * 0.6}})`;
    ctx.fill();
  }});

  ctx.restore();
  requestAnimationFrame(draw);
}}

// --- Interaction ---
canvas.addEventListener('mousedown', e => {{
  isDragging = true;
  dragStartX = e.clientX;
  dragStartY = e.clientY;
  camStartX = camX;
  camStartY = camY;
  document.body.classList.add('dragging');
}});
window.addEventListener('mousemove', e => {{
  if (isDragging) {{
    const nx = camStartX - (e.clientX - dragStartX) / camZoom;
    const ny = camStartY - (e.clientY - dragStartY) / camZoom;
    camX = targetCamX = nx;
    camY = targetCamY = ny;
  }}

  // Hover detection
  const [wx, wy] = screenToWorld(e.clientX, e.clientY);
  let found = null;
  // Check in reverse (top nodes last drawn = on top)
  for (let i = nodes.length - 1; i >= 0; i--) {{
    const n = nodes[i];
    const a = nodeAnim[n.id];
    if (a.scale < 0.1) continue;
    const dx = wx - n.x;
    const dy = wy - n.y;
    const hitR = Math.max(n.r * a.scale, 10);
    if (dx*dx + dy*dy < hitR * hitR) {{
      found = n;
      break;
    }}
  }}

  hoveredNode = found;
  const tooltip = document.getElementById('tooltip');
  if (found && (found.type === 'bullet' || found.type === 'subsection')) {{
    tooltip.classList.add('show');
    tooltip.style.left = (e.clientX + 16) + 'px';
    tooltip.style.top = (e.clientY - 10) + 'px';
    // Clamp
    if (e.clientX + 340 > W) tooltip.style.left = (e.clientX - 330) + 'px';
    if (e.clientY + 80 > H) tooltip.style.top = (e.clientY - 60) + 'px';

    const tagEl = document.getElementById('tt-tag');
    const secEl = document.getElementById('tt-section');
    const textEl = document.getElementById('tt-text');

    if (found.tag) {{
      tagEl.textContent = found.tag;
      tagEl.className = 'tt-tag ' + found.tag.toLowerCase();
      tagEl.style.display = '';
    }} else {{
      tagEl.style.display = 'none';
    }}
    secEl.textContent = (found.section || '') + (found.subsection ? ' › ' + found.subsection : '');
    textEl.textContent = found.label;
  }} else {{
    tooltip.classList.remove('show');
  }}
}});
window.addEventListener('mouseup', () => {{
  isDragging = false;
  document.body.classList.remove('dragging');
}});

canvas.addEventListener('wheel', e => {{
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
}}, {{ passive: false }});

// --- Touch support ---
let lastTouchDist = 0;
canvas.addEventListener('touchstart', e => {{
  e.preventDefault();
  if (e.touches.length === 1) {{
    isDragging = true;
    dragStartX = e.touches[0].clientX;
    dragStartY = e.touches[0].clientY;
    camStartX = camX;
    camStartY = camY;
  }} else if (e.touches.length === 2) {{
    isDragging = false;
    const dx = e.touches[0].clientX - e.touches[1].clientX;
    const dy = e.touches[0].clientY - e.touches[1].clientY;
    lastTouchDist = Math.sqrt(dx * dx + dy * dy);
  }}
}}, {{ passive: false }});
canvas.addEventListener('touchmove', e => {{
  e.preventDefault();
  if (e.touches.length === 1 && isDragging) {{
    const nx = camStartX - (e.touches[0].clientX - dragStartX) / camZoom;
    const ny = camStartY - (e.touches[0].clientY - dragStartY) / camZoom;
    camX = targetCamX = nx;
    camY = targetCamY = ny;
  }} else if (e.touches.length === 2) {{
    const dx = e.touches[0].clientX - e.touches[1].clientX;
    const dy = e.touches[0].clientY - e.touches[1].clientY;
    const dist = Math.sqrt(dx * dx + dy * dy);
    if (lastTouchDist > 0) {{
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
    }}
    lastTouchDist = dist;
  }}
}}, {{ passive: false }});
canvas.addEventListener('touchend', e => {{
  isDragging = false;
  lastTouchDist = 0;
}});

// --- Timeline controls ---
const stepLabel = document.getElementById('step-label');

function setStep(s) {{
  currentStep = s;
  slider.value = s;
  setVisibility();
  if (s === 0) {{
    stepLabel.textContent = 'origin';
  }} else {{
    const c = DATA.changes[s - 1];
    stepLabel.textContent = (c.timestamp || '').slice(11, 16) || '#' + s;
  }}
}}

slider.oninput = () => setStep(parseInt(slider.value));

// Play
let playing = false;
let playTimer = null;
document.getElementById('btn-play').onclick = () => {{
  const btn = document.getElementById('btn-play');
  if (playing) {{
    clearInterval(playTimer);
    playing = false;
    btn.textContent = '▶';
    btn.classList.remove('active');
    return;
  }}
  playing = true;
  btn.textContent = '⏸';
  btn.classList.add('active');

  // Start at origin: all base nodes visible, no changes applied
  setStep(0);

  // Instantly grow all base (non-change) nodes with a quick stagger
  nodes.forEach(n => {{
    const a = nodeAnim[n.id];
    if (n.changeIdx === undefined && a.visible) {{
      setTimeout(() => {{ a.targetScale = 1; }}, n.growStep * 25);
    }}
  }});

  // Fit tight on the base tree first
  setTimeout(() => fitToVisible(false), 200);

  // After base tree is grown, play changes one by one at uniform pace
  const baseGrowTime = Math.min(maxGrowStep * 25 + 400, 1500);
  const changePause = 2000; // 2 seconds per change

  let changeIdx = 0;
  setTimeout(() => {{
    if (!playing) return;
    // Fit to base tree before changes start
    fitToVisible(false);

    playTimer = setInterval(() => {{
      changeIdx++;
      if (changeIdx <= DATA.changes.length) {{
        setStep(changeIdx);
        // Smoothly zoom out to include the new node
        fitToVisible(false);
        // Celebrate the new node
        const c = DATA.changes[changeIdx - 1];
        if (c && c.after) {{
          const match = nodes.find(n => n.raw && n.raw.trim() === c.after.trim());
          if (match) {{
            spawnParticles(match.x, match.y, match.color);
            const toast = document.getElementById('change-toast');
            document.getElementById('ct-text').textContent =
              c.after.replace(/\\s*\\[(CORE|MUTABLE)\\]\\s*/g, '').replace(/^- /, '').slice(0, 120);
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), changePause - 300);
          }}
        }}
      }} else {{
        clearInterval(playTimer);
        playing = false;
        btn.textContent = '▶';
        btn.classList.remove('active');
      }}
    }}, changePause);
  }}, baseGrowTime);
}};

document.getElementById('btn-reset').onclick = () => {{
  if (playing) {{
    clearInterval(playTimer);
    playing = false;
    document.getElementById('btn-play').textContent = '▶';
    document.getElementById('btn-play').classList.remove('active');
  }}
  // Reset all scales to 0, then grow
  nodes.forEach(n => {{
    nodeAnim[n.id].scale = 0;
    nodeAnim[n.id].targetScale = 0;
  }});
  setStep(0);
  // Quick regrow
  setTimeout(() => {{
    nodes.forEach(n => {{
      if (!n.raw || !getVisibleGrowStep(0).has(n.raw.trim())) {{
        setTimeout(() => {{ nodeAnim[n.id].targetScale = 1; }}, n.growStep * 40);
      }}
    }});
    fitToVisible(false);
  }}, 200);
}};

// Fit camera to visible nodes, always centered on SOUL (0,0)
function fitToVisible(instant) {{
  let maxDist = 0;
  nodes.forEach(n => {{
    if (nodeAnim[n.id].scale > 0.1 || nodeAnim[n.id].targetScale > 0.5) {{
      const dist = Math.sqrt(n.x * n.x + n.y * n.y) + n.r + 40;
      if (dist > maxDist) maxDist = dist;
    }}
  }});
  maxDist = Math.max(maxDist, 80); // minimum extent
  const padding = 1.15;
  const halfExtent = maxDist * padding;
  const zoom = Math.min(W / (halfExtent * 2), H / (halfExtent * 2), 2.5);

  targetCamX = 0;
  targetCamY = 0;
  targetCamZoom = zoom;
  if (instant) {{
    camX = targetCamX;
    camY = targetCamY;
    camZoom = targetCamZoom;
  }}
}}

document.getElementById('btn-fit').onclick = () => fitToVisible(false);

// Legend
document.getElementById('legend').innerHTML = [
  {{ c: '#e05050', l: 'CORE' }},
  {{ c: '#50c878', l: 'MUTABLE' }},
  ...Object.entries(SECTION_COLORS).map(([k, v]) => ({{ c: v, l: k }})),
].map(i => `<div class="l-item"><div class="l-dot" style="background:${{i.c}}"></div>${{i.l}}</div>`).join('');

// Init
// Start fully grown
nodes.forEach(n => {{
  nodeAnim[n.id].scale = nodeAnim[n.id].targetScale;
}});
setStep(DATA.changes.length);
setTimeout(() => fitToVisible(true), 100);
draw();
</script>
</body>
</html>"""


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
                    self.wfile.write(json.dumps({{"enabled": enabled}}).encode())

                elif self.path == "/api/model/config":
                    # Get or set model configuration
                    model_config_path = os.path.join(workspace, "memory", "reality", "model_config.json")

                    if self.command == 'GET':
                        # Return current config
                        config = {{"models": {{}}}}
                        if os.path.exists(model_config_path):
                            try:
                                with open(model_config_path) as f:
                                    config = json.load(f)
                            except:
                                pass
                        # Don't send API key to frontend for security
                        config_safe = {{"models": config.get("models", {{}})}}
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps(config_safe).encode())
                    else:
                        # Save config
                        length = int(self.headers.get("Content-Length", 0))
                        body = self.rfile.read(length).decode("utf-8")
                        try:
                            data = json.loads(body)
                            models = data.get("models", {{}})
                            api_key = data.get("api_key", "")

                            # Save to file (API key stored locally only)
                            config = {{"models": models}}
                            if api_key:
                                config["api_key"] = api_key

                            os.makedirs(os.path.dirname(model_config_path), exist_ok=True)
                            with open(model_config_path, "w") as f:
                                json.dump(config, f, indent=2)

                            self.send_response(200)
                            self.send_header("Content-Type", "application/json")
                            self.end_headers()
                            self.wfile.write(json.dumps({{"success": True}}).encode())
                            print(f"  ✓ Model config saved")
                        except Exception as e:
                            self.send_response(500)
                            self.send_header("Content-Type", "application/json")
                            self.end_headers()
                            self.wfile.write(json.dumps({{"success": False, "message": str(e)}}).encode())

                elif self.path == "/api/genesis/request-status":
                    request_path = os.path.join(workspace, "memory", "reality", "genesis_request.json")
                    pending = os.path.exists(request_path)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({{"pending": pending}}).encode())

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
                            json.dump({{"enabled": enabled, "updated_at": datetime.now().isoformat()}}, f, indent=2)
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({{"success": True, "enabled": enabled}}).encode())
                        print(f"  \u2713 Genesis enabled: {enabled}")
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({{"success": False, "message": str(e)}}).encode())

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
                            json.dump({{"prompt": prompt_text, "requested_at": datetime.now().isoformat()}}, f, indent=2)
                        self.send_response(200)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({{"success": True}}).encode())
                        print(f"  \u2713 Genesis request saved")
                    except Exception as e:
                        self.send_response(500)
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps({{"success": False, "message": str(e)}}).encode())

                elif self.path == "/api/genesis/request-status":
                    request_path = os.path.join(workspace, "memory", "reality", "genesis_request.json")
                    pending = os.path.exists(request_path)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({{"pending": pending}}).encode())

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

        with socketserver.TCPServer(("127.0.0.1", port), SoulEvolutionHandler) as httpd:
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
