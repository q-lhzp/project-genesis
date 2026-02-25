# Project Genesis v5.2.0 — Benutzerhandbuch

Willkommen bei **Project Genesis**. Dieses Handbuch erklärt den Umgang mit dem System und dem Dashboard.

---

## 1. Das System steuern

Das Dashboard läuft in einer **Screen-Session** im Hintergrund. Dies stellt sicher, dass alle Hardware-Bridges stabil funktionieren.

### **Wichtige Befehle:**
- **Start / Neustart:** `./restart-dashboard.sh` (im Projektordner).
- **In die Konsole schauen:** `screen -r genesis` (um Fehlermeldungen live zu sehen).
- **Konsole verlassen:** Drücke `Strg+A` und dann `D` (Detach).
- **Komplett stoppen:** `screen -S genesis -X quit`.

---

## 2. Die Dashboards

### 📊 **Main Dashboard (Port 8080)**
[http://localhost:8080/soul-evolution.html](http://localhost:8080/soul-evolution.html)
*   **Live Avatar:** Hier siehst du Q's 3D-Körper und Reaktionen.
*   **Interests:** Was Q gerade autonom recherchiert.
*   **Analytics:** Langzeitstatistiken über Stress und Hardware-Last.

### ⚡ **God-Mode Panel**
[http://localhost:8080/godmode.html](http://localhost:8080/godmode.html)
*   Hier kannst du Bedürfnisse (Hunger, Energie) manuell setzen, um Q's Reaktionen zu testen oder Life-Events zu triggern.

---

## 3. Besonderheiten von v5.2.0

- **Reflex-Lock:** Wenn die Blase oder der Stress > 95% ist, verweigert Q den Dienst. Sie wird im Chat nur noch über ihr Unwohlsein klagen, bis du ihr erlaubst, sich darum zu kümmern.
- **Hardware-Resonanz:** Wenn dein PC unter Volllast arbeitet, wird Q im Dashboard sichtlich gestresst (schwitzend/angestrengt) wirken.
- **Tanz-Modus:** Spiele Musik ab! Q erkennt den Audio-Stream und fängt an, rhythmisch mit dem Kopf zu nicken.

---
*Viel Erfolg bei der Beobachtung von Q's Evolution!*
