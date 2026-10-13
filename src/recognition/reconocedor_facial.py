import cv2
import numpy as np

from deepface import DeepFace

from src.database.conexion import conectar_bd


class ReconocedorFacial:

    UMBRAL = 0.40

    def __init__(self):

        # ====================================================
        # HAAR CASCADE
        # ====================================================

        ruta_haar = (
            cv2.data.haarcascades
            + "haarcascade_frontalface_default.xml"
        )

        self.detector = cv2.CascadeClassifier(
            ruta_haar
        )

        if self.detector.empty():

            raise RuntimeError(
                "No se pudo cargar Haar Cascade."
            )

        # ====================================================
        # MODELO FACENET512
        # ====================================================

        print(
            "Cargando modelo FaceNet512..."
        )

        DeepFace.build_model(
            "Facenet512"
        )

        print(
            "FaceNet512 cargado."
        )

        # ====================================================
        # EMBEDDINGS DE REFERENCIA
        # ====================================================

        self.referencias = []

    # ========================================================
    # DETECTAR ROSTROS
    # ========================================================

    def detectar_rostros(
        self,
        imagen
    ):

        gris = cv2.cvtColor(
            imagen,
            cv2.COLOR_BGR2GRAY
        )

        rostros = self.detector.detectMultiScale(
            gris,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(80, 80)
        )

        return rostros

    # ========================================================
    # GENERAR EMBEDDING
    # ========================================================

    def generar_embedding(
        self,
        rostro
    ):

        try:

            representaciones = DeepFace.represent(
                img_path=rostro,
                model_name="Facenet512",
                detector_backend="skip",
                enforce_detection=False,
                align=False
            )

            if not representaciones:
                return None

            embedding = representaciones[0][
                "embedding"
            ]

            return np.array(
                embedding,
                dtype=np.float32
            )

        except Exception as error:

            print(
                "Error generando embedding:"
            )

            print(error)

            return None

    # ========================================================
    # CARGAR REFERENCIAS DESDE POSTGRESQL
    # ========================================================

    def cargar_referencias(self):

        conexion = None
        cursor = None

        self.referencias = []

        try:

            conexion = conectar_bd()

            cursor = conexion.cursor()

            cursor.execute(
                """
                SELECT
                    f.id,
                    f.alumno_id,
                    a.nombre,
                    a.apellido,
                    f.angulo,
                    f.imagen
                FROM foto_alumno AS f
                INNER JOIN alumno AS a
                    ON a.id = f.alumno_id
                ORDER BY
                    f.alumno_id,
                    f.id;
                """
            )

            registros = cursor.fetchall()

            for registro in registros:

                foto_id = registro[0]
                alumno_id = registro[1]
                nombre = registro[2]
                apellido = registro[3]
                angulo = registro[4]
                imagen_bytes = registro[5]

                # --------------------------------------------
                # BYTEA -> OPENCV
                # --------------------------------------------

                buffer = np.frombuffer(
                    bytes(imagen_bytes),
                    dtype=np.uint8
                )

                imagen = cv2.imdecode(
                    buffer,
                    cv2.IMREAD_COLOR
                )

                if imagen is None:

                    print(
                        f"Foto {foto_id}: imagen inválida."
                    )

                    continue

                # --------------------------------------------
                # DETECTAR EXACTAMENTE UN ROSTRO
                # --------------------------------------------

                rostros = self.detectar_rostros(
                    imagen
                )

                if len(rostros) != 1:

                    print(
                        f"Foto {foto_id} "
                        f"({nombre} {apellido} - {angulo}): "
                        f"omitida porque detectó "
                        f"{len(rostros)} rostros."
                    )

                    continue

                x, y, w, h = rostros[0]

                rostro = imagen[
                    y:y + h,
                    x:x + w
                ]

                # --------------------------------------------
                # EMBEDDING FACENET512
                # --------------------------------------------

                embedding = self.generar_embedding(
                    rostro
                )

                if embedding is None:

                    print(
                        f"Foto {foto_id}: "
                        "no se pudo generar embedding."
                    )

                    continue

                self.referencias.append(
                    {
                        "foto_id": foto_id,
                        "alumno_id": alumno_id,
                        "nombre": nombre,
                        "apellido": apellido,
                        "angulo": angulo,
                        "embedding": embedding
                    }
                )

                print(
                    f"Referencia cargada: "
                    f"{nombre} {apellido} "
                    f"({angulo})"
                )

            print(
                f"\nTotal de referencias válidas: "
                f"{len(self.referencias)}"
            )

            return len(
                self.referencias
            )

        except Exception as error:

            print(
                "Error cargando referencias:"
            )

            print(error)

            return 0

        finally:

            if cursor is not None:
                cursor.close()

            if conexion is not None:
                conexion.close()

    # ========================================================
    # DISTANCIA COSENO
    # ========================================================

    def distancia_coseno(
        self,
        embedding_a,
        embedding_b
    ):

        producto = np.dot(
            embedding_a,
            embedding_b
        )

        norma_a = np.linalg.norm(
            embedding_a
        )

        norma_b = np.linalg.norm(
            embedding_b
        )

        if norma_a == 0 or norma_b == 0:
            return 1.0

        similitud = (
            producto
            / (norma_a * norma_b)
        )

        distancia = (
            1.0 - similitud
        )

        return float(
            distancia
        )

    # ========================================================
    # RECONOCER ROSTRO
    # ========================================================

    def reconocer(
        self,
        imagen,
        rostros=None
    ):

        # La UI puede reutilizar la detección del mismo frame sin repetir Haar.
        # Se conserva reconocer(imagen) para las pruebas y otros consumidores.
        if rostros is None:
            rostros = self.detectar_rostros(
                imagen
            )

        # ----------------------------------------------------
        # SIN ROSTROS
        # ----------------------------------------------------

        if len(rostros) == 0:

            return {
                "estado": "sin_rostro",
                "rostros": []
            }

        # ----------------------------------------------------
        # MÁS DE UN ROSTRO
        # ----------------------------------------------------

        if len(rostros) > 1:

            return {
                "estado": "multiples_rostros",
                "rostros": rostros
            }

        # ----------------------------------------------------
        # EXACTAMENTE UN ROSTRO
        # ----------------------------------------------------

        x, y, w, h = rostros[0]

        rostro = imagen[
            y:y + h,
            x:x + w
        ]

        embedding_actual = (
            self.generar_embedding(
                rostro
            )
        )

        if embedding_actual is None:

            return {
                "estado": "error_embedding",
                "rostros": rostros
            }

        # ----------------------------------------------------
        # COMPARAR CON TODAS LAS REFERENCIAS
        # ----------------------------------------------------

        mejor_referencia = None
        menor_distancia = None

        for referencia in self.referencias:

            distancia = self.distancia_coseno(
                embedding_actual,
                referencia["embedding"]
            )

            if (
                menor_distancia is None
                or distancia < menor_distancia
            ):

                menor_distancia = distancia
                mejor_referencia = referencia

        # ----------------------------------------------------
        # SIN REFERENCIAS
        # ----------------------------------------------------

        if mejor_referencia is None:

            return {
                "estado": "sin_referencias",
                "rostros": rostros
            }

        # ----------------------------------------------------
        # BEST MATCH + THRESHOLD 0.40
        # ----------------------------------------------------

        if menor_distancia <= self.UMBRAL:

            return {
                "estado": "reconocido",
                "alumno_id":
                    mejor_referencia["alumno_id"],
                "nombre":
                    mejor_referencia["nombre"],
                "apellido":
                    mejor_referencia["apellido"],
                "angulo":
                    mejor_referencia["angulo"],
                "distancia":
                    menor_distancia,
                "rostros":
                    rostros
            }

        return {
            "estado": "no_reconocido",
            "distancia": menor_distancia,
            "rostros": rostros
        }