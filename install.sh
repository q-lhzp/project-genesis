#!/bin/bash
# Project Genesis Installation Script
# Automatische Installation für neue Benutzer

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="project-genesis"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
USER="$(whoami)"

echo "🔧 Project Genesis Installation"
echo "================================"
echo "Projekt: $PROJECT_NAME"
echo "Benutzer: $USER"
echo ""

# Prüfen ob OpenClaw installiert ist
if ! command -v openclaw &> /dev/null; then
    echo "❌ OpenClaw nicht gefunden. Bitte zuerst installieren:"
    echo "   npm install -g openclaw"
    exit 1
fi

# 1. Symlinks für Soul Evolution Skill erstellen
echo "📦 Erstelle Symlinks für Soul Evolution Skill..."

# Direkter Symlink im Workspace (für Agent-Pfad-Aufrufe)
if [ -L "$PROJECT_ROOT/soul-evolution" ]; then
    EXISTING_TARGET=$(readlink -f "$PROJECT_ROOT/soul-evolution")
    if [ "$EXISTING_TARGET" = "$SCRIPT_DIR/skills/soul-evolution" ]; then
        echo "   ✅ Direkter Symlink existiert bereits (korrekt)"
    else
        rm "$PROJECT_ROOT/soul-evolution"
        ln -s "$SCRIPT_DIR/skills/soul-evolution" "$PROJECT_ROOT/soul-evolution"
        echo "   ✅ Direkter Symlink aktualisiert"
    fi
elif [ -d "$PROJECT_ROOT/soul-evolution" ]; then
    echo "   ⚠️ Verzeichnis bereits vorhanden"
else
    ln -s "$SCRIPT_DIR/skills/soul-evolution" "$PROJECT_ROOT/soul-evolution"
    echo "   ✅ Direkter Symlink erstellt"
fi

# Symlink im skills-Ordner (für OpenClaw skill-System)
mkdir -p "$PROJECT_ROOT/skills"

if [ -L "$PROJECT_ROOT/skills/soul-evolution" ]; then
    EXISTING_TARGET=$(readlink -f "$PROJECT_ROOT/skills/soul-evolution")
    if [ "$EXISTING_TARGET" = "$SCRIPT_DIR/skills/soul-evolution" ]; then
        echo "   ✅ Symlink existiert bereits (korrekt)"
    else
        rm "$PROJECT_ROOT/skills/soul-evolution"
        ln -s "$SCRIPT_DIR/skills/soul-evolution" "$PROJECT_ROOT/skills/soul-evolution"
        echo "   ✅ Symlink aktualisiert"
    fi
elif [ -d "$PROJECT_ROOT/skills/soul-evolution" ]; then
    echo "   ⚠️ Verzeichnis bereits vorhanden"
else
    ln -s "$SCRIPT_DIR/skills/soul-evolution" "$PROJECT_ROOT/skills/soul-evolution"
    echo "   ✅ Symlink erstellt"
fi

# 2. OpenClaw Config automatisch einrichten
echo ""
echo "⚙️ Aktualisiere OpenClaw Config..."

CONFIG_FILE="$HOME/.openclaw/openclaw.json"
PROJECT_PATH="$PROJECT_ROOT/$PROJECT_NAME"

# Backup erstellen
if [ -f "$CONFIG_FILE" ]; then
    cp "$CONFIG_FILE" "${CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    echo "   📋 Backup der Config erstellt"
fi

# Config mit openclaw CLI setzen (sauberer Weg)
echo "   🔄 Füge Plugin zu OpenClaw hinzu..."

# Prüfen und hinzufügen
openclaw config set "plugins.load.paths" "[$(echo "$PROJECT_PATH" | sed 's/"/\\"/g' | sed 's/^/"/;s/$/"/')]" 2>/dev/null || true
openclaw config set "plugins.allow" '["project_genesis"]' 2>/dev/null || true
openclaw config set "plugins.entries.project_genesis" '{"enabled": true}' 2>/dev/null || true

# 3. Gateway neu starten
echo ""
echo "🔄 Starte Gateway neu..."
openclaw gateway restart

echo ""
echo "📋 Verifiziere Installation..."
sleep 3

# Prüfen
if openclaw plugins list 2>/dev/null | grep -q "project_genesis"; then
    echo "   ✅ Plugin geladen!"
else
    echo "   ⚠️ Plugin nicht gefunden - manuellen Check erforderlich"
fi

echo ""
echo "================================"
echo "✅ Installation abgeschlossen!"
echo ""
echo "Nächste Schritte:"
echo "   1. Teste Skill: /soul_evolution status"
echo "   2. Prüfe Dashboard: http://localhost:8080"
echo ""
