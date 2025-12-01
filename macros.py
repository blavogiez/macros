import json
import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox
import keyboard
import queue
import threading
import pyperclip
import time

DEFAULT_CONFIG = "macros.json"
current_config_file = DEFAULT_CONFIG
config = {}
root_window = None
action_queue = queue.Queue()

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

def request_context_selector():
    action_queue.put('show_selector')

def request_quit():
    action_queue.put('quit')

def show_context_selector():
    dialog = tk.Toplevel(root_window)
    dialog.title("Sélection du contexte")
    dialog.geometry("300x300")
    dialog.resizable(False, False)

    screen_width = dialog.winfo_screenwidth()
    screen_height = dialog.winfo_screenheight()
    x = (screen_width - 300) // 2
    y = (screen_height - 300) // 2
    dialog.geometry(f"300x300+{x}+{y}")

    dialog.attributes("-topmost", True)
    dialog.focus_force()
    dialog.grab_set()

    tk.Label(dialog, text="Choisissez un contexte:", font=("Arial", 12)).pack(pady=15)

    contexts = [
        ("C", "macros_c.json"),
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
        dialog.destroy()

    for name, filename in contexts:
        btn = tk.Button(
            dialog,
            text=name,
            command=lambda f=filename: select_context(f),
            width=20,
            height=1,
            font=("Arial", 10)
        )
        btn.pack(pady=5)

    def quit_app():
        dialog.destroy()
        root_window.quit()

    quit_btn = tk.Button(
        dialog,
        text="Quitter",
        command=quit_app,
        width=20,
        height=1,
        font=("Arial", 10),
        bg="#ff6b6b",
        fg="white"
    )
    quit_btn.pack(pady=10)

    dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)

def check_queue():
    try:
        action = action_queue.get_nowait()
        if action == 'show_selector':
            show_context_selector()
        elif action == 'quit':
            root_window.quit()
            return
    except queue.Empty:
        pass
    root_window.after(100, check_queue)

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
    global config, root_window

    root_window = tk.Tk()
    root_window.withdraw()

    print("=== Macros F1-F12 ===")
    print("Ctrl+² : Sélectionner le contexte / Quitter")
    print("Types d'actions supportés : text, keys, command\n")

    reload_config()

    function_keys = [f"f{i}" for i in range(1, 13)]

    keyboard.add_hotkey('Ctrl+²', request_context_selector, suppress=True)

    for fk in function_keys:
        keyboard.add_hotkey(fk, lambda fk=fk: run_macro(fk, config), suppress=True)

    root_window.after(100, check_queue)
    root_window.mainloop()

    print("\n[INFO] Script arrêté.")

if __name__ == "__main__":
    main()
