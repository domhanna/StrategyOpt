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


def series_event_select_GUI():
    result = {}

    def on_confirm():
        if series_var.get() == "IMSA":
            base_url = "https://imsa.results.alkamelcloud.com/"
        elif series_var.get() == "WEC":
            base_url= "https://fiawec.alkamelsystems.com/"
        result["url"] = base_url
        root.destroy()

    def on_season_selected(event):
        confirm_button["state"] = "normal"

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
    header = ttk.Label(frame, text="Select Series", style="Header.TLabel")
    header.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 4))

    # --- Season ---
    season_label = ttk.Label(frame, text="Series")
    season_label.grid(row=2, column=0, sticky="w", pady=(0, 4))

    series_var = tk.StringVar()
    series_box = ttk.Combobox(
        frame, textvariable=series_var,
        values=["IMSA", "WEC"],
        state="readonly", width=32,
    )
    series_box.grid(row=3, column=0, sticky="ew", padx=(0, 15), pady=(0, 20))

    # --- Confirm button ---
    confirm_button = ttk.Button(frame, text="Confirm", command=on_confirm, state="disabled")
    confirm_button.grid(row=4, column=1, sticky="e")

    series_box.bind("<<ComboboxSelected>>", on_season_selected)

    root.mainloop()

    return result["url"]

if __name__ == "__main__":
    result = series_event_select_GUI()
    print("Returned:", result)