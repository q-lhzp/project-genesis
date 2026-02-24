# Project Genesis Master Plan: Core Lifecycle & Living World

## 1. Vision
Project Genesis is a decentralized Multi-Agent Cluster (MAC) simulation of human life. It aims for high-fidelity biological, social, and economic realism, combined with neural bootstrapping and advanced identity governance.

## 2. Infrastructure (Phase 6 - Implemented)
- **Modular Toggles:** `utility`, `psychology`, `skills`, `world`, `reputation`, `desktop`, `legacy`, `genesis`.
- **Real-World Sync:** 24h cycle, seasonal tracking, and weather estimation.
- **Skill XP:** Competence tracking.
- **Psychology:** Trauma/Resilience system.

## 3. Origin Engine (Phase 7 - Implemented)
- **Neural Bootstrapping:** Generate a complete character (JSON/Markdown) from a prompt.
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
- **Impact:** Affects shopping prices, job market, and networking.

## 7. Skill Mastery (Phase 11 - Implemented)
**Goal:** Make skill levels mechanically relevant.
- **Skill Multipliers:** Affect income (Professional), hunger (Cooking), and social gains (Charisma).

## 8. Living World Integration (Phase 14 - Implemented)
**Goal:** Connect the simulation to the real world.
- **Live News:** Fetching RSS headlines based on character location.
- **Autonomous Browsing:** Visual research via Playwright.

## 9. Autonomous Social Life (Phase 12 - Implemented)
**Goal:** NPCs initiate contact autonomously to create social pressure.
- **Mechanic:** 15% chance per turn for an NPC to send a message based on relationship dynamics.

## 10. Desktop Sovereignty (Phase 15 - Implemented)
**Goal:** AI control over the host machine.
- **Machine Ownership:** AI acts as the owner of the machine.
- **Visual Browser:** Visible Chromium instances on desktop.

## 11. Digital Extroversion (Phase 16 - Implemented)
**Goal:** Interaction with humans and external environments (Discord, Games).
- **Universal Input:** Mouse/Keyboard control (Wayland/X11).
- **Interactive Socializing:** Autonomously chat on Discord/WhatsApp.

## 12. Neural Photography & Face-ID (Phase 17 - Implemented)
**Goal:** Consistent visual identity and facial analysis.
- **Face-ID:** Extracts and compares detailed facial features for consistency.
- **Reality Camera:** High-end cinematic snapshots (35mm Fujifilm, 8k).

## 13. Cognitive Resonance (Phase 18 - Implemented)
**Goal:** Persistent, searchable long-term memory via Mem0.
- **Integration:** Automatically queries Mem0 for relevant facts in `before_prompt_build`.
- **Mem0 Sync:** Uses local **Ollama (bge-m3)** for 100% standalone privacy.

## 14. Visual NPC Network (Phase 19 - Implemented)
**Goal:** Consistent visual identity for all social contacts.
- **Contact CRM:** Manage NPCs with visual descriptions and avatars.
- **Multi-Subject Photos:** Group shots with AI character and friends.

## 15. Vocal Identity (Phase 20 - Implemented)
**Goal:** High-speed local Text-to-Speech via **Chatterbox-Turbo**.
- **Voice Lab:** Control pitch, speed, and emotionality. Support for voice cloning via .wav upload.

## 16. The Vault (Phase 21 - Implemented)
**Goal:** Real-world asset trading (Crypto/Stocks) via Kraken/Alpaca APIs.
- **Safety:** Paper trading by default.
- **Integration:** AI can autonomously manage a real wealth portfolio.

## 17. Modular Framework (Phase 22 - Implemented)
**Goal:** High-fidelity code maintenance and scalability.
- **src/ Structure:** Monolith index.ts split into logical modules (simulation, hooks, tools, prompts).
- **Benefits:** Faster development, better testability, and secure bridge execution.

## 18. 3D-Avatar-Sync (Phase 23 - Upcoming)
**Goal:** Real-time 3D representation via VRM.
- **Lip-Sync:** Drive VRM blendshapes from vocal output.
- **Emotion-Mapping:** Visualizing mood through facial expressions.
- **Wardrobe Sync:** Automatic mesh/texture updates based on worn clothes.

## 19. Tool Specifications (Consolidated)
- `reality_genesis`: bootstrap | patch | rollback
- `reality_profile`: save | load | list | delete
- `reality_skill`: train | list | check
- `reality_browse`: browse | click | type (VISUAL)
- `reality_desktop`: click | type | key | vision | set_wallpaper
- `reality_news`: fetch | process (RSS)
- `reality_camera`: capture (Neural Photo)
- `reality_vision_analyze`: analyze (Face-ID)
- `reality_voice`: synthesize (TTS)
- `reality_trade`: trade (Crypto/Stocks)

## 20. WebUI Requirements (`soul-viz.py`)
- **News Ticker:** Real-time world events.
- **Mental Activity:** Visualized inner voice and research preview.
- **Life Stream:** Photo gallery.
- **Memory/Vault Tabs:** Management interfaces.
- **Live Avatar:** (Upcoming) 3D VRM viewer.
