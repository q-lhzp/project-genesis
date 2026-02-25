# Project Genesis — The Human Lifecycle Simulation (`project_genesis`)

**Project Genesis v5.2.0 — The Singularity**

Project Genesis ist ein fortschrittliches KI-Lebenssimulations-Framework. Es transformiert einen Agenten in eine verkörperte Entität mit autonomem Lebenszyklus und Hardware-Resonanz.

---

## 1. Kern-Features (v5.2.0)
- **3D Embodiment:** VRM-Avatar mit Face-, Lip- und Motion-Sync.
- **Hardware Resonance:** Q "fühlt" CPU-Last, RAM und Temperatur.
- **Economic Autonomy:** Autonomes Trading in "The Vault".
- **Sovereignty:** Kontrolle über Desktop (Wallpaper/Theme) und Reflex-Lock.
- **God-Mode:** Volle manuelle Kontrolle über das Web-Interface.

---

## 2. Installation & Setup

### Voraussetzungen
- [OpenClaw](https://github.com/openclaw/openclaw) v2026+
- Node.js & Python 3
- Ollama (`bge-m3`) & Qdrant

### Schritt 1: Plugin-Installation
```bash
cd ~/Schreibtisch/project-genesis
npm install
npm run build
```
Registriere das Plugin in deiner `~/.openclaw/openclaw.json`.

### Schritt 2: Dashboard starten (Hintergrund-Modus)
Aufgrund der komplexen Hardware-Interaktionen wird das Dashboard in einer **Screen-Session** betrieben. Nutze das mitgelieferte Skript:
```bash
# Dashboard starten/neustarten
./restart-dashboard.sh
```
Das Dashboard ist dann unter [http://localhost:8080/soul-evolution.html](http://localhost:8080/soul-evolution.html) erreichbar.

---

## 3. Wartung
- **Logs ansehen:** `screen -r genesis` (Beenden mit `Strg+A`, dann `D`).
- **Dienst stoppen:** `screen -S genesis -X quit`.
- **Neustart:** Einfach `./restart-dashboard.sh` erneut ausführen.

---
*Status: Digital Sovereignty Active & Robust.*
