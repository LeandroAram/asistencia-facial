import cv2

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
    QFrame,
    QButtonGroup
)

from PySide6.QtCore import (
    Qt,
    QDate,
    QRegularExpression,
    QTimer
)

from PySide6.QtGui import (
    QRegularExpressionValidator,
    QImage,
    QPixmap
)

from src.ui.registro_alumno import RegistroAlumnoWidget
from src.camera.camera_manager import CameraManager


class MainWindow(QMainWindow):

    def __init__(self, nombre_usuario):
        super().__init__()

        self.nombre_usuario = nombre_usuario

        # ====================================================
        # CÁMARA COMPARTIDA
        # ====================================================

        self.camara_abierta = False

        self.camera = CameraManager()

        self.timer_camara = QTimer(self)

        self.timer_camara.timeout.connect(
            self.actualizar_video_camara
        )

        # ====================================================
        # VENTANA
        # ====================================================

        self.setWindowTitle(
            "Sistema de Asistencia Facial"
        )

        self.resize(
            1400,
            850
        )

        self.setMinimumSize(
            1200,
            750
        )

        # ====================================================
        # ESTILO GENERAL
        # ====================================================

        self.aplicar_estilos()

        # ====================================================
        # CONTENEDOR PRINCIPAL
        # ====================================================

        contenedor = QWidget()
        contenedor.setObjectName("root")

        self.setCentralWidget(contenedor)

        layout_principal = QHBoxLayout(contenedor)

        layout_principal.setContentsMargins(
            0, 0, 0, 0
        )

        layout_principal.setSpacing(0)

        # ====================================================
        # SIDEBAR
        # ====================================================

        sidebar = QFrame()

        sidebar.setObjectName(
            "sidebar"
        )

        sidebar.setFixedWidth(
            280
        )

        layout_sidebar = QVBoxLayout(
            sidebar
        )

        layout_sidebar.setContentsMargins(
            22, 30, 22, 25
        )

        layout_sidebar.setSpacing(
            10
        )

        # ====================================================
        # LOGO
        # ====================================================

        logo = QLabel(
            "◉  FACE CHECK"
        )

        logo.setObjectName(
            "logo"
        )

        subtitulo_logo = QLabel(
            "Sistema de Asistencia Facial"
        )

        subtitulo_logo.setObjectName(
            "logoSubtitulo"
        )

        layout_sidebar.addWidget(
            logo
        )

        layout_sidebar.addWidget(
            subtitulo_logo
        )

        layout_sidebar.addSpacing(
            35
        )

        # ====================================================
        # TEXTO MENÚ
        # ====================================================

        menu_label = QLabel(
            "MENÚ PRINCIPAL"
        )

        menu_label.setObjectName(
            "menuLabel"
        )

        layout_sidebar.addWidget(
            menu_label
        )

        layout_sidebar.addSpacing(
            5
        )

        # ====================================================
        # BOTONES NAVEGACIÓN
        # ====================================================

        self.boton_asistencia = self.crear_boton_menu(
            "◉   Asistencia Facial"
        )

        self.boton_jornada = self.crear_boton_menu(
            "◷   Configurar Jornada"
        )

        self.boton_alumno = self.crear_boton_menu(
            "＋   Registrar Alumno"
        )

        self.grupo_menu = QButtonGroup(
            self
        )

        self.grupo_menu.setExclusive(
            True
        )

        self.grupo_menu.addButton(
            self.boton_asistencia
        )

        self.grupo_menu.addButton(
            self.boton_jornada
        )

        self.grupo_menu.addButton(
            self.boton_alumno
        )

        self.boton_asistencia.setChecked(
            True
        )

        layout_sidebar.addWidget(
            self.boton_asistencia
        )

        layout_sidebar.addWidget(
            self.boton_jornada
        )

        layout_sidebar.addWidget(
            self.boton_alumno
        )

        layout_sidebar.addStretch()

        # ====================================================
        # USUARIO ABAJO
        # ====================================================

        usuario_card = QFrame()

        usuario_card.setObjectName(
            "usuarioCard"
        )

        layout_usuario = QVBoxLayout(
            usuario_card
        )

        etiqueta_sesion = QLabel(
            "SESIÓN ACTIVA"
        )

        etiqueta_sesion.setObjectName(
            "usuarioTitulo"
        )

        nombre_usuario = QLabel(
            f"👤  {self.nombre_usuario}"
        )

        nombre_usuario.setObjectName(
            "usuarioNombre"
        )

        layout_usuario.addWidget(
            etiqueta_sesion
        )

        layout_usuario.addWidget(
            nombre_usuario
        )

        layout_sidebar.addWidget(
            usuario_card
        )

        # ====================================================
        # CONTENIDO DERECHO
        # ====================================================

        contenido = QFrame()

        contenido.setObjectName(
            "contenido"
        )

        layout_contenido = QVBoxLayout(
            contenido
        )

        layout_contenido.setContentsMargins(
            35, 25, 35, 25
        )

        layout_contenido.setSpacing(
            20
        )

        # ====================================================
        # HEADER
        # ====================================================

        header = QHBoxLayout()

        bloque_titulo = QVBoxLayout()

        self.titulo_pagina = QLabel(
            "Asistencia por Captura Facial"
        )

        self.titulo_pagina.setObjectName(
            "tituloPagina"
        )

        self.subtitulo_pagina = QLabel(
            "Controle la cámara y gestione la asistencia en tiempo real."
        )

        self.subtitulo_pagina.setObjectName(
            "subtituloPagina"
        )

        bloque_titulo.addWidget(
            self.titulo_pagina
        )

        bloque_titulo.addWidget(
            self.subtitulo_pagina
        )

        header.addLayout(
            bloque_titulo
        )

        header.addStretch()

        sistema_estado = QLabel(
            "● SISTEMA ACTIVO"
        )

        sistema_estado.setObjectName(
            "sistemaActivo"
        )

        header.addWidget(
            sistema_estado
        )

        layout_contenido.addLayout(
            header
        )

        # ====================================================
        # STACK
        # ====================================================

        self.paginas = QStackedWidget()

        layout_contenido.addWidget(
            self.paginas
        )

        # ====================================================
        # PÁGINA ASISTENCIA
        # ====================================================

        self.crear_pagina_asistencia()

        # ====================================================
        # PÁGINA JORNADA
        # ====================================================

        self.crear_pagina_jornada()

        # ====================================================
        # PÁGINA REGISTRAR ALUMNO
        # ====================================================

        self.pagina_alumno = RegistroAlumnoWidget(
            self.camera
        )

        self.paginas.addWidget(
            self.pagina_alumno
        )

        self.pagina_alumno.alumno_registrado.connect(
            self.cerrar_camara
        )

        # ====================================================
        # AGREGAR SIDEBAR + CONTENIDO
        # ====================================================

        layout_principal.addWidget(
            sidebar
        )

        layout_principal.addWidget(
            contenido
        )

        # ====================================================
        # NAVEGACIÓN
        # ====================================================

        self.boton_asistencia.clicked.connect(
            self.ir_asistencia
        )

        self.boton_jornada.clicked.connect(
            self.ir_jornada
        )

        self.boton_alumno.clicked.connect(
            self.ir_registro_alumno
        )

        # ====================================================
        # BOTONES CÁMARA
        # ====================================================

        self.boton_abrir_camara.clicked.connect(
            self.abrir_camara
        )

        self.boton_cerrar_camara.clicked.connect(
            self.cerrar_camara
        )

        self.paginas.setCurrentIndex(
            0
        )

        self.actualizar_estado_camara()

    # ========================================================
    # ESTILOS
    # ========================================================

    def aplicar_estilos(self):

        self.setStyleSheet("""

            /* ==============================
               GENERAL
            ============================== */

            QMainWindow {
                background-color: #08111f;
            }

            QWidget#root {
                background-color: #08111f;
            }

            QFrame#contenido {
                background-color: #0b1424;
            }

            QLabel {
                color: #e5edf8;
                font-family: "Segoe UI";
            }

            /* ==============================
               SIDEBAR
            ============================== */

            QFrame#sidebar {
                background: qlineargradient(
                    x1:0, y1:0,
                    x2:0, y2:1,
                    stop:0 #0f1e38,
                    stop:1 #081426
                );

                border-right: 1px solid #21324d;
            }

            QLabel#logo {
                color: #60a5fa;
                font-size: 23px;
                font-weight: 800;
            }

            QLabel#logoSubtitulo {
                color: #94a3b8;
                font-size: 12px;
            }

            QLabel#menuLabel {
                color: #64748b;
                font-size: 11px;
                font-weight: bold;
                letter-spacing: 1px;
            }

            QPushButton[nav="true"] {

                background-color: transparent;

                color: #a9b8ce;

                border: none;

                border-radius: 10px;

                text-align: left;

                padding: 13px 16px;

                font-size: 14px;

                font-weight: 600;
            }

            QPushButton[nav="true"]:hover {

                background-color: #162742;

                color: white;
            }

            QPushButton[nav="true"]:checked {

                background-color: #2563eb;

                color: white;

                border-left: 4px solid #60a5fa;
            }

            /* ==============================
               USUARIO
            ============================== */

            QFrame#usuarioCard {

                background-color: #101f35;

                border: 1px solid #203652;

                border-radius: 12px;
            }

            QLabel#usuarioTitulo {

                color: #64748b;

                font-size: 10px;

                font-weight: bold;
            }

            QLabel#usuarioNombre {

                color: white;

                font-size: 14px;

                font-weight: 600;
            }

            /* ==============================
               HEADER
            ============================== */

            QLabel#tituloPagina {

                color: white;

                font-size: 27px;

                font-weight: 800;
            }

            QLabel#subtituloPagina {

                color: #94a3b8;

                font-size: 13px;
            }

            QLabel#sistemaActivo {

                color: #34d399;

                background-color: #0c2b28;

                border: 1px solid #145e52;

                border-radius: 12px;

                padding: 7px 12px;

                font-size: 11px;

                font-weight: bold;
            }

            /* ==============================
               TARJETAS
            ============================== */

            QFrame[card="true"] {

                background-color: #101b2d;

                border: 1px solid #22324a;

                border-radius: 16px;
            }

            QLabel[cardTitle="true"] {

                color: #8191a9;

                font-size: 11px;

                font-weight: 700;
            }

            QLabel[cardValue="true"] {

                color: white;

                font-size: 17px;

                font-weight: 700;
            }

            /* ==============================
               CÁMARA
            ============================== */

            QLabel#cameraPanel {

                background-color: #050a12;

                border: 2px solid #243954;

                border-radius: 18px;

                color: #53657d;

                font-size: 17px;
            }

            /* ==============================
               BOTONES
            ============================== */

            QPushButton#botonAbrir {

                background-color: #2563eb;

                color: white;

                border: none;

                border-radius: 10px;

                padding: 12px 20px;

                font-weight: 700;

                font-size: 14px;
            }

            QPushButton#botonAbrir:hover {

                background-color: #3b82f6;
            }

            QPushButton#botonCerrar {

                background-color: #b42336;

                color: white;

                border: none;

                border-radius: 10px;

                padding: 12px 20px;

                font-weight: 700;

                font-size: 14px;
            }

            QPushButton#botonCerrar:hover {

                background-color: #dc3545;
            }

            QPushButton:disabled {

                background-color: #172235;

                color: #526177;

                border: 1px solid #26364e;
            }

            /* ==============================
               CAMPOS
            ============================== */

            QLineEdit,
            QDateEdit,
            QSpinBox {

                background-color: #0a1424;

                color: white;

                border: 1px solid #30425d;

                border-radius: 9px;

                padding: 9px 12px;

                min-height: 24px;

                font-size: 13px;
            }

            QLineEdit:focus,
            QDateEdit:focus,
            QSpinBox:focus {

                border: 1px solid #3b82f6;
            }

            /* ==============================
               GROUP BOX REGISTRO
            ============================== */

            QGroupBox {

                color: #dbeafe;

                background-color: #101b2d;

                border: 1px solid #253650;

                border-radius: 12px;

                margin-top: 16px;

                padding: 18px 12px 12px 12px;

                font-size: 14px;

                font-weight: bold;
            }

            QGroupBox::title {

                subcontrol-origin: margin;

                left: 14px;

                padding: 0 6px;

                color: #60a5fa;
            }

            /* ==============================
               SCROLL
            ============================== */

            QScrollArea {

                border: none;

                background: transparent;
            }

            QScrollArea > QWidget > QWidget {

                background: transparent;
            }

            QScrollBar:vertical {

                background: #0b1424;

                width: 10px;

                border-radius: 5px;
            }

            QScrollBar::handle:vertical {

                background: #31435e;

                border-radius: 5px;

                min-height: 30px;
            }

            QScrollBar::handle:vertical:hover {

                background: #3b82f6;
            }

        """)

    # ========================================================
    # CREAR BOTÓN MENÚ
    # ========================================================

    def crear_boton_menu(self, texto):

        boton = QPushButton(texto)

        boton.setProperty(
            "nav",
            True
        )

        boton.setCheckable(
            True
        )

        boton.setMinimumHeight(
            47
        )

        return boton

    # ========================================================
    # CREAR TARJETA DE ESTADO
    # ========================================================

    def crear_tarjeta_estado(
        self,
        titulo,
        valor
    ):

        card = QFrame()

        card.setProperty(
            "card",
            True
        )

        card.setMinimumHeight(
            90
        )

        layout = QVBoxLayout(
            card
        )

        layout.setContentsMargins(
            18, 14, 18, 14
        )

        titulo_label = QLabel(
            titulo
        )

        titulo_label.setProperty(
            "cardTitle",
            True
        )

        valor_label = QLabel(
            valor
        )

        valor_label.setProperty(
            "cardValue",
            True
        )

        layout.addWidget(
            titulo_label
        )

        layout.addWidget(
            valor_label
        )

        return card, valor_label

    # ========================================================
    # CREAR PÁGINA ASISTENCIA
    # ========================================================

    def crear_pagina_asistencia(self):

        pagina = QWidget()

        layout = QVBoxLayout(
            pagina
        )

        layout.setContentsMargins(
            0, 5, 0, 0
        )

        layout.setSpacing(
            18
        )

        # ====================================================
        # TARJETAS SUPERIORES
        # ====================================================

        tarjetas = QHBoxLayout()

        card_camara, self.estado_camara_label = (
            self.crear_tarjeta_estado(
                "● ESTADO DE CÁMARA",
                "Apagada"
            )
        )

        card_jornada, self.estado_jornada_label = (
            self.crear_tarjeta_estado(
                "◷ JORNADA",
                "Sin configurar"
            )
        )

        card_fecha, self.estado_fecha_label = (
            self.crear_tarjeta_estado(
                "▣ FECHA",
                QDate.currentDate().toString(
                    "dd/MM/yyyy"
                )
            )
        )

        tarjetas.addWidget(
            card_camara
        )

        tarjetas.addWidget(
            card_jornada
        )

        tarjetas.addWidget(
            card_fecha
        )

        layout.addLayout(
            tarjetas
        )

        # ====================================================
        # BOTONES
        # ====================================================

        layout_botones = QHBoxLayout()

        self.boton_abrir_camara = QPushButton(
            "▶  Abrir Cámara"
        )

        self.boton_abrir_camara.setObjectName(
            "botonAbrir"
        )

        self.boton_cerrar_camara = QPushButton(
            "■  Cerrar Cámara"
        )

        self.boton_cerrar_camara.setObjectName(
            "botonCerrar"
        )

        self.boton_abrir_camara.setMinimumHeight(
            48
        )

        self.boton_cerrar_camara.setMinimumHeight(
            48
        )

        layout_botones.addStretch()

        layout_botones.addWidget(
            self.boton_abrir_camara
        )

        layout_botones.addWidget(
            self.boton_cerrar_camara
        )

        layout_botones.addStretch()

        layout.addLayout(
            layout_botones
        )

        # ====================================================
        # PANEL CÁMARA GRANDE
        # ====================================================

        self.panel_camara = QLabel(
            "📷\n\nLa cámara aparecerá aquí"
        )

        self.panel_camara.setObjectName(
            "cameraPanel"
        )

        self.panel_camara.setAlignment(
            Qt.AlignCenter
        )

        # GRANDE DESDE EL PRINCIPIO
        self.panel_camara.setFixedSize(
            860,
            500
        )

        layout.addWidget(
            self.panel_camara,
            alignment=Qt.AlignCenter
        )

        layout.addStretch()

        self.paginas.addWidget(
            pagina
        )

    # ========================================================
    # CREAR PÁGINA JORNADA
    # ========================================================

    def crear_pagina_jornada(self):

        pagina = QWidget()

        layout = QVBoxLayout(
            pagina
        )

        layout.setContentsMargins(
            0, 20, 0, 0
        )

        tarjeta = QFrame()

        tarjeta.setProperty(
            "card",
            True
        )

        tarjeta.setMaximumWidth(
            760
        )

        layout_tarjeta = QVBoxLayout(
            tarjeta
        )

        layout_tarjeta.setContentsMargins(
            35, 30, 35, 35
        )

        layout_tarjeta.setSpacing(
            20
        )

        titulo = QLabel(
            "Configuración de la Jornada"
        )

        titulo.setStyleSheet("""
            font-size: 22px;
            font-weight: 800;
            color: white;
        """)

        descripcion = QLabel(
            "Defina los parámetros antes de habilitar la cámara de asistencia."
        )

        descripcion.setStyleSheet("""
            color: #94a3b8;
            font-size: 13px;
        """)

        layout_tarjeta.addWidget(
            titulo
        )

        layout_tarjeta.addWidget(
            descripcion
        )

        formulario = QFormLayout()

        formulario.setVerticalSpacing(
            18
        )

        formulario.setHorizontalSpacing(
            30
        )

        # ====================================================
        # FECHA
        # ====================================================

        self.fecha_label = QLabel(
            QDate.currentDate().toString(
                "dd/MM/yyyy"
            )
        )

        self.fecha_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #60a5fa;
        """)

        formulario.addRow(
            "Fecha:",
            self.fecha_label
        )

        # ====================================================
        # HORARIOS
        # ====================================================

        expresion = QRegularExpression(
            r"^([01][0-9]|2[0-3]):[0-5][0-9]$"
        )

        self.horario_entrada_input = QLineEdit()

        self.horario_entrada_input.setPlaceholderText(
            "Ej: 08:00"
        )

        self.horario_entrada_input.setMaxLength(
            5
        )

        self.horario_entrada_input.setValidator(
            QRegularExpressionValidator(
                expresion,
                self
            )
        )

        formulario.addRow(
            "Horario de entrada:",
            self.horario_entrada_input
        )

        self.horario_salida_input = QLineEdit()

        self.horario_salida_input.setPlaceholderText(
            "Ej: 12:00"
        )

        self.horario_salida_input.setMaxLength(
            5
        )

        self.horario_salida_input.setValidator(
            QRegularExpressionValidator(
                expresion,
                self
            )
        )

        formulario.addRow(
            "Horario de salida:",
            self.horario_salida_input
        )

        self.catedra_input = QLineEdit()

        self.catedra_input.setPlaceholderText(
            "Ej: Reconocimiento Visual"
        )

        formulario.addRow(
            "Cátedra:",
            self.catedra_input
        )

        layout_tarjeta.addLayout(
            formulario
        )

        aviso = QLabel(
            "✓ Cuando complete todos los campos, la cámara quedará habilitada automáticamente."
        )

        aviso.setStyleSheet("""
            color: #34d399;
            background-color: #0c2b28;
            border: 1px solid #145e52;
            border-radius: 8px;
            padding: 10px;
        """)

        layout_tarjeta.addWidget(
            aviso
        )

        layout.addWidget(
            tarjeta,
            alignment=Qt.AlignHCenter
        )

        layout.addStretch()

        self.paginas.addWidget(
            pagina
        )

        # ====================================================
        # DETECTAR CAMBIOS
        # ====================================================

        self.horario_entrada_input.textChanged.connect(
            self.actualizar_estado_camara
        )

        self.horario_salida_input.textChanged.connect(
            self.actualizar_estado_camara
        )

        self.catedra_input.textChanged.connect(
            self.actualizar_estado_camara
        )

    # ========================================================
    # NAVEGACIÓN
    # ========================================================

    def ir_asistencia(self):

        self.paginas.setCurrentIndex(
            0
        )

        self.titulo_pagina.setText(
            "Asistencia por Captura Facial"
        )

        self.subtitulo_pagina.setText(
            "Controle la cámara y gestione la asistencia en tiempo real."
        )

        if (
            self.camara_abierta
            and self.camera.esta_abierta()
        ):

            self.timer_camara.start(
                30
            )

    def ir_jornada(self):

        # NO cerramos la webcam.
        # Solo detenemos la visualización.
        if self.timer_camara.isActive():

            self.timer_camara.stop()

        self.paginas.setCurrentIndex(
            1
        )

        self.titulo_pagina.setText(
            "Configuración de la Jornada"
        )

        self.subtitulo_pagina.setText(
            "Configure fecha, horarios y cátedra para la sesión."
        )

    def ir_registro_alumno(self):

        # IMPORTANTE:
        # la webcam permanece encendida.
        if self.timer_camara.isActive():

            self.timer_camara.stop()

        self.paginas.setCurrentIndex(
            2
        )

        self.titulo_pagina.setText(
            "Registrar Alumno"
        )

        self.subtitulo_pagina.setText(
            "Complete los datos personales y capture las fotografías del alumno."
        )

    # ========================================================
    # JORNADA CONFIGURADA
    # ========================================================

    def jornada_configurada(self):

        entrada = (
            self.horario_entrada_input
            .text()
            .strip()
        )

        salida = (
            self.horario_salida_input
            .text()
            .strip()
        )

        catedra = (
            self.catedra_input
            .text()
            .strip()
        )

        if not entrada:
            return False

        if not salida:
            return False

        if not catedra:
            return False

        if not self.horario_entrada_input.hasAcceptableInput():
            return False

        if not self.horario_salida_input.hasAcceptableInput():
            return False

        return True

    # ========================================================
    # ACTUALIZAR ESTADOS
    # ========================================================

    def actualizar_estado_camara(self):

        if self.jornada_configurada():

            self.estado_jornada_label.setText(
                "Configurada ✓"
            )

            self.estado_jornada_label.setStyleSheet(
                "color: #34d399;"
            )

        else:

            self.estado_jornada_label.setText(
                "Sin configurar"
            )

            self.estado_jornada_label.setStyleSheet(
                "color: #f59e0b;"
            )

        if not self.jornada_configurada():

            if self.camara_abierta:
                self.cerrar_camara()

            self.boton_abrir_camara.setEnabled(
                False
            )

            self.boton_cerrar_camara.setEnabled(
                False
            )

            self.estado_camara_label.setText(
                "Apagada"
            )

            self.estado_camara_label.setStyleSheet(
                "color: #94a3b8;"
            )

            return

        if self.camara_abierta:

            self.boton_abrir_camara.setEnabled(
                False
            )

            self.boton_cerrar_camara.setEnabled(
                True
            )

            self.estado_camara_label.setText(
                "Activa ●"
            )

            self.estado_camara_label.setStyleSheet(
                "color: #34d399;"
            )

        else:

            self.boton_abrir_camara.setEnabled(
                True
            )

            self.boton_cerrar_camara.setEnabled(
                False
            )

            self.estado_camara_label.setText(
                "Lista para iniciar"
            )

            self.estado_camara_label.setStyleSheet(
                "color: #60a5fa;"
            )

    # ========================================================
    # ABRIR CÁMARA
    # ========================================================

    def abrir_camara(self):

        if not self.jornada_configurada():

            QMessageBox.warning(
                self,
                "Jornada no configurada",
                "Debe configurar primero la Jornada."
            )

            return

        if not self.camera.abrir():

            QMessageBox.critical(
                self,
                "Error de cámara",
                "No se pudo abrir la webcam."
            )

            return

        self.camara_abierta = True

        self.timer_camara.start(
            30
        )

        self.actualizar_estado_camara()

    # ========================================================
    # VIDEO
    # ========================================================

    def actualizar_video_camara(self):

        frame = self.camera.leer_frame()

        if frame is None:
            return

        # MODO ESPEJO
        frame = cv2.flip(
            frame,
            1
        )

        frame_rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        alto, ancho, canales = (
            frame_rgb.shape
        )

        bytes_por_linea = (
            canales * ancho
        )

        imagen = QImage(
            frame_rgb.data,
            ancho,
            alto,
            bytes_por_linea,
            QImage.Format_RGB888
        )

        pixmap = QPixmap.fromImage(
            imagen
        )

        self.panel_camara.setPixmap(
            pixmap.scaled(
                self.panel_camara.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

    # ========================================================
    # CERRAR CÁMARA
    # ========================================================

    def cerrar_camara(self):

        if self.timer_camara.isActive():

            self.timer_camara.stop()

        self.camera.cerrar()

        self.camara_abierta = False

        self.panel_camara.clear()

        self.panel_camara.setText(
            "📷\n\nLa cámara aparecerá aquí"
        )

        self.actualizar_estado_camara()

    # ========================================================
    # CERRAR APLICACIÓN
    # ========================================================

    def closeEvent(self, event):

        if self.timer_camara.isActive():

            self.timer_camara.stop()

        self.camera.cerrar()

        self.camara_abierta = False

        event.accept()