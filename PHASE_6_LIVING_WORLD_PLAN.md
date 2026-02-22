# Phase 6: The Living World & Sovereignty — Technical Specification

## 1. Vision
Transform Project Genesis from a closed agent simulation into a dynamic, interconnected lifecycle within a "Living World." The agent shall gain psychological depth, professional competence, and the ability to influence its host environment.

## 2. Modular Architecture
All Phase 6 features must be togglable via `openclaw.plugin.json`.

### Module Definitions:
- `utility`: Items in inventory gain functional effects (consumables/equipment).
- `psychology`: Long-term mental states (traumas, scars, resilience).
- `skills`: XP-based progression and competence levels.
- `world`: Dynamic environment (weather, seasons, market trends).
- `reputation`: Global social standing and circle-based dynamics.
- `desktop`: Host system integration (wallpaper/theme control).
- `legacy`: Mortality and inheritance mechanics.

## 3. Data Structures (State Files)

### `memory/reality/skills.json`
```json
{
  "skills": [
    { "id": "skill_001", "name": "Cooking", "level": 5, "xp": 450, "xp_to_next": 1000 }
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
  "last_update": "ISO-Timestamp"
}
```

### `memory/reality/psychology.json`
```json
{
  "resilience": 85,
  "traumas": [
    { "id": "t_001", "description": "Fear of failure", "severity": 20, "decay_rate": 0.5 }
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

### `reality_desktop(action: "set_wallpaper", path: "...")`
- Prepares shell scripts for host interaction.

## 5. Visual Lab Requirements (WebUI)
- **Skills Radar:** Graphical representation of competence.
- **Psych Dashboard:** Visualization of mental health and resilience trends.
- **World Status:** Live weather and market widget.
