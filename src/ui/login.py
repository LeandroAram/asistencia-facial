from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QMessageBox
)

from src.database.conexion import validar_usuario
from src.ui.main_window import MainWindow


class LoginWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "Sistema de Asistencia Facial"
        )

        self.setFixedSize(
            400,
            300
        )

        # ====================================================
        # TÍTULO
        # ====================================================

        titulo = QLabel(
            "Inicio de Sesión"
        )

        # ====================================================
        # USUARIO
        # ====================================================

        self.usuario_input = QLineEdit()

        self.usuario_input.setPlaceholderText(
            "Usuario, correo, DNI o CUIL"
        )

        # Si se presiona Enter estando en usuario,
        # pasa automáticamente a contraseña.
        self.usuario_input.returnPressed.connect(
            self.contrasenia_input_focus
        )

        # ====================================================
        # CONTRASEÑA
        # ====================================================

        self.contrasenia_input = QLineEdit()

        self.contrasenia_input.setPlaceholderText(
            "Contraseña"
        )

        self.contrasenia_input.setEchoMode(
            QLineEdit.Password
        )

        # Si se presiona Enter después de escribir
        # la contraseña, inicia sesión.
        self.contrasenia_input.returnPressed.connect(
            self.iniciar_sesion
        )

        # ====================================================
        # BOTÓN INGRESAR
        # ====================================================

        self.boton_ingresar = QPushButton(
            "Ingresar"
        )

        self.boton_ingresar.clicked.connect(
            self.iniciar_sesion
        )

        # ====================================================
        # LAYOUT
        # ====================================================

        layout = QVBoxLayout()

        layout.addWidget(
            titulo
        )

        layout.addWidget(
            self.usuario_input
        )

        layout.addWidget(
            self.contrasenia_input
        )

        layout.addWidget(
            self.boton_ingresar
        )

        self.setLayout(
            layout
        )

        # El cursor comienza directamente
        # en el campo usuario.
        self.usuario_input.setFocus()

    # ========================================================
    # PASAR DEL USUARIO A LA CONTRASEÑA CON ENTER
    # ========================================================

    def contrasenia_input_focus(self):

        self.contrasenia_input.setFocus()

    # ========================================================
    # INICIAR SESIÓN
    # ========================================================

    def iniciar_sesion(self):

        identificador = (
            self.usuario_input
            .text()
            .strip()
        )

        contrasenia = (
            self.contrasenia_input
            .text()
        )

        # ----------------------------------------------------
        # CAMPOS VACÍOS
        # ----------------------------------------------------

        if not identificador or not contrasenia:

            QMessageBox.warning(
                self,
                "Campos incompletos",
                "Ingrese usuario y contraseña."
            )

            return

        # ----------------------------------------------------
        # VALIDAR CONTRA POSTGRESQL
        # ----------------------------------------------------

        usuario = validar_usuario(
            identificador,
            contrasenia
        )

        # ----------------------------------------------------
        # ACCESO CORRECTO
        # ----------------------------------------------------

        if usuario:

            self.ventana_principal = MainWindow(
                usuario[1]
            )

            self.ventana_principal.show()

            self.close()

        # ----------------------------------------------------
        # ACCESO INCORRECTO
        # ----------------------------------------------------

        else:

            QMessageBox.critical(
                self,
                "Acceso denegado",
                "Usuario o contraseña incorrectos."
            )

            self.contrasenia_input.clear()

            self.contrasenia_input.setFocus()