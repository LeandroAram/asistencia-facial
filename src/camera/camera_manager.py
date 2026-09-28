import cv2


class CameraManager:

    def __init__(self, indice=0):
        self.indice = indice
        self.cap = None

    def abrir(self):
        if self.cap is not None and self.cap.isOpened():
            return True

        self.cap = cv2.VideoCapture(self.indice)

        return self.cap.isOpened()

    def leer_frame(self):
        if self.cap is None or not self.cap.isOpened():
            return None

        ok, frame = self.cap.read()

        if not ok:
            return None

        return frame

    def cerrar(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def esta_abierta(self):
        return (
            self.cap is not None
            and self.cap.isOpened()
        )