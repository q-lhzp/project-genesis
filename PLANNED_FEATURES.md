# Project Genesis - Vollständige Feature-Liste

**Version:** 5.2.1
**Stand:** 2026-02-25

---

## 1. Biologische Simulation

### 1.1 Metabolism & Needs
- 9 Vitalwerte (energy, hunger, thirst, hygiene, bladder, bowel, stress, arousal, libido)
- Zeitbasierter Verfall via `last_tick` Berechnung
- Konfigurierbare Metabolism-Raten pro Need
- Sensorische Kontext-Injektion (natürliche Sprache statt Metriken)

### 1.2 Lifecycle & Aging
- Birthdate und biologisches Alter
- Life-Stages (baby, child, teen, adult, senior)
- Automatisches Altern
- Age-Sensation Mapping (was Q in diesem Alter fühlt)

### 1.3 Hormonzyklus (28-Tage)
- 4 Phasen: REGENERATION, EXPANSION, PEAK, CONSOLIDATION
- Phasen-spezifische Stimmungen, Energie-Level, Symptome
- Emotionale Modifikatoren
- Tools: `cycle_status`, `cycle_set_start`, `cycle_toggle`

### 1.4 Hardware-Resonanz
- CPU/RAM Last → Stress/Energy Korrelation
- Automatische System-Monitoring

---

## 2. Kognition & Gedächtnis

### 2.1 Langzeitgedächtnis (Mem0)
- Lokale Qdrant + Ollama Integration
- Vector-Suche in natürlicher Sprache
- `memory/reality/mem0_config.json` für Konfiguration

### 2.2 Soul Evolution Pipeline (10 Schritte)
1. INGEST - Erfahrungen sammeln
2. REFLECT - Reflektieren
3. PROPOSE - Änderungen vorschlagen
4. GOVERN - Governance anwenden
5. APPLY - Genehmigte Änderungen umsetzen
6. LOG - Änderungen dokumentieren
7. STATE - Status aktualisieren
8. NOTIFY - Benachrichtigung
9. FINAL CHECK - Verifikation
10. REPORT - Bericht

### 2.3 SOUL.md Identitätsmanagement
- `[CORE]` Tags für unveränderliche Identität
- `[MUTABLE]` Tags für veränderbare Eigenschaften
- Proposal-System für Charakteränderungen
- Validatoren gegen Halluzinationen

### 2.4 Erfahrungs-Klassifizierung
- `routine` - Alltägliche Interaktionen
- `notable` - Bedeutsame Erlebnisse
- `pivotal` - Fundamentale Überzeugungs-Änderungen

---

## 3. Emotionale Engine

### 3.1 Emotions-System
- Stimmungstracking (happy, sad, anxious, excited, etc.)
- Emotionale Injection in Prompts
- EMOTIONS.md Integration

### 3.2 Desires & Dreams
- Wunschlisten und Ziele
- Traum-Analyse und -Verarbeitung
- DESIRES.md Tracking

### 3.3 GROWTH.md
- Persönlichkeitsentwicklung
- Lernfortschritt
- Fähigkeiten-Entwicklung

---

## 4. Soziale Engine

### 4.1 Social CRM
- Kontaktverwaltung mit UUIDs
- Bond/Trust System
- Beziehungs-Tracking
- Visual Lab für NPC-Gesichter

### 4.2 Proaktive Interaktionen
- NPC-Nachrichten generieren
- Dynamische Konversationen
- Social Events verarbeiten

### 4.3 Presence Feed
- Digital Extroversion
- Social Media Simulation
- Automatische Content-Generierung

---

## 5. Ökonomische Engine

### 5.1 The Vault (Trading)
- Echte Krypto-/Aktien-Trades
- Kraken/Alpaca API Integration
- Automatisches Trading
- Portfolio-Tracking

### 5.2 Finanzen
- Balance und Einkommen
- Ausgaben-Tracking
- Finanzielle Ziele

### 5.3 Job Market (Optional)
- Arbeitsplatz-Simulation
- Bewerbungs-System
- Karriere-Entwicklung

---

## 6. 3D Avatar & Visuelle Präsenz

### 6.1 VRM Viewer
- Three.js basierte 3D-Darstellung
- @pixiv/three-vrm Integration
- Live Avatar Tab im Dashboard

### 6.2 Face-Sync
- Emotionale BlendShapes
- Joy, Sad, Angry, Fear, Surprise, Neutral
- LERP-Übergänge zwischen Expressionen

### 6.3 Lip-Sync
- Audio-Analyse (Frequency/Amplitude)
- Vokale Viseme (A, I, U, E, O)

### 6.4 Idle Animations
- Biologisch-basierte Posen
- High bladder → Fidgeting
- High stress → Shaking
- Location-Change Animationen

### 6.5 VMC/OSC Streaming
- Virtual Motion Capture Protokoll
- Externe Apps (VSeeFace, Unity, 3DXChat)
- OSC Streaming

### 6.6 Wardrobe Sync
- Kleidung aus wardrobe.json → VRM Texturen
- Automatische Outfit-Wechsel

---

## 7. Environment & Desktop

### 7.1 GNOME Integration
- Wallpaper-Wechsel basierend auf Location
- Theme-Sync (Dark/Light Mode)
- wallpaper_map.json Konfiguration

### 7.2 Atmosphere Sync
- Real-world Wetter-Daten
- Zeitbasierte Beleuchtung
- Stimmungsvolle Umgebungsanpassung

### 7.3 Interior Management
- Raum-Layout Verwaltung
- Möbel und Einrichtung
- Interaktions-Möglichkeiten

---

## 8. Traum & Hobby Engine

### 8.1 Dream Mode
- Trigger: Energy < 20% + 23:00-05:00 Uhr
- Automatische Traum-Session
- memory/reality/dreams.md
- memory/reality/dream_state.json

### 8.2 Hobby Engine
- Interest Tracking
- Autonomous Web Research
- Favoriten und Wunschlisten
- Proaktive Kommunikation von Funden

---

## 9. Werkzeuge (Tools)

### 9.1 Needs Tools
- `reality_needs` - eat, drink, sleep, shower, toilet
- `reality_move` - Location-Wechsel
- `reality_dress` - Outfit-Wechsel
- `reality_shop` - Einkaufen

### 9.2 Social Tools
- `reality_socialize` - Soziale Interaktionen
- `reality_befriend` - Neue Kontakte
- `reality_contact` - Kommunikation

### 9.3 Economy Tools
- `reality_vault` - Trading und Portfolio
- `reality_trade` - Einzelne Trades

### 9.4 Identity Tools
- `reality_profile` - Aktuellen Status anzeigen
- `reality_avatar` - 3D Avatar steuern
- `reality_genesis` - Character Bootstrap
- `reality_voice` - TTS Generierung
- `reality_camera` - Webcam Fotos
- `reality_vision_analyze` - Bildanalyse

### 9.5 Evolution Tools
- `reality_diary` - Tagebucheinträge
- `reality_grow` - Wachstum tracken
- `reality_emotion` - Emotionen aktualisieren
- `reality_desire` - Wünsche verwalten
- `reality_manage_memos` - Mem0 verwalten

### 9.6 Research Tools
- `reality_override` - Werte überschreiben
- `reality_inject_event` - Events injizieren
- `reality_export_research_data` - Daten exportieren

### 9.7 System Tools
- `reality_browse` - Web-Browsing
- `reality_news` - Nachrichten
- `reality_desktop` - Desktop-Automation

---

## 10. Dashboard & WebUI

### 10.1 Haupt-Dashboard (soul-viz.py)
- Interaktive Visualisierung
- Multi-Tab Interface
- Echtzeit-Updates

### 10.2 Tabs
- Dashboard - Übersicht
- Interior - Raum-Verwaltung
- Inventory - Gegenstände
- Wardrobe - Kleidung
- Development - Selbstentwicklung
- Cycle - Hormonzyklus
- World - Orte
- Skills - Fähigkeiten
- Psychology - Persönlichkeit
- Social Standing - CRM
- Life Stream - Aktivitäten
- Genesis Lab - Charakter-Bootstrap
- Memory - Mem0 Suche
- The Vault - Trading
- Live Avatar - 3D Viewer
- Interests - Interessen
- Dream Journal - Träume
- Analytics - Statistiken
- Config - Einstellungen
- Diagnostics - System-Status
- **God-Mode** - Simulation Control

### 10.3 Mindmap
- Soul Evolution Visualisierung
- Persönlichkeits-Wachstum
- Interaktiver Canvas

### 10.4 God-Mode
- Needs Slider (8 Parameter)
- Event Injection
- Reflex-Lock Status
- Alle auf Port 8080

---

## 11. Sicherheit & Validierung

### 11.1 CORE-Schutz
- `[CORE]` Tags in SOUL.md sind unveränderlich
- Validator verhindert Manipulation

### 11.2 Reflex-Lock
- Blockiert Tools bei kritischen Needs (≥95)
- Biologische Prioritäten erzwungen
- Nur `reality_*` Tools erlaubt

### 11.3 Pipeline Validatoren
- validate_experience.py
- validate_reflection.py
- validate_proposal.py
- validate_soul.py
- validate_state.py
- check_pipeline_ran.py
- check_workspace.py

---

## 12. Testing & Selbstheilung

### 12.1 Genesis Doctor
- Bridge Verification (chmod +x)
- Dependency Audit (System-Tools)
- Path Alignment
- State Integrity (Template-Recovery)

### 12.2 Test Suite
- `reality_doctor` - Diagnose
- `reality_run_self_test` - Engine-Tests
- `reality_simulate_scenario` - Szenarien

### 12.3 Szenarien
- night_recovery - Energy=10%, 02:00 Uhr
- critical_reflex - Bladder/Stress=98%
- market_surge - Portfolio +15%
- social_event - Test-Event erstellen
- hobby_session - Research aktivieren
- full_health - Reset auf gesund

---

## 13. Sprachen & Lokalisierung

- Mehrsprachig (DE/EN)
- Konfigurierbare Inject-Sprache
- Bilingual Output Support

---

## Implementierungsstatus

| Kategorie | Status |
|-----------|--------|
| Biologie | ~100% |
| Kognition | ~95% |
| Emotional | ~100% |
| Sozial | ~95% |
| Economy | ~95% |
| 3D Avatar | ~90% |
| Environment | ~100% |
| Traum/Hobby | ~100% |
| Tools | ~100% |
| Dashboard | ~100% |
| Sicherheit | ~100% |
| Testing | ~100% |

**Gesamt: ~98%**

---

## Optionale Features (Nicht implementiert)

1. **Job Market** - Vollständige Arbeitsplatz-Simulation
2. **Vollständiges VRM BlendShape-Mapping** - Alle Expressionen

---

*Zuletzt aktualisiert: 2026-02-25*
