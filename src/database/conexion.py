import os
from pathlib import Path

import psycopg2

from psycopg2 import Binary
from psycopg2 import errors

from dotenv import load_dotenv


# ============================================================
# VARIABLES DE ENTORNO
# ============================================================

BASE_DIR = Path(
    __file__
).resolve().parents[2]

load_dotenv(
    BASE_DIR / ".env"
)


# ============================================================
# CONEXIÓN A POSTGRESQL
# ============================================================

def conectar_bd():

    return psycopg2.connect(

        host=os.getenv(
            "POSTGRES_HOST"
        ),

        port=os.getenv(
            "POSTGRES_PORT"
        ),

        dbname=os.getenv(
            "POSTGRES_DB"
        ),

        user=os.getenv(
            "POSTGRES_USER"
        ),

        password=os.getenv(
            "POSTGRES_PASSWORD"
        )
    )


# ============================================================
# VALIDAR USUARIO
# ============================================================

def validar_usuario(
    identificador,
    contrasenia
):

    conexion = None

    try:

        conexion = conectar_bd()

        cursor = conexion.cursor()

        consulta = """
            SELECT
                id,
                nombre_usuario
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

        print(
            "Error al validar usuario:"
        )

        print(error)

        return None

    finally:

        if conexion is not None:

            conexion.close()


# ============================================================
# REGISTRAR ALUMNO
# ============================================================

def registrar_alumno(
    datos,
    fotos
):

    conexion = None
    cursor = None

    try:

        conexion = conectar_bd()

        cursor = conexion.cursor()

        # ----------------------------------------------------
        # INSERTAR DATOS DEL ALUMNO
        # ----------------------------------------------------

        consulta_alumno = """
            INSERT INTO alumno (
                nombre,
                apellido,
                dni,
                carrera,
                celular,
                correo_electronico,
                fecha_nacimiento,
                anio_ingreso,
                domicilio,
                libreta
            )
            VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )
            RETURNING id;
        """

        cursor.execute(
            consulta_alumno,
            (
                datos["nombre"],
                datos["apellido"],
                datos["dni"],
                datos["carrera"],
                datos["celular"],
                datos["correo_electronico"],
                datos["fecha_nacimiento"],
                datos["anio_ingreso"],
                datos["domicilio"],
                datos["libreta"]
            )
        )

        alumno_id = (
            cursor.fetchone()[0]
        )

        # ----------------------------------------------------
        # INSERTAR LAS TRES FOTOGRAFÍAS
        # ----------------------------------------------------

        consulta_foto = """
            INSERT INTO foto_alumno (
                alumno_id,
                angulo,
                imagen
            )
            VALUES (
                %s,
                %s,
                %s
            );
        """

        for angulo in [
            "frontal",
            "izquierdo",
            "derecho"
        ]:

            cursor.execute(
                consulta_foto,
                (
                    alumno_id,
                    angulo,
                    Binary(
                        fotos[angulo]
                    )
                )
            )

        conexion.commit()

        return (
            True,
            "Alumno registrado exitosamente."
        )

    # ========================================================
    # CAMPOS UNIQUE
    # ========================================================

    except errors.UniqueViolation as error:

        if conexion is not None:
            conexion.rollback()

        restriccion = (
            error.diag.constraint_name
        )

        if restriccion == "alumno_dni_unique":

            mensaje = (
                "Ya existe un alumno "
                "con ese DNI."
            )

        elif restriccion == (
            "alumno_correo_electronico_unique"
        ):

            mensaje = (
                "Ya existe un alumno "
                "con ese correo electrónico."
            )

        elif restriccion == (
            "alumno_libreta_unique"
        ):

            mensaje = (
                "Ya existe un alumno "
                "con ese número de libreta."
            )

        else:

            mensaje = (
                "Ya existe un alumno "
                "con alguno de esos datos."
            )

        return (
            False,
            mensaje
        )

    # ========================================================
    # OTROS ERRORES
    # ========================================================

    except Exception as error:

        if conexion is not None:
            conexion.rollback()

        print(
            "Error al registrar alumno:"
        )

        print(error)

        return (
            False,
            "Ocurrió un error al registrar el alumno."
        )

    finally:

        if cursor is not None:
            cursor.close()

        if conexion is not None:
            conexion.close()


# ============================================================
# PRUEBA DIRECTA DE CONEXIÓN
# ============================================================

if __name__ == "__main__":

    conexion = None
    cursor = None

    try:

        conexion = conectar_bd()

        cursor = conexion.cursor()

        cursor.execute(
            """
            SELECT
                current_database(),
                current_user;
            """
        )

        resultado = cursor.fetchone()

        print(
            "Conexión exitosa."
        )

        print(
            "Base de datos:",
            resultado[0]
        )

        print(
            "Usuario:",
            resultado[1]
        )

    except Exception as error:

        print(
            "Error al conectar con PostgreSQL:"
        )

        print(error)

    finally:

        if cursor is not None:
            cursor.close()

        if conexion is not None:
            conexion.close()