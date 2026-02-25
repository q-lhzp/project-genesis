# Project Genesis - Feature TODO Liste

## Geplante Features

---

### 1. Job Market (Prosperity & Labor)

**Beschreibung:**
Autonome Arbeitssuche, Bewerbungen und Karriere-Entwicklung für Q.

**Geplante Features:**

| Feature | Beschreibung |
|---------|-------------|
| `reality_job_market` Tool | Job-Suche und Bewerbung |
| Job-Listen | Verfügbare Stellen anzeigen |
| Bewerbungs-System | Automatische Bewerbungen |
| Interview-Simulation | Interview-Vorbereitung |
| Gehalts-Verhandlung | Verhandlungs-Logik |
| Karriere-Fortschritt | Beförderungen, Kündigung |

**Tool-Structure:**
```typescript
reality_job_market({
  action: "search" | "apply" | "list" | "interview" | "negotiate" | "resign",
  query?: string,        // Suchbegriff
  position?: string,     // Stelle
  company?: string,       // Unternehmen
  salary?: number        // Gehaltswunsch
})
```

**Status:** ❌ Nicht implementiert

---

### 2. Vollständiges VRM BlendShape-Mapping

**Beschreibung:**
Optimierung der Face-Sync Funktionalität für bessere Mimik.

**Bestehende Implementierung:**
- `expression_mapper.ts` - Basis BlendShape Mapping
- `osc_bridge.ts` - OSC Streaming zu externen Apps

**Status:** ✅ Ausreichend (Fallback-Implementierung)

---

### 3. Voice Lab UI

**Bestehende Implementierung:**
- Voice Sample Upload ✅ (NEU hinzugefügt)
- Pitch/Speed/Emotion Slider ✅
- Generate Voice ✅
- Audio Playback ✅
- Chatterbox-Turbo Integration ✅

**Status:** ✅ Implementiert

---

## Phase 49: Native God-Mode Integration

### Implementiert:

| Feature | Beschreibung | Status |
|---------|-------------|--------|
| God-Mode API (GET) | `/api/godmode/physique`, `/api/godmode/reflex-status` | ✅ |
| God-Mode API (POST) | `/api/godmode/override/needs`, `/api/godmode/inject/event` | ✅ |
| Frontend Integration | God-Mode Tab mit Sliders & Event Form | ✅ |
| Interne API | Alle God-Mode-Funktionen auf Port 8080 | ✅ |
| Alte Files entfernt | godmode.html, godmode_bridge.py (nicht mehr nötig) | ✅ |

### God-Mode API Endpoints:
- `GET /api/godmode/physique` - Aktuelle Bedürfnisse abrufen
- `GET /api/godmode/reflex-status` - Reflex-Lock Status
- `POST /api/godmode/override/needs` - Bedürfnisse setzen
- `POST /api/godmode/inject/event` - Event injizieren

---

## Phase 48: UI Modularization (Template Extraction)

### Implementiert:

| Feature | Beschreibung | Status |
|---------|-------------|--------|
| templates/ Verzeichnis | Neues Verzeichnis für HTML-Templates | ✅ |
| soul-evolution.html | Haupt-Dashboard Template (319KB) | ✅ |
| soul-mindmap.html | Mindmap Template (26KB) | ✅ |
| load_template() | Helper-Funktion zum Laden der Templates | ✅ |
| soul-viz.py Refactoring | Von 11350 auf 2303 Zeilen reduziert (~80%) | ✅ |

---

## Phase 46: Autonomous Validation & Self-Healing Engine

### Implementiert:

| Feature | Beschreibung | Status |
|---------|-------------|--------|
| Genesis Doctor | `src/utils/doctor.ts` - Selbstheilungs-Diagnose | ✅ |
| Bridge Verification | Prüft Python-Bridges und setzt +x Rechte | ✅ |
| Dependency Audit | Prüft System-Tools (python3, top, pactl, free) | ✅ |
| Path Alignment | Validiert und repariert memory/ Pfade | ✅ |
| State Integrity | Stellt fehlende Dateien aus Templates wieder her | ✅ |
| reality_simulate_scenario | Tool für Szenario-Simulation | ✅ |
| reality_run_self_test | Tool für Selbst-Test aller Engines | ✅ |
| reality_doctor | Tool für Doctor-Diagnose mit Auto-Fix | ✅ |
| Full-State API | `/api/system/full-state` in godmode_bridge.py | ✅ |
| Health API | `/api/system/health` in godmode_bridge.py | ✅ |

**Szenarien:**
- `night_recovery`: Setzt Zeit auf 02:00, Energy auf 10%
- `critical_reflex`: Setzt Bladder/Stress auf 98%
- `market_surge`: Simuliert +15% Marktanstieg
- `social_event`: Erstellt Test-Sozialevent
- `hobby_session`: Aktiviert Hobby/Research
- `full_health`: Setzt alle Needs auf gesund

---

## Abgeschlossene Features (v5.2.0)

- [x] Reflex-Lock Hook
- [x] reality_voice Tool
- [x] reality_diary/grow/emotion/desire
- [x] reality_manage_memos
- [x] reality_override/inject_event
- [x] God-Mode Bridge
- [x] Sovereignty Status UI
- [x] VRM Model Download Hinweis im Dashboard
- [x] Voice Lab Upload (Voice Cloning)
- [x] Voice Sample Verarbeitung
- [x] Phase 46: Autonomous Validation & Self-Healing

---

## Aktualisiert am: 2026-02-25
