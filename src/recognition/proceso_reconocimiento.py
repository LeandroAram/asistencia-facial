"""Proceso sin Qt ni acceso de escritura: protocolo JSON por stdin/stdout."""
import base64
from contextlib import redirect_stdout
import json
import sys
import time
import traceback


def enviar(datos):
    print(json.dumps(datos, ensure_ascii=False), flush=True)


def main():
    reconocedor = None
    for linea in sys.stdin:
        inicio = time.monotonic()
        try:
            trabajo = json.loads(linea)
            if trabajo['tipo'] == 'preparar':
                if reconocedor is None:
                    enviar({'progreso': 'Iniciando FaceNet512. La primera carga puede tardar... '})
                    with redirect_stdout(sys.stderr):
                        from src.recognition.reconocedor_facial import ReconocedorFacial
                        reconocedor = ReconocedorFacial()
                        import numpy as np
                        # Preparar el primer cálculo antes de habilitar el reconocimiento.
                        if reconocedor.generar_embedding(np.full((160, 160, 3), 128, np.uint8)) is None:
                            raise RuntimeError('No se pudo inicializar la inferencia FaceNet512')
                enviar({'progreso': 'Cargando referencias; se reutilizan las fotos ya procesadas...'})
                with redirect_stdout(sys.stderr):
                    cantidad = reconocedor.cargar_referencias()
                enviar({'cantidad': cantidad})
            elif trabajo['tipo'] == 'reconocer':
                with redirect_stdout(sys.stderr):
                    import cv2
                    import numpy as np
                    imagen = cv2.imdecode(np.frombuffer(base64.b64decode(trabajo['imagen']), dtype=np.uint8), cv2.IMREAD_COLOR)
                    if imagen is None or reconocedor is None:
                        raise ValueError('Motor o imagen no disponibles')
                    alto, ancho = imagen.shape[:2]
                    resultado = reconocedor.reconocer(imagen, rostros=[(0, 0, ancho, alto)])
                    resultado.pop('rostros', None)
                enviar({'resultado': resultado})
            else:
                raise ValueError('Trabajo desconocido')
            print(f"Motor facial: {trabajo['tipo']} en {time.monotonic()-inicio:.2f}s", file=sys.stderr, flush=True)
        except Exception:
            traceback.print_exc(file=sys.stderr)
            enviar({'error': True, 'mensaje': 'Error del motor facial. Revise la terminal.'})


if __name__ == '__main__':
    main()
