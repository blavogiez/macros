#!/bin/bash
# Script d'installation automatique du projet macros
# Configure tout automatiquement : dossiers, venv, dépendances

set -e  # Arrêter en cas d'erreur

echo "=== Installation de Macros F1-F12 ==="
echo ""

# Créer les dossiers s'ils n'existent pas
echo "Création des dossiers..."
mkdir -p scripts
mkdir -p macros
echo "[OK] Dossiers créés"
echo ""

# Détecter la plateforme
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="linux"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    PLATFORM="windows"
else
    PLATFORM="unknown"
fi

echo "Plateforme détectée : $PLATFORM"
echo ""

# Configuration sur Linux
if [ "$PLATFORM" = "linux" ]; then
    echo "Configuration de l'environnement virtuel Python..."

    # Vérifier que python3 est installé
    if ! command -v python3 &> /dev/null; then
        echo "[ERREUR] python3 n'est pas installé"
        exit 1
    fi

    # Créer le venv s'il n'existe pas
    if [ ! -d "venv" ]; then
        echo "Création du venv..."
        python3 -m venv venv
        echo "[OK] Venv créé"
    else
        echo "[INFO] Venv déjà existant"
    fi

    # Activer le venv et installer pynput
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
        echo "[OK] Scripts rendus exécutables"
    fi
fi

# Configuration sur Windows
if [ "$PLATFORM" = "windows" ]; then
    echo "Installation des dépendances Windows..."

    # Vérifier que python est installé
    if ! command -v python &> /dev/null; then
        echo "[ERREUR] python n'est pas installé"
        exit 1
    fi

    pip install --quiet keyboard pyperclip
    echo "[OK] Dépendances Windows installées"
fi

echo ""
echo "=== Installation terminée ! ==="
echo ""
echo "Pour lancer le script :"
if [ "$PLATFORM" = "linux" ]; then
    echo "  ./scripts/run.sh"
    echo ""
    echo "Pour le lancement automatique au démarrage :"
    echo "  ./scripts/install_autostart.sh"
else
    echo "  python macros.py"
fi
echo ""
