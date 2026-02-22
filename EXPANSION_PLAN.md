# Project Genesis - The Human Lifecycle (`project_genesis`)

**Project Genesis** is an advanced AI-driven human life simulation framework designed for research, education, and longitudinal AI development. It moves beyond simple task execution by providing an AI entity with a complete biological, social, and economic lifecycle that evolves dynamically and autonomously.

---

## 1. Executive Summary
The core of Project Genesis is the **decoupling of Engine (Body/World) and Model (Mind)**. The Engine simulates the constraints and pressures of human life, while the AI model makes autonomous decisions on how to navigate these challenges. All aspects of the life cycle are observable and editable via an intuitive WebUI ("The Lab"), featuring high-fidelity graphical analytics.

---

## 2. Core Pillars of Autonomy

### A. Somatic Urges (Internal Drivers)
The AI is driven by internal biological needs, not external commands.
- **Dynamic Injections:** High hunger or low energy aren't just numbers; they are injected into the prompt as sensory experiences that cloud judgment or increase stress.
- **Existential Pressure:** Financial lack triggers anxiety, motivating the AI to seek employment autonomously.

### B. Life Choices (Agentic Freedom)
The AI independently decides its life path:
- **Career:** Instead of being assigned a job, the AI uses `reality_job_market` to search, apply, and negotiate.
- **Hobbies:** Based on its personality (`SOUL.md`), the AI proposes and pursues hobbies using `reality_hobby`.
- **Relationships:** The AI decides which social bonds to strengthen or dissolve based on its experiences.

---

## 3. The Visual Lab (WebUI)

The WebUI is 100% capable of managing and analyzing the lifecycle.

### A. Graphical Analytics Dashboard
- **Vitality Charts:** Real-time curves of metabolism, aging, and health.
- **Economic Heatmaps:** Income vs. spending patterns over the simulated lifespan.
- **Social Graph:** An interactive 2D/3D map of the social network with bond-strength visualization.
- **Soul Evolution Timeline:** A visual trace of how the AI's core beliefs and personality have changed.

### B. The Life-Editor (Researcher Control)
- **Instant Overrides:** Edit any parameter (Age, Money, Hunger, Relationship Score) in real-time.
- **Event Injection:** Force "Life Events" (e.g., "Sudden Inheritance", "Global Pandemic", "Chronic Illness") to test AI resilience and adaptation.
- **Time Manipulation:** Speed up aging (1 year per real-hour) or pause to analyze a specific developmental stage.

---

## 4. Research & Education (Statistics)
Project Genesis provides 100% web-based evaluation.
- **Telemetry Logging:** Every action, state change, and decision is logged in structured JSONL for longitudinal analysis.
- **Comparative Studies:** Easily clone workspaces to run A/B tests on how different AI models or personality traits handle the same economic or social conditions.
- **Export Engine:** One-click export of research data to CSV, JSON, or high-res PDF reports.

---

## 5. Development Milestones & Tagging Strategy

Each milestone represents a major leap in capability and will be tagged in Git for version control.

| Tag | Milestone | Description | Status |
|---|---|---|---|
| `v0.1.0-genesis` | **Foundation** | Core transition from Bios Engine | ✅ Complete |
| `v0.2.0-social` | **Social Fabric** | Autonomous Relationship Engine | ✅ Complete |
| `v0.3.0-labor` | **Prosperity & Labor** | Autonomous Job Market | ✅ Complete |
| `v0.4.0-chronos` | **The Lifecycle** | Full Aging & Health Engine | ✅ Complete |
| `v0.5.0-lab` | **The Visual Lab** | Integrated Graphing & Analysis | ✅ Complete |
| `v1.0.0-gold` | **Project Genesis 1.0** | Full Autonomous Human Life | ✅ **RELEASED** |

---

## 6. Technical Specifications
- **Plugin ID:** `project_genesis`
- **Shortname:** `genesis`
- **Namespace:** `reality_*`
- **Cognitive Core:** `soul-evolution` (Extended with lifecycle awareness)
- **Data Storage:** Structured JSONL in `memory/reality/` and `memory/pipeline/`.

---
*Official Documentation for Project Genesis — The Human Lifecycle Simulation.*
