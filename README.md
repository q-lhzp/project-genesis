# Project Genesis — The Human Lifecycle Simulation (`project_genesis`)

**Project Genesis** is an advanced AI-driven human life simulation framework built for the OpenClaw ecosystem. It transforms a standard AI agent into an embodied entity with a complete biological, social, and economic lifecycle that evolves dynamically and autonomously.

---

## 1. Core Pillars

### A. The Living World (Phase 6 & 14)
- **Real-World Sync:** Simulation time, seasons, and weather are synchronized with the host system's real-time environment.
- **Live News Feed:** The `world_engine` fetches LIVE RSS headlines based on character location, influencing market modifiers.
- **Dynamic Weather:** Affects metabolism and energy consumption.

### B. The Origin Engine & Identity (Phase 7, 8 & 17)
- **Neural Bootstrapping:** Generate a complete life story, financial status, and psychological profile from a single prompt.
- **Neural Photography:** AI generates consistent self-portraits using internal engines (Flux, Venice, Nano Banana) synced with wardrobe and location.
- **Face-ID Integration:** Detailed facial feature extraction for visual consistency.

### C. Cognitive Resonance & Voice (Phase 18 & 20)
- **Long-Term Memory (Mem0):** Searchable persistent memory using local **Qdrant** and **Ollama (bge-m3)**. 
- **Vocal Identity:** Local high-speed Text-to-Speech via **Chatterbox-Turbo** with voice cloning support.
- **Memory Lab:** Dedicated WebUI tab to search and manage the AI's "unconscious mind".

### D. Digital Extroversion & Sovereignty (Phase 15 & 16)
- **Desktop Sovereignty:** AI acts as the owner of the machine with visual browser control (Playwright) and universal mouse/keyboard input.
- **Interactive Socializing:** AI can autonomously chat on Discord, WhatsApp Web, or within 3D games (like 3DXChat).

### E. Social Fabric & CRM (Phase 10, 12 & 19)
- **Social Reputation:** Tracks global standing across professional and private circles.
- **Visual NPC Network:** Consistent visual identities for all social contacts, manageable via a WebUI CRM.
- **Autonomous Social Life:** NPCs initiate contact autonomously based on relationship dynamics.

### F. The Vault - Real Economy (Phase 21)
- **Real Asset Trading:** Autonomous trading of Crypto (Kraken) and Stocks (Alpaca).
- **Morning Analysis:** AI writes daily performance reports.
- **Safety First:** Default Paper Trading mode with real-time Toast notifications.

---

## 2. Installation & Quick Start

### Prerequisites
- [OpenClaw](https://github.com/openclaw/openclaw) (v2026.1.26+)
- Node.js & npm
- Python 3 (for WebUI and Bridges)
- **Ollama** (with `bge-m3` model for memory)
- **Qdrant** (running on localhost:6333)

### Setup
1. **Install Plugin:**
   ```bash
   cd project-genesis
   npm install
   ```
2. **Setup Voice Models:**
   ```bash
   python3 skills/soul-evolution/tools/voice/download_voice_models.py
   ```
3. **Configure OpenClaw:** Add `project_genesis` to your `openclaw.json`.
4. **Bootstrap Your Life:** Use the **Genesis Lab** in the WebUI to generate your character.

---

## 3. The Visual Lab (Dashboard)
Run the visualizer:
```bash
python3 skills/soul-evolution/tools/soul-viz.py "$(pwd)" --serve 8080
```
**Tabs:**
- **Dashboard:** Vitals, Soul Map, and Cognitive Activity (Inner Voice).
- **Life Stream:** Photo gallery of captured moments.
- **The Vault:** Real-time portfolio and trading terminal.
- **Memory:** Fact search and long-term memory management.
- **Social Standing:** Reputation and Contact CRM.
- **Genesis Lab:** Profile switching, Voice Lab, and Model Configuration.

---

## 4. Architecture: "English Mind / Bilingual UI"
- **Mind:** Internal logic and prompt injections are in **English**.
- **Interface:** User-facing labels and tool outputs support **German (DE)** and **English (EN)**.

---

## 5. Technical Specifications
- **ID:** `project_genesis`
- **Standalone:** All vision, trading, and voice engines are internalized.
- **Compliance:** Uses the OpenClaw `async activate` pattern for SDK v2026+.

---
*Official Documentation for Project Genesis v3.5.1.*
