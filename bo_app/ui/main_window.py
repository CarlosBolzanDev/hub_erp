from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QPushButton, QLineEdit, QLabel, QTextEdit, QTabWidget, QFileDialog, QInputDialog)
from bo_app.db import SessionLocal
from bo_app.services.bo_service import BOService
from bo_app.models import BO, BOEvent, Attachment, LinkItem

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BO Operacional")
        self.resize(1200, 760)
        self.session = SessionLocal()
        self.service = BOService(self.session)
        self._build()
        self.refresh_bos()

    def _build(self):
        root = QWidget(); self.setCentralWidget(root)
        hl = QHBoxLayout(root)
        left = QVBoxLayout(); right = QVBoxLayout(); hl.addLayout(left,2); hl.addLayout(right,3)
        self.search = QLineEdit(); self.search.setPlaceholderText("Busca rápida")
        self.search.textChanged.connect(self.refresh_bos)
        self.list = QListWidget(); self.list.currentRowChanged.connect(self.load_bo)
        left.addWidget(self.search); left.addWidget(self.list)
        bnew = QPushButton("Novo BO"); bnew.clicked.connect(self.new_bo)
        bcap = QPushButton("Captura rápida"); bcap.clicked.connect(self.quick_capture)
        bex = QPushButton("Exportar CSV"); bex.clicked.connect(lambda: self.service.export_csv())
        left.addWidget(bnew); left.addWidget(bcap); left.addWidget(bex)
        self.title = QLabel("Selecione um BO")
        self.tabs = QTabWidget()
        self.timeline = QTextEdit(); self.timeline.setReadOnly(True)
        self.attachments = QTextEdit(); self.attachments.setReadOnly(True)
        self.links = QTextEdit(); self.links.setReadOnly(True)
        self.notes = QTextEdit()
        self.tabs.addTab(self.timeline, "Timeline")
        self.tabs.addTab(self.attachments, "Anexos")
        self.tabs.addTab(self.links, "Links")
        self.tabs.addTab(self.notes, "Observações")
        right.addWidget(self.title); right.addWidget(self.tabs)

    def refresh_bos(self):
        q = self.search.text().strip()
        self.list.clear()
        if q:
            ids = [r[0] for r in self.service.repo.search(q + "*")]
            rows = [self.service.repo.get(i) for i in ids if self.service.repo.get(i)]
        else:
            rows = self.service.repo.list_all()
        self._rows = rows
        for bo in rows:
            self.list.addItem(f"#{bo.id} [{bo.status}] {bo.title}")

    def load_bo(self, idx):
        if idx < 0 or idx >= len(getattr(self, "_rows", [])): return
        bo = self._rows[idx]
        self.title.setText(f"BO #{bo.id} - {bo.title}")
        events = self.session.query(BOEvent).filter_by(bo_id=bo.id).order_by(BOEvent.created_at.desc()).all()
        self.timeline.setText("\n".join(f"{e.created_at} | {e.event_type} | {e.title} | {e.description}" for e in events))
        atts = self.session.query(Attachment).filter_by(bo_id=bo.id).all()
        self.attachments.setText("\n".join(f"{a.file_name} ({a.size_bytes} bytes)" for a in atts))
        links = self.session.query(LinkItem).filter_by(bo_id=bo.id).all()
        self.links.setText("\n".join(f"{l.url} | {l.title}" for l in links))
        self.notes.setText(bo.observations or "")

    def new_bo(self):
        title, ok = QInputDialog.getText(self, "Novo BO", "Título")
        if not ok or not title: return
        self.service.create_bo({"title": title, "summary":"criado via UI"})
        self.refresh_bos()

    def quick_capture(self):
        if not getattr(self, "_rows", None):
            self.new_bo(); self.refresh_bos()
            if not getattr(self, "_rows", None): return
        bo = self._rows[0]
        path, _ = QFileDialog.getOpenFileName(self, "Escolher imagem", "", "Imagens (*.png *.jpg *.jpeg *.webp)")
        if path:
            self.service.add_attachment(bo.id, path, comment="captura rápida")
            self.load_bo(0)
