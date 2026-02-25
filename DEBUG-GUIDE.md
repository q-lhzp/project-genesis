# Genesis Sovereignty & Debug Suite — Bedienungsanleitung (v5.6.0)

Dieses Dokument beschreibt die Nutzung der integrierten Debug-, Kontroll- und Onboarding-Werkzeuge von Project Genesis.

## 1. Initiales Setup (Onboarding Wizard)
Beim ersten Start oder bei fehlenden API-Keys startet automatisch der **Interactive Setup Wizard**.
- **URL:** `http://localhost:8080/soul-evolution.html`
- **Ablauf:** Der Wizard führt durch 5 Schritte (Infrastruktur, KI-Modelle, Finanzen, 3D-Avatar, Biologie). Jeder Schritt beinhaltet einen Live-Funktionstest.
- **Reset:** Um den Wizard erneut zu starten, setze `"setup_complete": false` in der `simulation_config.json`.

---

## 2. Das Web-Interface (God-Mode)
Der integrierte **⚡ God-Mode** Tab im Haupt-Dashboard ist der zentrale Kontrollpunkt für Forscher.

### Features:
- **🎚️ Direct Needs Control:** Echtzeit-Manipulation der Biologie via Slider.
- **🎲 Event Injector:** Manuelle Injektion von Lebensereignissen (positiv/negativ).
- **🛡️ Reflex Status:** Live-Anzeige der Souveränitätssperre (aktiv bei Needs >= 95%).
- **📈 Vault Sandbox:** Überwachung der Alpaca-Konnektivität und Simulation von Trades.
- **🎭 Expression Monitor:** Live-Anzeige der 52+ BlendShape-Gewichte des Avatars.

---

## 3. Autonome Diagnose-Tools (Agent-Mode)
Diese Tools können direkt als KI-Befehl oder über das Terminal aufgerufen werden.

| Befehl | Zweck |
| :--- | :--- |
| `reality_doctor` | Tiefenprüfung (Pfade, Rechte, API-Credentials, BlendShape-Keys). |
| `reality_run_self_test` | Umfassender Integritätsbericht aller Engines (Metabolism, Economy, Social, Hardware). |
| `reality_simulate_scenario` | Erzwingt Zustände (z.B. `critical_reflex`, `market_surge`, `night_recovery`). |

---

## 4. Entwickler-API (Port 8080)
Zusätzliche Endpunkte für externe Überwachung und Automatisierung:

| Methode | Pfad | Beschreibung |
| :--- | :--- | :--- |
| GET | `/api/godmode/physique` | Aktuellen Status der Bedürfnisse lesen |
| GET | `/api/godmode/vault/status` | Kontostand, Positionen und API-Status prüfen |
| GET | `/api/godmode/avatar/weights` | Aktuelle Gesichtsausdrücke (52 BlendShapes) auslesen |
| GET | `/api/wizard/status` | Aktuellen Setup-Fortschritt abfragen |
| POST | `/api/godmode/override/needs` | Bedürfnisse hart überschreiben |
| POST | `/api/godmode/inject/event` | Ein manuelles Lebensereignis triggern |

---

## 5. Troubleshooting
Falls das Interface oder Subsysteme nicht reagieren:
1. **Dienst neu starten:** `./restart-dashboard.sh` ausführen.
2. **Browser-Cache:** `Strg + F5` drücken (zwingend erforderlich nach Updates!).
3. **Doctor ausführen:** Rufe `reality_doctor` auf, um automatische Reparaturen (z.B. Rechte-Fixes) zu triggern.

---
*Status: Digital Sovereignty v5.6.0 - High-Fidelity Infrastructure Verified.*
