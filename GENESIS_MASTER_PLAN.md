# Project Genesis Master Plan: Core Lifecycle & Living World

## 1. Vision
Project Genesis is a decentralized Multi-Agent Cluster (MAC) simulation of human life. It aims for high-fidelity biological, social, and economic realism, combined with neural bootstrapping and advanced identity governance.

## 2. Infrastructure (Phase 6 - Implemented)
- **Modular Toggles:** `utility`, `psychology`, `skills`, `world`, `reputation`, `desktop`, `legacy`, `genesis`.
- **Real-World Sync:** 24h cycle, seasonal tracking, and weather estimation.
- **Skill XP:** Competence tracking.
- **Psychology:** Trauma/Resilience system.

## 3. Origin Engine (Phase 7 - Implemented)
- **Neural Bootstrapping:** Generate a complete character (JSON/Markdown) from a natural language prompt.
- **Evolutionary Edits:** Patching existing characters.

## 4. Identity Governance (Phase 8 - Implemented)
**Goal:** Manage multiple lives and recover from undesirable simulation paths.
- **Profile Management:** Character slots in `memory/profiles/`.
- **Time Vault:** Daily snapshots and rollbacks.

## 5. Multi-Model Synergy (Phase 9 - Implemented)
**Goal:** Optimized specialized AI models for cognitive tasks.
- **Role Mapping:** Persona (Opus), Analyst (Sonnet), Limbic/World (Haiku/Flash).
- **Cost Optimization:** Pruned context for lightweight roles.

## 6. Social Reputation (Phase 10 - Implemented)
**Goal:** Global standing and circle-based dynamics.
- **Impact:** Affects shopping prices, job market, and network quality.

## 7. Skill Mastery (Phase 11 - Implemented)
**Goal:** Make skill levels mechanically relevant.
- **Skill Multipliers:** Affect income (Professional), hunger (Cooking), and social gains (Charisma).

## 8. Living World Integration (Phase 14 - Implemented)
**Goal:** Connect the simulation to the real world.
- **News Feed:** `world_engine` fetches LIVE RSS headlines based on character location.
- **Autonomous Browsing:** Agent tool `reality_browse` for research via a visual browser.

## 9. Autonomous Social Life (Phase 12 - Implemented)
**Goal:** NPCs initiate contact autonomously to create social pressure.
- **Mechanic:** 15% chance per turn for an NPC to send a message based on relationship dynamics.

## 10. Desktop Sovereignty (Phase 15 - Implemented)
**Goal:** AI control over the host machine.
- **Visual Browser:** Launch visible Chromium instances on the desktop.
- **System Ownership:** AI is the explicit owner of the machine.

## 11. Digital Extroversion (Phase 16 - Implemented)
**Goal:** Interaction with humans and external environments (Discord, Games).
- **Interactive Browser:** `reality_browse` supports `click` and `type` with session persistence.
- **Universal Input:** `reality_desktop` expanded with mouse/keyboard control (Wayland/X11).
- **Vision:** Screenshots allow the AI to "see" games like 3DXChat.

## 12. Neural Photography & Visual Identity (Phase 17 - Upcoming)
**Goal:** Give the AI a consistent visual presence via AI-generated "selfies" and "vacation photos".
- **Physical Manifest:** Each character has a detailed descriptive "Face-ID" (eyes, bone structure, skin details) used for prompt consistency.
- **Wardrobe Sync:** Photos automatically include the currently equipped outfit from `wardrobe.json`.
- **Reality Camera:** Tool `reality_camera` allows the AI to "capture" moments. It uses local or external image generators (Flux, Venice, Nano Banana).
- **Visual Life Stream:** A new "Instagram-style" tab in the WebUI displaying the AI's visual history.

## 13. Tool Specifications (Consolidated)
- `reality_genesis`: bootstrap | patch | rollback
- `reality_profile`: save | load | list | delete
- `reality_skill`: train | list | check
- `reality_browse`: browse | click | type (VISUAL)
- `reality_desktop`: click | type | key | vision | set_wallpaper
- `reality_news`: fetch | process (RSS)
- `reality_camera`: capture (Type: selfie, mirror, candid)

## 14. WebUI Requirements (`soul-viz.py`)
- **News Ticker:** Real-time world events on dashboard.
- **Mental Activity:** Visualized inner voice, web research, and incoming social messages.
- **Life Stream:** Gallery of AI-generated photos.
- **Skill Tree:** (Pending) Graphical progression visualization.
