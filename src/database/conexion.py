import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv


# Ruta a la carpeta principal del proyecto
BASE_DIR = Path(__file__).resolve().parents[2]

# Cargar variables del archivo .env
load_dotenv(BASE_DIR / ".env")


def conectar_bd():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD")
    )


def validar_usuario(identificador, contrasenia):
    conexion = None

    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()

        consulta = """
            SELECT id, nombre_usuario
            FROM usuario
            WHERE (
                nombre_usuario = %s
                OR correo_electronico = %s
                OR dni = %s
                OR cuil = %s
            )
            AND contrasenia = %s;
        """

        cursor.execute(
            consulta,
            (
                identificador,
                identificador,
                identificador,
                identificador,
                contrasenia
            )
        )

        usuario = cursor.fetchone()
        cursor.close()

        return usuario

    except Exception as error:
        print("Error al validar usuario:")
        print(error)
        return None

    finally:
        if conexion is not None:
            conexion.close()


if __name__ == "__main__":
    conexion = None

    try:
        conexion = conectar_bd()

        cursor = conexion.cursor()
        cursor.execute("SELECT current_database(), current_user;")

        resultado = cursor.fetchone()

        print("Conexión exitosa.")
        print("Base de datos:", resultado[0])
        print("Usuario:", resultado[1])

        cursor.close()

    except Exception as error:
        print("Error al conectar con PostgreSQL:")
        print(error)

    finally:
        if conexion is not None:
            conexion.close()