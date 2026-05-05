from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.ui.widgets import LabeledFrame


class ScriptPanel(LabeledFrame):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, "Scripts / Plugins")
        self.listbox = tk.Listbox(self, height=12)
        self.listbox.pack(fill="both", expand=True)


class LogPanel(LabeledFrame):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, "Runtime Logs")
        self.text = tk.Text(self, height=14, state="disabled")
        self.text.pack(fill="both", expand=True)


class StatusPanel(LabeledFrame):
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, "Status")
        self.var = tk.StringVar(value="Ready")
        ttk.Label(self, textvariable=self.var).pack(anchor="w")
