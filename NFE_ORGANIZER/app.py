"""Desktop application for automatic NF-e XML classification and organization."""

from __future__ import annotations

import logging
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext

from nfe_organizer.config import AppConfig, ConfigManager
from nfe_organizer.monitor import FolderMonitor
from nfe_organizer.processor import NFeProcessor, ProcessEvent

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config" / "configuracoes.json"
LOG_PATH = BASE_DIR / "logs" / "processamento.log"


def setup_logger() -> logging.Logger:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("nfe_organizer")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
        logger.addHandler(handler)
    return logger


class NFeOrganizerApp(tk.Tk):
    """Tkinter GUI aimed at non-technical users."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Organizador de XML NF-e")
        self.geometry("820x520")
        self.resizable(True, True)

        self.config_manager = ConfigManager(CONFIG_PATH, BASE_DIR)
        self.config_data = self.config_manager.load()
        self.logger = setup_logger()
        self.monitor: FolderMonitor | None = None
        self.event_queue: queue.Queue[ProcessEvent] = queue.Queue()

        self.input_var = tk.StringVar(value=self.config_data.entrada)
        self.output_var = tk.StringVar(value=self.config_data.saida)
        self.status_var = tk.StringVar(value="● Parado")

        self._build_ui()
        self._poll_events()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        container = tk.Frame(self, padx=16, pady=16)
        container.pack(fill=tk.BOTH, expand=True)

        self._path_row(container, "Caminho Entrada", self.input_var, 0, self._select_input)
        self._path_row(container, "Caminho Destino", self.output_var, 1, self._select_output)

        controls = tk.Frame(container)
        controls.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(12, 8))
        tk.Button(controls, text="INICIAR MONITORAMENTO", command=self.start_monitoring, bg="#2e7d32", fg="white").pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(controls, text="PARAR MONITORAMENTO", command=self.stop_monitoring, bg="#b71c1c", fg="white").pack(side=tk.LEFT)
        tk.Label(controls, textvariable=self.status_var, font=("Arial", 12, "bold"), fg="#b71c1c").pack(side=tk.RIGHT)

        tk.Label(container, text="Painel de Eventos").grid(row=3, column=0, sticky="w")
        self.events = scrolledtext.ScrolledText(container, height=18, state=tk.DISABLED)
        self.events.grid(row=4, column=0, columnspan=3, sticky="nsew")
        container.columnconfigure(1, weight=1)
        container.rowconfigure(4, weight=1)

    def _path_row(self, parent: tk.Frame, label: str, variable: tk.StringVar, row: int, command) -> None:  # noqa: ANN001
        tk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=4)
        tk.Entry(parent, textvariable=variable).grid(row=row, column=1, sticky="ew", padx=8, pady=4)
        tk.Button(parent, text="Selecionar Pasta", command=command).grid(row=row, column=2, pady=4)

    def _select_input(self) -> None:
        self._select_folder(self.input_var)

    def _select_output(self) -> None:
        self._select_folder(self.output_var)

    def _select_folder(self, variable: tk.StringVar) -> None:
        folder = filedialog.askdirectory(initialdir=variable.get() or str(BASE_DIR))
        if folder:
            variable.set(folder)
            self._save_config()

    def start_monitoring(self) -> None:
        self._save_config()
        input_dir = Path(self.input_var.get())
        output_dir = Path(self.output_var.get())
        processor = NFeProcessor(output_dir, self.logger)
        self.monitor = FolderMonitor(input_dir, processor, self.event_queue.put)
        self.monitor.start()
        self.status_var.set("● Monitorando")
        self._append_text(f"Monitoramento iniciado em: {input_dir}\n")

    def stop_monitoring(self) -> None:
        if self.monitor:
            threading.Thread(target=self.monitor.stop, daemon=True).start()
        self.status_var.set("● Parado")
        self._append_text("Monitoramento parado.\n")

    def _save_config(self) -> None:
        self.config_data = AppConfig(entrada=self.input_var.get(), saida=self.output_var.get())
        self.config_manager.save(self.config_data)

    def _poll_events(self) -> None:
        while not self.event_queue.empty():
            event = self.event_queue.get_nowait()
            self._append_text(
                f"Arquivo recebido: {event.original_name}\n"
                f"Classificação: {event.nfe_type}\n"
                f"Novo nome: {event.new_name}\n"
                f"Destino: {event.destination}\n"
                f"Status: {event.status} - {event.message}\n\n"
            )
        self.after(500, self._poll_events)

    def _append_text(self, text: str) -> None:
        self.events.configure(state=tk.NORMAL)
        self.events.insert(tk.END, text)
        self.events.see(tk.END)
        self.events.configure(state=tk.DISABLED)

    def _on_close(self) -> None:
        try:
            self.stop_monitoring()
            self._save_config()
        except Exception as exc:  # noqa: BLE001 - show shutdown issues without hiding the window close.
            messagebox.showwarning("Aviso", f"Falha ao encerrar monitoramento: {exc}")
        self.destroy()


if __name__ == "__main__":
    NFeOrganizerApp().mainloop()
