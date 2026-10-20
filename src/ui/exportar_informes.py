"""Listado y exportación sin bloquear el hilo de la interfaz."""
from pathlib import Path

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal, Slot, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QFileDialog, QMessageBox, QAbstractItemView,
)

from src.database.informes import listar_jornadas, obtener_informe
from src.reports.exportador import exportar_informe, hora, nombre_sugerido


class SenalesInforme(QObject):
    terminado = Signal(object)


class TrabajoInforme(QRunnable):
    def __init__(self, tipo, funcion):
        super().__init__()
        self.tipo = tipo
        self.funcion = funcion
        self.senales = SenalesInforme()

    def run(self):
        try:
            respuesta = {"tipo": self.tipo, "datos": self.funcion()}
        except Exception as error:
            print("Error de informes:", error)
            respuesta = {"tipo": self.tipo, "error": True}
        self.senales.terminado.emit(respuesta)


class ExportarInformesWidget(QWidget):
    def __init__(self, usuario_id):
        super().__init__()
        self.usuario_id = usuario_id
        self.trabajo = None
        self.refresco_pendiente = False
        self.jornadas = []
        layout = QVBoxLayout(self)
        self.estado = QLabel("Consulte sus Jornadas y guarde una planilla de asistencia.")
        self.estado.setWordWrap(True)
        layout.addWidget(self.estado)
        self.tabla = QTableWidget(0, 5)
        self.tabla.setHorizontalHeaderLabels(["Fecha", "Cátedra", "Horario", "Excel", "PDF"])
        self.tabla.verticalHeader().hide()
        self.tabla.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabla.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabla.setStyleSheet("""
            QTableWidget { background: #101b2d; alternate-background-color: #17263a;
                           color: #eef4ff; gridline-color: #30425d; }
            QHeaderView::section { background: #203450; color: white; padding: 10px;
                                   border: 0; font-weight: bold; }
        """)
        layout.addWidget(self.tabla)
        self.actualizar = QPushButton("Actualizar listado")
        self.actualizar.clicked.connect(self.refrescar)
        layout.addWidget(self.actualizar, alignment=Qt.AlignLeft)

    def iniciar(self, tipo, funcion):
        self.tabla.setEnabled(False)
        self.actualizar.setEnabled(False)
        self.trabajo = TrabajoInforme(tipo, funcion)
        self.trabajo.senales.terminado.connect(self.recibir, Qt.QueuedConnection)
        QThreadPool.globalInstance().start(self.trabajo)

    def refrescar(self):
        if self.trabajo is not None:
            self.refresco_pendiente = True
            return
        self.tabla.setRowCount(0)
        self.estado.setText("Consultando Jornadas...")
        self.iniciar("listar", lambda: listar_jornadas(self.usuario_id))

    @Slot(object)
    def recibir(self, respuesta):
        self.trabajo = None
        self.tabla.setEnabled(True)
        self.actualizar.setEnabled(True)
        if respuesta.get("error"):
            self.estado.setText("No se pudo completar la operación. Revise la conexión o la ubicación del archivo e intente nuevamente.")
            QMessageBox.warning(self, "Informe no disponible", self.estado.text())
        elif respuesta["tipo"] == "listar":
            self.jornadas = respuesta["datos"]
            self.mostrar_jornadas()
        else:
            self.estado.setText("Informe creado correctamente.")
            QMessageBox.information(self, "Informe creado", f"Archivo guardado en:\n{respuesta['datos']}")
        if self.refresco_pendiente:
            self.refresco_pendiente = False
            self.refrescar()

    def mostrar_jornadas(self):
        self.tabla.setRowCount(len(self.jornadas))
        for fila, jornada in enumerate(self.jornadas):
            valores = [jornada["fecha"].strftime("%d/%m/%Y"), jornada["catedra"] or "Sin cátedra",
                       f"{hora(jornada['horario_entrada'])} - {hora(jornada['horario_salida'])}"]
            for columna, valor in enumerate(valores):
                self.tabla.setItem(fila, columna, QTableWidgetItem(valor))
            for columna, formato, etiqueta in [(3, "xlsx", "Excel"), (4, "pdf", "PDF")]:
                boton = QPushButton(etiqueta)
                boton.clicked.connect(lambda checked=False, j=jornada, f=formato: self.exportar(j, f))
                self.tabla.setCellWidget(fila, columna, boton)
            self.tabla.setRowHeight(fila, 48)
        self.estado.setText(
            "Seleccione Excel o PDF en la Jornada que desea exportar."
            if self.jornadas else "Todavía no tiene Jornadas registradas."
        )

    def exportar(self, jornada, formato):
        if self.trabajo is not None:
            return
        filtro = "Excel (*.xlsx)" if formato == "xlsx" else "PDF (*.pdf)"
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Guardar informe", nombre_sugerido(jornada, formato), filtro
        )
        if not ruta:
            return
        destino = Path(ruta)
        if destino.suffix.lower() != f".{formato}":
            destino = Path(str(destino) + f".{formato}")
            # El diálogo sólo confirmó la ruta original, no la extensión añadida.
            if destino.exists() and QMessageBox.question(
                self, "Reemplazar archivo", f"Ya existe {destino.name}. ¿Desea reemplazarlo?"
            ) != QMessageBox.Yes:
                return
        self.estado.setText("Generando informe...")
        def generar():
            datos, alumnos = obtener_informe(self.usuario_id, jornada["id"])
            return exportar_informe(destino, formato, datos, alumnos)
        self.iniciar("exportar", generar)
