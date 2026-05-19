from PySide6.QtWidgets import QApplication
from bo_app.init_db import init_db
from bo_app.ui.main_window import MainWindow


def main():
    init_db()
    app = QApplication([])
    w = MainWindow()
    w.show()
    app.exec()

if __name__ == "__main__":
    main()
