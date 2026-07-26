import tkinter as tk
from tkinter import ttk
from webRequest import web_request
from get_dropdown_options import get_dropdown_options

# Color palette
NAVY = "#000C34"
CREAM = "#FDF5BF"
SLATE = "#9AADBF"
BLUE = "#044B7F"
GRAY = "#646464"


def season_event_select_GUI(base_url):
    result = {}
    params = {}

    def on_confirm():
        season_value = next(v for t, v in season_options if t == season_var.get())
        event_value = next(v for t, v in event_options if t == event_var.get())
        result["params"] = {"season": season_value, "evvent": event_value}
        root.destroy()

    def on_season_selected(event):
        nonlocal event_options
        params = {"season": next(v for t, v in season_options if t == season_var.get())}
        soup, _ = web_request(base_url, params=params)
        event_options = get_dropdown_options(soup, 'evvent')
        event_box["values"] = [event[0] for event in event_options]
        event_box["state"] = "readonly"
        confirm_button["state"] = "normal"

    soup, _ = web_request(base_url)
    season_options = get_dropdown_options(soup, 'season')
    event_options = []

    # --- Window setup ---
    root = tk.Tk()
    root.title("Season / Event Selector")
    root.geometry("560x260")
    root.configure(bg=NAVY)
    root.resizable(False, False)

    # --- Style setup ---
    style = ttk.Style()
    style.theme_use("clam")

    style.configure("TLabel", background=NAVY, foreground=CREAM,
                     font=("Segoe UI", 11))
    style.configure("Header.TLabel", background=NAVY, foreground=CREAM,
                     font=("Segoe UI", 18, "bold"))
    style.configure("Sub.TLabel", background=NAVY, foreground=SLATE,
                     font=("Segoe UI", 9))

    style.configure("TCombobox",
                     fieldbackground=CREAM,
                     background=CREAM,
                     foreground=NAVY,
                     arrowcolor=NAVY,
                     padding=6,
                     font=("Segoe UI", 10))
    style.map("TCombobox",
              fieldbackground=[("readonly", CREAM), ("disabled", GRAY)],
              foreground=[("disabled", NAVY)])

    style.configure("TButton",
                     background=BLUE,
                     foreground=CREAM,
                     font=("Segoe UI", 11, "bold"),
                     padding=(18, 8),
                     borderwidth=0)
    style.map("TButton",
              background=[("active", CREAM), ("disabled", SLATE)],
              foreground=[("active", NAVY), ("disabled", NAVY)])

    # --- Content frame (adds a consistent margin around everything) ---
    frame = tk.Frame(root, bg=NAVY)
    frame.grid(row=0, column=0, sticky="nsew", padx=30, pady=25)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(1, weight=1)

    # --- Header ---
    header = ttk.Label(frame, text="Select Season & Event", style="Header.TLabel")
    header.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 4))

    subheader = ttk.Label(
        frame,
        text="Choose a season to load its available events.",
        style="Sub.TLabel",
    )
    subheader.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 20))

    # --- Season ---
    season_label = ttk.Label(frame, text="Season")
    season_label.grid(row=2, column=0, sticky="w", pady=(0, 4))

    season_var = tk.StringVar()
    season_box = ttk.Combobox(
        frame, textvariable=season_var,
        values=[season[0] for season in season_options],
        state="readonly", width=32,
    )
    season_box.grid(row=3, column=0, sticky="ew", padx=(0, 15), pady=(0, 20))

    # --- Event ---
    event_label = ttk.Label(frame, text="Event")
    event_label.grid(row=2, column=1, sticky="w", pady=(0, 4))

    event_var = tk.StringVar()
    event_box = ttk.Combobox(
        frame, textvariable=event_var,
        values=[],
        state="disabled", width=32,
    )
    event_box.grid(row=3, column=1, sticky="ew", pady=(0, 20))

    season_box.bind("<<ComboboxSelected>>", on_season_selected)

    # --- Confirm button ---
    confirm_button = ttk.Button(frame, text="Confirm", command=on_confirm, state="disabled")
    confirm_button.grid(row=4, column=1, sticky="e")

    root.mainloop()

    return result["params"]