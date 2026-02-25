# Project Genesis - Vollständige Feature-Liste

Basierend auf allen Planungsdokumenten:

---

## 1. KERN-SYSTEME

### 1.1 Metabolismus & Biologie
- **9 Needs:** energy, hunger, thirst, hygiene, bladder, bowel, stress, arousal, libido
- **Reflex-Lock:** Blockiert Tools wenn Need > 95
- **Zeitbasierter Verfall:** Berechnung basierend auf Time-Delta
- **Sensorische Injektion:** Natürlichsprachliche Empfindungen im Prompt

### 1.2 Lebenszyklus (Chronos)
- birthDate / initialAgeDays Konfiguration
- Aging-Berechnung (Tage/Jahre)
- Metabolismus-Raten nach Lebensalter skaliert

### 1.3 Hormon-Zyklus (Cycle)
- 28-Tage-Phasen: REGENERATION (1-5), EXPANSION (6-12), PEAK (13-16), CONSOLIDATION (17-28)
- Symptom-Tracking: cramps, bloating, fatigue, mood_swings, headache
- EMOTIONS.md Injection

---

## 2. SOUL EVOLUTION (Kognitive Evolution)

### 2.1 Pipeline (10-Schritte)
0. Workspace Boundary Check
1. INGEST - Erfahrungen sammeln
2. REFLECT - Reflexionen schreiben
3. PROPOSE - Änderungsvorschläge generieren
4. GOVERN - Genehmigung (autonomous/advisory/supervised)
5. APPLY - SOUL.md ändern
6. LOG - Änderungen dokumentieren
7. STATE - soul-state.json aktualisieren
8. NOTIFY - Mensch informieren
9. FINAL CHECK - Validierung

### 2.2 Erfahrungs-Klassifizierung
- **Routine:** Alltägliche Erlebnisse
- **Notable:** Bedeutsame Perspektivwechsel
- **Pivotal:** Fundamentale Glaubens-Änderungen

### 2.3 SOUL.md Struktur
- [CORE]: Unveränderliche Identität
- [MUTABLE]: Evolvable via Pipeline

### 2.4 Validatoren (Python)
- check_workspace.py
- validate_experience.py
- validate_reflection.py
- validate_proposal.py
- validate_soul.py
- validate_state.py
- check_pipeline_ran.py

---

## 3. SOCIAL & RELATIONSHIPS

### 3.1 Social CRM
- Kontakte mit Bond/Trust/Intimacy
- personality Traits
- visual_description für Avatar
- social_events.json Tracking

### 3.2 Proaktive NPC-Interaktionen
- Social Engine mit emotional impacts
- Dynamic messaging

### 3.3 Social Media / Presence
- Digital Extroversion (Presence Engine)
- social_posts.jsonl Tracking

---

## 4. ECONOMY & TRADING

### 4.1 The Vault
- Real trading: Kraken (Crypto), Alpaca (Stocks)
- vault_state.json (echte Konten)
- Automatische Trading-Entscheidungen

### 4.2 Finanzen
- Balance, Income, Expenses, Debt
- Job Market (optional geplant)

---

## 5. 3D AVATAR & VISUALS

### 5.1 VRM Avatar
- Three.js Viewer (soul-viz.py)
- @pixiv/three-vrm Integration
- Wardrobe Sync (Kleidung wechseln)

### 5.2 Face-Sync
- Expression Mapper
- BlendShapes: Joy, Stress, Energy -> facial expressions
- Smooth transitions (lerping)

### 5.3 Lip-Sync
- Audio Worklet analysis
- A/I/U/E/O Blendshapes

### 5.4 Idle Animations
- Biological drive: bladder, stress, energy -> animations
- Location-based: walking transitions

### 5.5 External Sync
- VMC (Virtual Motion Capture) Protocol
- OSC (Open Sound Control)
- 3DXChat / VSeeFace / Unity integration

---

## 6. VOICE & AUDIO

### 6.1 Chatterbox-Turbo
- Local TTS
- Voice Cloning
- Emotional intonation

### 6.2 Voice Tools
- reality_voice: Audio-Dateien generieren
- Voice Lab (Dashboard)

---

## 7. ENVIRONMENT & DESKTOP

### 7.1 Desktop Sovereignty
- GNOME wallpaper sync
- Theme sync (dark/light)
- Per Location wallpaper mapping

### 7.2 Atmosphere Sync
- Real-world weather integration
- Time-based lighting

---

## 8. DREAMS & SUBCONSCIOUS

### 8.1 Dream Mode
- Trigger: energy < 20% AND 23:00-05:00
- Traum-Protokoll in spezieller Session
- dream_state.json
- dreams.md Journal

### 8.2 GROWTH.md Injection
- Nachts konsolidierte Erkenntnisse
- Memory consolidation

---

## 9. HOBBIES & RESEARCH

### 9.1 Hobby Engine
- interests.json: Favoriten, Links, Notizen
- Idle activity selection
- Web research (browser tool)

### 9.2 Self-Expansion
- Q schreibt eigene Tools/Code
- development/ Verzeichnis
- Proposal -> Review -> Approve workflow

---

## 10. MEMORY SYSTEMS

### 10.1 Short-Term
- HEARTBEAT.md
- memory/experiences/*.jsonl

### 10.2 Long-Term (Mem0)
- Ollama (bge-m3 embedder)
- Qdrant vector store
- autoRecall / autoCapture

### 10.3 Persistent Files
- SOUL.md, EMOTIONS.md, GROWTH.md
- physique.json, wardrobe.json, world.json
- interests.json, interior.json, inventory.json

---

## 11. HARDWARE RESONANCE

- CPU load -> stress
- RAM usage -> mental state
- System temperature -> comfort

---

## 12. MAC ARCHITEKTUR (Multi-Agent Cluster)

### 12.1 Rollen
- **Persona:** Haupt-Interaktion (Q)
- **Analyst:** Strategische Entscheidungen
- **Limbic:** Emotionale Verarbeitung
- **Developer:** Self-Expansion
- **World Engine:** Umgebungssimulation

### 12.2 Role Detection
- detectAgentRole() Funktion
- roleMapping Config
- Spezifische Context-Injection

---

## 13. DASHBOARD & VISUALIZATION

### 13.1 soul-viz.py
- Live Avatar Tab
- Interessen Tab
- Analytics
- Memory Search
- Contact Manager (CRM)

### 13.2 Mindmap
- soul-mindmap.html
- Organische Persönlichkeits-Visualisierung

---

## 14. TOOLS (Plugin)

| Tool | Funktion |
|------|----------|
| reality_needs | eat, drink, sleep, toilet, shower |
| reality_move | location wechseln |
| reality_dress | outfit wechseln |
| reality_shop | einkaufen |
| reality_diary | Tagebuch-Eintrag |
| reality_pleasure | arousal (wenn eros aktiv) |
| reality_update_interests | Hobby/Like/Wish pflegen |
| reality_emotion | Gefühle tracken |
| reality_grow | GROWTH-Einträge |
| reality_desire | Wünsche tracken |
| reality_hobby | Hobby-Aktivität |
| reality_dream | Traum-Verarbeitung |
| reality_avatar | pose, emote, calibrate |
| reality_trade | echtes Trading |
| evolution_debug | Debug-Output |
| reality_genesis | Character-Bootstrap |
| reality_profile | Profile laden/speichern |
| reality_camera | Foto generieren |
| reality_vision | Face-ID Analyse |
| reality_browse | Web-Research |
| reality_news | Welt-Nachrichten |
| reality_desktop | Desktop-Kontrolle |

---

## 15. CRON JOBS

| Job | Zeit | Funktion |
|-----|------|----------|
| self-reflection | Alle 6 Stunden | Reflexion |
| soul-evolution-pipeline | Täglich 22 Uhr | Soul Evolution Pipeline |

---

## 16. KONFIGURATION

### 16.1 Module (openclaw.plugin.json)
- eros (Arousal)
- cycle (Hormone)
- dreams
- hobbies
- economy
- social
- statistics
- utility
- psychology
- skills
- world
- reputation
- desktop
- legacy
- genesis
- voice_enabled
- mem0

### 16.2 Metabolism Rates
- hunger, thirst, energy, bladder, bowel, arousal, libido, hygiene, stress

### 16.3 Governance
- autonomous (auto-apply)
- advisory (mit Bestätigung)
- supervised (alle Vorschläge brauchen Approval)

---

## 17. STATUS: IMPLEMENTIERT

✅ ~98% aller geplanten Features implementiert

Nicht implementiert:
- Job Market (Trading bereits vorhanden)

---

*Zuletzt aktualisiert: 2026-02-25*
