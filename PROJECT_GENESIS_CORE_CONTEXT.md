# Project Genesis - Core Implementation Context (for Opus 4.6)

## 1. Project Vision
A Multi-Agent Cluster (MAC) simulation of a human psyche. Engine provides biology/world; specialized AI agents provide mind/emotion/growth.

---

## 2. Multi-Agent Cluster (MAC) Architecture

### Role-Based Access Control (RBAC)
- **Detection:** Identify the agent using `ctx.agent.id` in every hook.
- **Enforcement:** Use `before_tool_call` to block tools not belonging to the agent's role.
- **Config:** `openclaw.plugin.json` defines the mapping between `agentId` and `role`.

### Specialized Roles
1. **Persona ("The Voice"):** 
   - Interaction focused.
   - Only sees the "State of Being" narrative (no raw JSON).
2. **Analyst ("The Brain"):**
   - Strategic and administrative.
   - Access to raw economy and lifecycle telemetry.
   - Runs the "Economic Tick" and "Soul Evolution Pipeline."
3. **Limbic System ("The Heart"):**
   - Data-to-Emotion converter.
   - Creates the "State of Being" narrative for the Persona.
4. **Developer ("The Hand"):**
   - System expansion.
   - Can write and register tools within the `development/` sandbox.

---

## 3. Communication & Observability

### Internal Communication (Memos)
- **Storage:** `memory/reality/internal_comm.json`.
- **Retention:** Standard 7-day TTL (Time-To-Live). Traumatic/Core memos use TTL: -1.
- **WebUI:** Memos must be listable and deletable via `reality_manage_memos`.

### Activity Telemetry
- **File:** `memory/telemetry/agents/activity.jsonl`.
- **Purpose:** Full research transparency. Log every major decision or injection.

---

## 4. Technical Invariants
1. **Tool Registration:** Register all tools at startup. Filter access at runtime via `before_tool_call`.
2. **Sanity Check:** Always verify `soul-evolution/SKILL.md` exists before pipeline execution.
3. **English Only:** All logs, code, and narratives must be in high-quality English.

---
*Technical Handover Documentation for MAC Refactoring.*
