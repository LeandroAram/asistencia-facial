import cv2
from time import monotonic

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
    QTimer,
    QThread,
    Signal,
    Slot
)

from PySide6.QtGui import (
    QRegularExpressionValidator,
    QImage,
    QPixmap
)

from src.ui.registro_alumno import RegistroAlumnoWidget
from src.camera.camera_manager import CameraManager
from src.recognition.trabajador_reconocimiento import TrabajadorReconocimiento

from src.database.conexion import (
    crear_jornada,
    actualizar_jornada,
    procesar_asistencia
)


class MainWindow(QMainWindow):

    solicitar_reconocimiento = Signal(object)

    def __init__(
        self,
        usuario_id,
        nombre_usuario
    ):
        super().__init__()

        self.usuario_id = usuario_id
        self.nombre_usuario = nombre_usuario

        # ====================================================
        # ESTADO DE JORNADA
        # ====================================================

        self.jornada_id = None
        self.jornada_en_edicion = False

        # ====================================================
        # CÁMARA COMPARTIDA
        # ====================================================

        self.camara_abierta = False

        self.camera = CameraManager()

        # La UI lee la cámara; un único trabajador ejecuta FaceNet.
        self.detector_asistencia = None
        self.referencias_listas = False
        self.recarga_pendiente = False
        self.sesion_reconocimiento = 0
        self.cerrando = False
        self.procesando_reconocimiento = False
        self.proximo_reconocimiento = 0.0
        self.intervalo_reconocimiento = 2.0

        self.hilo_reconocimiento = QThread(self)
        self.trabajador_reconocimiento = TrabajadorReconocimiento()
        self.trabajador_reconocimiento.moveToThread(self.hilo_reconocimiento)
        self.solicitar_reconocimiento.connect(
            self.trabajador_reconocimiento.ejecutar,
            Qt.QueuedConnection
        )
        self.trabajador_reconocimiento.terminado.connect(
            self.recibir_reconocimiento,
            Qt.QueuedConnection
        )
        self.hilo_reconocimiento.finished.connect(
            self.trabajador_reconocimiento.deleteLater
        )
        self.hilo_reconocimiento.finished.connect(self.finalizar_cierre)

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

        self.aplicar_estilos()

        # ====================================================
        # CONTENEDOR
        # ====================================================

        contenedor = QWidget()
        contenedor.setObjectName("root")

        self.setCentralWidget(
            contenedor
        )

        layout_principal = QHBoxLayout(
            contenedor
        )

        layout_principal.setContentsMargins(
            0,
            0,
            0,
            0
        )

        layout_principal.setSpacing(
            0
        )

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
            22,
            30,
            22,
            25
        )

        layout_sidebar.setSpacing(
            10
        )

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

        menu_label = QLabel(
            "MENÚ PRINCIPAL"
        )

        menu_label.setObjectName(
            "menuLabel"
        )

        layout_sidebar.addWidget(
            menu_label
        )

        # ====================================================
        # BOTONES MENÚ
        # ====================================================

        self.boton_asistencia = (
            self.crear_boton_menu(
                "◉   Asistencia Facial"
            )
        )

        self.boton_jornada = (
            self.crear_boton_menu(
                "◷   Configurar Jornada"
            )
        )

        self.boton_alumno = (
            self.crear_boton_menu(
                "＋   Registrar Alumno"
            )
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
        # USUARIO
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

        nombre_label = QLabel(
            f"👤  {self.nombre_usuario}"
        )

        nombre_label.setObjectName(
            "usuarioNombre"
        )

        layout_usuario.addWidget(
            etiqueta_sesion
        )

        layout_usuario.addWidget(
            nombre_label
        )

        layout_sidebar.addWidget(
            usuario_card
        )

        # ====================================================
        # CONTENIDO
        # ====================================================

        contenido = QFrame()

        contenido.setObjectName(
            "contenido"
        )

        layout_contenido = QVBoxLayout(
            contenido
        )

        layout_contenido.setContentsMargins(
            35,
            25,
            35,
            25
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
            "Controle la cámara y gestione la asistencia."
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

        self.crear_pagina_asistencia()

        self.crear_pagina_jornada()

        # ====================================================
        # REGISTRAR ALUMNO
        # ====================================================

        self.pagina_alumno = (
            RegistroAlumnoWidget(
                self.camera
            )
        )

        self.paginas.addWidget(
            self.pagina_alumno
        )

        self.pagina_alumno.alumno_registrado.connect(
            self.cerrar_camara
        )

        # ====================================================
        # AGREGAR PANELES
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
        # CÁMARA
        # ====================================================

        self.boton_abrir_camara.clicked.connect(
            self.abrir_camara
        )

        self.boton_cerrar_camara.clicked.connect(
            self.cerrar_camara
        )

        # ====================================================
        # JORNADA
        # ====================================================

        self.boton_guardar_jornada.clicked.connect(
            self.guardar_jornada
        )

        self.boton_editar_jornada.clicked.connect(
            self.editar_jornada
        )

        self.boton_terminar_jornada.clicked.connect(
            self.terminar_jornada
        )

        self.paginas.setCurrentIndex(
            0
        )

        self.actualizar_estado_jornada()

    # ========================================================
    # ESTILOS
    # ========================================================

    def aplicar_estilos(self):

        self.setStyleSheet("""

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

            QFrame#sidebar {
                background-color: #0f1e38;
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
            }

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

            QLabel#cameraPanel {
                background-color: #050a12;
                border: 2px solid #243954;
                border-radius: 18px;
                color: #53657d;
                font-size: 17px;
            }

            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 11px 18px;
                font-weight: 700;
                font-size: 13px;
            }

            QPushButton:hover {
                background-color: #3b82f6;
            }

            QPushButton:disabled {
                background-color: #172235;
                color: #526177;
                border: 1px solid #26364e;
            }

            QPushButton#botonCerrar,
            QPushButton#botonTerminar {
                background-color: #b42336;
            }

            QPushButton#botonEditar {
                background-color: #d97706;
            }

            QPushButton#botonGuardar {
                background-color: #059669;
            }

            QLineEdit {
                background-color: #0a1424;
                color: white;
                border: 1px solid #30425d;
                border-radius: 9px;
                padding: 9px 12px;
                min-height: 24px;
                font-size: 13px;
            }

            QLineEdit:focus {
                border: 1px solid #3b82f6;
            }

            QLineEdit:disabled {
                color: #94a3b8;
                background-color: #111c2d;
            }

            QGroupBox {
                color: #dbeafe;
                background-color: #101b2d;
                border: 1px solid #253650;
                border-radius: 12px;
                margin-top: 16px;
                padding: 18px 12px 12px 12px;
            }

            QScrollArea {
                border: none;
                background: transparent;
            }

        """)

    # ========================================================
    # BOTÓN MENÚ
    # ========================================================

    def crear_boton_menu(
        self,
        texto
    ):

        boton = QPushButton(
            texto
        )

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
    # TARJETA
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

        layout = QVBoxLayout(
            card
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

        return (
            card,
            valor_label
        )

    # ========================================================
    # ASISTENCIA
    # ========================================================

    def crear_pagina_asistencia(self):

        pagina = QWidget()

        layout = QVBoxLayout(
            pagina
        )

        layout.setSpacing(
            18
        )

        tarjetas = QHBoxLayout()

        (
            card_camara,
            self.estado_camara_label
        ) = self.crear_tarjeta_estado(
            "● ESTADO DE CÁMARA",
            "Apagada"
        )

        (
            card_jornada,
            self.estado_jornada_label
        ) = self.crear_tarjeta_estado(
            "◷ JORNADA",
            "Sin Jornada"
        )

        (
            card_fecha,
            self.estado_fecha_label
        ) = self.crear_tarjeta_estado(
            "▣ FECHA",
            QDate.currentDate().toString(
                "dd/MM/yyyy"
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

        botones = QHBoxLayout()

        self.boton_abrir_camara = QPushButton(
            "▶  Abrir Cámara"
        )

        self.boton_cerrar_camara = QPushButton(
            "■  Cerrar Cámara"
        )

        self.boton_cerrar_camara.setObjectName(
            "botonCerrar"
        )

        botones.addStretch()

        botones.addWidget(
            self.boton_abrir_camara
        )

        botones.addWidget(
            self.boton_cerrar_camara
        )

        botones.addStretch()

        layout.addLayout(
            botones
        )

        self.estado_reconocimiento_label = QLabel(
            "Guarde una Jornada y abra la cámara para reconocer."
        )
        self.estado_reconocimiento_label.setWordWrap(True)
        self.estado_reconocimiento_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.estado_reconocimiento_label)

        self.panel_camara = QLabel(
            "📷\n\nLa cámara aparecerá aquí"
        )

        self.panel_camara.setObjectName(
            "cameraPanel"
        )

        self.panel_camara.setAlignment(
            Qt.AlignCenter
        )

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
    # JORNADA
    # ========================================================

    def crear_pagina_jornada(self):

        pagina = QWidget()

        layout = QVBoxLayout(
            pagina
        )

        layout.setContentsMargins(
            0,
            20,
            0,
            0
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
            35,
            30,
            35,
            35
        )

        layout_tarjeta.setSpacing(
            20
        )

        titulo = QLabel(
            "Configuración de la Jornada"
        )

        titulo.setStyleSheet(
            "font-size:22px; font-weight:800;"
        )

        self.estado_jornada_config = QLabel(
            "● Sin Jornada activa"
        )

        self.estado_jornada_config.setStyleSheet(
            "color:#f59e0b; font-weight:bold;"
        )

        layout_tarjeta.addWidget(
            titulo
        )

        layout_tarjeta.addWidget(
            self.estado_jornada_config
        )

        formulario = QFormLayout()

        formulario.setVerticalSpacing(
            18
        )

        self.fecha_label = QLabel(
            QDate.currentDate().toString(
                "dd/MM/yyyy"
            )
        )

        formulario.addRow(
            "Fecha:",
            self.fecha_label
        )

        expresion = QRegularExpression(
            r"^([01][0-9]|2[0-3]):[0-5][0-9]$"
        )

        self.horario_entrada_input = QLineEdit()

        self.horario_entrada_input.setPlaceholderText(
            "--:--"
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
            "--:--"
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
            "Ingrese la cátedra"
        )

        formulario.addRow(
            "Cátedra:",
            self.catedra_input
        )

        layout_tarjeta.addLayout(
            formulario
        )

        # ====================================================
        # BOTONES JORNADA
        # ====================================================

        layout_botones = QHBoxLayout()

        self.boton_guardar_jornada = QPushButton(
            "Guardar Jornada"
        )

        self.boton_guardar_jornada.setObjectName(
            "botonGuardar"
        )

        self.boton_editar_jornada = QPushButton(
            "Editar Jornada"
        )

        self.boton_editar_jornada.setObjectName(
            "botonEditar"
        )

        self.boton_terminar_jornada = QPushButton(
            "Terminar Jornada"
        )

        self.boton_terminar_jornada.setObjectName(
            "botonTerminar"
        )

        layout_botones.addWidget(
            self.boton_guardar_jornada
        )

        layout_botones.addWidget(
            self.boton_editar_jornada
        )

        layout_botones.addWidget(
            self.boton_terminar_jornada
        )

        layout_tarjeta.addLayout(
            layout_botones
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
        # VALIDACIÓN AUTOMÁTICA
        # ====================================================

        self.horario_entrada_input.textChanged.connect(
            self.actualizar_estado_jornada
        )

        self.horario_salida_input.textChanged.connect(
            self.actualizar_estado_jornada
        )

        self.catedra_input.textChanged.connect(
            self.actualizar_estado_jornada
        )

    # ========================================================
    # VALIDAR DATOS DE JORNADA
    # ========================================================

    def datos_jornada_validos(self):

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
    # ESTADO JORNADA
    # ========================================================

    def actualizar_estado_jornada(self):

        datos_validos = (
            self.datos_jornada_validos()
        )

        # ----------------------------------------------------
        # SIN JORNADA
        # ----------------------------------------------------

        if self.jornada_id is None:

            self.boton_guardar_jornada.setVisible(
                True
            )

            self.boton_guardar_jornada.setEnabled(
                datos_validos
            )

            self.boton_editar_jornada.setVisible(
                False
            )

            self.boton_terminar_jornada.setVisible(
                False
            )

            self.estado_jornada_config.setText(
                "● Sin Jornada activa"
            )

            self.estado_jornada_config.setStyleSheet(
                "color:#f59e0b; font-weight:bold;"
            )

        # ----------------------------------------------------
        # JORNADA EN EDICIÓN
        # ----------------------------------------------------

        elif self.jornada_en_edicion:

            self.boton_guardar_jornada.setVisible(
                True
            )

            self.boton_guardar_jornada.setEnabled(
                datos_validos
            )

            self.boton_editar_jornada.setVisible(
                False
            )

            self.boton_terminar_jornada.setVisible(
                True
            )

            self.estado_jornada_config.setText(
                f"✎ Editando Jornada ID {self.jornada_id}"
            )

            self.estado_jornada_config.setStyleSheet(
                "color:#f59e0b; font-weight:bold;"
            )

        # ----------------------------------------------------
        # JORNADA GUARDADA
        # ----------------------------------------------------

        else:

            self.boton_guardar_jornada.setVisible(
                False
            )

            self.boton_editar_jornada.setVisible(
                True
            )

            self.boton_terminar_jornada.setVisible(
                True
            )

            self.estado_jornada_config.setText(
                f"● Jornada guardada · ID {self.jornada_id}"
            )

            self.estado_jornada_config.setStyleSheet(
                "color:#34d399; font-weight:bold;"
            )

        self.actualizar_estado_camara()

    # ========================================================
    # GUARDAR JORNADA
    # ========================================================

    def guardar_jornada(self):

        if not self.datos_jornada_validos():

            return

        fecha = QDate.currentDate().toString(
            "yyyy-MM-dd"
        )

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

        # ====================================================
        # CREAR NUEVA
        # ====================================================

        if self.jornada_id is None:

            (
                exito,
                jornada_id,
                mensaje
            ) = crear_jornada(
                fecha,
                entrada,
                salida,
                self.usuario_id,
                catedra
            )

            if not exito:

                QMessageBox.critical(
                    self,
                    "Error",
                    mensaje
                )

                return

            self.jornada_id = (
                jornada_id
            )

        # ====================================================
        # ACTUALIZAR EXISTENTE
        # ====================================================

        else:

            (
                exito,
                mensaje
            ) = actualizar_jornada(
                self.jornada_id,
                fecha,
                entrada,
                salida,
                catedra
            )

            if not exito:

                QMessageBox.critical(
                    self,
                    "Error",
                    mensaje
                )

                return

        self.jornada_en_edicion = False

        self.horario_entrada_input.setEnabled(
            False
        )

        self.horario_salida_input.setEnabled(
            False
        )

        self.catedra_input.setEnabled(
            False
        )

        self.actualizar_estado_jornada()

        QMessageBox.information(
            self,
            "Jornada",
            (
                "Jornada guardada correctamente.\n\n"
                f"ID de Jornada: {self.jornada_id}"
            )
        )

    # ========================================================
    # EDITAR JORNADA
    # ========================================================

    def editar_jornada(self):

        # Requisito del profesor:
        # si cámara está abierta, cerrarla.
        if self.camara_abierta:

            self.cerrar_camara()

        self.jornada_en_edicion = True

        self.horario_entrada_input.setEnabled(
            True
        )

        self.horario_salida_input.setEnabled(
            True
        )

        self.catedra_input.setEnabled(
            True
        )

        self.actualizar_estado_jornada()

    # ========================================================
    # TERMINAR JORNADA
    # ========================================================

    def terminar_jornada(self):

        if self.camara_abierta:

            self.cerrar_camara()

        # IMPORTANTE:
        # No se elimina nada de PostgreSQL.
        self.jornada_id = None

        self.jornada_en_edicion = False

        self.horario_entrada_input.setEnabled(
            True
        )

        self.horario_salida_input.setEnabled(
            True
        )

        self.catedra_input.setEnabled(
            True
        )

        self.horario_entrada_input.clear()
        self.horario_salida_input.clear()
        self.catedra_input.clear()

        self.actualizar_estado_jornada()

    # ========================================================
    # CÁMARA HABILITADA
    # ========================================================

    def puede_abrir_camara(self):

        return (
            self.jornada_id is not None
            and not self.jornada_en_edicion
        )

    # ========================================================
    # ESTADO CÁMARA
    # ========================================================

    def actualizar_estado_camara(self):

        if not self.puede_abrir_camara():

            self.boton_abrir_camara.setEnabled(
                False
            )

            self.boton_cerrar_camara.setEnabled(
                False
            )

            self.estado_camara_label.setText(
                "Apagada"
            )

            self.estado_jornada_label.setText(
                "Sin Jornada guardada"
                if self.jornada_id is None
                else "Jornada en edición"
            )

            return

        self.estado_jornada_label.setText(
            f"Guardada · ID {self.jornada_id}"
        )

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

    # ========================================================
    # ABRIR CÁMARA
    # ========================================================

    def abrir_camara(self):

        if not self.puede_abrir_camara():

            QMessageBox.warning(
                self,
                "Jornada requerida",
                (
                    "Debe guardar una Jornada "
                    "antes de abrir la cámara."
                )
            )

            return

        if not self.camera.abrir():

            QMessageBox.critical(
                self,
                "Error",
                "No se pudo abrir la webcam."
            )

            return

        self.camara_abierta = True

        self.preparar_reconocimiento()

        self.timer_camara.start(
            30
        )

        self.actualizar_estado_camara()

    # ========================================================
    # VIDEO
    # ========================================================

    def actualizar_video_camara(self):

        if (
            self.cerrando
            or not self.camara_abierta
            or not self.puede_abrir_camara()
            or self.paginas.currentIndex() != 0
        ):
            return

        frame = self.camera.leer_frame()

        if frame is None:
            self.sesion_reconocimiento += 1
            self.estado_reconocimiento_label.setText(
                "No se pudo leer la cámara. Cierre y vuelva a abrirla."
            )
            return

        frame = cv2.flip(
            frame,
            1
        )

        # Detectar y reconocer antes de dibujar sobre la imagen.
        rostros = self.procesar_frame_asistencia(frame)
        for x, y, w, h in rostros:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 200, 0), 2)

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

    def preparar_reconocimiento(self):
        self.referencias_listas = False
        self.sesion_reconocimiento += 1
        self.estado_reconocimiento_label.setText(
            "Cargando reconocimiento y fotografías de referencia..."
        )
        if self.procesando_reconocimiento:
            # Reabrir durante una inferencia no encola otro trabajo.
            self.recarga_pendiente = True
            return
        self.recarga_pendiente = False
        try:
            if self.detector_asistencia is None:
                self.detector_asistencia = cv2.CascadeClassifier(
                    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
                )
                if self.detector_asistencia.empty():
                    self.detector_asistencia = None
                    raise RuntimeError("No se pudo cargar Haar Cascade.")
            if not self.hilo_reconocimiento.isRunning():
                self.hilo_reconocimiento.start()
            self.enviar_trabajo("preparar")
        except Exception as error:
            print("Error preparando reconocimiento:", error)
            self.estado_reconocimiento_label.setText(
                "No se pudo iniciar el reconocimiento. Vuelva a abrir la cámara."
            )

    def enviar_trabajo(self, tipo, frame=None, rostros=None):
        if self.procesando_reconocimiento or self.cerrando:
            return
        self.procesando_reconocimiento = True
        self.solicitar_reconocimiento.emit({
            "tipo": tipo,
            "sesion": self.sesion_reconocimiento,
            "jornada_id": self.jornada_id,
            # El dibujo y el siguiente frame no modifican la imagen del trabajador.
            "frame": frame.copy() if frame is not None else None,
            "rostros": rostros.copy() if rostros is not None else None,
        })

    def procesar_frame_asistencia(self, frame):
        if (
            self.cerrando
            or self.detector_asistencia is None
            or not self.camara_abierta
            or not self.puede_abrir_camara()
            or self.paginas.currentIndex() != 0
        ):
            return []
        try:
            # Detector exclusivo de la UI: no se comparte con la carga de fotos.
            gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rostros = self.detector_asistencia.detectMultiScale(
                gris, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)
            )
            if len(rostros) != 1:
                # Si la escena deja de ser válida, descartar también el resultado pendiente.
                self.sesion_reconocimiento += 1
                self.estado_reconocimiento_label.setText(
                    "Sin rostro. Mire a la cámara." if len(rostros) == 0 else
                    "Hay varios rostros. Debe quedar una sola persona."
                )
            elif self.procesando_reconocimiento:
                self.estado_reconocimiento_label.setText(
                    "Reconociendo rostro..." if self.referencias_listas else
                    "Cargando reconocimiento y fotografías de referencia..."
                )
            elif self.referencias_listas and monotonic() >= self.proximo_reconocimiento:
                self.estado_reconocimiento_label.setText("Reconociendo rostro...")
                self.enviar_trabajo("reconocer", frame, rostros)
            elif not self.referencias_listas:
                self.estado_reconocimiento_label.setText(
                    "Sin referencias disponibles. Revise las fotos y la conexión; "
                    "luego vuelva a abrir la cámara."
                )
            return rostros
        except Exception as error:
            self.sesion_reconocimiento += 1
            print("Error detectando rostros:", error)
            self.estado_reconocimiento_label.setText("No se pudo detectar el rostro.")
            return []

    @Slot(object)
    def recibir_reconocimiento(self, respuesta):
        self.procesando_reconocimiento = False
        self.proximo_reconocimiento = monotonic() + self.intervalo_reconocimiento
        if self.cerrando:
            return
        if self.recarga_pendiente:
            if self.camara_abierta:
                self.preparar_reconocimiento()
            return
        if respuesta["tipo"] == "preparar":
            self.referencias_listas = not respuesta.get("error") and respuesta.get("cantidad", 0) > 0
            if self.camara_abierta and self.paginas.currentIndex() == 0:
                self.estado_reconocimiento_label.setText(
                    "Referencias listas. Ubique un solo rostro." if self.referencias_listas else
                    "Sin referencias disponibles. Revise las fotos y la conexión; "
                    "luego vuelva a abrir la cámara."
                )
            return
        # Solo la UI persiste, después de validar que el contexto siga vigente.
        if (
            respuesta["sesion"] != self.sesion_reconocimiento
            or respuesta["jornada_id"] != self.jornada_id
            or not self.camara_abierta
            or not self.puede_abrir_camara()
            or self.paginas.currentIndex() != 0
        ):
            return
        if respuesta.get("error"):
            self.estado_reconocimiento_label.setText(
                "Error en el reconocimiento. Se reintentará."
            )
            return
        resultado = respuesta["resultado"]
        if resultado["estado"] == "reconocido":
            try:
                exito, estado = procesar_asistencia(
                    resultado["alumno_id"], self.jornada_id
                )
            except Exception as error:
                print("Error registrando asistencia:", error)
                exito, estado = False, "error"
            nombre = f'{resultado["nombre"]} {resultado["apellido"]}'
            mensajes = {
                "entrada_registrada": "Entrada registrada",
                "salida_registrada": "Salida registrada",
                "asistencia_completa": "Ya tiene entrada y salida registradas",
                "salida_no_habilitada": "Entrada registrada; salida aún no habilitada",
            }
            mensaje = mensajes.get(estado, "Asistencia procesada") if exito else (
                "No se pudo registrar la asistencia. Se reintentará."
            )
            self.estado_reconocimiento_label.setText(f"{nombre}: {mensaje}")
        else:
            mensajes = {
                "no_reconocido": "Rostro no reconocido.",
                "error_embedding": "No se pudo analizar el rostro. Se reintentará.",
                "sin_referencias": "No hay referencias válidas.",
                "sin_rostro": "Sin rostro. Mire a la cámara.",
                "multiples_rostros": "Debe quedar una sola persona.",
            }
            self.estado_reconocimiento_label.setText(
                mensajes.get(resultado["estado"], "No se pudo reconocer el rostro.")
            )

    def cerrar_camara(self):

        self.sesion_reconocimiento += 1
        self.referencias_listas = False
        self.recarga_pendiente = False

        if self.timer_camara.isActive():

            self.timer_camara.stop()

        self.camera.cerrar()

        self.camara_abierta = False
        self.proximo_reconocimiento = 0.0
        self.estado_reconocimiento_label.setText("Cámara cerrada. Reconocimiento detenido.")

        self.panel_camara.clear()

        self.panel_camara.setText(
            "📷\n\nLa cámara aparecerá aquí"
        )

        self.actualizar_estado_camara()

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
            "Reconocimiento y registro automático de asistencia."
        )

        if (
            self.camara_abierta
            and self.camera.esta_abierta()
        ):

            self.timer_camara.start(
                30
            )

    def ir_jornada(self):

        self.sesion_reconocimiento += 1

        # Solo dejamos de dibujar.
        # No cerramos la webcam salvo que se pulse Editar.
        if self.timer_camara.isActive():

            self.timer_camara.stop()

        self.paginas.setCurrentIndex(
            1
        )

        self.titulo_pagina.setText(
            "Configuración de la Jornada"
        )

        self.subtitulo_pagina.setText(
            "Cree, edite o termine una Jornada."
        )

    def ir_registro_alumno(self):

        self.sesion_reconocimiento += 1

        # Cámara permanece encendida.
        if self.timer_camara.isActive():

            self.timer_camara.stop()

        self.paginas.setCurrentIndex(
            2
        )

        self.titulo_pagina.setText(
            "Registrar Alumno"
        )

        self.subtitulo_pagina.setText(
            "Complete los datos y fotografías del alumno."
        )

    # ========================================================
    # CERRAR PROGRAMA
    # ========================================================

    @Slot()
    def finalizar_cierre(self):
        if self.cerrando:
            self.close()

    def closeEvent(self, event):
        self.cerrando = True
        self.cerrar_camara()
        if self.hilo_reconocimiento.isRunning():
            # No destruir ni terminar forzosamente un hilo que aún ejecuta FaceNet.
            # La ventana sigue atendiendo eventos hasta recibir finished.
            self.setEnabled(False)
            self.estado_reconocimiento_label.setText(
                "Cerrando: esperando que termine el procesamiento actual..."
            )
            self.hilo_reconocimiento.quit()
            event.ignore()
            return
        event.accept()
