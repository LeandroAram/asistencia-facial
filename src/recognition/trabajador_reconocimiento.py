from PySide6.QtCore import QObject, Signal, Slot


class TrabajadorReconocimiento(QObject):
    """FaceNet y sus referencias pertenecen exclusivamente a este trabajador."""

    terminado = Signal(object)

    def __init__(self):
        super().__init__()
        self.reconocedor = None

    @Slot(object)
    def ejecutar(self, trabajo):
        respuesta = {
            "tipo": trabajo["tipo"],
            "sesion": trabajo["sesion"],
            "jornada_id": trabajo["jornada_id"],
        }
        try:
            if trabajo["tipo"] == "preparar":
                if self.reconocedor is None:
                    from src.recognition.reconocedor_facial import ReconocedorFacial
                    self.reconocedor = ReconocedorFacial()
                respuesta["cantidad"] = self.reconocedor.cargar_referencias()
            else:
                respuesta["resultado"] = self.reconocedor.reconocer(
                    trabajo["frame"], rostros=trabajo["rostros"]
                )
        except Exception as error:
            print("Error en trabajador de reconocimiento:", error)
            respuesta["error"] = True
        # Incluso ante un error, liberar el único trabajo admitido por la UI.
        self.terminado.emit(respuesta)
