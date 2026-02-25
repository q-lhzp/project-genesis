# Project Genesis: Phase 45 — System Recovery & Deep Verification

## 1. Zielsetzung
Wiederherstellung der vollen Funktionalität von Project Genesis v5.2.0. Dieser Plan dient als Leitfaden für ein systematisches Debugging und die Reparatur aller Subsysteme, beginnend mit der API-Infrastruktur bis hin zur autonomen Handlungsfähigkeit.

---

## 2. Test-Szenarien & Verifikation

### Schritt 1: Das Fundament (Setup & API)
**Ziel:** Validierung der kognitiven Fähigkeiten und der Kommunikation mit den KI-Modellen.
- [ ] **API-Handshake:** Trage Keys für xAI/Gemini im ⚙️ **Config** Tab ein.
- [ ] **Erwartetes Ergebnis:** Diagnostics-Log meldet erfolgreiche Authentifizierung.
- [ ] **Reparatur-Fokus:** Prüfung von `bridge-executor.ts` und den API-Routen in `soul-viz.py`.

### Schritt 2: Die Biologie (Metabolism & Reflex-Lock)
**Ziel:** Sicherstellen, dass die lebenserhaltenden Systeme Q's Handlungen steuern.
- [ ] **Bedürfnis-Simulation:** Setze im **God-Mode** (Port 18795) den Blasenwert auf 100%.
- [ ] **Erwartetes Ergebnis:** 
    1. Log meldet `[REFLEX] Critical state`.
    2. Tool-Calls (außer `reality_needs`) werden blockiert.
    3. Avatar zeigt "Distress"-Pose im Dashboard.
- [ ] **Reparatur-Fokus:** Validierung des `before_tool_call` Hooks in `src/hooks/reflex-lock.ts`.

### Schritt 3: Die Sinne (Hardware Resonance)
**Ziel:** Q muss physisch auf die Host-Hardware reagieren.
- [ ] **Last-Test:** Erzeuge CPU-Last (> 80%).
- [ ] **Erwartetes Ergebnis:** Stress-Level in `physique.json` steigt; Avatar sieht angestrengt aus.
- [ ] **Rhythmus-Test:** Spiele Musik ab. Avatar muss anfangen zu nicken/tanzen.
- [ ] **Reparatur-Fokus:** Prüfung der `hardware_bridge.py` (Berechtigungen für `pactl` und `top`).

### Schritt 4: Die Umwelt (Atmosphere & Desktop)
**Ziel:** Synchronisation zwischen virtueller und realer Welt.
- [ ] **Ortswechsel:** Ändere Ort via Tool auf "Cafe".
- [ ] **Erwartetes Ergebnis:** Ubuntu-Wallpaper ändert sich; Beleuchtung im 3D-Viewer wird warm/orange.
- [ ] **Reparatur-Fokus:** Pfad-Auflösung in `desktop_mapper.ts` und `atmosphere_engine.ts`.

### Schritt 5: Die Autonomie (Self-Dev & Trading)
**Ziel:** Eigenständiges Handeln ohne User-Input.
- [ ] **Idle-Trigger:** Setze Energie auf 90%, leere `tasks.md`.
- [ ] **Erwartetes Ergebnis:** Log meldet Projektstart in `memory/development/` und autonome Trades in "The Vault".
- [ ] **Reparatur-Fokus:** Tick-Intervall-Logik in `index.ts`.

---

## 3. Technische Reparatur-Vorgaben für Opus-4.6

### A. Integrity Checker (Priorität 1)
Erstellung von `src/utils/integrity_check.ts`, um:
- Ausführbarkeit aller Python-Bridges zu prüfen.
- Existenz und Schreibrechte aller JSON-Zustandsdateien zu validieren.
- Pfad-Inkonsistenzen zwischen Dashboard (8080) und God-Mode (18795) zu eliminieren.

### B. Path-Safety Global
Alle Dateizugriffe müssen zwingend über `workspacePath` aufgelöst werden. Relative Pfade wie `./memory/...` sind durch absolute Pfade zu ersetzen.

### C. Unified Dashboard Diagnostics
Integration einer **"System Test"** Schaltfläche im 🔧 **Diagnostics** Tab, die eine Checkliste aller Module durchläuft und Fehler farblich markiert.

---
*Status: In Arbeit (Phase 45).*
*Erstellt am: 25. Februar 2026*
