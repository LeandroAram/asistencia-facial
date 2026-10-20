"""Consultas de informes, siempre limitadas al propietario de la Jornada."""
from contextlib import closing

from psycopg2.extras import RealDictCursor

from src.database.conexion import conectar_bd


def listar_jornadas(usuario_id):
    with closing(conectar_bd()) as conexion:
        conexion.set_session(readonly=True)
        with conexion.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT id, fecha, catedra, horario_entrada, horario_salida
                FROM jornada WHERE usuario_id = %s
                ORDER BY fecha DESC, horario_entrada DESC, id DESC
            """, (usuario_id,))
            return [dict(fila) for fila in cursor.fetchall()]


def obtener_informe(usuario_id, jornada_id):
    # Una sola instantánea para los datos de Jornada y sus asistencias.
    with closing(conectar_bd()) as conexion:
        conexion.set_session(readonly=True, isolation_level="REPEATABLE READ")
        with conexion.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT j.id, j.fecha, j.catedra, j.horario_entrada,
                       j.horario_salida, u.nombre_usuario
                FROM jornada j JOIN usuario u ON u.id = j.usuario_id
                WHERE j.id = %s AND j.usuario_id = %s
            """, (jornada_id, usuario_id))
            jornada = cursor.fetchone()
            if jornada is None:
                raise ValueError("La Jornada no existe o no pertenece a su usuario.")
            cursor.execute("""
                SELECT al.apellido, al.nombre, al.dni, al.libreta,
                       a.entrada, a.salida
                FROM asistencia a
                JOIN jornada j ON j.id = a.jornada_id
                JOIN alumno al ON al.id = a.alumno_id
                WHERE j.id = %s AND j.usuario_id = %s
                ORDER BY al.apellido, al.nombre, al.id
            """, (jornada_id, usuario_id))
            return dict(jornada), [dict(fila) for fila in cursor.fetchall()]
