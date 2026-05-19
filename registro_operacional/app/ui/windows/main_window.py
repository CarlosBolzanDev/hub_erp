from PySide6.QtWidgets import QMainWindow,QWidget,QHBoxLayout,QVBoxLayout,QListWidget,QPushButton,QLineEdit,QTabWidget,QTextEdit,QLabel,QInputDialog,QFileDialog,QMessageBox
from registro_operacional.app.database.session import SessionLocal
from registro_operacional.app.services.occurrence_service import OccurrenceService
from registro_operacional.app.models.occurrence import OccurrenceEvent, Attachment, LinkItem, RaciAssignment, RaciPerson

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.setWindowTitle("Registro Operacional - Ocorrências"); self.resize(1280,800)
        self.session = SessionLocal(); self.service = OccurrenceService(self.session); self._build(); self.refresh()

    def _build(self):
        w=QWidget(); self.setCentralWidget(w); h=QHBoxLayout(w); l=QVBoxLayout(); r=QVBoxLayout(); h.addLayout(l,2); h.addLayout(r,3)
        self.search=QLineEdit(); self.search.setPlaceholderText("Busca global"); self.search.textChanged.connect(self.refresh)
        self.list=QListWidget(); self.list.currentRowChanged.connect(self.load_detail); l.addWidget(self.search); l.addWidget(self.list)
        for txt, fn in [("Nova Ocorrência", self.new_occurrence),("Finalizar", self.finalize_selected),("Reabrir", self.reopen_selected),("Colar print", self.paste_print),("Anexar arquivo", self.attach_file),("Adicionar link", self.add_link)]:
            b=QPushButton(txt); b.clicked.connect(fn); l.addWidget(b)
        self.title=QLabel("Selecione uma ocorrência")
        self.tabs=QTabWidget(); self.resumo=QTextEdit(); self.timeline=QTextEdit(); self.anexos=QTextEdit(); self.links=QTextEdit(); self.raci=QTextEdit(); self.historico=QTextEdit(); self.obs=QTextEdit()
        for n,t in [("Resumo",self.resumo),("Timeline",self.timeline),("Anexos",self.anexos),("Links",self.links),("RACI",self.raci),("Histórico",self.historico),("Observações",self.obs)]: self.tabs.addTab(t,n)
        r.addWidget(self.title); r.addWidget(self.tabs)

    def refresh(self):
        q=self.search.text().strip(); self.list.clear()
        rows=self.service.repo.list_all() if not q else [self.service.repo.get(i) for i in self.service.repo.search_ids(q+"*") if self.service.repo.get(i)]
        self._rows=rows
        for o in rows: self.list.addItem(f"{o.code} | {o.status} | {o.title}")

    def selected(self):
        i=self.list.currentRow(); return None if i<0 or i>=len(getattr(self,'_rows',[])) else self._rows[i]

    def load_detail(self, _):
        o=self.selected();
        if not o: return
        self.title.setText(f"{o.code} - {o.title}")
        self.resumo.setText(f"Status: {o.status}\nPrioridade: {o.priority}\nSetor: {o.sector}\nResponsável: {o.owner}\nResumo: {o.summary}")
        ev=self.session.query(OccurrenceEvent).filter_by(occurrence_id=o.id).order_by(OccurrenceEvent.created_at.desc()).all(); self.timeline.setText("\n".join(f"{x.created_at} | {x.event_type} | {x.title} | {x.description}" for x in ev))
        at=self.session.query(Attachment).filter_by(occurrence_id=o.id).all(); self.anexos.setText("\n".join(f"{x.original_name} ({x.size_bytes} bytes)" for x in at))
        lk=self.session.query(LinkItem).filter_by(occurrence_id=o.id).all(); self.links.setText("\n".join(f"{x.url} | {x.title}" for x in lk))
        ra=self.session.query(RaciAssignment,RaciPerson).join(RaciPerson,RaciPerson.id==RaciAssignment.raci_person_id).filter(RaciAssignment.occurrence_id==o.id).all()
        self.raci.setText("\n".join(f"{p.name} ({p.role}) R:{a.responsible} A:{a.accountable} C:{a.consulted} I:{a.informed}" for a,p in ra))
        self.obs.setText(o.observations or "")

    def new_occurrence(self):
        t,ok=QInputDialog.getText(self,"Nova Ocorrência","Título");
        if not ok or not t: return
        self.service.open_occurrence({"title":t,"summary":"aberta via interface"}); self.refresh()

    def finalize_selected(self):
        o=self.selected();
        if not o: return
        txt,ok=QInputDialog.getText(self,"Finalizar","Resultado final");
        if ok and txt: self.service.finalize_occurrence(o.id, txt); self.refresh(); self.load_detail(0)

    def reopen_selected(self):
        o=self.selected();
        if not o: return
        txt,ok=QInputDialog.getText(self,"Reabrir","Motivo");
        if ok and txt: self.service.reopen_occurrence(o.id, txt); self.refresh(); self.load_detail(0)

    def paste_print(self):
        o=self.selected();
        if not o: return
        if self.service.paste_print_from_clipboard(o.id, "print colado"):
            QMessageBox.information(self,"OK","Print vinculado à ocorrência")
            self.load_detail(0)
        else: QMessageBox.warning(self,"Aviso","Clipboard sem imagem")

    def attach_file(self):
        o=self.selected();
        if not o: return
        p,_=QFileDialog.getOpenFileName(self,"Anexar arquivo")
        if p: self.service.add_attachment(o.id,p); self.load_detail(0)

    def add_link(self):
        o=self.selected();
        if not o: return
        u,ok=QInputDialog.getText(self,"Link","URL")
        if ok and u: self.service.add_link(o.id,u); self.load_detail(0)
