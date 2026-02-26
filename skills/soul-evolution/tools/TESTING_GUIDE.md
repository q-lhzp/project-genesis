# 🧪 Project Genesis: Plugin Testing Guide (v6.0.0)

Dieses Dokument beschreibt die Test-Prozeduren für jedes modularisierte Plugin. Alle Tests können manuell oder über die beiliegenden Test-Scripte validiert werden.

---

## 🛠️ Generelle Infrastruktur (Core)
- **Check:** Lädt der `PluginManager` alle Manifeste?
- **Validierung:** `curl -s http://localhost:8080/api/core/plugins` muss ein JSON-Array aller aktiven Plugins zurückgeben.

---

## 💰 Plugin: The Vault (vault)
- **Backend Test:** `python3 plugins/vault/test_backend.py`
- **Funktionen:**
    - GET `/api/plugins/vault/status` -> Aktueller Kontostand.
    - POST `/api/plugins/vault/trade` -> Handels-Simulation.
- **Frontend:** Tab "The Vault" muss Kontostand und Portfolio anzeigen.

## 🎭 Plugin: Live Avatar (avatar)
- **Backend Test:** `python3 plugins/avatar/test_backend.py`
- **Funktionen:**
    - GET `/api/plugins/avatar/config` -> VRM Pfad.
    - POST `/api/plugins/avatar/update` -> Pose/Emote Update.
- **Frontend:** 3D Modell muss laden, Animationen (Atmung) müssen aktiv sein.

## ⚡ Plugin: God-Mode (godmode)
- **Backend Test:** `python3 plugins/godmode/test_backend.py`
- **Funktionen:**
    - GET `/api/plugins/godmode/physique` -> Bedürfnisse.
    - POST `/api/plugins/godmode/override/needs` -> Schieberegler-Werte setzen.
- **Frontend:** Slider müssen aktuelle Werte aus `physique.json` anzeigen.

## ⚙️ Plugin: System Config (config)
- **Backend Test:** `python3 plugins/config/test_backend.py`
- **Funktionen:**
    - GET `/api/plugins/config/all` -> Models & Sim Config.
    - GET `/api/plugins/config/openclaw/models` -> Modellliste vom Gateway.
- **Frontend:** Dropdowns müssen mit Modellen (OpenAI, Anthropic etc.) gefüllt sein.

---

## 📋 Debugging & Monitoring
Jedes Plugin loggt wichtige Ereignisse mit dem Präfix `[PLUGIN:ID]`.
- **Backend:** `journalctl -u project-genesis-dashboard.service -f`
- **Frontend:** Browser Konsole (F12) -> Filter: `Plugin`
