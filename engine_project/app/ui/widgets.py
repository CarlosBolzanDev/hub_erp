from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class LabeledFrame(ttk.LabelFrame):
    def __init__(self, master: tk.Misc, title: str) -> None:
        super().__init__(master, text=title, padding=8)
