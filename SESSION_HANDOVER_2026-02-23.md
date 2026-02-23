# Session Handover: Project Genesis v3.5.1 — The Standalone Peak
**Date:** Monday, Feb 23, 2026
**Status:** 100% Standalone, Privacy-Focused Neural Identity

## 1. Executive Summary
Project Genesis has reached v3.5.1. It is now a fully standalone digital lifecycle simulation that operates entirely locally while being connected to real-world data and economies. The AI has its own voice, long-term memory, visual social circle, and real trading capabilities—all while maintaining 100% privacy via local Qdrant and Ollama.

## 2. Major Features (v3.0 - v3.5.1)
- **Local Long-Term Memory (Mem0):**
    - Integrated local **Qdrant** database.
    - Uses local **Ollama** with **bge-m3** embedder (1024 dims) for interoperability with other OpenClaw memory plugins.
- **Vocal Identity:**
    - High-speed local TTS via **Chatterbox-Turbo**.
    - Voice Lab in WebUI for pitch/speed/emotion control and voice cloning.
- **Visual NPC CRM:**
    - NPCs have consistent visual identities and portraits.
    - Supported multi-subject photography for group shots.
- **The Vault (Real Economy):**
    - Real asset trading (Kraken/Alpaca) with paper trading safety.
    - Automated morning market reports and real-time dashboard notifications.
- **Compliance & Privacy:**
    - Removed all Cloud API dependencies (Face-ID, Image-Gen, Mem0).
    - Unified notification system and fixed SDK loader warnings.

## 3. Core Architecture
- **Standalone Engines:** Vision (Face-ID), Image Generation, TTS, and Trading are all internal to the plugin directory.
- **Privacy-First:** Local vector storage and local embeddings.
- **Digital Extroversion:** Full desktop ownership and interactive visual browsing.

## 4. File Registry
- `index.ts`: Main logic (v3.5.1).
- `skills/soul-evolution/tools/vision/`: Face-ID and Image engines.
- `skills/soul-evolution/tools/voice/`: TTS bridge and model downloader.
- `skills/soul-evolution/tools/memory_bridge.py`: Local Mem0/Qdrant interface.
- `skills/soul-evolution/tools/vault_bridge.py`: Trading interface.

## 5. Deployment Checklist
1. Ensure **Qdrant** is running on `localhost:6333`.
2. Run `ollama pull bge-m3`.
3. Run `python3 skills/soul-evolution/tools/voice/download_voice_models.py`.
4. Configure API keys for Kraken/Alpaca in the "Vault" tab (if live trading is desired).

---
*End of Handover.*
