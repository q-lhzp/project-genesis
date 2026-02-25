# Project Genesis: Phase 51 — Interactive Setup Wizard

## 1. Vision
Ein geführter Prozess im Web-Interface, der sicherstellt, dass Project Genesis v5.6.0 korrekt konfiguriert ist. Jedes Subsystem wird erst aktiviert, wenn der zugehörige Live-Test erfolgreich war.

## 2. Onboarding-Workflow

### Schritt 1: Infrastruktur-Check
- **Ziel:** Sicherstellen, dass Python-Bridges und Verzeichnisse bereit sind.
- **UI:** Liste aller Komponenten (Hardware, Vault, Voice, Vision).
- **Test:** Führt `reality_doctor` aus.
- **Erfolgskriterium:** Alle Brücken sind grün.

### Schritt 2: Kognitive Anbindung (AI Models)
- **Ziel:** Authentifizierung bei xAI und Google Gemini.
- **UI:** Eingabefelder für API-Keys.
- **Test:** Kleiner "Ping"-Prompt an das Modell.
- **Erfolgskriterium:** Modell antwortet mit Status "Ready".

### Schritt 3: Finanzielle Basis (The Vault)
- **Ziel:** Verbindung zum Alpaca Live/Paper Trading.
- **UI:** Alpaca Key & Secret Key Felder + Mode-Switch.
- **Test:** Abfrage des Account-Guthabens.
- **Erfolgskriterium:** Aktueller Kontostand wird angezeigt.

### Schritt 4: Visuelle Identität (Avatar)
- **Ziel:** Verifikation des 3D-Modells.
- **UI:** Vorschaubild des Avatars.
- **Test:** Initialisierung des VRM-Loaders.
- **Erfolgskriterium:** "52 BlendShapes detected".

### Schritt 5: Biologische Parameter (Metabolism)
- **Ziel:** Verständnis für Q's Bedürfnisse.
- **UI:** Erklärung des Reflex-Locks.
- **Test:** Simulierter "Stress-Anfall".
- **Erfolgskriterium:** "Sovereignty Status: LOCKED" wird korrekt angezeigt.

## 3. Implementierungs-Vorgaben für Opus-4.6
- Integration direkt in `templates/soul-evolution.html`.
- Keine neuen Ports; Nutzung der bestehenden API auf 8080.
- Automatischer Start, wenn `model_config.json` leer ist.

---
*Status: Geplant (Phase 51).*
