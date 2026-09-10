from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QFileDialog,
    QMessageBox,
    QDateEdit,
    QSpinBox,
    QScrollArea,
    QGroupBox
)

from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QPixmap

from src.database.conexion import registrar_alumno


# ============================================================
# SECCIÓN PARA UNA FOTO
# ============================================================

class FotoAnguloWidget(QGroupBox):

    def __init__(self, titulo):
        super().__init__(titulo)

        self.ruta_imagen = None

        layout = QVBoxLayout()
        self.setLayout(layout)

        # ----------------------------------------------------
        # PANEL DE PREVISUALIZACIÓN
        # ----------------------------------------------------

        self.preview = QLabel("Sin imagen todavía")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setFixedSize(200, 140)

        self.preview.setStyleSheet("""
            QLabel {
                border: 1px dashed #777777;
                border-radius: 6px;
                padding: 5px;
            }
        """)

        # ----------------------------------------------------
        # BOTONES
        # ----------------------------------------------------

        self.boton_cargar = QPushButton("Cargar Foto")
        self.boton_tomar = QPushButton("Tomar Foto")

        self.boton_eliminar = QPushButton("🗑")
        self.boton_eliminar.setFixedWidth(40)
        self.boton_eliminar.setVisible(False)

        self.boton_eliminar.setStyleSheet("""
            QPushButton {
                background-color: #b00020;
                color: white;
                font-weight: bold;
            }
        """)

        layout_botones = QHBoxLayout()

        layout_botones.addWidget(self.boton_cargar)
        layout_botones.addWidget(self.boton_tomar)
        layout_botones.addWidget(self.boton_eliminar)

        layout.addWidget(
            self.preview,
            alignment=Qt.AlignCenter
        )

        layout.addLayout(layout_botones)

        # ----------------------------------------------------
        # EVENTOS
        # ----------------------------------------------------

        self.boton_cargar.clicked.connect(
            self.cargar_foto
        )

        self.boton_eliminar.clicked.connect(
            self.limpiar_foto
        )

        # El botón Tomar Foto queda habilitado,
        # pero no hace nada en este incremento.

    # ========================================================
    # CARGAR FOTO DESDE LA COMPUTADORA
    # ========================================================

    def cargar_foto(self):

        ruta, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar imagen",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.webp)"
        )

        if not ruta:
            return

        pixmap = QPixmap(ruta)

        if pixmap.isNull():

            QMessageBox.warning(
                self,
                "Imagen inválida",
                "No se pudo cargar la imagen seleccionada."
            )

            return

        self.ruta_imagen = ruta

        imagen_escalada = pixmap.scaled(
            self.preview.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.preview.setPixmap(
            imagen_escalada
        )

        self.boton_eliminar.setVisible(True)

    # ========================================================
    # OBTENER IMAGEN COMO BYTES
    # ========================================================

    def obtener_bytes(self):

        if not self.ruta_imagen:
            return None

        try:

            with open(
                self.ruta_imagen,
                "rb"
            ) as archivo:

                return archivo.read()

        except Exception:

            return None

    # ========================================================
    # BORRAR FOTO
    # ========================================================

    def limpiar_foto(self):

        self.ruta_imagen = None

        self.preview.clear()

        self.preview.setText(
            "Sin imagen todavía"
        )

        self.boton_eliminar.setVisible(False)


# ============================================================
# FORMULARIO REGISTRAR ALUMNO
# ============================================================

class RegistroAlumnoWidget(QWidget):

    def __init__(self):
        super().__init__()

        layout_general = QVBoxLayout()
        self.setLayout(layout_general)

        # ====================================================
        # SCROLL
        # ====================================================

        scroll = QScrollArea()

        scroll.setWidgetResizable(True)

        contenido = QWidget()

        layout_contenido = QVBoxLayout()

        contenido.setLayout(
            layout_contenido
        )

        scroll.setWidget(contenido)

        layout_general.addWidget(scroll)

        # ====================================================
        # TÍTULO
        # ====================================================

        titulo = QLabel(
            "Registrar Alumno"
        )

        titulo.setAlignment(
            Qt.AlignCenter
        )

        titulo.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 15px;
        """)

        layout_contenido.addWidget(
            titulo
        )

        # ====================================================
        # DATOS PERSONALES
        # ====================================================

        grupo_datos = QGroupBox(
            "Datos personales"
        )

        formulario = QFormLayout()

        grupo_datos.setLayout(
            formulario
        )

        # ----------------------------------------------------
        # NOMBRE
        # ----------------------------------------------------

        self.nombre_input = QLineEdit()

        formulario.addRow(
            "Nombre:",
            self.nombre_input
        )

        # ----------------------------------------------------
        # APELLIDO
        # ----------------------------------------------------

        self.apellido_input = QLineEdit()

        formulario.addRow(
            "Apellido:",
            self.apellido_input
        )

        # ----------------------------------------------------
        # DNI
        # ----------------------------------------------------

        self.dni_input = QLineEdit()

        formulario.addRow(
            "DNI:",
            self.dni_input
        )

        # ----------------------------------------------------
        # CARRERA
        # ----------------------------------------------------

        self.carrera_input = QLineEdit()

        formulario.addRow(
            "Carrera:",
            self.carrera_input
        )

        # ----------------------------------------------------
        # CELULAR
        # ----------------------------------------------------

        self.celular_input = QLineEdit()

        formulario.addRow(
            "Celular:",
            self.celular_input
        )

        # ----------------------------------------------------
        # CORREO
        # ----------------------------------------------------

        self.correo_input = QLineEdit()

        formulario.addRow(
            "Correo electrónico:",
            self.correo_input
        )

        # ----------------------------------------------------
        # FECHA DE NACIMIENTO
        # ----------------------------------------------------

        self.fecha_nacimiento_input = QDateEdit()

        self.fecha_nacimiento_input.setCalendarPopup(
            True
        )

        self.fecha_nacimiento_input.setDisplayFormat(
            "dd/MM/yyyy"
        )

        self.fecha_minima = QDate(
            1900,
            1,
            1
        )

        self.fecha_nacimiento_input.setMinimumDate(
            self.fecha_minima
        )

        self.fecha_nacimiento_input.setSpecialValueText(
            "--/--/----"
        )

        self.fecha_nacimiento_input.setDate(
            self.fecha_minima
        )

        formulario.addRow(
            "Fecha de nacimiento:",
            self.fecha_nacimiento_input
        )

        # ----------------------------------------------------
        # AÑO DE INGRESO
        # ----------------------------------------------------

        self.anio_ingreso_input = QSpinBox()

        self.anio_ingreso_input.setRange(
            0,
            QDate.currentDate().year() + 1
        )

        self.anio_ingreso_input.setSpecialValueText(
            "Seleccione el año"
        )

        self.anio_ingreso_input.setValue(0)

        formulario.addRow(
            "Año de ingreso:",
            self.anio_ingreso_input
        )

        # ----------------------------------------------------
        # DOMICILIO
        # ----------------------------------------------------

        self.domicilio_input = QLineEdit()

        formulario.addRow(
            "Domicilio:",
            self.domicilio_input
        )

        # ----------------------------------------------------
        # LIBRETA
        # ----------------------------------------------------

        self.libreta_input = QLineEdit()

        formulario.addRow(
            "Número de libreta:",
            self.libreta_input
        )

        layout_contenido.addWidget(
            grupo_datos
        )

        # ====================================================
        # FOTOGRAFÍAS
        # ====================================================

        titulo_fotos = QLabel(
            "Fotografías para reconocimiento facial"
        )

        titulo_fotos.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            margin-top: 20px;
        """)

        layout_contenido.addWidget(
            titulo_fotos
        )

        layout_fotos = QHBoxLayout()

        # ----------------------------------------------------
        # FRONTAL
        # ----------------------------------------------------

        self.foto_frontal = FotoAnguloWidget(
            "Ángulo Frontal"
        )

        # ----------------------------------------------------
        # IZQUIERDO
        # ----------------------------------------------------

        self.foto_izquierda = FotoAnguloWidget(
            "Ángulo Izquierdo"
        )

        # ----------------------------------------------------
        # DERECHO
        # ----------------------------------------------------

        self.foto_derecha = FotoAnguloWidget(
            "Ángulo Derecho"
        )

        layout_fotos.addWidget(
            self.foto_frontal
        )

        layout_fotos.addWidget(
            self.foto_izquierda
        )

        layout_fotos.addWidget(
            self.foto_derecha
        )

        layout_contenido.addLayout(
            layout_fotos
        )

        # ====================================================
        # BOTÓN REGISTRAR
        # ====================================================

        self.boton_registrar = QPushButton(
            "Registrar"
        )

        self.boton_registrar.setMinimumHeight(
            40
        )

        self.boton_registrar.clicked.connect(
            self.registrar
        )

        layout_contenido.addSpacing(20)

        layout_contenido.addWidget(
            self.boton_registrar
        )

        layout_contenido.addSpacing(20)

    # ========================================================
    # REGISTRAR ALUMNO
    # ========================================================

    def registrar(self):

        nombre = (
            self.nombre_input.text().strip()
        )

        apellido = (
            self.apellido_input.text().strip()
        )

        dni = (
            self.dni_input.text().strip()
        )

        carrera = (
            self.carrera_input.text().strip()
        )

        celular = (
            self.celular_input.text().strip()
        )

        correo = (
            self.correo_input.text().strip()
        )

        domicilio = (
            self.domicilio_input.text().strip()
        )

        libreta = (
            self.libreta_input.text().strip()
        )

        fecha = (
            self.fecha_nacimiento_input.date()
        )

        anio_ingreso = (
            self.anio_ingreso_input.value()
        )

        # ====================================================
        # OBTENER FOTOS
        # ====================================================

        frontal = (
            self.foto_frontal.obtener_bytes()
        )

        izquierda = (
            self.foto_izquierda.obtener_bytes()
        )

        derecha = (
            self.foto_derecha.obtener_bytes()
        )

        # ====================================================
        # VALIDAR CAMPOS OBLIGATORIOS
        # ====================================================

        campos_texto = [
            nombre,
            apellido,
            dni,
            carrera,
            celular,
            correo,
            domicilio,
            libreta
        ]

        if (
            not all(campos_texto)
            or fecha == self.fecha_minima
            or anio_ingreso == 0
            or frontal is None
            or izquierda is None
            or derecha is None
        ):

            QMessageBox.critical(
                self,
                "Campos incompletos",
                (
                    "Existen campos obligatorios "
                    "sin completar.\n\n"
                    "Debe completar todos los datos "
                    "y cargar las tres imágenes."
                )
            )

            return

        # ====================================================
        # DATOS PARA POSTGRESQL
        # ====================================================

        datos = {

            "nombre": nombre,

            "apellido": apellido,

            "dni": dni,

            "carrera": carrera,

            "celular": celular,

            "correo_electronico": correo,

            "fecha_nacimiento":
                fecha.toString("yyyy-MM-dd"),

            "anio_ingreso": anio_ingreso,

            "domicilio": domicilio,

            "libreta": libreta
        }

        fotos = {

            "frontal": frontal,

            "izquierdo": izquierda,

            "derecho": derecha
        }

        # ====================================================
        # GUARDAR
        # ====================================================

        exito, mensaje = registrar_alumno(
            datos,
            fotos
        )

        if exito:

            QMessageBox.information(
                self,
                "Registro exitoso",
                mensaje
            )

            self.limpiar_formulario()

        else:

            QMessageBox.critical(
                self,
                "Error",
                mensaje
            )

    # ========================================================
    # LIMPIAR FORMULARIO
    # ========================================================

    def limpiar_formulario(self):

        self.nombre_input.clear()
        self.apellido_input.clear()
        self.dni_input.clear()
        self.carrera_input.clear()
        self.celular_input.clear()
        self.correo_input.clear()
        self.domicilio_input.clear()
        self.libreta_input.clear()

        self.fecha_nacimiento_input.setDate(
            self.fecha_minima
        )

        self.anio_ingreso_input.setValue(0)

        self.foto_frontal.limpiar_foto()
        self.foto_izquierda.limpiar_foto()
        self.foto_derecha.limpiar_foto()