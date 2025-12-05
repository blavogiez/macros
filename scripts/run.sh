#!/bin/bash
# Script de lancement pour macros.py sur Linux
# Utilise un environnement virtuel Python pour éviter les problèmes de permissions

# Aller à la racine du projet
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Vérifie si le venv existe
if [ ! -d "venv" ]; then
    echo "[ERREUR] Environnement virtuel non trouvé"
    echo "Créez-le avec:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install pynput"
    exit 1
fi

# Active le venv et lance le script
source venv/bin/activate
python3 macros.py
