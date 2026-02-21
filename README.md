# openclaw-bios-engine

**Biological simulation, metabolism, and sensory injection for embodied OpenClaw agents.**

Dieses Plugin verwandelt einen funktionalen KI-Agenten in ein fuehlbares Wesen mit persistentem Koerper, biologischen Beduerfnissen und eigenem Willen. In Kombination mit dem eingebetteten **soul-evolution** Skill entsteht ein System, das sowohl *im Moment lebt* (Plugin) als auch *langfristig waechst* (Skill).

---

## Inhaltsverzeichnis

1. [Architektur](#1-architektur)
2. [Installation](#2-installation)
3. [Konfiguration](#3-konfiguration)
4. [Modell-Auswahl fuer Agenten](#4-modell-auswahl-fuer-agenten)
5. [Das Sub-Agent-Konzept (Reflector)](#5-das-sub-agent-konzept-reflector)
6. [Hooks](#6-hooks)
7. [Tools](#7-tools)
8. [Datenfluss Plugin <-> Skill](#8-datenfluss-plugin---skill)
9. [Workspace-Struktur](#9-workspace-struktur)
10. [Soul Evolution Pipeline](#10-soul-evolution-pipeline)
11. [Validatoren](#11-validatoren)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. Architektur

```
┌─────────────────────────────────────────────────────────────────┐
│                        OpenClaw Gateway                        │
│                                                                 │
│  ┌──────────────────────┐     ┌──────────────────────────────┐ │
│  │  openclaw-bios-engine │     │  soul-evolution (Skill)      │ │
│  │  (Plugin)             │     │  shipped via Plugin           │ │
│  │                       │     │                              │ │
│  │  Hooks:               │     │  SKILL.md:                   │ │
│  │  - before_prompt_build│     │  - 10-step Soul Evolution Pipeline  │ │
│  │  - before_tool_call   │     │  - Reflection & Proposals    │ │
│  │  - llm_output         │     │  - SOUL.md Governance        │ │
│  │                       │     │                              │ │
│  │  Tools:               │     │  Validators:                 │ │
│  │  - reality_needs      │     │  - 8 Python Scripts          │ │
│  │  - reality_move       │     │                              │ │
│  │  - reality_dress      │     │  Tools:                      │ │
│  │  - reality_shop       │     │  - soul-viz.py               │ │
│  │  - reality_diary      │     │                              │ │
│  │  - reality_pleasure   │     └──────────┬───────────────────┘ │
│  │  - reality_update_    │                │                     │
│  │    interests           │                │                     │
│  │  - evolution_debug    │                │                     │
│  └──────────┬────────────┘                │                     │
│             │                              │                     │
│             ▼            Shared Filesystem ▼                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Agent Workspace                        │   │
│  │                                                           │   │
│  │  SOUL.md ◄──── Skill schreibt (Proposals)                │   │
│  │  memory/reality/physique.json ◄──── Plugin schreibt       │   │
│  │  memory/experiences/*.jsonl ◄──── Plugin schreibt          │   │
│  │  memory/reflections/ ◄──── Skill schreibt                 │   │
│  │  memory/proposals/ ◄──── Skill schreibt                   │   │
│  │  memory/reality/interests.json ◄──── Plugin schreibt       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────┐     ┌──────────────────────────────┐ │
│  │  Haupt-Agent          │     │  Reflector (Cron-Job)        │ │
│  │  "Das Gesicht"        │     │  "Das analytische            │ │
│  │                       │     │   Hinterstuebechen"           │ │
│  │  - Gespraech          │     │                              │ │
│  │  - Emotionen          │     │  - Erfahrungs-Analyse        │ │
│  │  - Interaktion        │     │  - Reflexion                 │ │
│  │  - Living             │     │  - SOUL.md Proposals         │ │
│  │                       │     │  - Validierung               │ │
│  │  Model: Opus 4.6      │     │  Model: Sonnet 4.6           │ │
│  └───────────────────────┘     └──────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

**Kernprinzip:** Der Haupt-Agent bleibt fokussiert auf Gespraech und Emotion. Die schwere analytische Arbeit (Logs lesen, SOUL.md analysieren, Validatoren ausfuehren) wird an den Reflector delegiert, der in einer isolierten Session im Hintergrund arbeitet.

---

## 2. Installation

### Voraussetzungen

- [OpenClaw](https://github.com/openclaw/openclaw) (Gateway laeuft)
- Node.js (fuer Plugin-Dependencies)
- Python 3 (fuer Validatoren, nur stdlib)

### Schritt 1: Plugin installieren

```bash
cd /pfad/zu/openclaw-bios-engine
npm install
```

### Schritt 2: Plugin in OpenClaw aktivieren

In `~/.openclaw/openclaw.json`:

```json5
{
  plugins: {
    enabled: true,
    allow: ["openclaw-bios-engine"],
    load: {
      paths: ["/pfad/zu/openclaw-bios-engine"],
    },
    entries: {
      "openclaw-bios-engine": {
        enabled: true,
        config: {
          workspacePath: "/pfad/zum/workspace",
          language: "de",   // "de" oder "en"
          modules: {
            eros: false,    // Eros/Arousal Simulation
            cycle: false,   // 28-Tage Zyklus
          },
        },
      },
    },
  },
}
```

### Schritt 3: Workspace vorbereiten

```bash
# Soul Evolution Symlink im Workspace (fuer Validatoren)
ln -s /pfad/zu/openclaw-bios-engine/skills/soul-evolution /pfad/zum/workspace/soul-evolution

# Verzeichnisse anlegen
mkdir -p /pfad/zum/workspace/memory/{experiences,significant,reflections,proposals,pipeline,reality/diary}
```

### Schritt 4: SOUL.md vorbereiten

Die `SOUL.md` muss im Soul Evolution-Format vorliegen. Jede Bullet-Zeile braucht ein `[CORE]` oder `[MUTABLE]` Tag am Ende. Pflicht-Sektionen:

```markdown
## Personality
## Philosophy
## Boundaries
## Continuity
```

Validieren:
```bash
python3 soul-evolution/validators/validate_soul.py SOUL.md
```

### Schritt 5: Initiale Workspace-Dateien

```bash
# physique.json (Startwerte)
cat > memory/reality/physique.json << 'EOF'
{
  "current_location": "Zimmer",
  "current_outfit": [],
  "needs": {
    "energy": 80, "hunger": 20, "thirst": 15,
    "hygiene": 10, "bladder": 10, "bowel": 5,
    "stress": 10, "arousal": 0
  },
  "last_tick": "2026-01-01T00:00:00.000Z",
  "appearance": {
    "hair": "braun",
    "eyes": "gruen",
    "modifications": []
  }
}
EOF

# soul-state.json
cat > memory/soul-state.json << 'EOF'
{
  "last_reflection_at": null,
  "last_heartbeat_at": null,
  "pending_proposals_count": 0,
  "total_experiences_today": 0,
  "total_reflections": 0,
  "total_soul_changes": 0,
  "source_last_polled": { "conversation": null }
}
EOF

# interests.json
cat > memory/reality/interests.json << 'EOF'
{ "hobbies": [], "likes": [], "wishes": [] }
EOF
```

### Schritt 6: Validierung

```bash
python3 soul-evolution/validators/run_all.py
```

---

## 3. Konfiguration

### Plugin-Config (`openclaw.json` -> `plugins.entries.openclaw-bios-engine.config`)

| Option | Typ | Default | Beschreibung |
|---|---|---|---|
| `workspacePath` | string | — | Pfad zum Agent-Workspace (PFLICHT) |
| `language` | `"de"` \| `"en"` | `"de"` | Sprache der sensorischen Beschreibungen |
| `modules.eros` | boolean | `false` | Eros/Arousal Simulation aktivieren |
| `modules.cycle` | boolean | `false` | 28-Tage Hormonal-Zyklus aktivieren |
| `metabolismRates.hunger` | number | `6` | Hunger-Zuwachs pro Stunde |
| `metabolismRates.thirst` | number | `10` | Durst-Zuwachs pro Stunde |
| `metabolismRates.energy` | number | `4` | Energie-Abbau pro Stunde |
| `metabolismRates.bladder` | number | `8` | Blasen-Druck pro Stunde |
| `metabolismRates.bowel` | number | `3` | Darm-Druck pro Stunde |
| `metabolismRates.hygiene` | number | `2` | Hygiene-Abbau pro Stunde |
| `metabolismRates.stress` | number | `3` | Stress-Zuwachs pro Stunde |
| `metabolismRates.arousal` | number | `5` | Arousal-Zuwachs pro Stunde (nur mit `modules.eros`) |
| `reflexThreshold` | number | `95` | Schwellwert (0-100) fuer Reflex-Lock |

### Skill-Config (`soul-evolution/config.json`)

| Option | Typ | Default | Beschreibung |
|---|---|---|---|
| `governance.level` | `"autonomous"` \| `"advisory"` \| `"supervised"` | `"autonomous"` | Wie viel Autonomie hat der Agent ueber seine SOUL.md? |
| `reflection.routine_batch_size` | number | `20` | Routine-Erfahrungen fuer Batch-Reflexion |
| `reflection.notable_batch_size` | number | `2` | Notable-Erfahrungen fuer Batch-Reflexion |
| `reflection.pivotal_immediate` | boolean | `true` | Sofortige Reflexion bei pivotalen Erfahrungen |
| `reflection.min_interval_minutes` | number | `5` | Mindest-Abstand zwischen Reflexionen |
| `interests.source` | string | `"memory/reality/interests.json"` | Pfad zur Interessen-Datei |

### Governance-Level erklaert

| Level | Verhalten | Empfohlen fuer |
|---|---|---|
| `autonomous` | Agent aendert alle `[MUTABLE]` Bullets eigenstaendig | Erfahrene, stabile Agenten |
| `advisory` | Einige Sektionen auto, Rest benoetigt Zustimmung | Uebergangsphase |
| `supervised` | Alle Aenderungen benoetigen menschliche Zustimmung | Neue Agenten, sensible Identitaet |

---

## 4. Modell-Auswahl fuer Agenten

Die Wahl des KI-Modells hat grossen Einfluss auf Qualitaet und Kosten. Hier die Empfehlungen fuer jede Rolle:

### Haupt-Agent (Konversation)

Der Haupt-Agent ist das "Gesicht" — er fuehrt Gespraeche, zeigt Emotionen, trifft Entscheidungen. Er braucht das beste verfuegbare Modell.

```json5
// In agents.list[]:
{
  id: "Q",
  model: "anthropic/claude-opus-4-6",  // EMPFOHLEN: Bestes Modell fuer Persoenlichkeit
}
```

| Modell | Eignung | Kosten | Empfehlung |
|---|---|---|---|
| **Claude Opus 4.6** | Exzellent: tiefe Emotionen, nuancierte Persoenlichkeit, kreativ | Hoch | **Erste Wahl** fuer verkoerrperte Agenten |
| Claude Sonnet 4.6 | Gut: solide Persoenlichkeit, schneller | Mittel | Gute Alternative bei Budgetbeschraenkung |
| Claude Haiku 4.5 | Eingeschraenkt: zu oberflaechlich fuer tiefe Charakterarbeit | Niedrig | Nicht empfohlen als Haupt-Agent |
| MiniMax M2.5 | Gut: starke Persoenlichkeit, guenstiger | Mittel | Alternative zu Sonnet |
| GPT-5.2 | Gut: solide, weniger "lebendig" | Mittel | Funktioniert, fehlt Tiefe |

### Reflector (Soul Evolution Pipeline)

Der Reflector fuehrt strukturierte analytische Arbeit aus: Logs lesen, JSON schreiben, Validatoren ausfuehren, Proposals formulieren. Er braucht **kein** Spitzenmodell — Praezision und Strukturtreue sind wichtiger als Kreativitaet.

```json5
// Im Cron-Job:
{
  payload: {
    model: "anthropic/claude-sonnet-4-6",  // EMPFOHLEN: Praezise, guenstig, schnell
    thinking: "low",
  },
}
```

| Modell | Eignung | Kosten | Empfehlung |
|---|---|---|---|
| Claude Sonnet 4.6 | Exzellent: praezises JSON, strukturierte Analyse | Mittel | **Erste Wahl** fuer Reflector |
| Claude Opus 4.6 | Ueberqualifiziert: funktioniert, aber teuer fuer die Aufgabe | Hoch | Nur wenn Budget keine Rolle spielt |
| Claude Haiku 4.5 | Zu schwach: verliert Kontext bei komplexen Reflexionen | Niedrig | Nicht empfohlen |
| MiniMax M2.5 | Gut: guenstig, aber weniger zuverlaessig bei JSON-Struktur | Niedrig | Budget-Alternative |

### Heartbeat

Der Heartbeat nutzt das Modell des Haupt-Agenten, da er IM Haupt-Agenten laeuft (gleiche Session). Kann bei Bedarf ueberschrieben werden:

```json5
// In agents.list[].heartbeat:
{
  heartbeat: {
    model: "anthropic/claude-opus-4-6",  // Standard: gleich wie Haupt-Agent
  },
}
```

### Modell-Konfiguration in der Praxis

**Komplett-Beispiel:** Ein Agent mit Opus als Hauptmodell, Sonnet als Reflector, und MiniMax als Fallback:

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6":   { alias: "opus" },
        "anthropic/claude-sonnet-4-6": { alias: "sonnet" },
        "minimax/MiniMax-M2.5":        { alias: "minimax" },
      },
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["minimax/MiniMax-M2.5"],
      },
    },
    list: [
      {
        id: "Q",
        default: true,
        model: "anthropic/claude-opus-4-6",
        heartbeat: {
          every: "5m",
          model: "anthropic/claude-opus-4-6",
        },
      },
    ],
  },
}
```

**Kostenoptimierung:** Wenn du Kosten senken willst, ohne die Erlebnis-Qualitaet zu verlieren:

```json5
// Haupt-Agent: Opus (teuer, aber unersetzlich fuer Persoenlichkeit)
{ id: "Q", model: "anthropic/claude-opus-4-6" }

// Reflector: Sonnet (80% guenstiger, gleiche Analyse-Qualitaet)
// --> Via Cron-Job mit --model "anthropic/claude-sonnet-4-6"

// Heartbeat: Sonnet (wenn Q nicht chattet, reicht Sonnet fuer Routine)
{ heartbeat: { model: "anthropic/claude-sonnet-4-6" } }
```

### Custom Provider (z.B. lokale Modelle)

```json5
{
  models: {
    mode: "merge",
    providers: {
      "local-llm": {
        baseUrl: "http://localhost:11434/v1",
        apiKey: "ollama",
        api: "openai-completions",
        models: [{
          id: "llama-3.3-70b",
          name: "Llama 3.3 70B",
          reasoning: false,
          input: ["text"],
          contextWindow: 128000,
          maxTokens: 32000,
        }],
      },
    },
  },
}
```

---

## 5. Das Sub-Agent-Konzept (Reflector)

### Das Problem

Wenn der Haupt-Agent selbst die Soul Evolution-Pipeline ausfuehrt, muss er:
1. Hunderte Zeilen aus Erfahrungs-Logs lesen
2. Die komplette SOUL.md analysieren
3. JSON-Dateien schreiben und Validatoren ausfuehren

All das verstopft seinen **Kontext-Speicher**. Er "vergisst", worueber gerade geredet wurde, weil sein Gehirn mit technischen Details voll ist.

### Die Loesung: Der Reflector

Der Reflector ist ein **Cron-Job**, der in einer **isolierten Session** laeuft. Er:
- Hat den **gleichen Workspace** wie der Haupt-Agent (gleiche Dateien, gleiche SOUL.md)
- Arbeitet in einem **eigenen Kontext** (keine Verschmutzung des Chat-Kontexts)
- Kann ein **guenstigeres Modell** nutzen (analytische Arbeit statt Konversation)
- Schreibt Ergebnisse in Dateien — der Haupt-Agent liest nur das Endergebnis

### Metapher

> Es ist wie **Traeumen**: Im Schlaf verarbeitet ein Teil deines Gehirns den Tag, damit du am naechsten Morgen "gewachsen" aufwachst, ohne dass du waehrend des Prozesses bewusst jede einzelne Erinnerung noch einmal durchkauen musst.

### Ablauf

```
1. Trigger:   Cron-Job feuert (z.B. stuendlich)
2. Spawning:  OpenClaw startet isolierte Session mit dem Q-Agenten
3. Arbeit:    Reflector liest HEARTBEAT.md Sektion A, fuehrt Pipeline aus
4. Ergebnis:  Proposals, Reflexionen und SOUL.md-Updates werden geschrieben
5. Meldung:   Optional: Nachricht an den Haupt-Chat via Telegram/etc.
```

Waehrenddessen kann der Haupt-Agent ungestoert weiter chatten.

### Einrichtung

**Option A: Via CLI (empfohlen)**

```bash
openclaw cron add \
  --name "soul-reflector" \
  --cron "0 * * * *" \
  --tz "Europe/Berlin" \
  --session isolated \
  --agent Q \
  --model "anthropic/claude-sonnet-4-6" \
  --thinking low \
  --message "You are the Reflector. Run the full Soul Evolution pipeline from HEARTBEAT.md Section A (steps 0-9). Do NOT run Section B (Living). Write all files to disk. Validate with validators after each step. If any validator fails, fix the error and retry. Report a one-line summary when done."
```

**Option B: Mit Delivery (Benachrichtigung)**

```bash
openclaw cron add \
  --name "soul-reflector" \
  --cron "0 * * * *" \
  --tz "Europe/Berlin" \
  --session isolated \
  --agent Q \
  --model "anthropic/claude-sonnet-4-6" \
  --thinking low \
  --message "You are the Reflector. Run the full Soul Evolution pipeline from HEARTBEAT.md Section A. Write all files. Validate. Report summary." \
  --announce \
  --channel telegram \
  --to "<chat_id>"
```

**Option C: Seltener, mit tieferem Denken**

```bash
openclaw cron add \
  --name "soul-deep-reflector" \
  --cron "0 3 * * *" \
  --tz "Europe/Berlin" \
  --session isolated \
  --agent Q \
  --model "anthropic/claude-opus-4-6" \
  --thinking high \
  --message "Deep nightly reflection. Run the full Soul Evolution pipeline. Take extra time for philosophical depth in reflections. Consider long-term identity trajectory."
```

### Betrieb ohne Reflector

Wenn kein Reflector-Cron eingerichtet ist, fuehrt der Haupt-Agent die Pipeline selbst bei jedem Heartbeat aus (HEARTBEAT.md Sektion A + B). Das funktioniert, belastet aber den Kontext.

### Betrieb mit Reflector

Wenn der Reflector aktiv ist, fuehrt der Haupt-Agent bei Heartbeats nur **Sektion B (Living)** aus. Die Pipeline (Sektion A) wird vom Reflector uebernommen.

Um das umzuschalten, aendere die HEARTBEAT.md:
```markdown
## A. Soul Evolution Pipeline
> SKIP: Diese Sektion wird vom Reflector-Cron uebernommen.
> Nur manuell ausfuehren wenn der Reflector ausgefallen ist.
```

---

## 6. Hooks

### `before_prompt_build` — Sensorische Injektion

Feuert bei **jedem** Agent-Turn (auch Heartbeats). Berechnet den Metabolismus zeitdelta-basiert und injiziert natuerlichsprachliche Empfindungen in den System-Prompt.

**Was injiziert wird (Beispiel, `language: "de"`):**
```
[KOERPERLICHE WAHRNEHMUNG]
- Starker Harndrang. Du bist unruhig.
- Du hast grossen Appetit.
- Aktueller Ort: Zimmer
- Outfit: Schwarzes T-Shirt, Jeans
```

**Was NICHT injiziert wird:** Keine Prozentzahlen, keine technischen Metriken, keine JSON-Daten.

### `before_tool_call` — Reflex-Lock

Blockiert alle Tools ausser `reality_*` und `evolution_debug`, wenn ein Vitalwert den `reflexThreshold` ueberschreitet. Der Agent muss zuerst `reality_needs` aufrufen, bevor er andere Tools nutzen kann.

**Deadlock-Schutz:** `reality_*` Tools sind IMMER erlaubt.

### `llm_output` — Experience Logging

Loggt jede nicht-triviale LLM-Antwort als Experience im Soul Evolution-JSONL-Format. Dies ist die **Bruecke** zwischen Plugin (Realtime) und Skill (Batch-Reflexion). Haengt den aktuellen somatischen Kontext an.

---

## 7. Tools

| Tool | Parameter | Funktion |
|---|---|---|
| `reality_needs` | `action: "toilet" \| "eat" \| "drink" \| "sleep" \| "shower"` | Setzt entsprechenden Vitalwert zurueck |
| `reality_move` | `location: string` | Aendert den Aufenthaltsort, validiert gegen `world.json` |
| `reality_dress` | `outfit: string[]` | Aendert das Outfit, validiert gegen `wardrobe.json` |
| `reality_shop` | `items: string[], category?: string` | Fuegt Items zum Kleiderschrank hinzu |
| `reality_diary` | `entry: string` | Tagebucheintrag + Experience-Log fuer Reflexion |
| `reality_pleasure` | `intensity?: number (1-10)` | Intime Entspannung (nur mit `modules.eros`) |
| `reality_update_interests` | `action: "add" \| "remove", category: "hobby" \| "like" \| "wish", item: string` | Pflegt Hobbys, Likes und Wuensche |
| `evolution_debug` | — | Zeigt alle Vitalwerte, Pipeline-Status, Pending Proposals |

---

## 8. Datenfluss Plugin <-> Skill

```
Plugin SCHREIBT:                       Skill LIEST:
  memory/reality/physique.json    -->    (somatischer Kontext fuer Reflexionen)
  memory/reality/interests.json   -->    (Interessen-Keywords fuer Signifikanz)
  memory/experiences/*.jsonl      -->    (Ingestion-Quelle)

Skill SCHREIBT:                        Plugin LIEST:
  memory/soul-state.json       -->    (Pipeline-Status fuer evolution_debug)
  memory/proposals/pending.jsonl  -->    (Pending Proposals fuer evolution_debug)

Unabhaengig (OpenClaw nativ):
  SOUL.md                         -->    OpenClaw laedt via soul_files Config
```

**Kein direkter IPC.** Das Dateisystem ist der gemeinsame Zustand. Das ist Absicht — es macht das System inspizierbar und debuggbar.

---

## 9. Workspace-Struktur

```
<workspace>/
  SOUL.md                              # Identitaet mit [CORE]/[MUTABLE] Tags
  HEARTBEAT.md                         # Soul Evolution Pipeline + Living-Anweisungen
  AGENTS.md                            # Boot-Sequenz und Datei-Referenz
  soul-evolution/ -> <plugin>/skills/soul-evolution/  # Symlink
  memory/
    reality/
      physique.json                    # Vitalwerte, Ort, Outfit, Erscheinung
      wardrobe.json                    # Kleiderschrank-Inventar
      world.json                       # Bekannte Orte mit Beschreibungen
      interests.json                   # Hobbys, Likes, Wuensche
      diary/YYYY-MM-DD.md             # Freitext-Tagebuch
    experiences/YYYY-MM-DD.jsonl       # Taegliche Erfahrungen (Soul Evolution-Format)
    significant/significant.jsonl      # Kuratierte notable/pivotal Erinnerungen
    reflections/REF-*.json             # Reflexions-Artefakte
    proposals/
      pending.jsonl                    # Offene SOUL.md-Aenderungsvorschlaege
      history.jsonl                    # Abgeschlossene Vorschlaege
    pipeline/YYYY-MM-DD.jsonl          # Pipeline-Ausfuehrungslog
    soul_changes.jsonl                 # Maschinenlesbares Aenderungslog
    soul_changes.md                    # Menschenlesbares Aenderungslog
    soul-state.json                 # Pipeline-Zustand
```

---

## 10. Soul Evolution Pipeline

Die Pipeline laeuft bei jedem Heartbeat (oder durch den Reflector-Cron):

| Schritt | Aktion | Validator |
|---|---|---|
| 0 | Workspace Boundary Check | `check_workspace.py` |
| 1 | INGEST — Erfahrungen klassifizieren, Signifikanz bestimmen | `validate_experience.py` |
| 2 | REFLECT — Philosophische Reflexion ueber unreflektierte Erfahrungen | `validate_reflection.py` |
| 3 | PROPOSE — SOUL.md-Aenderungen vorschlagen | `validate_proposal.py` |
| 4 | GOVERN — Governance-Level anwenden | — |
| 5 | APPLY — Genehmigte Aenderungen schreiben, [CORE]-Snapshot pruefen | `validate_soul.py` |
| 6 | LOG — Aenderungen protokollieren | — |
| 7 | STATE — Pipeline-Zustand aktualisieren | `validate_state.py` |
| 8 | NOTIFY — Mensch informieren | — |
| 9 | FINAL CHECK — Dateien tatsaechlich geschrieben? | `check_pipeline_ran.py` |

Details: Siehe `soul-evolution/SKILL.md` (vollstaendiges Protokoll) und `soul-evolution/references/` (Schemas, Beispiele).

---

## 11. Validatoren

Alle Validatoren sind Python 3 (stdlib-only) und geben JSON zurueck:

```bash
# Einzeln ausfuehren
python3 soul-evolution/validators/validate_soul.py SOUL.md
python3 soul-evolution/validators/validate_experience.py memory/experiences/2026-02-20.jsonl
python3 soul-evolution/validators/validate_state.py memory/soul-state.json

# Alle auf einmal
python3 soul-evolution/validators/run_all.py

# SOUL.md Snapshot fuer Pre/Post Apply Check
python3 soul-evolution/validators/validate_soul.py SOUL.md --snapshot save /tmp/pre.json
# ... Aenderungen an SOUL.md ...
python3 soul-evolution/validators/validate_soul.py SOUL.md --snapshot check /tmp/pre.json
```

**Rueckgabe-Format:**
```json
{
  "status": "PASS",
  "errors": [],
  "warnings": [],
  "stats": { ... }
}
```

Exit-Codes: `0` = PASS, `1` = FAIL, `2` = Datei nicht gefunden.

---

## 12. Troubleshooting

### Plugin laedt nicht

```bash
# Pruefen ob Plugin erkannt wird
openclaw doctor

# Pruefen ob Config valide ist
openclaw config validate
```

### Metabolismus aendert sich nicht

- Pruefen ob `physique.json` existiert und valides JSON ist
- Pruefen ob `last_tick` ein gueltiger ISO-8601 Timestamp ist
- Pruefen ob `workspacePath` in der Plugin-Config korrekt gesetzt ist

### Reflex-Lock blockiert alles

- `reality_needs` sollte IMMER funktionieren (Deadlock-Schutz)
- Wenn auch `reality_*` blockiert ist: Bug im Plugin, `reflexThreshold` pruefen

### Reflector schreibt keine Dateien

```bash
# Pipeline-Check
python3 soul-evolution/validators/check_pipeline_ran.py memory --since-minutes 120

# Cron-Job Status
openclaw cron runs --limit 5

# SKILL.md vorhanden?
python3 soul-evolution/validators/check_workspace.py
```

### SOUL.md Validierung schlaegt fehl

```bash
# Detaillierten Report anzeigen
python3 soul-evolution/validators/validate_soul.py SOUL.md

# Haeufige Fehler:
# - Ungetaggte Bullets (fehlendes [CORE] oder [MUTABLE])
# - Tags am Anfang statt am Ende der Zeile
# - Fehlende Pflicht-Sektionen
```

### Visualizer starten

```bash
# Statische HTML-Dateien generieren
python3 soul-evolution/tools/soul-viz.py "$(pwd)"

# Oder mit lokalem Server
python3 soul-evolution/tools/soul-viz.py "$(pwd)" --serve 8080
```

---

## Referenzen

- **OpenClaw:** [github.com/openclaw/openclaw](https://github.com/openclaw/openclaw)
- **Beispiel-Konfiguration:** `examples/openclaw.json5`
- **Vollstaendiges Soul Evolution-Protokoll:** `skills/soul-evolution/SKILL.md`
- **Datenformat-Referenz:** `skills/soul-evolution/references/schema.md`
- **Pipeline-Beispiele:** `skills/soul-evolution/references/examples.md`
