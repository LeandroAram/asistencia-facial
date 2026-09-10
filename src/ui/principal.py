from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout
)


class VentanaPrincipal(QWidget):

    def __init__(self, nombre_usuario):
        super().__init__()

        self.setWindowTitle("Sistema de Asistencia Facial")
        self.setFixedSize(600, 400)

        titulo = QLabel(f"Bienvenido, {nombre_usuario}")

        layout = QVBoxLayout()
        layout.addWidget(titulo)

        self.setLayout(layout)