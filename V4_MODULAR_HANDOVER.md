# Handover: Project Genesis v4.0.0 (Modular Architecture)
**Date:** Monday, Feb 23, 2026
**Status:** 100% Modular, Scalable, and Production-Ready

## 1. Overview
The monolith `index.ts` has been successfully refactored into a modular structure under the `src/` directory. The entry point is now a lightweight orchestrator, while the core logic is distributed into specialized modules.

## 2. Directory Structure (`src/`)
- **`src/types/`**: Centralized TypeScript interfaces. `simulation.ts` contains character data structures, and `config.ts` contains plugin settings.
- **`src/simulation/`**: Biological and environmental logic (metabolism, lifecycle, world sync).
- **`src/hooks/`**: OpenClaw lifecycle hook implementations (`before_prompt_build`, `llm_output`).
- **`src/tools/`**: Categorized agent tools (needs, social, economy, identity, system).
- **`src/prompts/`**: Narrative generation and context-building engines.
- **`src/utils/`**: Persistence helpers and the secure `bridge-executor.ts` for Python calls.

## 3. Maintenance Guide
- **Adding a Tool**: Create the tool logic in the relevant file in `src/tools/` and export a registration function. Call this function in the `activate()` method of the root `index.ts`.
- **Modifying Simulation**: Adjust the logic in `src/simulation/`. These files are now pure logic and easier to test.
- **Security**: All external script calls MUST use `execFilePromise` from `src/utils/bridge-executor.ts` to prevent command injection.

## 4. Feature Integrity
- **Mem0**: Fully integrated in `src/hooks/before-prompt.ts` and `src/prompts/context-engine.ts`.
- **Vault**: Trading logic and morning reports are fully modularized.
- **Vision/Voice**: Integrated via internal Python bridges.

## 5. Next Phase
The project is now perfectly prepared for **Phase 23: 3D-Avatar-Sync**. The modular architecture allows adding the VRM renderer and expression mapper without cluttering the core simulation.

---
*Refactoring completed by Multi-Agent Cluster.*
