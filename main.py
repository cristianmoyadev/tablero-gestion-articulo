import ctypes
import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QPushButton, QScrollArea, QDialog, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

import database
from components.board import BoardWidget
from components.dialogs import CardDialog, ListDialog
from styles.theme import build_stylesheet

def obtener_ruta_recurso(nombre_archivo):
    if getattr(sys, 'frozen', False):
        # Si se está ejecutando como .exe, busca en la carpeta temporal
        ruta_base = sys._MEIPASS
    else:
        # Si se está ejecutando normalmente desde Python
        ruta_base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(ruta_base, nombre_archivo)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("nnColection")
        ruta_icono = obtener_ruta_recurso("icono.ico")
        self.setWindowIcon(QIcon(ruta_icono))
        self.resize(1400, 850)
        self.setMinimumSize(900, 600)
        
        self.build_ui()
        self.apply_theme()

    def build_ui(self):
        central = QWidget()
        central.setObjectName("central_widget")
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        central.setLayout(self.main_layout)

        # TOP BAR
        self.top_bar = QWidget()
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(30, 20, 30, 20)

        title_container = QVBoxLayout()
        self.title = QLabel("nnColection")
        self.title.setObjectName("app_title")
        self.subtitle = QLabel("Mis colecciones")
        self.subtitle.setObjectName("app_subtitle")

        title_container.addWidget(self.title)
        title_container.addWidget(self.subtitle)
        top_layout.addLayout(title_container)
        top_layout.addStretch()

        # NUEVA LISTA
        self.new_list_button = QPushButton("Nueva lista")
        self.new_list_button.setObjectName("primary_btn")
        self.new_list_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.new_list_button.clicked.connect(self.open_new_list)
        top_layout.addWidget(self.new_list_button)

        self.top_bar.setLayout(top_layout)
        self.main_layout.addWidget(self.top_bar)

        # TABLERO / SCROLL
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.board = BoardWidget()
        self.board.setObjectName("board_widget")
        self.board.card_clicked.connect(self.open_card)
        self.board.create_card_requested.connect(self.open_new_card)
        
        # Conectar señal de eliminar lista
        self.board.list_deleted_requested.connect(self.delete_list)
        
        self.scroll.setWidget(self.board)
        self.main_layout.addWidget(self.scroll, 1)

    def apply_theme(self):
        self.setStyleSheet(build_stylesheet())

    def open_new_list(self):
        dialog = ListDialog(self)
        dialog.setStyleSheet(build_stylesheet())
        if dialog.exec() == QDialog.DialogCode.Accepted:
            database.crear_lista(dialog.get_name())
            self.board.reload()

    def delete_list(self, id_lista):
        # Diálogo de confirmación antes de borrar
        resp = QMessageBox.question(
            self, 
            "Eliminar Lista", 
            "¿Estás seguro de que quieres eliminar esta lista? \n¡Se borrarán todas las tarjetas dentro de ella!", 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if resp == QMessageBox.StandardButton.Yes:
            database.eliminar_lista(id_lista)
            self.board.reload()

    def open_new_card(self, id_lista):
        dialog = CardDialog(self)
        dialog.setStyleSheet(build_stylesheet())
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            database.crear_tarjeta(
                id_lista=id_lista, titulo=data["titulo"], descripcion=data["descripcion"],
                url=data["url"], foto_ruta=data["foto_ruta"], precio=data["precio"],
                moneda=data["moneda"], estado=data["estado"]
            )
            self.board.reload()

    def open_card(self, id_tarjeta):
        tarjeta = database.obtener_tarjeta(id_tarjeta)
        if not tarjeta: return
        
        dialog = CardDialog(self, tarjeta=tarjeta)
        dialog.setStyleSheet(build_stylesheet())
        if dialog.exec() == QDialog.DialogCode.Accepted:
            if getattr(dialog, 'is_deleted', False):
                database.eliminar_tarjeta(id_tarjeta)
            else:
                data = dialog.get_data()
                database.actualizar_tarjeta(
                    id_tarjeta, data["titulo"], data["descripcion"], data["url"],
                    data["foto_ruta"], data["precio"], data["moneda"], data["estado"]
                )
            self.board.reload()

def main():
    try:
        myappid = 'mi.app.coleccion.1.0' 
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()




# .exe
# python -m PyInstaller --noconsole --onefile --icon=icono.ico --add-data "icono.ico;." -n "nnColection_beta" main.py
# (queda en la carpeta dist)
# para empaquetar borrar build, dist y.spec
