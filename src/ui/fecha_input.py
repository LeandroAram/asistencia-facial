from PySide6.QtCore import QDate, QTime
from PySide6.QtWidgets import QLineEdit


class FechaInput(QLineEdit):
    """Fecha escrita de corrido: 15032005 se muestra como 15/03/2005."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setInputMask("00/00/0000;_")
        self.setToolTip("Escriba día, mes y año (8 números). Ejemplo: 15032005.")
        self.setAccessibleName("Fecha de nacimiento, día mes y año")

    def date(self):
        if not self.hasAcceptableInput():
            return QDate()
        return QDate.fromString(self.text(), "dd/MM/yyyy")


class HorarioInput(QLineEdit):
    """La máscara permite escribir seguido; la validez se comprueba al guardar."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setInputMask("00:00;_")
        self.setToolTip("Escriba 4 números. Ejemplo: 0830 para 08:30.")

    def hasAcceptableInput(self):
        return super().hasAcceptableInput() and QTime.fromString(self.text(), "HH:mm").isValid()
