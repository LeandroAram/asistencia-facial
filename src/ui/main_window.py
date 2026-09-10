from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QPushButton,
    QLabel,
    QLineEdit,
    QHBoxLayout,
    QVBoxLayout,
    QFormLayout,
    QStackedWidget,
    QMessageBox,
    QFrame
)

from PySide6.QtCore import (
    Qt,
    QDate,
    QRegularExpression
)

from PySide6.QtGui import (
    QRegularExpressionValidator
)

from src.ui.registro_alumno import RegistroAlumnoWidget


class MainWindow(QMainWindow):

    def __init__(self, nombre_usuario):
        super().__init__()

        self.nombre_usuario = nombre_usuario

        self.setWindowTitle(
            "Sistema de Asistencia Facial"
        )

        self.resize(1100, 700)

        # ====================================================
        # CONTENEDOR PRINCIPAL
        # ====================================================

        contenedor_principal = QWidget()
        self.setCentralWidget(contenedor_principal)

        layout_principal = QHBoxLayout()
        contenedor_principal.setLayout(layout_principal)

        # ====================================================
        # MENÚ LATERAL
        # ====================================================

        menu_lateral = QWidget()
        menu_lateral.setFixedWidth(260)

        layout_menu = QVBoxLayout()
        menu_lateral.setLayout(layout_menu)

        titulo_sistema = QLabel(
            "Sistema de Asistencia Facial"
        )

        titulo_sistema.setAlignment(
            Qt.AlignCenter
        )

        usuario_label = QLabel(
            f"Bienvenido, {self.nombre_usuario}"
        )

        usuario_label.setAlignment(
            Qt.AlignCenter
        )

        self.boton_asistencia = QPushButton(
            "Asistencia por Captura Facial"
        )

        self.boton_jornada = QPushButton(
            "Configuración de la Jornada"
        )

        self.boton_alumno = QPushButton(
            "Registrar Alumno"
        )

        layout_menu.addWidget(
            titulo_sistema
        )

        layout_menu.addWidget(
            usuario_label
        )

        layout_menu.addSpacing(30)

        layout_menu.addWidget(
            self.boton_asistencia
        )

        layout_menu.addWidget(
            self.boton_jornada
        )

        layout_menu.addWidget(
            self.boton_alumno
        )

        layout_menu.addStretch()

        # ====================================================
        # ÁREA DE CONTENIDO
        # ====================================================

        self.paginas = QStackedWidget()

        # ====================================================
        # PÁGINA 1 - ASISTENCIA POR CAPTURA FACIAL
        # ====================================================

        self.pagina_asistencia = QWidget()

        layout_asistencia = QVBoxLayout()

        self.pagina_asistencia.setLayout(
            layout_asistencia
        )

        titulo_asistencia = QLabel(
            "Asistencia por Captura Facial"
        )

        titulo_asistencia.setAlignment(
            Qt.AlignCenter
        )

        titulo_asistencia.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 20px;
        """)

        layout_asistencia.addWidget(
            titulo_asistencia
        )

        # ----------------------------------------------------
        # BOTONES DE CÁMARA
        # ----------------------------------------------------

        layout_botones_camara = QHBoxLayout()

        self.boton_abrir_camara = QPushButton(
            "Abrir Cámara"
        )

        self.boton_cerrar_camara = QPushButton(
            "Cerrar Cámara"
        )

        self.boton_abrir_camara.setMinimumHeight(
            40
        )

        self.boton_cerrar_camara.setMinimumHeight(
            40
        )

        # Estado inicial:
        # cámara cerrada
        self.boton_abrir_camara.setEnabled(
            True
        )

        self.boton_cerrar_camara.setEnabled(
            False
        )

        layout_botones_camara.addWidget(
            self.boton_abrir_camara
        )

        layout_botones_camara.addWidget(
            self.boton_cerrar_camara
        )

        layout_asistencia.addLayout(
            layout_botones_camara
        )

        layout_asistencia.addSpacing(
            20
        )

        # ----------------------------------------------------
        # PANEL DE CÁMARA
        # ----------------------------------------------------
        # En este incremento debe quedar vacío.
        # En el siguiente se mostrará el video.

        self.panel_camara = QLabel("")

        self.panel_camara.setAlignment(
            Qt.AlignCenter
        )

        self.panel_camara.setMinimumSize(
            600,
            400
        )

        self.panel_camara.setFrameShape(
            QFrame.Box
        )

        self.panel_camara.setStyleSheet("""
            QLabel {
                border: 2px dashed #666666;
                border-radius: 8px;
            }
        """)

        layout_asistencia.addWidget(
            self.panel_camara,
            alignment=Qt.AlignCenter
        )

        layout_asistencia.addStretch()

        # ====================================================
        # PÁGINA 2 - CONFIGURACIÓN DE LA JORNADA
        # ====================================================

        self.pagina_jornada = QWidget()

        layout_jornada_principal = QVBoxLayout()

        self.pagina_jornada.setLayout(
            layout_jornada_principal
        )

        titulo_jornada = QLabel(
            "Configuración de la Jornada"
        )

        titulo_jornada.setAlignment(
            Qt.AlignCenter
        )

        titulo_jornada.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 20px;
        """)

        layout_jornada_principal.addWidget(
            titulo_jornada
        )

        layout_jornada_principal.addSpacing(
            30
        )

        formulario_jornada = QFormLayout()

        # ----------------------------------------------------
        # FECHA
        # ----------------------------------------------------

        self.fecha_label = QLabel(
            QDate.currentDate().toString(
                "dd/MM/yyyy"
            )
        )

        formulario_jornada.addRow(
            "Fecha:",
            self.fecha_label
        )

        # ----------------------------------------------------
        # VALIDACIÓN HH:MM
        # ----------------------------------------------------

        expresion_hora = QRegularExpression(
            r"^([01][0-9]|2[0-3]):[0-5][0-9]$"
        )

        validador_hora_entrada = (
            QRegularExpressionValidator(
                expresion_hora,
                self
            )
        )

        validador_hora_salida = (
            QRegularExpressionValidator(
                expresion_hora,
                self
            )
        )

        # ----------------------------------------------------
        # HORARIO DE ENTRADA
        # ----------------------------------------------------

        self.horario_entrada_input = QLineEdit()

        self.horario_entrada_input.setPlaceholderText(
            "--:--"
        )

        self.horario_entrada_input.setMaxLength(
            5
        )

        self.horario_entrada_input.setValidator(
            validador_hora_entrada
        )

        formulario_jornada.addRow(
            "Horario de entrada:",
            self.horario_entrada_input
        )

        # ----------------------------------------------------
        # HORARIO DE SALIDA
        # ----------------------------------------------------

        self.horario_salida_input = QLineEdit()

        self.horario_salida_input.setPlaceholderText(
            "--:--"
        )

        self.horario_salida_input.setMaxLength(
            5
        )

        self.horario_salida_input.setValidator(
            validador_hora_salida
        )

        formulario_jornada.addRow(
            "Horario de salida:",
            self.horario_salida_input
        )

        # ----------------------------------------------------
        # CÁTEDRA
        # ----------------------------------------------------

        self.catedra_input = QLineEdit()

        self.catedra_input.setPlaceholderText(
            "Ingrese la cátedra"
        )

        formulario_jornada.addRow(
            "Cátedra:",
            self.catedra_input
        )

        layout_jornada_principal.addLayout(
            formulario_jornada
        )

        layout_jornada_principal.addStretch()

        # ====================================================
        # PÁGINA 3 - REGISTRAR ALUMNO
        # ====================================================

        self.pagina_alumno = (
            RegistroAlumnoWidget()
        )

        # ====================================================
        # AGREGAR PÁGINAS
        # ====================================================

        self.paginas.addWidget(
            self.pagina_asistencia
        )

        self.paginas.addWidget(
            self.pagina_jornada
        )

        self.paginas.addWidget(
            self.pagina_alumno
        )

        # La primera opción debe aparecer
        # al iniciar sesión.
        self.paginas.setCurrentIndex(0)

        # ====================================================
        # BOTONES DEL MENÚ
        # ====================================================

        self.boton_asistencia.clicked.connect(
            lambda:
            self.paginas.setCurrentIndex(0)
        )

        self.boton_jornada.clicked.connect(
            lambda:
            self.paginas.setCurrentIndex(1)
        )

        self.boton_alumno.clicked.connect(
            lambda:
            self.paginas.setCurrentIndex(2)
        )

        # ====================================================
        # BOTONES DE CÁMARA
        # ====================================================

        self.boton_abrir_camara.clicked.connect(
            self.abrir_camara
        )

        self.boton_cerrar_camara.clicked.connect(
            self.cerrar_camara
        )

        # ====================================================
        # AGREGAR MENÚ Y CONTENIDO
        # ====================================================

        layout_principal.addWidget(
            menu_lateral
        )

        layout_principal.addWidget(
            self.paginas
        )

    # ========================================================
    # COMPROBAR CONFIGURACIÓN DE JORNADA
    # ========================================================

    def jornada_configurada(self):

        horario_entrada = (
            self.horario_entrada_input
            .text()
            .strip()
        )

        horario_salida = (
            self.horario_salida_input
            .text()
            .strip()
        )

        catedra = (
            self.catedra_input
            .text()
            .strip()
        )

        if (
            horario_entrada == ""
            or horario_salida == ""
            or catedra == ""
        ):
            return False

        return True

    # ========================================================
    # ABRIR CÁMARA
    # ========================================================

    def abrir_camara(self):

        # Primero comprobar que la Jornada
        # esté configurada.
        if not self.jornada_configurada():

            QMessageBox.critical(
                self,
                "Jornada no configurada",
                (
                    "Antes de abrir la Cámara del Sistema "
                    "debe configurarse los parámetros de la "
                    "Jornada (segunda opción del Menú Lateral)."
                )
            )

            # Si la Jornada no está configurada,
            # los botones no cambian.
            return

        # En este incremento NO se abre
        # realmente la webcam.
        #
        # Solamente alternamos los botones.

        self.boton_abrir_camara.setEnabled(
            False
        )

        self.boton_cerrar_camara.setEnabled(
            True
        )

        # El panel permanece vacío.
        self.panel_camara.clear()

    # ========================================================
    # CERRAR CÁMARA
    # ========================================================

    def cerrar_camara(self):

        self.boton_abrir_camara.setEnabled(
            True
        )

        self.boton_cerrar_camara.setEnabled(
            False
        )

        # El panel continúa vacío.
        self.panel_camara.clear()