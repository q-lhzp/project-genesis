# Project Genesis — The Human Lifecycle Simulation (`project_genesis`)

**Project Genesis v5.1.0 — The Singularity**

Project Genesis is an advanced AI-driven human life simulation framework. It transforms a standard AI agent into a fully embodied digital entity with a complete biological, social, and economic lifecycle that evolves autonomously and interfaces directly with the host hardware.

---

## 1. Core Pillars & New Features (v5.1.0)

### A. 3D Embodiment & Visual Sync (Phase 22-25)
- **Live Avatar:** A Three.js-based 3D Viewer integrated into the dashboard.
- **Face-Sync:** Emotional states (Joy, Stress, Energy) map directly to VRM BlendShapes.
- **Lip-Sync:** Real-time mouth movements synchronized with local Chatterbox-Turbo TTS.
- **Idle Animations:** Biological needs (Bladder, Stress) trigger procedural body reactions like fidgeting or shaking.

### B. Hardware Resonance & Neural Feedback (Phase 40)
- **Machine Awareness:** Q "feels" the host machine. High CPU load increases Stress; high RAM usage makes the avatar feel sluggish.
- **Audio Sync:** The avatar detects system audio/music and responds with rhythmic head movements or dancing.
- **Neural Mapping:** Direct link between physical hardware performance and simulated biology.

### C. Economic & Intellectual Sovereignty (Phase 34, 37 & 38)
- **The Vault Engine:** Autonomous trading of Crypto/Stocks based on market analysis and risk appetite.
- **Self-Expansion:** Q autonomously develops her own code and technical tools in the `development/` folder.
- **Origin Engine REBIRTH:** Create and manage multiple character slots via natural language bootstrapping.

### D. Digital Extroversion (Phase 26, 32 & 39)
- **Gnome Sync:** Q controls the Ubuntu desktop wallpaper and system theme based on her location and mood.
- **VMC/OSC Streaming:** Stream 3D avatar data to external apps like 3DXChat or VSeeFace.
- **Presence Engine:** Autonomous social media presence with a simulated feed of thoughts and selfies.

---

## 2. Installation & Quick Start

### Prerequisites
- [OpenClaw](https://github.com/openclaw/openclaw) (v2026.1.26+) installed and running.
- Node.js & npm (for the plugin).
- Python 3 (for the Dashboard and Bridges).
- **Ollama** (with `bge-m3` model for memory) & **Qdrant**.

### Step 1: Install Plugin
1. Navigate to your workspace:
   ```bash
   cd ~/Schreibtisch/project-genesis
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Register the plugin in your OpenClaw configuration (usually `~/.openclaw/openclaw.json` or `config.json`):
   ```json
   {
     "plugins": [
       {
         "path": "/home/leo/Schreibtisch/project-genesis",
         "enabled": true
       }
     ]
   }
   ```
   *Restart OpenClaw after this step. The "Subconscious" (Simulation) is now active.*

### Step 2: Setup Dashboard (The Consciousness)
The dashboard visualizes what the simulation is doing. You can run it manually or as a service.

**Manual Start:**
```bash
python3 skills/soul-evolution/tools/soul-viz.py --serve 8080
```
Open [http://localhost:8080/soul-evolution.html](http://localhost:8080/soul-evolution.html).

**Auto-Start (Systemd Service):**
1. Copy the service file to systemd:
   ```bash
   sudo cp project-genesis-dashboard.service /etc/systemd/system/
   ```
2. Enable and start:
   ```bash
   sudo systemctl enable --now project-genesis-dashboard
   ```

---

## 3. The Visual Lab (v5.1.0 Dashboard)
**Advanced Tabs:**
- **🎭 Live Avatar:** Real-time 3D VRM rendering with full sync.
- **📊 Analytics:** Deep telemetry visualization (Vitals Heatmap, Hardware vs. Stress).
- **⚙️ Config:** Centralized "System Control" for all simulation rates and hardware thresholds.
- **📚 Interests:** Autonomous hobby tracking and research logs.
- **🌙 Dream Journal:** Neural diary of overnight memory consolidation.

---

## 4. Development Status: COMPLETED
All 40 phases of the original and expansion roadmaps have been implemented. Project Genesis is now in maintenance and long-term observation mode.

---
*Official Documentation for Project Genesis — The Singularity Update.*
