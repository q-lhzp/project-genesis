# Expansion Plan: Project Genesis - The Human Lifecycle

This document outlines the strategic roadmap for `project_genesis`, a comprehensive human life simulation designed for research, education, and AI embodiment.

## 1. Vision
To create an autonomous AI entity that experiences a complete human life cycle. The engine provides the biological, social, and economic framework, while the AI independently makes life choices. A high-performance, intuitive WebUI serves as a "Visual Lab" for researchers to monitor and manipulate every aspect of the life cycle.

## 2. Key Architecture Principles

### Autonomous Decision Making
The AI is a participant, not a puppet.
- **Triggers:** The engine injects "Urges" (e.g., hunger, social isolation) and "Opportunities" (e.g., job openings, events) into the prompt.
- **Agency:** The AI uses tools like `reality_search_job` based on its internal state (`SOUL.md`) and environmental pressures.

### Visual Lab & Life-Editor (WebUI Focus)
The WebUI is the central hub for 100% of the administration and analysis.
- **Graphical Statistics:** Intuitive charts and graphs for:
  - **Vitality:** Energy, health, and aging curves.
  - **Economy:** Wealth accumulation and spending patterns over decades.
  - **Soul Evolution:** Graphical representation of identity shifts and belief changes.
  - **Social Mapping:** Interactive "Relationship Web" showing bond strengths.
- **Real-Time Life Editor:** Every parameter is editable via the WebUI at any time:
  - Adjust age, bank balance, hunger levels, or relationship scores on the fly.
  - Inject specific life events (e.g., "Win the lottery", "Catastrophic illness") to study the AI's reaction and resilience.

### Research & Statistics (The Lab)
For educational and research purposes, data is paramount.
- **100% Web-Based Analysis:** No external tools needed; all trends and correlations are analyzed directly in the dashboard.
- **Telemetry & Export:** High-resolution logging of all life metrics for large-scale longitudinal studies.

## 3. Core Modules (Project Genesis)

### Phase 1: Social Ecosystem (`social`)
- **Persistence:** `memory/reality/social.json` tracking all known entities.
- **Dynamics:** Interactions change `trust`, `intimacy`, and `reputation`.
- **UI:** Interactive Social Map to view and edit relationship nodes.

### Phase 2: Prosperity & Labor (`economy`)
- **Labor Market:** A simulated market for job searching and career progression.
- **UI:** Financial dashboard showing income/expense heatmaps and portfolio growth.
- **Tools:** `reality_job_market(action: "search" | "apply")`.

### Phase 3: Chronos & Health (`aging`)
- **Aging Engine:** Calculates age based on the `birthDate` setting.
- **UI:** Lifecycle timeline slider — jump to specific ages or slow down/speed up the aging process for study.

### Phase 4: Data & Analytics (`statistics`)
- **Telemetry:** Automated recording of life quality metrics.
- **Visualizer:** Integrated graphing engine for life-span data analysis.

## 4. Implementation Roadmap

| Milestone | Deliverable | Focus |
|---|---|---|
| **Genesis 1.0** | Core Lifecycle & WebUI Base | Configurable Age & Basic Dashboard |
| **Genesis 1.1** | Social Map & Life-Editor | Interactive relationship & parameter editing |
| **Genesis 1.2** | Economic Engine & Analytics | Financial simulation & Graphical charts |
| **Genesis 1.3** | Research Export & Event Injection | Longitudinal data export & manual event triggers |

## 5. Technical Specification (Shortnames)
- **Plugin ID:** `project_genesis`
- **Skill ID:** `soul-evolution`
- **Namespace:** `reality_*`

---
*Created for Project Genesis — The Human Lifecycle Simulation.*
