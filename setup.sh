#!/bin/bash
# Script de déploiement complet du projet macros
# Clone le repo, configure tout automatiquement et active le démarrage auto

set -e  # Arrêter en cas d'erreur

REPO_URL="https://github.com/blavogiez/macros"
TARGET_DIR="$HOME/macros"

echo "=== Installation automatique de Macros F1-F12 ==="
echo ""

# Vérifier que git est installé
if ! command -v git &> /dev/null; then
    echo "[ERREUR] git n'est pas installé"
    echo "Installez-le avec : sudo apt install git"
    exit 1
fi

# Vérifier que python3 est installé
if ! command -v python3 &> /dev/null; then
    echo "[ERREUR] python3 n'est pas installé"
    exit 1
fi

# Vérifier si le dossier existe déjà
if [ -d "$TARGET_DIR" ]; then
    echo "Le dossier $TARGET_DIR existe déjà"
    read -p "Mettre à jour (git pull) ? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd "$TARGET_DIR"
        echo "Mise à jour du dépôt..."
        git pull
    else
        echo "Installation annulée"
        exit 0
    fi
else
    # Cloner le projet
    echo "Clonage du projet depuis GitHub..."
    git clone "$REPO_URL" "$TARGET_DIR"
    cd "$TARGET_DIR"
    echo "[OK] Projet cloné"
fi

cd "$TARGET_DIR"
echo ""

# Créer les dossiers s'ils n'existent pas
echo "Création des dossiers..."
mkdir -p scripts
mkdir -p macros
echo "[OK] Dossiers créés"
echo ""

# Créer le venv
echo "Configuration de l'environnement virtuel Python..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "[OK] Venv créé"
else
    echo "[INFO] Venv déjà existant"
fi

# Installer pynput
echo "Installation de pynput..."
source venv/bin/activate
pip install --quiet pynput
deactivate
echo "[OK] pynput installé"
echo ""

# Rendre les scripts exécutables
if [ -d "scripts" ]; then
    echo "Configuration des scripts..."
    chmod +x scripts/*.sh 2>/dev/null || true
    chmod +x install.sh 2>/dev/null || true
    echo "[OK] Scripts rendus exécutables"
fi
echo ""

# Configurer le démarrage automatique
echo "Configuration du démarrage automatique..."

AUTOSTART_DIR="$HOME/.config/autostart"
mkdir -p "$AUTOSTART_DIR"

DESKTOP_FILE="$AUTOSTART_DIR/macros.desktop"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=Macros F1-F12
Comment=Lance le gestionnaire de macros clavier
Exec=$TARGET_DIR/scripts/run.sh
Terminal=false
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF

chmod +x "$DESKTOP_FILE"
echo "[OK] Démarrage automatique configuré"
echo ""

echo "=== Installation terminée ! ==="
echo ""
echo "Le script se lancera automatiquement au prochain démarrage."
echo ""
echo "Pour le lancer maintenant :"
echo "  cd $TARGET_DIR"
echo "  ./scripts/run.sh"
echo ""
echo "Pour désactiver le démarrage automatique :"
echo "  rm ~/.config/autostart/macros.desktop"
echo ""
