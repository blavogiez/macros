#!/bin/bash
# Script d'installation pour lancer macros.py au démarrage de Linux

# Couleurs pour les messages
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "=== Installation de macros.py au démarrage ==="
echo ""

# Obtenir le chemin absolu de la racine du projet
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
echo "Dossier du projet : $PROJECT_DIR"
echo ""

# Vérifier que venv existe
if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo -e "${RED}[ERREUR]${NC} Environnement virtuel non trouvé"
    echo "Créez-le d'abord avec :"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install pynput"
    exit 1
fi

# Créer le dossier autostart s'il n'existe pas
AUTOSTART_DIR="$HOME/.config/autostart"
mkdir -p "$AUTOSTART_DIR"

# Créer le fichier .desktop
DESKTOP_FILE="$AUTOSTART_DIR/macros.desktop"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=Macros F1-F12
Comment=Lance le gestionnaire de macros clavier
Exec=$SCRIPT_DIR/run.sh
Terminal=false
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF

# Rendre le fichier exécutable
chmod +x "$DESKTOP_FILE"
chmod +x "$SCRIPT_DIR/run.sh"

echo -e "${GREEN}[OK]${NC} Fichier créé : $DESKTOP_FILE"
echo ""
echo "Macros.py se lancera automatiquement au prochain démarrage !"
echo ""
echo "Commandes utiles :"
echo "  - Désactiver : rm $DESKTOP_FILE"
echo "  - Tester maintenant : $SCRIPT_DIR/run.sh"
echo ""
