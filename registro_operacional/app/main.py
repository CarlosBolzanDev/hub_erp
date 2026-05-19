from PySide6.QtWidgets import QApplication
import qdarktheme
from registro_operacional.app.database.init_db import init_db
from registro_operacional.app.ui.windows.main_window import MainWindow

if __name__ == "__main__":
    init_db()
    app = QApplication([])
    app.setStyleSheet(qdarktheme.load_stylesheet())
    w = MainWindow(); w.show()
    app.exec()
