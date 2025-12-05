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

def request_help_window():
    action_queue.put('show_help')

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

    def show_help_from_dialog():
        show_help_window()

    help_btn = tk.Button(
        dialog,
        text="Aide (Raccourcis)",
        command=show_help_from_dialog,
        width=20,
        height=1,
        font=("Arial", 10),
        bg="#4a90e2",
        fg="white"
    )
    help_btn.pack(pady=5)

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

def format_macro_preview(value, max_length=50):
    """Formate une valeur de macro pour l'affichage (tronque et nettoie)."""
    if not value:
        return ""

    # Remplace les retours à la ligne et tabulations par des espaces
    cleaned = value.replace('\n', ' ').replace('\t', ' ').replace('\r', ' ')

    # Retire les espaces multiples
    cleaned = ' '.join(cleaned.split())

    # Tronque si nécessaire
    if len(cleaned) > max_length:
        return cleaned[:max_length] + "..."
    return cleaned

def show_help_window():
    """Affiche une fenêtre avec tous les raccourcis clavier disponibles."""
    dialog = tk.Toplevel(root_window)
    dialog.title("Raccourcis Clavier")
    dialog.geometry("600x500")
    dialog.resizable(False, False)

    # Centre la fenêtre
    screen_width = dialog.winfo_screenwidth()
    screen_height = dialog.winfo_screenheight()
    x = (screen_width - 600) // 2
    y = (screen_height - 500) // 2
    dialog.geometry(f"600x500+{x}+{y}")

    dialog.attributes("-topmost", True)
    dialog.focus_force()

    # Titre avec le contexte actuel
    context_name = current_config_file.replace("macros_", "").replace(".json", "").replace("macros", "Défaut")
    tk.Label(
        dialog,
        text=f"Raccourcis Clavier - Contexte: {context_name.upper()}",
        font=("Arial", 12, "bold")
    ).pack(pady=10)

    # Frame avec scrollbar
    container = tk.Frame(dialog)
    container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    canvas = tk.Canvas(container)
    scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Variable pour stocker le tooltip actuel
    tooltip_window = [None]

    def show_tooltip(event, text):
        """Affiche un tooltip avec le texte complet."""
        if tooltip_window[0]:
            tooltip_window[0].destroy()

        tooltip = tk.Toplevel(dialog)
        tooltip.wm_overrideredirect(True)
        tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")

        label = tk.Label(
            tooltip,
            text=text,
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            font=("Courier New", 9),
            wraplength=400,
            justify="left",
            padx=5,
            pady=5
        )
        label.pack()
        tooltip_window[0] = tooltip

    def hide_tooltip(event):
        """Cache le tooltip."""
        if tooltip_window[0]:
            tooltip_window[0].destroy()
            tooltip_window[0] = None

    # Affiche les 12 touches F1-F12
    function_keys = [f"f{i}" for i in range(1, 13)]

    for idx, fk in enumerate(function_keys):
        key_label = fk.upper()

        # Frame pour chaque ligne
        row_frame = tk.Frame(scrollable_frame)
        row_frame.pack(fill=tk.X, pady=2)

        # Label de la touche
        tk.Label(
            row_frame,
            text=key_label,
            font=("Arial", 10, "bold"),
            width=5,
            anchor="w"
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Vérifie si la macro existe
        if fk in config:
            action = config[fk]
            value = action.get("value", "")
            action_type = action.get("type", "")

            # Preview court
            preview = format_macro_preview(value, 70)
            if not preview:
                preview = "[Vide]"

            # Label avec preview
            preview_label = tk.Label(
                row_frame,
                text=preview,
                font=("Courier New", 9),
                anchor="w",
                fg="#000000"
            )
            preview_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

            # Ajoute les événements pour le tooltip
            full_text = f"Type: {action_type}\n\nContenu:\n{value}"
            preview_label.bind("<Enter>", lambda e, t=full_text: show_tooltip(e, t))
            preview_label.bind("<Leave>", hide_tooltip)
        else:
            # Macro non configurée
            tk.Label(
                row_frame,
                text="[Non configuré]",
                font=("Courier New", 9),
                anchor="w",
                fg="#888888"
            ).pack(side=tk.LEFT, fill=tk.X, expand=True)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Bouton fermer
    tk.Button(
        dialog,
        text="Fermer",
        command=dialog.destroy,
        width=20,
        height=1,
        font=("Arial", 10)
    ).pack(pady=10)

    dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)

def check_queue():
    try:
        action = action_queue.get_nowait()
        if action == 'show_selector':
            show_context_selector()
        elif action == 'show_help':
            show_help_window()
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
    print("Ctrl+² : Sélectionner le contexte / Quitter / Aide")
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
