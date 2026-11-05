"""
Calculator with GUI
Auspify Technologies - Python Development Internship (Task 3)
Author: Aliyer Bakers Musaazi

A desktop calculator built with Tkinter. The calculation rules live in
calculator_logic.py; this file only draws the window and handles events.

Run with:  py calculator.py
"""

import tkinter as tk

from calculator_logic import DIVIDE, MINUS, PLUS, TIMES, Calculator

# ---------- Colours and fonts ----------

COLORS = {
    "window": "#1e1f26",
    "text": "#ffffff",
    "muted": "#8b8d98",
    "error": "#ff6b6b",
    "panel": "#262833",
    "digit": "#2f313d",
    "digit_hover": "#3b3e4c",
    "function": "#3d4051",
    "function_hover": "#4a4e63",
    "operator": "#ff9f0a",
    "operator_hover": "#ffb340",
    "equals": "#30d158",
    "equals_hover": "#4ee072",
}

FONT = "Segoe UI"

# Button layout: (label, style). Each inner list is one row.
BUTTONS = [
    [("√", "function"), ("x²", "function"), ("%", "function"), ("⌫", "function")],
    [("C", "function"), ("(", "function"), (")", "function"), (DIVIDE, "operator")],
    [("7", "digit"), ("8", "digit"), ("9", "digit"), (TIMES, "operator")],
    [("4", "digit"), ("5", "digit"), ("6", "digit"), (MINUS, "operator")],
    [("1", "digit"), ("2", "digit"), ("3", "digit"), (PLUS, "operator")],
    [("±", "digit"), ("0", "digit"), (".", "digit"), ("=", "equals")],
]

# Keyboard shortcuts: typed character -> calculator key
KEY_CHARS = {
    **{digit: digit for digit in "0123456789"},
    ".": ".",
    ",": ".",
    "+": PLUS,
    "-": MINUS,
    "*": TIMES,
    "x": TIMES,
    "/": DIVIDE,
    "(": "(",
    ")": ")",
    "%": "%",
    "=": "=",
    "r": "√",
    "s": "x²",
}

# Special keys (by name) -> calculator key
KEY_NAMES = {
    "Return": "=",
    "KP_Enter": "=",
    "BackSpace": "⌫",
    "Escape": "C",
    "Delete": "C",
}


class CalculatorApp:
    """The calculator window."""

    def __init__(self, root):
        self.root = root
        self.calculator = Calculator()

        root.title("Calculator")
        root.configure(bg=COLORS["window"], padx=12, pady=12)
        root.resizable(False, False)

        self.secondary_text = tk.StringVar()
        self.display_text = tk.StringVar(value="0")

        self._build_display()
        self._build_buttons()
        self._build_history()

        root.bind("<Key>", self.on_key)
        self.refresh()

    # ---------- Layout ----------

    def _build_display(self):
        frame = tk.Frame(self.root, bg=COLORS["window"])
        frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        # Small line: live result while typing, or the last calculation after "="
        tk.Label(
            frame,
            textvariable=self.secondary_text,
            bg=COLORS["window"],
            fg=COLORS["muted"],
            font=(FONT, 13),
            anchor="e",
        ).pack(fill="x")

        # Main display
        self.display_label = tk.Label(
            frame,
            textvariable=self.display_text,
            bg=COLORS["window"],
            fg=COLORS["text"],
            font=(FONT, 32, "bold"),
            anchor="e",
            width=14,
        )
        self.display_label.pack(fill="x")

    def _build_buttons(self):
        frame = tk.Frame(self.root, bg=COLORS["window"])
        frame.grid(row=1, column=0)

        for row_index, row in enumerate(BUTTONS):
            for column_index, (label, style) in enumerate(row):
                button = tk.Button(
                    frame,
                    text=label,
                    command=lambda key=label: self.press(key),
                    font=(FONT, 16, "bold" if style != "digit" else "normal"),
                    width=4,
                    height=1,
                    bg=COLORS[style],
                    fg=COLORS["text"],
                    activebackground=COLORS[f"{style}_hover"],
                    activeforeground=COLORS["text"],
                    relief="flat",
                    borderwidth=0,
                    cursor="hand2",
                )
                button.grid(row=row_index, column=column_index, padx=4, pady=4, ipady=10)
                button.bind("<Enter>", lambda e, b=button, s=style: b.configure(bg=COLORS[f"{s}_hover"]))
                button.bind("<Leave>", lambda e, b=button, s=style: b.configure(bg=COLORS[s]))

    def _build_history(self):
        frame = tk.Frame(self.root, bg=COLORS["panel"], padx=10, pady=10)
        frame.grid(row=0, column=1, rowspan=2, sticky="ns", padx=(14, 0))

        tk.Label(
            frame,
            text="History",
            bg=COLORS["panel"],
            fg=COLORS["text"],
            font=(FONT, 13, "bold"),
            anchor="w",
        ).pack(fill="x")

        tk.Label(
            frame,
            text="Click an entry to reuse its result",
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=(FONT, 9),
            anchor="w",
        ).pack(fill="x", pady=(0, 6))

        list_frame = tk.Frame(frame, bg=COLORS["panel"])
        list_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.history_list = tk.Listbox(
            list_frame,
            width=26,
            height=16,
            bg=COLORS["panel"],
            fg=COLORS["text"],
            selectbackground=COLORS["function"],
            font=(FONT, 11),
            borderwidth=0,
            highlightthickness=0,
            activestyle="none",
            yscrollcommand=scrollbar.set,
        )
        self.history_list.pack(side="left", fill="both", expand=True)
        scrollbar.configure(command=self.history_list.yview)
        self.history_list.bind("<<ListboxSelect>>", self.on_history_select)

        tk.Button(
            frame,
            text="Clear history",
            command=self.clear_history,
            font=(FONT, 10),
            bg=COLORS["function"],
            fg=COLORS["text"],
            activebackground=COLORS["function_hover"],
            activeforeground=COLORS["text"],
            relief="flat",
            borderwidth=0,
            cursor="hand2",
        ).pack(fill="x", pady=(8, 0), ipady=4)

    # ---------- Events ----------

    def press(self, key):
        self.calculator.press(key)
        self.refresh()

    def on_key(self, event):
        key = KEY_NAMES.get(event.keysym) or KEY_CHARS.get(event.char)
        if key:
            self.press(key)

    def on_history_select(self, event):
        selection = self.history_list.curselection()
        if not selection:
            return
        # The list shows the newest entry first
        history_index = len(self.calculator.history) - 1 - selection[0]
        self.calculator.use_history(history_index)
        self.refresh()

    def clear_history(self):
        self.calculator.clear_history()
        self.refresh()

    # ---------- Drawing ----------

    def refresh(self):
        """Update every part of the window from the calculator's state."""
        calc = self.calculator
        text = calc.display

        # Shrink the font for long expressions, and show the end if it is very long
        size = 32 if len(text) <= 12 else 24 if len(text) <= 17 else 18
        if len(text) > 22:
            text = "…" + text[-21:]
        self.display_text.set(text)
        self.display_label.configure(
            font=(FONT, size, "bold"),
            fg=COLORS["error"] if calc.error else COLORS["text"],
        )

        if calc.just_evaluated and calc.last_calculation:
            self.secondary_text.set(f"{calc.last_calculation} =")
        else:
            self.secondary_text.set(calc.preview)

        self.history_list.delete(0, "end")
        for expression, result in reversed(calc.history):
            self.history_list.insert("end", f"{expression} = {result}")


def main():
    root = tk.Tk()
    CalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()