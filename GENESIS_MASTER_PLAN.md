# Project Genesis Master Plan: Phases 6, 7 & 8

## 1. Vision
Project Genesis is a decentralized Multi-Agent Cluster (MAC) simulation of human life. It aims for high-fidelity biological, social, and economic realism, combined with neural bootstrapping and advanced identity governance.

## 2. Infrastructure (Phase 6 - Implemented)
- **Modular Toggles:** `utility`, `psychology`, `skills`, `world`, `reputation`, `desktop`, `legacy`, `genesis`.
- **Real-World Sync:** 24h cycle, seasonal tracking, and weather estimation.
- **Skill XP:** Competence tracking.
- **Psychology:** Trauma/Resilience system.

## 3. Origin Engine (Phase 7 - Implemented)
- **Neural Bootstrapping:** Generate a complete character (JSON/Markdown) from a natural language prompt.
- **Workflow:** User Prompt -> Agent Processing -> `reality_genesis(action: "bootstrap")` -> File Overwrite.

## 4. Identity Governance (Phase 8 - Implemented)
**Goal:** Empower the user to manage multiple lives, tweak existing characters, and revert simulation errors.

### A. Evolutionary Edits (Patching)
- **Concept:** Modify existing characters without resetting history.
- **Logic:** The `reality_genesis` tool gains a `patch` action.
- **Workflow:**
  1. User enters: "Make him more arrogant."
  2. Agent reads existing `SOUL.md` and `psychology.json`.
  3. Agent generates *only* the required changes.
  4. Agent calls `reality_genesis(action: "patch", manifest: "...")`.

### B. Profile Management (Character Slots)
- **Concept:** Multi-character support.
- **Storage:** `memory/profiles/{name}/`.
- **Logic:** `reality_profile` tool manages copying files between the active `memory/reality/` + root MD files and the profile slot.
- **Actions:** `save`, `load`, `list`, `delete`.

### C. Time Vault (Snapshot & Rollback)
- **Concept:** 1-to-X day rollback capability.
- **Automation:** Daily snapshots triggered in `before_prompt_build`.
- **Storage:** `memory/backups/YYYY-MM-DD/`.
- **Logic:** `reality_genesis(action: "rollback", date: "...")` restores a full state.

## 5. Phase 9: Multi-Model Synergy & Cost Optimization (Implemented)
**Goal:** Deploy specialized AI models for different tasks to maximize reasoning depth while minimizing token costs.

### A. Role-to-Model Mapping
| Role | Recommended Model | Reasoning Profile |
| :--- | :--- | :--- |
| **Persona** | Opus 4.6 / GPT-4o | High EQ, Nuance, Roleplay stability. |
| **Analyst** | Sonnet 4.6 / o1-preview | High Logic, Strategic Planning, Governance. |
| **Developer** | Claude Code / MiniMax-2.5 | Technical Syntax, Tool Building. |
| **Limbic** | Haiku / Llama-3-8B | Fast, Cheap, Somatic-to-Narrative translation. |
| **World Engine** | Haiku / Gemini Flash | Background environment ticks & random events. |

### B. Technical Implementation
- **Model Awareness:** The `before_prompt_build` hook detects the `agentId` and injects a role-optimized system prompt.
- **Context Pruning:** Lightweight models (Limbic/World) receive only the minimum necessary JSON data to reduce latency and cost.
- **Workflow Isolation:** Persona only sees the *output* of the Limbic system (emotional narrative), never the raw biological data.

## 6. Phase 10: Social Reputation & Circles (Implemented)
**Goal:** Implement a global standing system where actions have consequences across different social groups.

### A. Reputation Mechanics
- **Global Score:** A value from -100 (Pariah) to +100 (Icon).
- **Social Circles:** Defined groups (e.g., Professional, Family, Underground, Public).
- **Propagation:** Actions in one circle affect that circle's local score immediately and the global score partially. Global score changes leak back into other circles over time.

### B. Functional Impact
- **Economy:** Low reputation increases prices in `reality_shop` and causes job application rejections in `reality_job_market`.
- **Social:** High reputation grants "Influence" bonuses, making `reality_socialize` actions more effective.
- **World Engine:** Low reputation may trigger "Harassment" or "Crisis" events, while high reputation triggers "Opportunities".

### C. State File
- `memory/reality/reputation.json`: Stores scores and circle definitions.

## 7. Tool Specifications

### `reality_genesis` (Extended)
- `action: "bootstrap"`: Full manifest overwrite.
- `action: "patch"`: Merge specific neural changes into existing state.
- `action: "rollback"`: Restore from a timestamped backup folder.

### `reality_profile` (New)
- `action: "save" | "load" | "list" | "delete"`: Manage identity folders.

## 6. WebUI Requirements (`soul-viz.py`)
- **Genesis Tab Expansion:**
  - **Patching UI:** Input field for character modification.
  - **Profile Grid:** Interactive cards for character slots (with "Save Current" and "Switch").
  - **Rollback Timeline:** List of daily snapshots with "Restore" buttons.
