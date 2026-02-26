# Strategie zur Modularisierung: Project Genesis Dashboard (v5.7.0)

Dieses Dokument beschreibt den schrittweisen Plan zur Dekonstruktion des `soul-viz.py` Monolithen (>12.700 Zeilen) in eine moderne, wartbare und modulare Architektur.

## 🎯 Zielzustand
*   **Backend:** `soul-viz.py` fungiert nur noch als schlanker API-Server (Python).
*   **Frontend:** Getrennte Dateien für HTML, CSS und JavaScript.
*   **Modularität:** Jedes Feature (Vault, Avatar, Config) hat seine eigene JS-Datei.
*   **Sicherheit:** Kein Codeverlust durch schrittweise Extraktion und paralleles Laden.

---

## 🏗️ Neue Ordnerstruktur
Wir erstellen eine dedizierte Web-Struktur unter `skills/soul-evolution/tools/web/`:
```text
web/
├── index.html          # Das HTML-Skelett
├── css/
│   ├── main.css        # Globales Styling & Variablen
│   └── components.css  # Feature-spezifisches Styling
└── js/
    ├── core.js         # Tab-Management, Modals, Toasts
    ├── vitals.js       # Bedürfnisse, Stats, Metabolism-Display
    ├── avatar.js       # VRM-Integration, BlendShapes, LipSync
    ├── economy.js      # The Vault, Trading, Alpaca-Bridge
    ├── config.js       # MAC-Zuweisung, API-Key-Management
    └── wizard.js       # Onboarding-Prozess
```

---

## 🛣️ Phasenplan (Schritt-für-Schritt)

### Phase 1: Die Infrastruktur (Vorbereitung)
1.  Erstellen der neuen Ordnerstruktur.
2.  Implementierung eines statischen File-Handlers in `soul-viz.py`, der Dateien aus dem `/web` Ordner ausliefern kann.
3.  **Sicherheitsnetz:** Das Backend kann weiterhin den alten "Inlined-String" ausliefern, falls eine Datei im `/web` Ordner fehlt.

### Phase 2: Extraktion des Stylings (CSS)
1.  Verschieben der CSS-Blöcke (Variablen, Layout, Panels) nach `web/css/main.css`.
2.  Anpassung der HTML-Generierung in Python, um die externe CSS-Datei zu verlinken.
3.  *Validierung:* Dashboard-Optik prüfen.

### Phase 3: Extraktion der Core-Logik (JS)
1.  Verschieben der grundlegenden JavaScript-Funktionen (`switchTab`, `openModal`, `showToast`) nach `web/js/core.js`.
2.  Test der Navigation.

### Phase 4: Feature-Modularisierung (Tab für Tab)
Dies ist der wichtigste Teil. Wir arbeiten uns von oben nach unten durch das Dashboard:

*   **Schritt 4.1: Vitals & Dashboard-Feed** (`vitals.js`)
*   **Schritt 4.2: Live Avatar & BlendShapes** (`avatar.js`) - *Massive Reduktion der Zeilenanzahl!*
*   **Schritt 4.3: The Vault (Economy)** (`economy.js`)
*   **Schritt 4.4: System Config & MAC Setup** (`config.js`)
*   **Schritt 4.5: Onboarding Wizard** (`wizard.js`)

### Phase 5: Das HTML-Skelett
1.  Der gesamte HTML-String wird aus `soul-viz.py` in `web/index.html` verschoben.
2.  Python nutzt nur noch eine minimale Template-Logik, um Variablen (wie `DATA_JSON`) in das HTML einzusetzen.

### Phase 6: Backend-Cleanup
1.  Löschen der jetzt redundanten Strings in `soul-viz.py`.
2.  Strukturierung der API-Routen in Python-Klassen oder separate Module (z.B. `routes/config.py`).

---

## 🛡️ Sicherheits-Prinzipien
1.  **Atomare Commits:** Nach jedem Schritt wird die Funktionalität verifiziert.
2.  **Keine Logik-Änderung:** Während der Extraktion wird nur Code verschoben, nicht umgeschrieben. Optimierungen erfolgen erst nach der Modularisierung.
3.  **Fallbacks:** Solange ein Modul nicht 100% stabil ist, bleibt das Python-Inline-Backup erhalten.

---
*Erstellt am: 26. Februar 2026*
*Status: In Planung*
