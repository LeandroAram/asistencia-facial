from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QMessageBox
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from src.database.conexion import validar_usuario
from src.ui.main_window import MainWindow


class LoginWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.ventana_principal = None

        # ====================================================
        # VENTANA
        # ====================================================

        self.setWindowTitle(
            "Sistema de Asistencia Facial - Iniciar Sesión"
        )

        self.resize(
            1100,
            700
        )

        self.setMinimumSize(
            950,
            620
        )

        # ====================================================
        # ESTILO GENERAL
        # ====================================================

        self.setStyleSheet("""
            QWidget {
                background-color: #08111f;
                color: white;
                font-family: "Segoe UI";
            }

            QFrame#panelIzquierdo {
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:1, y2:1,
                    stop:0 #0f2550,
                    stop:0.5 #123b78,
                    stop:1 #2563eb
                );
                border-radius: 22px;
            }

            QLabel#logoGrande {
                color: white;
                font-size: 36px;
                font-weight: 900;
            }

            QLabel#descripcion {
                color: #dbeafe;
                font-size: 15px;
            }

            QLabel#tituloLogin {
                color: white;
                font-size: 31px;
                font-weight: 800;
            }

            QLabel#subtituloLogin {
                color: #94a3b8;
                font-size: 14px;
            }

            QLabel#campoTitulo {
                color: #cbd5e1;
                font-size: 13px;
                font-weight: 600;
            }

            QLineEdit {
                background-color: #101b2d;
                color: white;
                border: 1px solid #30425d;
                border-radius: 11px;
                padding: 13px 15px;
                font-size: 14px;
                min-height: 25px;
            }

            QLineEdit:focus {
                border: 2px solid #3b82f6;
                background-color: #0e192a;
            }

            QLineEdit::placeholder {
                color: #64748b;
            }

            QPushButton#loginButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 11px;
                padding: 13px;
                font-size: 15px;
                font-weight: 700;
            }

            QPushButton#loginButton:hover {
                background-color: #3b82f6;
            }

            QPushButton#loginButton:pressed {
                background-color: #1d4ed8;
            }

            QPushButton#mostrarButton {
                background-color: transparent;
                color: #60a5fa;
                border: none;
                font-size: 12px;
                font-weight: 600;
                padding: 5px;
            }

            QPushButton#mostrarButton:hover {
                color: #93c5fd;
            }

            QLabel#seguridad {
                color: #64748b;
                font-size: 11px;
            }

            QFrame#loginCard {
                background-color: #0d1728;
                border: 1px solid #1e304a;
                border-radius: 20px;
            }
        """)

        # ====================================================
        # LAYOUT PRINCIPAL
        # ====================================================

        layout_principal = QHBoxLayout(
            self
        )

        layout_principal.setContentsMargins(
            35,
            35,
            35,
            35
        )

        layout_principal.setSpacing(
            35
        )

        # ====================================================
        # PANEL IZQUIERDO
        # ====================================================

        panel_izquierdo = QFrame()

        panel_izquierdo.setObjectName(
            "panelIzquierdo"
        )

        panel_izquierdo.setMinimumWidth(
            470
        )

        layout_izquierdo = QVBoxLayout(
            panel_izquierdo
        )

        layout_izquierdo.setContentsMargins(
            45,
            55,
            45,
            55
        )

        # ----------------------------------------------------
        # LOGO
        # ----------------------------------------------------

        logo = QLabel(
            "◉  FACE CHECK"
        )

        logo.setObjectName(
            "logoGrande"
        )

        layout_izquierdo.addWidget(
            logo
        )

        layout_izquierdo.addSpacing(
            20
        )

        # ----------------------------------------------------
        # TEXTO PRINCIPAL
        # ----------------------------------------------------

        titulo_sistema = QLabel(
            "Sistema de\nAsistencia Facial"
        )

        titulo_sistema.setFont(
            QFont(
                "Segoe UI",
                30,
                QFont.Bold
            )
        )

        titulo_sistema.setStyleSheet("""
            color: white;
        """)

        layout_izquierdo.addWidget(
            titulo_sistema
        )

        layout_izquierdo.addSpacing(
            18
        )

        descripcion = QLabel(
            "Gestión de asistencia mediante captura facial,\n"
            "registro de alumnos y control de jornadas."
        )

        descripcion.setObjectName(
            "descripcion"
        )

        descripcion.setWordWrap(
            True
        )

        layout_izquierdo.addWidget(
            descripcion
        )

        layout_izquierdo.addStretch()

        # ----------------------------------------------------
        # CARACTERÍSTICAS
        # ----------------------------------------------------

        caracteristicas = QLabel(
            "✓  Captura mediante webcam\n\n"
            "✓  Registro de alumnos\n\n"
            "✓  Configuración de jornadas\n\n"
            "✓  Gestión segura de la información"
        )

        caracteristicas.setStyleSheet("""
            color: #e0ecff;
            font-size: 14px;
            font-weight: 500;
        """)

        layout_izquierdo.addWidget(
            caracteristicas
        )

        layout_izquierdo.addStretch()

        pie_izquierdo = QLabel(
            "Proyecto de Reconocimiento Visual · 2026"
        )

        pie_izquierdo.setStyleSheet("""
            color: #bfdbfe;
            font-size: 11px;
        """)

        layout_izquierdo.addWidget(
            pie_izquierdo
        )

        # ====================================================
        # PANEL DERECHO
        # ====================================================

        panel_derecho = QWidget()

        layout_derecho = QVBoxLayout(
            panel_derecho
        )

        layout_derecho.setContentsMargins(
            25,
            40,
            25,
            40
        )

        layout_derecho.addStretch()

        # ====================================================
        # TARJETA LOGIN
        # ====================================================

        login_card = QFrame()

        login_card.setObjectName(
            "loginCard"
        )

        login_card.setMaximumWidth(
            470
        )

        layout_login = QVBoxLayout(
            login_card
        )

        layout_login.setContentsMargins(
            38,
            38,
            38,
            38
        )

        layout_login.setSpacing(
            12
        )

        # ----------------------------------------------------
        # ENCABEZADO
        # ----------------------------------------------------

        bienvenida = QLabel(
            "Bienvenido"
        )

        bienvenida.setObjectName(
            "tituloLogin"
        )

        subtitulo = QLabel(
            "Ingresá tus credenciales para acceder al sistema."
        )

        subtitulo.setObjectName(
            "subtituloLogin"
        )

        subtitulo.setWordWrap(
            True
        )

        layout_login.addWidget(
            bienvenida
        )

        layout_login.addWidget(
            subtitulo
        )

        layout_login.addSpacing(
            25
        )

        # ====================================================
        # USUARIO
        # ====================================================

        usuario_label = QLabel(
            "Usuario"
        )

        usuario_label.setObjectName(
            "campoTitulo"
        )

        self.usuario_input = QLineEdit()

        self.usuario_input.setPlaceholderText(
            "Usuario, correo, DNI o CUIL"
        )

        self.usuario_input.setClearButtonEnabled(
            True
        )

        layout_login.addWidget(
            usuario_label
        )

        layout_login.addWidget(
            self.usuario_input
        )

        layout_login.addSpacing(
            10
        )

        # ====================================================
        # CONTRASEÑA
        # ====================================================

        contrasena_label = QLabel(
            "Contraseña"
        )

        contrasena_label.setObjectName(
            "campoTitulo"
        )

        self.contrasena_input = QLineEdit()

        self.contrasena_input.setPlaceholderText(
            "Ingresá tu contraseña"
        )

        self.contrasena_input.setEchoMode(
            QLineEdit.Password
        )

        layout_login.addWidget(
            contrasena_label
        )

        layout_login.addWidget(
            self.contrasena_input
        )

        # ====================================================
        # MOSTRAR CONTRASEÑA
        # ====================================================

        layout_mostrar = QHBoxLayout()

        layout_mostrar.addStretch()

        self.boton_mostrar = QPushButton(
            "Mostrar contraseña"
        )

        self.boton_mostrar.setObjectName(
            "mostrarButton"
        )

        self.boton_mostrar.setCheckable(
            True
        )

        self.boton_mostrar.clicked.connect(
            self.alternar_contrasena
        )

        layout_mostrar.addWidget(
            self.boton_mostrar
        )

        layout_login.addLayout(
            layout_mostrar
        )

        layout_login.addSpacing(
            12
        )

        # ====================================================
        # BOTÓN INGRESAR
        # ====================================================

        self.boton_ingresar = QPushButton(
            "Ingresar al sistema  →"
        )

        self.boton_ingresar.setObjectName(
            "loginButton"
        )

        self.boton_ingresar.setMinimumHeight(
            52
        )

        self.boton_ingresar.clicked.connect(
            self.iniciar_sesion
        )

        layout_login.addWidget(
            self.boton_ingresar
        )

        layout_login.addSpacing(
            15
        )

        seguridad = QLabel(
            "🔒  Acceso restringido a usuarios autorizados"
        )

        seguridad.setObjectName(
            "seguridad"
        )

        seguridad.setAlignment(
            Qt.AlignCenter
        )

        layout_login.addWidget(
            seguridad
        )

        # ====================================================
        # CENTRAR TARJETA
        # ====================================================

        contenedor_card = QHBoxLayout()

        contenedor_card.addStretch()

        contenedor_card.addWidget(
            login_card
        )

        contenedor_card.addStretch()

        layout_derecho.addLayout(
            contenedor_card
        )

        layout_derecho.addStretch()

        # ====================================================
        # AGREGAR PANELES
        # ====================================================

        layout_principal.addWidget(
            panel_izquierdo,
            5
        )

        layout_principal.addWidget(
            panel_derecho,
            5
        )

        # ====================================================
        # ENTER
        # ====================================================

        self.usuario_input.returnPressed.connect(
            self.contrasena_input.setFocus
        )

        self.contrasena_input.returnPressed.connect(
            self.iniciar_sesion
        )

        self.usuario_input.setFocus()

    # ========================================================
    # MOSTRAR / OCULTAR CONTRASEÑA
    # ========================================================

    def alternar_contrasena(self):

        if self.boton_mostrar.isChecked():

            self.contrasena_input.setEchoMode(
                QLineEdit.Normal
            )

            self.boton_mostrar.setText(
                "Ocultar contraseña"
            )

        else:

            self.contrasena_input.setEchoMode(
                QLineEdit.Password
            )

            self.boton_mostrar.setText(
                "Mostrar contraseña"
            )

    # ========================================================
    # LOGIN
    # ========================================================

    def iniciar_sesion(self):

        identificador = (
            self.usuario_input
            .text()
            .strip()
        )

        contrasena = (
            self.contrasena_input
            .text()
        )

        # ----------------------------------------------------
        # CAMPOS VACÍOS
        # ----------------------------------------------------

        if not identificador or not contrasena:

            QMessageBox.warning(
                self,
                "Datos incompletos",
                "Ingrese su usuario y contraseña."
            )

            return

        # ----------------------------------------------------
        # VALIDAR EN BASE DE DATOS
        # ----------------------------------------------------

        try:

            usuario = validar_usuario(
                identificador,
                contrasena
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Error de conexión",
                (
                    "No se pudo consultar la base de datos.\n\n"
                    f"{error}"
                )
            )

            return

        # ----------------------------------------------------
        # LOGIN CORRECTO
        # ----------------------------------------------------

        if usuario:

            self.ventana_principal = MainWindow(
                usuario[1]
            )

            self.ventana_principal.show()

            self.close()

        # ----------------------------------------------------
        # LOGIN INCORRECTO
        # ----------------------------------------------------

        else:

            QMessageBox.warning(
                self,
                "Acceso denegado",
                "Usuario o contraseña incorrectos."
            )

            self.contrasena_input.clear()

            self.contrasena_input.setFocus()