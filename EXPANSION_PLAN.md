# Expansion Plan: Project Genesis - The Human Lifecycle

This document outlines the strategic roadmap for `project_genesis`, a comprehensive human life simulation designed for research, education, and AI embodiment.

## 1. Vision
To create an autonomous AI entity that experiences a complete human life cycle. The engine provides the biological, social, and economic framework, while the AI independently makes life choices. The system operates as a **Multi-Agent Cluster (MAC)** to simulate a complex psyche with specialized roles for logic, emotion, interaction, and technical growth.

## 2. Key Architecture Principles

### Multi-Agent Cluster (MAC)
The psyche is divided into specialized agents to ensure context hygiene and depth:
- **Persona ("The Voice"):** Interaction with the user. Focus on empathy and character.
- **Analyst ("The Brain"):** Strategy, finances, and identity governance.
- **Limbic System ("The Heart"):** Translates data into emotional narratives.
- **Developer ("The Hand"):** Self-programming and tool creation.

### Research Transparency & Observability
100% of internal agent processes must be visible and manageable via the WebUI:
- **Activity Feed:** Real-time logging of inter-agent decisions ("Who thought what and why?").
- **Memo Management:** Visual "bulletin board" of internal memos with TTL (Time-To-Live) logic.
- **Parameter Override:** Real-time manipulation of all biological, social, and psychological values.

## 3. Core Modules (Project Genesis)

### Phase 1: Chronos & Social Fabric (Complete)
- **Status:** Biological aging, life stages, and NPC relationship dynamics are implemented.

### Phase 2: Prosperity & Labor (Complete)
- **Status:** Economy engine, job market, and automated bills/rent are functional.

### Phase 3: MAC Refactoring & Observability (Current)
- **Objective:** Split the monolith into the MAC architecture.
- **Infrastructure:** Role-based access control (RBAC) for tools.
- **Observability:** Centralized activity logging and memo manager.

### Phase 4: Self-Development Engine
- **Objective:** Enable the Developer agent to write and register its own tools.
- **Safety:** Sandboxed filesystem and review-based approval system.

## 4. Development Milestones & Tagging Strategy

| Tag | Milestone | Description | Status |
|---|---|---|---|
| `v1.0.0-gold` | **Project Genesis 1.0** | Monolithic Human Lifecycle | ✅ Complete |
| `v1.1.0-mac` | **The Psyche** | Multi-Agent Architecture | ⏳ In Progress |
| `v1.2.0-observ` | **The Lab** | Full WebUI Observability & Dashboard | 📅 Planned |
| `v1.3.0-hand` | **The Hand** | Technical Self-Evolution (Coding Agent) | 📅 Planned |

## 5. Technical Specification
- **Inter-Agent Comm:** `memory/reality/internal_comm.json` (Memos with 7-day TTL).
- **Activity Logs:** `memory/telemetry/agents/activity.jsonl`.
- **Role Detection:** `ctx.agent.id` mapping to roles.

---
*Official Roadmap for Project Genesis MAC Evolution.*
