# Project Genesis — Technical Specification (Phase 6, 7 & 8)

## 1. Vision
Transform Project Genesis into a dynamic, interconnected lifecycle simulation with neural bootstrapping, identity governance, and time-travel capabilities.

## 2. Modular Architecture (Togglable)
- `utility`: Item effects and equipment.
- `psychology`: Long-term mental states (traumas/resilience).
- `skills`: XP progression and skill mastery.
- `world`: Weather, seasons, market trends.
- `reputation`: Global social standing.
- `desktop`: Host system integration (wallpaper).
- `genesis`: Neural Life Bootstrapping.
- `governance`: Phase 8 - Profile management and targeted edits.
- `chronos_vault`: Phase 8 - Rollback and snapshot system.

## 3. Phase 7: Origin Engine (Neural Bootstrapping)
- **Bootstrap:** Generate full character from scratch.
- **Patch:** Modify specific traits of an existing character while preserving history.

## 4. Phase 8: Identity Governance & Time Travel
**Goal:** Manage multiple identities and recover from undesirable simulation paths.

### Profile Management:
- Store complete state snapshots in `memory/profiles/{name}/`.
- Actions: `save_profile`, `load_profile`, `delete_profile`.

### Rollback System (The Vault):
- Automatic daily snapshots in `memory/backups/{date}/`.
- Tool: `reality_genesis(action: "rollback", date: "{date}")`.

## 5. Tool Specifications

### `reality_genesis` (Expanded)
- `action: "bootstrap"`: Full overwrite.
- `action: "patch"`: Targeted neural edit.
- `action: "rollback"`: Restore from a specific date.

### `reality_profile` (New)
- `action: "save" | "load" | "list"`: Manage identity slots.

## 6. Visual Lab Requirements (WebUI)
- **Genesis Lab:** Unified interface for creation and patching.
- **Profile Manager:** Grid of saved characters with "Quick Switch" buttons.
- **Time Vault:** List of rollback points with date/time.
