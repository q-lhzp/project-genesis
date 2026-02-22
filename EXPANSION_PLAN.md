# Expansion Plan & Technical Audit Log: Project Genesis

This document serves as the strategic roadmap and the authoritative verification registry for **Project Genesis**. It tracks the implementation of the human lifecycle simulation and provides technical pointers for auditing the system's integrity.

---

## 1. Vision
To create an autonomous AI entity that experiences a complete human life cycle within a **Multi-Agent Cluster (MAC)**. The engine provides the biological, social, economic, and technical environment, while specialized AI agents provide mind, emotion, interaction, and growth.

---

## 2. Technical Verification Registry (Audit Log)

### Phase 1: Chronos (Aging & Lifecycle)
- **Status:** ✅ Complete
- **Verification Points:**
  - `index.ts`: `LifecycleState` interface and `updateLifecycle()` function.
  - Logic: Age is calculated in days from `birthDate`. Metabolism rates scale via `getLifeStageMultipliers()`.
  - Stages: Infant, Child, Teen, Adult, Middle Adult, Senior.
  - File: `memory/reality/lifecycle.json`.

### Phase 2: Social Fabric (Relationship Engine)
- **Status:** ✅ Complete
- **Verification Points:**
  - `index.ts`: `SocialEntity` interface and `reality_socialize` tool.
  - Logic: `bond`, `trust`, and `intimacy` scores with dynamic decay via `applySocialDecay()`.
  - File: `memory/reality/social.json`.
  - Telemetry: `memory/telemetry/social/interactions.jsonl`.

### Phase 3: Prosperity & Labor (Economy)
- **Status:** ✅ Complete
- **Verification Points:**
  - `index.ts`: `FinanceState` interface and `reality_job_market` / `reality_work` tools.
  - Logic: Recurring expenses processed during heartbeat. Dynamic job offers linked to social status.
  - File: `memory/reality/finances.json`.
  - Telemetry: `memory/telemetry/economy/events_YYYY-MM-DD.jsonl`.

### Phase 4: The Hand (Self-Development Engine)
- **Status:** ✅ Complete
- **Verification Points:**
  - `index.ts`: `reality_develop` tool (init, test, write) and `reality_review_project` (Analyst).
  - Logic: Sandbox security using `path.resolve`. Dynamic tool loading on next agent turn.
  - Directory: `memory/development/projects/`.
  - File: `memory/development/manifest.json`.

---

## 3. Current Objective: Phase 5 - The Lab (WebUI Observability)

**Goal:** Transform the simulated data into an intuitive, high-fidelity research dashboard.

### Core Requirements:
1. **MAC Transparency:**
   - Visual log of agent activity ("Who thought what?").
   - Interactive Memo Board (View/Edit/Delete memos).
2. **Graphical Vitality:**
   - Lifespan charts (Energy, Stress, Wealth curves).
3. **Social Mapping:**
   - 2D Relationship Graph visualization.
4. **Researcher Controls:**
   - Direct override buttons for all vitals and finance parameters.

---

## 4. Development Milestones & Tagging Strategy

| Tag | Milestone | Focus | Status |
|---|---|---|---|
| `v1.0.0-gold` | **Genesis Gold** | Monolithic foundation | ✅ Complete |
| `v1.1.0-mac` | **The Psyche** | Multi-Agent Refactoring | ✅ Complete |
| `v1.2.0-hand` | **The Hand** | Self-Development Engine | ✅ Complete |
| `v1.3.0-observ` | **The Lab** | WebUI Observability | ⏳ In Progress |
| `v2.0.0-omega` | **Full Autonomy** | Stability & Refinement | 📅 Planned |

---
*This log is the source of truth for Project Genesis implementation audits.*
