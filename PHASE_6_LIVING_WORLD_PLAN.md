# Phase 6 & 7: The Living World & Origin Engine — Technical Specification

## 1. Vision
Transform Project Genesis from a closed agent simulation into a dynamic, interconnected lifecycle within a "Living World." The agent shall gain psychological depth, professional competence, and the ability to influence its host environment. Phase 7 introduces the "Origin Engine" for automated character creation.

## 2. Modular Architecture
All features must be togglable via `openclaw.plugin.json`.

### Module Definitions:
- `utility`: Items in inventory gain functional effects (consumables/equipment).
- `psychology`: Long-term mental states (traumas, scars, resilience).
- `skills`: XP-based progression and competence levels.
- `world`: Dynamic environment (weather, seasons, market trends).
- `reputation`: Global social standing and circle-based dynamics.
- `desktop`: Host system integration (wallpaper/theme control).
- `legacy`: Mortality and inheritance mechanics.
- `genesis`: Neural Life Bootstrapping (automated biography generation).

## 3. Data Structures (State Files)

### `memory/reality/skills.json`
```json
{
  "skills": [
    { "id": "skill_001", "name": "Cooking", "level": 5, "xp": 450, "xp_to_next": 1000, "last_trained": "ISO" }
  ],
  "total_xp": 450
}
```

### `memory/reality/world_state.json`
```json
{
  "weather": "rainy",
  "temperature": 12,
  "season": "autumn",
  "market_modifier": 0.95,
  "last_update": "ISO-Timestamp",
  "sync_to_real_world": true
}
```

### `memory/reality/psychology.json`
```json
{
  "resilience": 85,
  "traumas": [
    { "id": "t_001", "description": "Fear of failure", "severity": 20, "decay_rate": 0.5, "trigger": "work" }
  ],
  "joys": ["Completed first project"]
}
```

## 4. Tool Specifications

### `reality_inventory(action: "use", item_id: "...")`
- Applies `effects` from the item to `physique.needs`.
- Consumes quantity.

### `reality_skill(action: "train" | "list", ...)`
- Increases XP for a specific skill.
- Consumes energy/time.

### `reality_genesis(action: "generate", prompt: "...")`
- Calls an LLM to generate a complete life state based on the prompt.
- Overwrites all state files to "bootstrap" the new life.

## 5. Phase 7: The Origin Engine (Neural Life Bootstrapping)
**Goal:** Instant generation of complex characters.
- **Processing:** Uses a high-reasoning model to populate all project JSON and MD files.
- **Outcome:** The simulation starts with a pre-filled social circle, bank account, career, and set of skills consistent with the user's description.

## 6. Visual Lab Requirements (WebUI)
- **Genesis Lab:** A dedicated setup screen for initial generation.
- **Skills Radar:** Graphical representation of competence.
- **Psych Dashboard:** Visualization of mental health and resilience trends.
- **World Status:** Live weather and market widget with Real-World Sync toggle.
