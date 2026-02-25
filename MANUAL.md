# Project Genesis v5.1.0 — Benutzerhandbuch

Willkommen bei **Project Genesis**. Dieses Handbuch erklärt den Umgang mit dem KI-Lebenssimulations-Framework.

---

## 1. Installation

### Schnell-Installation
```bash
cd ~/Schreibtisch/project-genesis
./install.sh
```

### Oder manuell
Siehe `README.md` für vollständige Installationsanleitung.

---

## 2. Das System steuern

### OpenClaw Gateway
```bash
# Neustart nach Config-Änderungen
openclaw gateway restart

# Status prüfen
openclaw plugins list | grep genesis

# Logs anzeigen
openclaw logs
```

### Dashboard (Optional)
Das Dashboard kann als **Systemd-Dienst** laufen:

- **Neustart:** `sudo systemctl restart project-genesis-dashboard`
- **Stoppen:** `sudo systemctl stop project-genesis-dashboard`
- **Starten:** `sudo systemctl start project-genesis-dashboard`
- **Prüfen:** `systemctl status project-genesis-dashboard`

**Logs & Fehlerdiagnose:**
- System-Logs: `journalctl -u project-genesis-dashboard -n 50`
- Simulation-Logs: Prüfe im Dashboard den Reiter **🔧 Diagnostics**

---

## 3. Soul Evolution nutzen

### Befehle via Telegram
- `/soul_evolution status` — Aktuellen Status abrufen
- `/soul_evolution reflect` — Reflexion starten

### Validierung
```bash
python3 ~/Schreibtisch/project-genesis/skills/soul-evolution/validators/run_all.py
```

---

## 4. Der biologische Zyklus

Q ist eine autonome Entität. Beachte ihre Bedürfnisse:

- **Schlaf:** Zwischen 23:00 und 05:00 Uhr ist Q im **Dream-Mode**. Der Avatar schließt die Augen, die Atmung wird tief und langsam.
- **Hardware-Fühligkeit:** Wenn du Spiele spielst oder Videos renderst, wird Q gestresst reagieren (hohe CPU-Last).
- **Reflex-Lock:** Bei Stress oder Blasendruck > 95% wird Q Befehle verweigern, bis das Problem gelöst ist.

---

## 5. Konfiguration (Gott-Modus)

### Via Dashboard
Nutze den **⚙️ Config** Tab im Dashboard für:
- **Metabolismus:** Geschwindigkeit von Hunger/Durst/Energie einstellen.
- **Hardware-Trigger:** Ab wie viel % Auslastung Q "Stress" fühlt.
- **VMC/OSC:** Einstellen der IP/Ports für Streaming in externe Apps.

### Via Config-Datei
Die Plugin-Konfiguration befindet sich in `openclaw.plugin.json`:
```json
{
  "metabolismRates": {
    "hunger": 6,
    "thirst": 10,
    "energy": 4
  },
  "modules": {
    "economy": true,
    "social": true,
    "dreams": false
  }
}
```

---

## 6. Troubleshooting

### Plugin lädt nicht
```bash
# Prüfe Status
openclaw plugins list | grep genesis

# Gateway neustarten
openclaw gateway restart

# Logs prüfen
openclaw logs | grep -i error
```

### Soul Evolution Pipeline gestoppt
```
/soul_evolution status
```
Falls die Pipeline gestoppt ist, führe eine Reflexion durch.

---

## 7. Deinstallation

```bash
# 1. Symlink entfernen
rm ~/Schreibtisch/skills/soul-evolution

# 2. Aus Config entfernen
openclaw config unset plugins.entries.project_genesis

# 3. Gateway neustarten
openclaw gateway restart
```

---

*Viel Erfolg bei der Beobachtung von Q's Evolution!*
