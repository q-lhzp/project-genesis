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
- **Workflow:** User Prompt -> Agent Processing -> `reality_genesis(action: "bootstrap")` -> File Overwrite.

## 4. Identity Governance (Phase 8 - Implemented)
**Goal:** Empower the user to manage multiple lives, tweak existing characters, and revert simulation errors.
- **Evolutionary Edits:** Patching existing characters.
- **Profile Management:** Character slots in `memory/profiles/`.
- **Time Vault:** Daily snapshots and rollbacks.

## 5. Multi-Model Synergy (Phase 9 - Implemented)
**Goal:** Optimized specialized AI models for cognitive tasks.
- **Role Mapping:** Persona (Opus), Analyst (Sonnet), Limbic/World (Haiku/Flash).
- **Cost Optimization:** Pruned context for lightweight roles.

## 6. Social Reputation (Phase 10 - Implemented)
**Goal:** Global standing and circle-based dynamics.
- **Impact:** Affects shopping prices, job market, and network quality.

## 7. Phase 11: Real-Impact Skills (Implemented)
**Goal:** Make skill levels mechanically relevant.
- **Skill Multipliers:**
    - *Work:* Income * (1 + Level/10).
    - *Needs:* Efficiency (e.g., eat hunger reduction * (1 + Level/20)).
    - *Charisma:* Social gains * (1 + Level/15).

## 8. Phase 14: World News & Autonomous Browsing (Implemented)
**Goal:** Connect the simulation to the host's real-world environment and the web.
- **News Feed:** `world_engine` role fetches real news based on `location.city` and `interests`.
- **Impact:** News adjust `market_modifier` or trigger world events.
- **Autonomous Browsing:** Agent tool `reality_browse` for research and internet exploration.

## 9. Phase 15: Desktop Sovereignty & Visual Browsing (Implemented)
**Goal:** Give the AI visible control over the host machine and reinforce ownership.
- **Visual Browser:** `reality_browse` launches a visible Chromium instance (Playwright `headless=False`) on the user's desktop. The user sees the AI scrolling and reading.
- **System Ownership:** The prompt explicitly states: *"This is YOUR computer. You have full control."*
- **Self-Maintenance:** The AI can install necessary packages (pip/npm/apt) to perform its tasks.

## 10. Tool Specifications (Consolidated)
- `reality_genesis`: bootstrap | patch | rollback
- `reality_profile`: save | load | list | delete
- `reality_skill`: train | list | check
- `reality_browse`: search | read (Web interaction)
- `reality_news`: fetch | process (World Engine only)

## 10. WebUI Requirements (`soul-viz.py`)
- **News Ticker:** Real-time world events on dashboard.
- **Skill Tree:** Graphical progression visualization.
- **Control Center:** Master toggles for all simulation modules.
