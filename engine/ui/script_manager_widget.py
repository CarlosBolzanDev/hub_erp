from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from core.config_manager import RegisteredScript


class ScriptManagerWidget(ttk.LabelFrame):
    """Tree-based script manager with active checkbox column and metadata."""

    ACTIVE_COLUMN = "active"

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, text="Scripts cadastrados")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self._scripts: dict[str, RegisteredScript] = {}

        columns = (self.ACTIVE_COLUMN, "name", "path", "status", "last_execution")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        self.tree.heading(self.ACTIVE_COLUMN, text="Ativo")
        self.tree.heading("name", text="Nome amigável")
        self.tree.heading("path", text="Caminho completo")
        self.tree.heading("status", text="Status")
        self.tree.heading("last_execution", text="Última execução")
        self.tree.column(self.ACTIVE_COLUMN, width=70, anchor="center", stretch=False)
        self.tree.column("name", width=180, anchor="w")
        self.tree.column("path", width=420, anchor="w")
        self.tree.column("status", width=150, anchor="w")
        self.tree.column("last_execution", width=150, anchor="w")

        self.scrollbar_y = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.scrollbar_x = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)
        self.tree.grid(row=0, column=0, sticky="nsew", padx=(8, 0), pady=(8, 0))
        self.scrollbar_y.grid(row=0, column=1, sticky="ns", pady=(8, 0), padx=(0, 8))
        self.scrollbar_x.grid(row=1, column=0, sticky="ew", padx=(8, 0), pady=(0, 8))
        self.tree.bind("<Button-1>", self._handle_click)
        self.tree.bind("<Double-1>", self._handle_double_click)

    def set_scripts(self, scripts: list[RegisteredScript]) -> None:
        self._scripts = {script.id: script for script in scripts}
        self.tree.delete(*self.tree.get_children())
        for script in scripts:
            self._upsert_row(script)

    def selected_script_id(self) -> str | None:
        selection = self.tree.selection()
        return selection[0] if selection else None

    def selected_script(self) -> RegisteredScript | None:
        script_id = self.selected_script_id()
        if script_id is None:
            return None
        return self._scripts.get(script_id)

    def active_scripts(self) -> list[RegisteredScript]:
        return [script for script in self._scripts.values() if script.enabled]

    def refresh_row(self, script: RegisteredScript) -> None:
        self._scripts[script.id] = script
        self._upsert_row(script)

    def _upsert_row(self, script: RegisteredScript) -> None:
        values = (
            "☑" if script.enabled else "☐",
            script.display_name,
            script.path,
            script.validation_status,
            script.last_execution,
        )
        if self.tree.exists(script.id):
            self.tree.item(script.id, values=values)
        else:
            self.tree.insert("", "end", iid=script.id, values=values)

    def _handle_click(self, event: tk.Event) -> None:
        region = self.tree.identify("region", event.x, event.y)
        column = self.tree.identify_column(event.x)
        item_id = self.tree.identify_row(event.y)
        if region == "cell" and column == "#1" and item_id in self._scripts:
            script = self._scripts[item_id]
            script.enabled = not script.enabled
            self.refresh_row(script)

    def _handle_double_click(self, event: tk.Event) -> None:
        item_id = self.tree.identify_row(event.y)
        if item_id:
            self.tree.selection_set(item_id)
