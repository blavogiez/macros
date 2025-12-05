# Installation automatique

## Linux (une seule commande)

```bash
curl -fsSL https://raw.githubusercontent.com/blavogiez/macros/master/setup.sh | bash
```

Ou manuellement :

```bash
wget https://raw.githubusercontent.com/blavogiez/macros/master/setup.sh
chmod +x setup.sh
./setup.sh
```

Ce script va :
1. Cloner le projet depuis GitHub
2. Créer l'environnement virtuel Python
3. Installer pynput
4. Configurer le démarrage automatique à chaque session

## Windows

```bash
git clone https://github.com/blavogiez/macros
cd macros
pip install keyboard pyperclip
python macros.py
```

## Désinstallation

```bash
# Supprimer le démarrage automatique
rm ~/.config/autostart/macros.desktop

# Supprimer le projet
rm -rf ~/macros
```
