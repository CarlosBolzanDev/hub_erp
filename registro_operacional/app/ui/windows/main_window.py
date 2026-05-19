from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMainWindow,QWidget,QHBoxLayout,QVBoxLayout,QListWidget,QPushButton,QLineEdit,QTabWidget,QTextEdit,QLabel,QInputDialog,QFileDialog,QMessageBox,QComboBox
from registro_operacional.app.database.session import SessionLocal
from registro_operacional.app.services.occurrence_service import OccurrenceService
from registro_operacional.app.models.occurrence import OccurrenceEvent, Attachment, LinkItem, RaciAssignment, RaciPerson

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("Registro Operacional de Decisões e Evidências"); self.resize(1320,820)
        self.session = SessionLocal(); self.service = OccurrenceService(self.session); self._build(); self.refresh()

    def _build(self):
        w=QWidget(); self.setCentralWidget(w); h=QHBoxLayout(w)
        l=QVBoxLayout(); r=QVBoxLayout(); h.addLayout(l,2); h.addLayout(r,4)
        self.search=QLineEdit(); self.search.setPlaceholderText("Busca rápida"); self.search.textChanged.connect(self.refresh)
        self.f_status = QComboBox(); self.f_status.addItems(["", "Aberta", "Em andamento", "Pendente", "Finalizada", "Reaberta"]); self.f_status.currentTextChanged.connect(self.refresh)
        self.list=QListWidget(); self.list.currentRowChanged.connect(self.load_detail); self.list.setAcceptDrops(True)
        l.addWidget(self.search); l.addWidget(self.f_status); l.addWidget(self.list)
        for txt, fn in [("Nova ocorrência", self.new_occurrence),("Abrir ocorrência", self.open_selected),("Finalizar ocorrência", self.finalize_selected),("Colar print", self.paste_print),("Exportar", self.export_selected),("Filtrar", self.refresh)]:
            b=QPushButton(txt); b.clicked.connect(fn); l.addWidget(b)

        self.title=QLabel("Selecione uma ocorrência")
        self.tabs=QTabWidget(); self.resumo=QTextEdit(); self.timeline=QTextEdit(); self.anexos=QTextEdit(); self.links=QTextEdit(); self.raci=QTextEdit(); self.hist=QTextEdit(); self.obs=QTextEdit()
        for n,t in [("Resumo",self.resumo),("Timeline",self.timeline),("Anexos",self.anexos),("Links",self.links),("RACI",self.raci),("Histórico",self.hist),("Observações",self.obs)]: self.tabs.addTab(t,n)
        r.addWidget(self.title); r.addWidget(self.tabs)

        paste = QAction("Colar print", self); paste.setShortcut(QKeySequence("Ctrl+V")); paste.triggered.connect(self.paste_print); self.addAction(paste)

    def refresh(self):
        q=self.search.text().strip(); status=self.f_status.currentText().strip() or None
        rows=self.service.repo.list_filtered({"status": status})
        if q:
            ids=set(self.service.repo.search_ids(q+"*")); rows=[o for o in rows if o.id in ids]
        self._rows=rows; self.list.clear(); [self.list.addItem(f"Ocorrência #{o.id} | {o.status} | {o.title}") for o in rows]

    def selected(self):
        i=self.list.currentRow(); return None if i<0 or i>=len(getattr(self,'_rows',[])) else self._rows[i]

    def load_detail(self, _):
        o=self.selected();
        if not o: return
        self.title.setText(f"Ocorrência #{o.id} - {o.title}")
        self.resumo.setText(f"Status: {o.status}\nPrioridade: {o.priority}\nSetor: {o.sector}\nResponsável: {o.owner}\nResumo: {o.summary}\nResultado: {o.final_result}")
        ev=self.session.query(OccurrenceEvent).filter_by(occurrence_id=o.id).order_by(OccurrenceEvent.created_at.desc()).all(); self.timeline.setText("\n".join(f"{x.created_at} | {x.created_by} | {x.event_type} | {x.title} | {x.description}" for x in ev))
        at=self.session.query(Attachment).filter_by(occurrence_id=o.id).all(); self.anexos.setText("\n".join(f"{x.original_name} | {x.comment}" for x in at))
        lk=self.session.query(LinkItem).filter_by(occurrence_id=o.id).all(); self.links.setText("\n".join(f"{x.url} | {x.title}" for x in lk))
        ra=self.session.query(RaciAssignment,RaciPerson).join(RaciPerson,RaciPerson.id==RaciAssignment.raci_person_id).filter(RaciAssignment.occurrence_id==o.id).all()
        self.raci.setText("\n".join(f"{p.name} | {p.sector} | {p.role} | R:{a.responsible} A:{a.accountable} C:{a.consulted} I:{a.informed} | {a.note}" for a,p in ra))

    def new_occurrence(self):
        t,ok=QInputDialog.getText(self,"Novo Registro","Título da ocorrência")
        if ok and t: self.service.open_occurrence({"title":t,"summary":"aberta via interface"}); self.refresh()

    def open_selected(self):
        o=self.selected();
        if o: self.service.update_status(o.id, "Em andamento", "aberta para tratativa"); self.refresh(); self.load_detail(0)

    def finalize_selected(self):
        o=self.selected();
        if not o: return
        txt,ok=QInputDialog.getText(self,"Finalizar Ocorrência","Resultado final")
        if ok: self.service.finalize_occurrence(o.id, txt); self.refresh(); self.load_detail(0)

    def paste_print(self):
        o=self.selected();
        if not o: return
        legenda,ok=QInputDialog.getText(self,"Colar print","Legenda opcional")
        if not ok: return
        if self.service.paste_print_from_clipboard(o.id, legenda or "print colado"):
            QMessageBox.information(self,"Confirmação","Print salvo na ocorrência")
            self.load_detail(0)
        else:
            QMessageBox.warning(self,"Aviso","Não há imagem no clipboard")

    def export_selected(self):
        o=self.selected();
        if not o: return
        self.service.export_json(o.id); self.service.export_csv(o.id); self.service.export_pdf(o.id)
        QMessageBox.information(self,"Exportação","JSON, CSV e PDF gerados em data/exports")
