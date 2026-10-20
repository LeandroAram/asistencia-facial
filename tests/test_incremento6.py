"""Ejecutar: python -m unittest discover -s tests -v.

TEST_POSTGRES=1 habilita además consultas en tablas TEMPORARY, sin tocar datos reales.
"""
import os
import tempfile
import time
import unittest
from datetime import date, datetime, time as hora_python
from pathlib import Path
from unittest.mock import Mock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox
from openpyxl import load_workbook

from src.database import informes
from src.reports.exportador import exportar_informe, contador, nombre_sugerido, SIN_ASISTENCIAS
from src.ui.exportar_informes import ExportarInformesWidget
from src.ui.main_window import MainWindow


JORNADA = dict(id=10, fecha=date(2026, 10, 20), catedra="Reconocimiento Visual",
               horario_entrada=hora_python(8), horario_salida=hora_python(9, 20),
               nombre_usuario="docente_prueba")
ALUMNO = dict(apellido="Pérez", nombre="Ana", dni="00123456", libreta="=A-001",
              entrada=datetime(2026, 10, 20, 8, 3), salida=None)
APP = QApplication.instance() or QApplication([])
APP.setQuitOnLastWindowClosed(False)


def esperar(condicion):
    limite = time.monotonic() + 10
    while not condicion() and time.monotonic() < limite:
        QTest.qWait(20)
    assert condicion(), "La operación no terminó"


class FormulariosTest(unittest.TestCase):
    def setUp(self):
        self.ventana = MainWindow(1, "docente_prueba")

    def tearDown(self):
        self.ventana.close()

    def test_horas_sin_separador_y_validacion(self):
        entrada = self.ventana.horario_entrada_input
        QTest.keyClicks(entrada, "08")
        self.assertEqual(entrada.cursorPosition(), 3)
        QTest.keyClicks(entrada, "30")
        self.assertEqual(entrada.text(), "08:30")
        self.assertTrue(entrada.hasAcceptableInput())
        entrada.setText("25:90")
        self.assertFalse(entrada.hasAcceptableInput())
        entrada.clear()
        self.assertFalse(entrada.hasAcceptableInput())
        salida = self.ventana.horario_salida_input
        QTest.keyClicks(salida, "0920")
        self.assertEqual(salida.text(), "09:20")

    def test_fecha_escritura_pegado_y_bisiesto(self):
        campo = self.ventana.pagina_alumno.fecha_nacimiento_input
        QTest.keyClicks(campo, "15")
        self.assertEqual(campo.cursorPosition(), 3)
        QTest.keyClicks(campo, "032005")
        self.assertEqual(campo.date().toString("yyyy-MM-dd"), "2005-03-15")
        campo.selectAll()
        APP.clipboard().setText("29022004")
        QTest.keyClick(campo, Qt.Key_V, Qt.ControlModifier)
        self.assertEqual(campo.text(), "29/02/2004")
        self.assertTrue(campo.date().isValid())
        campo.setText("29022005")
        self.assertFalse(campo.date().isValid())
        self.ventana.pagina_alumno.limpiar_formulario()
        self.assertFalse(campo.date().isValid())

    def test_fecha_imposible_o_futura_no_llega_a_la_base(self):
        formulario = self.ventana.pagina_alumno
        for atributo in ["nombre_input", "apellido_input", "dni_input", "carrera_input",
                         "celular_input", "correo_input", "domicilio_input", "libreta_input"]:
            getattr(formulario, atributo).setText("prueba")
        formulario.anio_ingreso_input.setValue(2020)
        for atributo in ["foto_frontal", "foto_izquierda", "foto_derecha"]:
            getattr(formulario, atributo).obtener_bytes = Mock(return_value=b"foto")
        with patch("src.ui.registro_alumno.registrar_alumno") as guardar, \
             patch.object(QMessageBox, "warning") as aviso:
            for fecha in ["31022005", "01012999", "01011899"]:
                formulario.fecha_nacimiento_input.setText(fecha)
                formulario.registrar()
            guardar.assert_not_called()
            self.assertEqual(aviso.call_count, 3)

    def test_ir_informes_refresca_sin_perder_jornada_ni_camara(self):
        ventana = self.ventana
        ventana.jornada_id = 42
        ventana.camera = Mock()
        with patch.object(ventana.pagina_informes, "refrescar") as refrescar:
            ventana.ir_informes()
            ventana.ir_jornada()
            ventana.ir_informes()
            self.assertEqual(refrescar.call_count, 2)
        self.assertEqual(ventana.jornada_id, 42)
        ventana.camera.cerrar.assert_not_called()
        self.assertIs(ventana.paginas.currentWidget(), ventana.pagina_informes)


class ExportacionTest(unittest.TestCase):
    def test_excel_vacio_uno_varios_y_datos_textuales(self):
        with tempfile.TemporaryDirectory(dir=os.getenv("TEST_TMPDIR")) as carpeta:
            for cantidad in [0, 1, 80]:
                ruta = Path(carpeta) / f"asistencia-{cantidad}.xlsx"
                exportar_informe(ruta, "xlsx", JORNADA, [ALUMNO.copy() for _ in range(cantidad)])
                libro = load_workbook(ruta)
                hoja = libro.active
                valores = [c.value for fila in hoja for c in fila]
                self.assertIn(contador(cantidad), valores)
                self.assertEqual(hoja["C7"].value, "docente_prueba")
                if cantidad:
                    self.assertEqual(hoja["D10"].value, "00123456")
                    self.assertEqual(hoja["E10"].data_type, "s")
                    self.assertEqual(hoja["F10"].value, "08:03")
                    self.assertEqual(hoja["G10"].value, "Sin registrar")
                else:
                    self.assertIn(SIN_ASISTENCIAS, valores)
                libro.close()

    def test_pdf_vacio_y_multipagina(self):
        with tempfile.TemporaryDirectory(dir=os.getenv("TEST_TMPDIR")) as carpeta:
            for cantidad in [0, 1, 80]:
                ruta = Path(carpeta) / f"asistencia-{cantidad}.pdf"
                exportar_informe(ruta, "pdf", JORNADA, [ALUMNO.copy() for _ in range(cantidad)])
                self.assertTrue(ruta.read_bytes().startswith(b"%PDF-"))

    def test_fallo_no_destruye_archivo_existente(self):
        with tempfile.TemporaryDirectory(dir=os.getenv("TEST_TMPDIR")) as carpeta:
            ruta = Path(carpeta) / "existente.xlsx"
            ruta.write_bytes(b"original")
            with patch("src.reports.exportador.generar_excel", side_effect=OSError("sin espacio")):
                with self.assertRaises(OSError):
                    exportar_informe(ruta, "xlsx", JORNADA, [])
            self.assertEqual(ruta.read_bytes(), b"original")
            self.assertEqual(len(list(Path(carpeta).iterdir())), 1)

    def test_nombre_seguro_y_contadores(self):
        self.assertEqual(nombre_sugerido(JORNADA, "pdf"),
                         "asistencia_2026-10-20_reconocimiento-visual.pdf")
        self.assertEqual(contador(1), "Se registró 1 alumno presente en total.")
        self.assertEqual(contador(0), "Se registraron 0 alumnos presentes en total.")


class PantallaInformesTest(unittest.TestCase):
    def test_cancelar_no_consulta_ni_crea(self):
        panel = ExportarInformesWidget(1)
        with patch("src.ui.exportar_informes.QFileDialog.getSaveFileName", return_value=("", "")), \
             patch.object(panel, "iniciar") as iniciar:
            panel.exportar(JORNADA, "pdf")
            iniciar.assert_not_called()
        panel.close()

    def test_refrescar_y_exportar_en_segundo_plano(self):
        panel = ExportarInformesWidget(7)
        with tempfile.TemporaryDirectory(dir=os.getenv("TEST_TMPDIR")) as carpeta, \
             patch("src.ui.exportar_informes.listar_jornadas", return_value=[JORNADA]) as listar, \
             patch("src.ui.exportar_informes.obtener_informe", return_value=(JORNADA, [ALUMNO])) as obtener, \
             patch.object(QMessageBox, "information") as aviso:
            panel.refrescar()
            esperar(lambda: panel.trabajo is None)
            listar.assert_called_once_with(7)
            self.assertEqual(panel.tabla.rowCount(), 1)
            self.assertEqual(panel.tabla.item(0, 2).text(), "08:00 - 09:20")
            ruta = str(Path(carpeta) / "elegido")
            with patch("src.ui.exportar_informes.QFileDialog.getSaveFileName", return_value=(ruta, "")):
                panel.exportar(JORNADA, "xlsx")
                esperar(lambda: panel.trabajo is None)
            obtener.assert_called_once_with(7, 10)
            self.assertTrue(Path(ruta + ".xlsx").exists())
            aviso.assert_called_once()
        panel.close()

    def test_error_de_base_se_puede_reintentar(self):
        panel = ExportarInformesWidget(7)
        with patch("src.ui.exportar_informes.listar_jornadas", side_effect=RuntimeError("prueba")), \
             patch.object(QMessageBox, "warning"):
            panel.refrescar()
            esperar(lambda: panel.trabajo is None)
            self.assertTrue(panel.actualizar.isEnabled())
            self.assertIn("No se pudo", panel.estado.text())
        panel.close()


@unittest.skipUnless(os.getenv("TEST_POSTGRES") == "1", "Requiere TEST_POSTGRES=1")
class ConsultasPostgresTest(unittest.TestCase):
    def test_propietario_orden_y_asistencias(self):
        from src.database.conexion import conectar_bd
        conexion = conectar_bd()
        try:
            with conexion.cursor() as c:
                c.execute("""
                    CREATE TEMP TABLE usuario (id integer, nombre_usuario text);
                    CREATE TEMP TABLE jornada (id integer, fecha date, horario_entrada time,
                        horario_salida time, usuario_id integer, catedra text);
                    CREATE TEMP TABLE alumno (id integer, apellido text, nombre text, dni text, libreta text);
                    CREATE TEMP TABLE asistencia (jornada_id integer, alumno_id integer, entrada timestamp, salida timestamp);
                    INSERT INTO usuario VALUES (1,'docente'), (2,'otro');
                    INSERT INTO jornada VALUES
                      (10,'2026-10-19','08:00','09:20',1,'Anterior'),
                      (11,'2026-10-20','08:00','09:20',1,'Mañana'),
                      (12,'2026-10-20','18:00','19:20',1,'Tarde'),
                      (13,'2026-10-21','08:00','09:20',2,'Ajena');
                    INSERT INTO alumno VALUES
                      (1,'Pérez','Juan','001','A'), (2,'Alonso','Zoe','002','B'),
                      (3,'Alonso','Ana','003','C'), (4,'Ausente','Ana','004','D');
                    INSERT INTO asistencia VALUES
                      (12,1,'2026-10-20 18:01',NULL),
                      (12,2,'2026-10-20 18:02','2026-10-20 19:20'),
                      (12,3,'2026-10-20 18:03',NULL),
                      (13,4,'2026-10-21 08:00',NULL);
                """)
            # Las tablas de prueba viven en una transacción ya abierta.
            proxy = Mock(wraps=conexion)
            proxy.close = Mock()
            proxy.set_session = Mock()
            with patch.object(informes, "conectar_bd", return_value=proxy):
                self.assertEqual([j["id"] for j in informes.listar_jornadas(1)], [12, 11, 10])
                with self.assertRaises(ValueError):
                    informes.obtener_informe(1, 13)
                jornada, alumnos = informes.obtener_informe(1, 12)
                self.assertEqual(jornada["nombre_usuario"], "docente")
                self.assertEqual([a["dni"] for a in alumnos], ["003", "002", "001"])
                self.assertIsNone(alumnos[-1]["salida"])
                self.assertEqual(informes.obtener_informe(1, 10)[1], [])
                with conexion.cursor() as c:
                    c.execute("INSERT INTO jornada VALUES (14,'2026-10-22','08:00','09:20',1,'Nueva')")
                self.assertEqual(informes.listar_jornadas(1)[0]["id"], 14)
        finally:
            conexion.rollback()
            conexion.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
