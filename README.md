# Project Genesis — The Human Lifecycle Simulation (`project_genesis`)

**Project Genesis** is an advanced AI-driven human life simulation framework built for the OpenClaw ecosystem. It transforms a standard AI agent into an embodied entity with a complete biological, social, and economic lifecycle that evolves dynamically and autonomously.

---

## 1. Core Pillars

### A. The Living World (Phase 6)
- **Real-World Sync:** Simulation time, seasons, and weather are synchronized with the host system's real-time environment.
- **Dynamic Weather:** Affects metabolism and energy consumption.
- **Market Modifiers:** Global reputation and world events influence shop prices and job opportunities.

### B. The Origin Engine (Phase 7)
- **Neural Bootstrapping:** Generate a complete life story, financial status, social circle, and psychological profile from a single text prompt (e.g., *"Create a 24-year-old artist living in Berlin"*).
- **Automated Setup:** Instantly populates all JSON state files and Markdown identity documents.

### C. Identity Governance (Phase 8)
- **Profile Management:** Save and switch between different character "slots" (`memory/profiles/`).
- **Time Vault (Rollback):** Daily automated snapshots allow you to revert the simulation to any previous day.
- **Evolutionary Edits (Patching):** Tweak specific character traits (e.g., *"Make her more confident"*) without resetting the entire biography.

### D. Multi-Model Cluster (Phase 9)
- **Model Specialization:** Optimized role-to-model mapping (e.g., Persona on Opus 4.6, Limbic System on Haiku) to maximize reasoning quality while minimizing costs.
- **Cost Optimization:** Pruned context delivery for lightweight background roles.

### E. Social Reputation (Phase 10)
- **Reputation Meter:** Tracks global standing from *Pariah* to *Icon*.
- **Social Circles:** Manage standing in Professional, Family, Friends, and Underground groups.
- **Consequences:** Reputation affects job requirements and networking success.

---

## 2. Installation & Quick Start

### Prerequisites
- [OpenClaw](https://github.com/openclaw/openclaw) (v2026.1.26+)
- Node.js & npm
- Python 3 (for WebUI Lab)

### Setup
1. **Install Plugin:**
   ```bash
   cd project-genesis
   npm install
   ```
2. **System Requirements:**
   - **Python 3** with `pip`
   - **Playwright** (Automatically installed on first browse, or run `pip install playwright && playwright install chromium`)
3. **Configure OpenClaw:** Add `project_genesis` to your `openclaw.json` plugins list.
3. **Bootstrap Your First Life:**
   - Start the agent.
   - Open the **Genesis Lab** tab in the WebUI.
   - Enter a description and click **🚀 Generate Character**.

---

## 3. The Visual Lab (Dashboard)
Run the visualizer to monitor and manage the simulation:
```bash
python3 skills/soul-evolution/tools/soul-viz.py "$(pwd)" --serve 8080
```
**Tabs:**
- **Dashboard:** Vitals, Soul Map, and Timeline.
- **Social Standing:** Reputation meter and Circle standing.
- **Skills:** XP-based progression tracking.
- **Psychology:** Resilience and Trauma management.
- **Genesis Lab:** Profile switching, Time Vault, and Model Configuration.

---

## 4. Architecture: "English Mind / Bilingual UI"
- **Mind:** All internal prompt injections (logic, somatic feelings, directives) are hardcoded in **English** for maximum model performance.
- **Interface:** All user-facing tool outputs, file templates, and dashboard labels support both **German (DE)** and **English (EN)** via the `language` config setting.

---

## 5. Technical Specifications
- **ID:** `project_genesis`
- **Data Layer:** JSON persistence in `memory/reality/`.
- **MAC Roles:** Persona, Analyst, Limbic, World Engine, Developer.
- **Safety:** Strict path-traversal guards and atomic file writes.

---
*Official Documentation for Project Genesis v1.7.0.*
