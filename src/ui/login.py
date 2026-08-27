from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QMessageBox
)

from src.database.conexion import validar_usuario


class LoginWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sistema de Asistencia Facial")
        self.setFixedSize(400, 300)

        titulo = QLabel("Inicio de Sesión")

        self.usuario_input = QLineEdit()
        self.usuario_input.setPlaceholderText(
            "Usuario, correo, DNI o CUIL"
        )

        self.contrasenia_input = QLineEdit()
        self.contrasenia_input.setPlaceholderText("Contraseña")
        self.contrasenia_input.setEchoMode(QLineEdit.Password)

        self.boton_ingresar = QPushButton("Ingresar")
        self.boton_ingresar.clicked.connect(self.iniciar_sesion)

        layout = QVBoxLayout()
        layout.addWidget(titulo)
        layout.addWidget(self.usuario_input)
        layout.addWidget(self.contrasenia_input)
        layout.addWidget(self.boton_ingresar)

        self.setLayout(layout)

    def iniciar_sesion(self):

        identificador = self.usuario_input.text().strip()
        contrasenia = self.contrasenia_input.text()

        if not identificador or not contrasenia:
            QMessageBox.warning(
                self,
                "Campos incompletos",
                "Ingrese usuario y contraseña."
            )
            return

        usuario = validar_usuario(
            identificador,
            contrasenia
        )

        if usuario:
            QMessageBox.information(
                self,
                "Acceso correcto",
                f"Bienvenido {usuario[1]}"
            )
        else:
            QMessageBox.critical(
                self,
                "Acceso denegado",
                "Usuario o contraseña incorrectos."
            )