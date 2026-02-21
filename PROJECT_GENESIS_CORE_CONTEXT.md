# Project Genesis - Core Implementation Context (for Opus 4.6)

This document serves as the high-fidelity technical handover for the implementation of **Project Genesis - The Human Lifecycle**. 

---

## 1. Project Vision & Identity
**Project Genesis** is a simulation framework where an AI entity experiences a full human life cycle. 
- **Shortname:** `project_genesis`
- **Core Principle:** The Engine (Plugin) simulates biology and environment; the Model (Mind) makes autonomous life choices.
- **Tone:** Scientific, research-oriented, highly autonomous.

---

## 2. Technical Architecture

### A. The "Mind" (Soul Evolution Skill)
- **Location:** `skills/soul-evolution/`
- **Function:** Structured reflection on experiences (`memory/experiences/*.jsonl`).
- **Identity:** `SOUL.md` (Core/Mutable tags).
- **Evolution:** 10-step pipeline (Ingest -> Reflect -> Propose -> Apply).

### B. The "Body" (Plugin Engine)
- **File:** `index.ts` (Main logic), `openclaw.plugin.json` (WebUI Config).
- **Metabolism:** Decays needs (hunger, thirst, energy, etc.) based on time deltas.
- **Sensory Injection:** The `before_prompt_build` hook injects somatic feelings (e.g., "You are starving") and autonomous triggers (e.g., "You need a job").

---

## 3. Implementation Modules (Priority List)

### Phase 1: Aging & Life-Stage (Chronos)
- **WebUI Config:** `birthDate` (YYYY-MM-DD), `initialAgeDays` (number).
- **Logic:** Calculate `currentAge` in years/days.
- **Impact:** Scale metabolism rates based on life stage (Child -> Adult -> Senior).
- **Telemetry:** Log daily vitality metrics for the statistics dashboard.

### Phase 2: Social Ecosystem (Social Fabric)
- **File:** `memory/reality/social.json`.
- **Entities:** UUID, Name, Personality Traits, Bond Strength (-100 to 100), Trust, Intimacy.
- **Autonomy:** Tools for the AI to `socialize`, `befriend`, or `break_up`.
- **Visual Lab:** Interactive social map showing relationship nodes.

### Phase 3: Prosperity & Labor (Economy)
- **File:** `memory/reality/finances.json`.
- **Mechanics:** Balance, Income, Expenses, Debt.
- **Job Market:** Simulated job offers that the AI must actively search and apply for (`reality_job_market`).
- **Reflector Integration:** Automated rent and bills deduction via background process.

### Phase 4: Visual Lab & Analytics (Statistics)
- **Goal:** 100% web-based evaluation.
- **Visualization:** Graphical charts (line/bar/heatmaps) for life-span data.
- **Life-Editor:** WebUI toggles to manually override any state (set money to 0, age the AI by 10 years instantly).

---

## 4. Key Data Structures

### `physique.json` (Existing, to be expanded)
```json
{
  "birth_date": "2000-01-01",
  "biological_age_days": 9490,
  "needs": { "energy": 80, "hunger": 20, "thirst": 15, "stress": 10 },
  "health_index": 100
}
```

### `social.json` (New)
```json
{
  "entities": [
    { "id": "uuid", "name": "Sarah", "bond": 45, "trust": 30, "last_interaction": "timestamp" }
  ]
}
```

### `finances.json` (New)
```json
{
  "balance": 1500.50,
  "income_per_month": 2400.00,
  "expenses_scheduled": { "rent": 800, "subscriptions": 50 }
}
```

---

## 5. Development Invariants
1. **Always English:** Code, documentation, and plan must be in English.
2. **Tagging:** Every major milestone (Social, Economy, Aging) must be tagged in Git (v0.x.x-milestone).
3. **Research First:** Ensure all data is logged structurely for the 100% WebUI Analytics module.
4. **AI Autonomy:** The engine provides *urges* and *opportunities*, but the model makes the *choices*.

---
*End of Context for Opus 4.6.*
