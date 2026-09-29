import cv2

from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox
)

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QImage, QPixmap

from src.camera.camera_manager import CameraManager


class CapturaFotoDialog(QDialog):

    foto_capturada = Signal(bytes)

    def __init__(self, parent=None, camera_compartida=None):
        super().__init__(parent)

        self.setWindowTitle("Tomar Foto")
        self.setFixedSize(760, 620)

        # Si ya existe una cámara abierta desde Asistencia,
        # utilizamos exactamente esa misma cámara.
        if camera_compartida is not None:
            self.camera = camera_compartida
        else:
            self.camera = CameraManager()

        # Recordamos si ya estaba abierta antes de entrar.
        self.camera_estaba_abierta = self.camera.esta_abierta()

        self.frame_actual = None

        # ====================================================
        # VIDEO
        # ====================================================

        self.video_label = QLabel("Iniciando cámara...")

        self.video_label.setAlignment(
            Qt.AlignCenter
        )

        self.video_label.setFixedSize(
            720,
            500
        )

        self.video_label.setStyleSheet("""
            QLabel {
                border: 2px solid #555555;
                border-radius: 8px;
                background-color: #111111;
            }
        """)

        # ====================================================
        # BOTONES
        # ====================================================

        self.boton_capturar = QPushButton(
            "Capturar Foto"
        )

        self.boton_cancelar = QPushButton(
            "Cancelar"
        )

        self.boton_capturar.setMinimumHeight(
            40
        )

        self.boton_cancelar.setMinimumHeight(
            40
        )

        self.boton_capturar.clicked.connect(
            self.capturar_foto
        )

        self.boton_cancelar.clicked.connect(
            self.reject
        )

        layout_botones = QHBoxLayout()

        layout_botones.addWidget(
            self.boton_capturar
        )

        layout_botones.addWidget(
            self.boton_cancelar
        )

        # ====================================================
        # LAYOUT
        # ====================================================

        layout = QVBoxLayout()

        layout.addWidget(
            self.video_label,
            alignment=Qt.AlignCenter
        )

        layout.addLayout(
            layout_botones
        )

        self.setLayout(
            layout
        )

        # ====================================================
        # TIMER
        # ====================================================

        self.timer = QTimer(self)

        self.timer.timeout.connect(
            self.actualizar_video
        )

        # ====================================================
        # ABRIR CÁMARA
        # ====================================================

        if not self.camera.esta_abierta():

            if not self.camera.abrir():

                QMessageBox.critical(
                    self,
                    "Error",
                    "No se pudo abrir la cámara."
                )

                self.reject()
                return

        self.timer.start(30)

    # ========================================================
    # VIDEO
    # ========================================================

    def actualizar_video(self):

        frame = self.camera.leer_frame()

        if frame is None:
            return

        # Modo espejo
        frame = cv2.flip(
            frame,
            1
        )

        self.frame_actual = frame.copy()

        frame_rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        alto, ancho, canales = frame_rgb.shape

        bytes_por_linea = canales * ancho

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

        self.video_label.setPixmap(
            pixmap.scaled(
                self.video_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

    # ========================================================
    # CAPTURAR FOTO
    # ========================================================

    def capturar_foto(self):

        if self.frame_actual is None:

            QMessageBox.warning(
                self,
                "Sin imagen",
                "Todavía no hay una imagen disponible."
            )

            return

        ok, buffer = cv2.imencode(
            ".jpg",
            self.frame_actual
        )

        if not ok:

            QMessageBox.critical(
                self,
                "Error",
                "No se pudo capturar la fotografía."
            )

            return

        imagen_bytes = buffer.tobytes()

        self.foto_capturada.emit(
            imagen_bytes
        )

        self.accept()

    # ========================================================
    # CERRAR VENTANA DE CAPTURA
    # ========================================================

    def detener_video(self):

        if self.timer.isActive():
            self.timer.stop()

        # IMPORTANTE:
        # Si la cámara ya estaba abierta desde Asistencia,
        # NO LA CERRAMOS.
        if not self.camera_estaba_abierta:
            self.camera.cerrar()

    def accept(self):

        self.detener_video()

        super().accept()

    def reject(self):

        self.detener_video()

        super().reject()

    def closeEvent(self, event):

        self.detener_video()

        event.accept()