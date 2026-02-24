# Refactoring Proposal: Project Genesis v4.0.0 (Modular Architecture)

## 1. Motivation
The current `index.ts` has grown to over 8,500 lines. To ensure long-term maintainability, improve testability, and simplify the integration of future features (like 3D Avatar Sync), the codebase must be split into logical modules.

## 2. Proposed Structure (`src/`)

- **`index.ts`**: The main entry point. Handles OpenClaw plugin registration and orchestrates the loading of all other modules in the `activate()` method.
- **`types/`**: Centralized TypeScript interfaces.
    - `simulation.ts`: Needs, Physique, Lifecycle, WorldState.
    - `social.ts`: SocialEntity, ReputationState, SocialEvent.
    - `config.ts`: PluginConfig and Module definitions.
- **`simulation/`**: Core biological and environmental logic.
    - `metabolism.ts`: Metabolism update logic and stage multipliers.
    - `lifecycle.ts`: Age progression and life stage transitions.
    - `world.ts`: Weather sync, RSS news processing, and time-based triggers.
- **`hooks/`**: OpenClaw lifecycle hooks.
    - `prompt-builder.ts`: The `before_prompt_build` logic, including Mem0 injection and character perceptions.
    - `llm-output.ts`: The `llm_output` handler for experience logging and NPC message processing.
- **`tools/`**: Categorized agent tools (registered via `api.registerTool`).
    - `needs.ts`: Biological maintenance (eat, sleep, shower).
    - `social.ts`: Social interaction and NPC management (socialize, network, contact CRM).
    - `economy.ts`: Labor and wealth management (work, shop, trade/vault).
    - `identity.ts`: Character governance (genesis, profile, camera/photography).
    - `system.ts`: Desktop and web interaction (browse, desktop control).
- **`prompts/`**: Narrative and context engines.
    - `context-engine.ts`: Functions like `buildSensoryContext` and `buildPersonaContext`.
    - `role-optimizer.ts`: Role-based context pruning (MAC optimization).
- **`utils/`**: Shared helper functions.
    - `persistence.ts`: Atomic JSON operations, file-locking, and path resolution.
    - `bridge-executor.ts`: Secure `execFilePromise` logic for Python bridge execution.

## 3. Benefits
- **Safety:** Security fixes (like command injection protection) are centralized in `bridge-executor.ts`.
- **Clarity:** "English Mind" prompts are separated from "Bilingual UI" logic.
- **Performance:** Smaller files lead to faster compilation and better IDE support.
- **Compliance:** Maintains the "async activate" pattern required by OpenClaw v2026+.
