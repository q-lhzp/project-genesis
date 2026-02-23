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
- **Profile Management:** Character slots in `memory/profiles/`.
- **Time Vault:** Daily snapshots and rollbacks.

## 5. Multi-Model Synergy (Phase 9 - Implemented)
- **Role Mapping:** Persona (Opus), Analyst (Sonnet), Limbic/World (Haiku/Flash).
- **Cost Optimization:** Pruned context for lightweight roles.

## 6. Social Reputation (Phase 10 - Implemented)
- **Global Score:** From Pariah to Icon.
- **Circle Dynamics:** Affects prices, job market, and networking.

## 7. Skill Mastery (Phase 11 - Implemented)
- **Mechanical Boni:** Professional (Income), Cooking (Hunger), Charisma (Social).

## 8. Living World Integration (Phase 14 - Implemented)
- **Live News:** Fetching RSS headlines based on character location.
- **Autonomous Browsing:** Visual research via Playwright.

## 9. Autonomous Social Life (Phase 12 - Implemented)
- **NPC Initiative:** Autonomous contact (15% chance per turn).

## 10. Desktop Sovereignty (Phase 15 - Implemented)
- **Machine Ownership:** AI acts as the owner of the machine.
- **Visual Browser:** Visible Chromium instances on desktop.

## 11. Digital Extroversion (Phase 16 - Implemented)
- **Universal Input:** Mouse/Keyboard control (Wayland/X11).
- **Interactive Socializing:** Autonomously chat on Discord/WhatsApp.

## 12. Neural Photography & Face-ID (Phase 17 - Implemented)
- **Face-ID:** Extracts and compares detailed facial features for consistency.
- **Reality Camera:** High-end cinematic snapshots (35mm Fujifilm, 8k).

## 13. Cognitive Resonance (Phase 18 - Implemented)
- **Long-Term Memory:** Searchable persistent memory via local **Qdrant**.
- **Mem0 Sync:** Uses local **Ollama (bge-m3)** for 100% standalone privacy.

## 14. Visual NPC Network (Phase 19 - Implemented)
- **Contact CRM:** Consistent visual identity for all NPCs.
- **Multi-Subject Photos:** Group shots with AI character and friends.

## 15. Vocal Identity (Phase 20 - Implemented)
- **Voice Lab:** High-speed local TTS via **Chatterbox-Turbo**.
- **Voice Cloning:** Support for .wav sample uploads.

## 16. The Vault (Phase 21 - Implemented)
- **Real Economy:** Asset trading (Crypto/Stocks) via Kraken/Alpaca APIs.
- **Portfolio Management:** Automated morning market reports and toast notifications.

## 17. Tool Specifications (Consolidated)
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

## 18. WebUI Requirements (`soul-viz.py`)
- **News Ticker:** Real-time world events.
- **Mental Activity:** Inner voice and research preview.
- **Life Stream:** Photo gallery.
- **Memory/Vault Tabs:** Management interfaces.
