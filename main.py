import sys
from app import WordApp
from PySide6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WordApp()
    window.show()
    sys.exit(app.exec())