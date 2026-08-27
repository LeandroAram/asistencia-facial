import sys

from PySide6.QtWidgets import QApplication

from src.ui.login import LoginWindow


def main():
    app = QApplication(sys.argv)

    ventana = LoginWindow()
    ventana.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()