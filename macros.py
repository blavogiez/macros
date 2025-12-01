import json
import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox
import keyboard

DEFAULT_CONFIG = "macros.json"
current_config_file = DEFAULT_CONFIG
config = {}

def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[!] Erreur dans le JSON '{path}': {e}")
            sys.exit(1)
    return data

def reload_config():
    global config
    try:
        config = load_config(current_config_file)
        print(f"[INFO] Configuration chargée: {current_config_file}")
    except FileNotFoundError:
        print(f"[!] Fichier non trouvé: {current_config_file}")
    except Exception as e:
        print(f"[!] Erreur lors du chargement: {e}")

def show_context_selector():
    root = tk.Tk()
    root.title("Sélection du contexte")
    root.geometry("300x250")
    root.resizable(False, False)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - 300) // 2
    y = (screen_height - 250) // 2
    root.geometry(f"300x250+{x}+{y}")

    root.attributes("-topmost", True)
    root.focus_force()

    tk.Label(root, text="Choisissez un contexte:", font=("Arial", 12)).pack(pady=15)

    contexts = [
        ("Java", "macros_java.json"),
        ("JavaScript", "macros_js.json"),
        ("Professionnel", "macros_pro.json"),
        ("LaTeX", "macros_latex.json"),
        ("Défaut", "macros.json")
    ]

    def select_context(filename):
        global current_config_file
        current_config_file = filename
        reload_config()
        root.destroy()

    for name, filename in contexts:
        btn = tk.Button(
            root,
            text=name,
            command=lambda f=filename: select_context(f),
            width=20,
            height=1,
            font=("Arial", 10)
        )
        btn.pack(pady=5)

    root.mainloop()

def run_macro(key_name, cfg):
    key = key_name.lower()
    if key not in cfg:
        print(f"[INFO] Aucune macro définie pour {key_name}")
        return

    action = cfg[key]
    action_type = action.get("type")
    value = action.get("value", "")

    print(f"[DEBUG] Macro déclenchée: {key_name} -> {action_type} : {value}")

    if action_type == "text":
        keyboard.write(value)

    elif action_type == "keys":
        keyboard.send(value)

    elif action_type == "command":
        try:
            if os.name == "nt":
                subprocess.Popen(value, shell=True)
            else:
                subprocess.Popen(value, shell=True)
        except Exception as e:
            print(f"[!] Erreur en lançant la commande '{value}': {e}")
    else:
        print(f"[!] Type d'action inconnu pour {key_name}: {action_type}")

def main():
    global config

    print("=== Macros F1-F12 ===")
    print("²+& : Sélectionner le contexte")
    print("Types d'actions supportés : text, keys, command")
    print("Appuie sur ESC pour quitter.\n")

    reload_config()

    function_keys = [f"f{i}" for i in range(1, 13)]

    keyboard.add_hotkey('²+&', show_context_selector, suppress=True)

    for fk in function_keys:
        keyboard.on_press_key(fk, lambda e, fk=fk: run_macro(fk, config))

    try:
        keyboard.wait("esc")
    except KeyboardInterrupt:
        pass

    print("\n[INFO] Script arrêté.")

if __name__ == "__main__":
    main()
