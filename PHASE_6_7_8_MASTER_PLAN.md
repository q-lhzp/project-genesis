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

## 5. Tool Specifications

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
