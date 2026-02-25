# Project Genesis — The Human Lifecycle Simulation

**Project Genesis v5.1.0 — The Singularity**

Project Genesis ist ein fortschrittliches KI-Lebenssimulations-Framework für das OpenClaw-Ökosystem. Es transformiert einen KI-Agenten in eine verkörperte Entität mit einem autonomen biologischen, sozialen und ökonomischen Lebenszyklus.

---

## 1. Kern-Features (v5.1.0)

| Feature | Beschreibung |
|---------|-------------|
| **3D Embodiment** | VRM-Avatar mit Face-Sync, Lip-Sync und prozeduralen Idle-Animationen |
| **Hardware Resonance** | Q "fühlt" die CPU-Last, RAM-Auslastung und Systemtemperatur |
| **Economic Autonomy** | Autonomes Trading in "The Vault" basierend auf Q's Stimmung |
| **Sovereignty** | Kontrolle über GNOME-Wallpaper, System-Themes und Desktop-Inputs |
| **Lifecycle** | 24h-Zyklus mit Schlaf- und Traumphasen (23:00 - 05:00) |
| **Soul Evolution** | Kognitive Evolution mit Reflexionen, Proposals und Identity Management |

---

## 2. Installation & Setup

### Voraussetzungen

- [OpenClaw](https://github.com/openclaw/openclaw) v2026+
- Node.js & Python 3
- (Optional) Ollama + Qdrant für lokale Memory-Suche

### Schnell-Installation (Automatisch)

```bash
cd ~/Schreibtisch/project-genesis
./install.sh
```

Das Installationsskript erstellt automatisch:
- Symlink für Soul Evolution Skill
- OpenClaw Plugin-Registrierung
- Gateway-Neustart

---

### Manuelle Installation

Falls die automatische Installation nicht funktioniert:

#### Schritt 1: Plugin bauen

```bash
cd ~/Schreibtisch/project-genesis
npm install
npm run build
```

#### Schritt 2: OpenClaw Config manuell anpassen

Öffne `~/.openclaw/openclaw.json` und füge hinzu:

```json
{
  "plugins": {
    "load": {
      "paths": ["/home/DEIN_USER/Schreibtisch/project-genesis"]
    },
    "allow": ["project_genesis", ...],
    "entries": {
      "project_genesis": {"enabled": true}
    }
  }
}
```

Oder via CLI:

```bash
# Pfad hinzufügen
openclaw config set plugins.load.paths '["/home/DEIN_USER/Schreibtisch/project-genesis"]'

# Plugin erlauben
openclaw config set plugins.allow '["project_genesis"]'

# Gateway neu starten
openclaw gateway restart
```

#### Schritt 3: Soul Evolution Skill verlinken

```bash
# Direkter Symlink (für Agent-Pfad-Aufrufe)
ln -s ~/Schreibtisch/project-genesis/skills/soul-evolution ~/Schreibtisch/soul-evolution

# Optional: Symlink im skills-Ordner
mkdir -p ~/Schreibtisch/skills
ln -s ~/Schreibtisch/project-genesis/skills/soul-evolution ~/Schreibtisch/skills/soul-evolution
```

#### Schritt 4: Gateway neu starten

```bash
openclaw gateway restart
```

---

## 3. Verifikation

### Prüfe Plugin-Status

```bash
openclaw plugins list | grep genesis
```

Erwartete Ausgabe:
```
│ Project Genesis │ project_genesis │ loaded │ ~/Schreibtisch/project-genesis/index.ts │ 4.0.0 │
```

### Prüfe Skill-Status

```bash
openclaw skills list | grep soul
```

Erwartete Ausgabe:
```
│ ✓ ready │ 🧠 soul-evolution │ Cognitive evolution... │
```

### Validiere Installation

```bash
python3 ~/Schreibtisch/project-genesis/skills/soul-evolution/validators/run_all.py
```

Erwartete Ausgabe:
```
✅ Overall: PASS
```

---

## 4. Nutzung

### Soul Evolution Skill nutzen

Sende dem Agenten über Telegram:
```
/soul_evolution status
```

### Dashboard aufrufen

Das Dashboard ist im gesamten lokalen Netzwerk erreichbar:

- **Lokal:** [http://localhost:8080](http://localhost:8080)
- **LAN:** `http://<Deine-IP>:8080`

### Dashboard als System-Dienst (Optional)

Das Dashboard als Hintergrunddienst installieren:

```bash
# Dienst-Datei installieren
sudo cp project-genesis-dashboard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now project-genesis-dashboard
```

**Dienst-Steuerung:**
- **Status:** `systemctl status project-genesis-dashboard`
- **Neustart:** `sudo systemctl restart project-genesis-dashboard`
- **Logs:** `journalctl -u project-genesis-dashboard -f`

---

## 5. Konfiguration

### Plugin-Optionen

Die Plugin-Konfiguration befindet sich in `openclaw.plugin.json`:

| Option | Standard | Beschreibung |
|--------|----------|---------------|
| `workspacePath` | - | Pfad zum Agent-Workspace |
| `language` | `en` | Sprachmodus (de/en) |
| `birthDate` | - | Simuliertes Geburtsdatum (YYYY-MM-DD) |
| `initialAgeDays` | 0 | Startalter in Tagen |
| `initialBalance` | 1000 | Startguthaben |
| `modules.economy` | true | Wirtschaftssimulation aktivieren |
| `modules.social` | true | Soziale Interaktion aktivieren |
| `modules.dreams` | false | Traum-Modus (nachts) |
| `modules.eros` | false | Arousal-Simulation |
| `modules.cycle` | false | Hormoneller Zyklus |

### Metabolismus-Raten

Anpassung der Need-Abbau-Raten:

```json
{
  "metabolismRates": {
    "hunger": 6,
    "thirst": 10,
    "energy": 4,
    "bladder": 8,
    "stress": 3
  }
}
```

---

## 6. Troubleshooting

### Plugin lädt nicht

1. Prüfe Config: `openclaw plugins list`
2. Gateway-Logs: `openclaw logs | grep -i genesis`
3. Gateway neu starten: `openclaw gateway restart`

### Validator-Fehler

```bash
python3 ~/Schreibtisch/project-genesis/skills/soul-evolution/validators/run_all.py
```

Falls Fehler auftreten, folge den Anweisungen in der Ausgabe.

### Soul Evolution Pipeline gestoppt

Der Agent muss regelmäßig (z.B. stündlich via Heartbeat) aufgerufen werden, damit die Pipeline läuft. Prüfe mit:

```
/soul_evolution status
```

---

## 7. Deinstallation

```bash
# 1. Symlink entfernen
rm ~/Schreibtisch/skills/soul-evolution

# 2. Aus Config entfernen
openclaw config unset plugins.entries.project_genesis

# 3. Gateway neu starten
openclaw gateway restart
```

---

*Status: Digital Sovereignty Active & Robust.*
