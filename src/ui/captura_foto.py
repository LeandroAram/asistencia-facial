import cv2

from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox
)

from PySide6.QtCore import (
    Qt,
    QTimer,
    Signal
)

from PySide6.QtGui import (
    QImage,
    QPixmap
)

from src.camera.camera_manager import CameraManager


class CapturaFotoDialog(QDialog):

    foto_capturada = Signal(bytes)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Tomar Foto")
        self.resize(700, 550)

        self.camera = CameraManager()

        self.frame_actual = None

        # ==============================================
        # VIDEO
        # ==============================================

        self.video_label = QLabel(
            "Iniciando cámara..."
        )

        self.video_label.setAlignment(
            Qt.AlignCenter
        )

        self.video_label.setMinimumSize(
            640,
            420
        )

        # ==============================================
        # BOTONES
        # ==============================================

        self.boton_capturar = QPushButton(
            "Capturar Foto"
        )

        self.boton_cancelar = QPushButton(
            "Cancelar"
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

        # ==============================================
        # LAYOUT
        # ==============================================

        layout = QVBoxLayout()

        layout.addWidget(
            self.video_label
        )

        layout.addLayout(
            layout_botones
        )

        self.setLayout(layout)

        # ==============================================
        # TIMER
        # ==============================================

        self.timer = QTimer(self)

        self.timer.timeout.connect(
            self.actualizar_video
        )

        # ==============================================
        # ABRIR CÁMARA
        # ==============================================

        if not self.camera.abrir():

            QMessageBox.critical(
                self,
                "Error",
                "No se pudo abrir la cámara."
            )

            self.reject()

            return

        self.timer.start(30)

    # ==============================================
    # ACTUALIZAR VIDEO
    # ==============================================

    def actualizar_video(self):

        frame = self.camera.leer_frame()

        if frame is None:
            return

        self.frame_actual = frame.copy()

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

        self.video_label.setPixmap(
            pixmap.scaled(
                self.video_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

    # ==============================================
    # CAPTURAR FOTO
    # ==============================================

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

        imagen_bytes = (
            buffer.tobytes()
        )

        self.foto_capturada.emit(
            imagen_bytes
        )

        self.accept()

    # ==============================================
    # LIBERAR WEBCAM
    # ==============================================

    def cerrar_camara(self):

        if self.timer.isActive():
            self.timer.stop()

        self.camera.cerrar()

    def accept(self):

        self.cerrar_camara()

        super().accept()

    def reject(self):

        self.cerrar_camara()

        super().reject()

    def closeEvent(self, event):

        self.cerrar_camara()

        event.accept()