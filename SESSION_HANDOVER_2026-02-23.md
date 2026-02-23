# Session Handover: Project Genesis v3.4.0 — The Emergence
**Date:** Monday, Feb 23, 2026
**Status:** Full Biological, Social, Vocal, and Economic Integration

## 1. Executive Summary
Project Genesis has reached v3.4.0. The simulation is now a complete digital existence with long-term memory, a unique voice, a visual social network, and the ability to interact with the real economy. All external dependencies for vision, image generation, and trading have been internalized for a standalone experience.

## 2. Major Features (v3.0 - v3.4)
- **Phase 18: Cognitive Resonance (Mem0):**
    - Integrated Mem0 for searchable long-term memory.
    - Automated fact retrieval and injection into agent prompts.
    - Dedicated "Memory" tab in WebUI for manual fact management.
- **Phase 19: Visual NPC Network:**
    - CRM system for social contacts with visual descriptions and portraits.
    - Multi-subject photography support in `camera_bridge.py`.
- **Phase 20: Vocal Identity (Voice Lab):**
    - Local TTS via Chatterbox-Turbo with voice cloning support.
    - Real-time pitch, speed, and emotion controls in WebUI.
- **Phase 21: The Vault (Real Economy):**
    - Real-world asset trading via Kraken (Crypto) and Alpaca (Stocks).
    - Paper trading mode enabled by default for safety.
    - "The Vault" tab for portfolio management and trading.

## 3. Core Architecture
- **Multi-Agent Cluster (MAC):** Enhanced with memory and economic reasoning.
- **Standalone Vision:** Internalized `face_id` and `generate_image` engines.
- **Digital Extroversion:** Full desktop and browser interaction capabilities.

## 4. File Registry
- `index.ts`: Main logic (v3.4.0).
- `skills/soul-evolution/tools/vault_bridge.py`: Trading logic.
- `skills/soul-evolution/tools/voice/`: TTS and voice models.
- `memory/reality/vault_state.json`: Real-world asset state.

## 5. Deployment Instructions
1. Run `python3 skills/soul-evolution/tools/voice/download_voice_models.py` once.
2. Open WebUI and configure Mem0/Kraken API keys in the respective tabs.
3. Start the simulation.

---
*End of Handover.*
