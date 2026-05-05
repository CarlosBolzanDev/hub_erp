from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from core.script_loader import ScriptInfo


class ScriptListWidget(ttk.LabelFrame):
    """Checkbox list for valid scripts discovered by the loader."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, text="Scripts disponíveis")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self._variables: dict[str, tk.BooleanVar] = {}
        self._messages: dict[str, str] = {}

        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.container = ttk.Frame(self.canvas)
        self.container.bind("<Configure>", lambda _event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.container, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind("<Configure>", self._resize_container)
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=(8, 0), pady=8)
        self.scrollbar.grid(row=0, column=1, sticky="ns", pady=8, padx=(0, 8))

    def set_scripts(self, scripts: list[ScriptInfo], selected: list[str]) -> None:
        for child in self.container.winfo_children():
            child.destroy()
        self._variables.clear()
        self._messages.clear()

        selected_set = set(selected)
        valid_scripts = [script for script in scripts if script.valid]
        if not valid_scripts:
            ttk.Label(self.container, text="Nenhum script válido encontrado em Scripts/.").grid(
                row=0, column=0, sticky="w", padx=8, pady=8
            )
            return

        for row, script in enumerate(valid_scripts):
            variable = tk.BooleanVar(value=script.name in selected_set)
            self._variables[script.name] = variable
            self._messages[script.name] = script.message
            checkbox = ttk.Checkbutton(self.container, text=script.name, variable=variable)
            checkbox.grid(row=row, column=0, sticky="w", padx=8, pady=4)

    def selected_scripts(self) -> list[str]:
        return [name for name, variable in self._variables.items() if variable.get()]

    def _resize_container(self, event: tk.Event) -> None:
        self.canvas.itemconfigure(self.canvas_window, width=event.width)
