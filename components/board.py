from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QScrollArea, QFrame
from PySide6.QtCore import Qt, Signal
import database
from components.card import CardWidget
from components.list_column import DropArea
from styles.theme import get_theme

class BoardWidget(QWidget):
    card_clicked = Signal(int)
    create_card_requested = Signal(int)
    list_deleted_requested = Signal(int) 

    def __init__(self, parent=None):
        super().__init__(parent)
        self.columns = {}
        self.build_ui()
        self.reload()

    def build_ui(self):
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(25, 20, 25, 25)
        self.main_layout.setSpacing(20)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.setLayout(self.main_layout)

    def reload(self):
        self.clear_layout()
        self.columns = {}
        listas = database.obtener_listas()
        for lista in listas:
            columna = self.create_list_column(lista)
            self.main_layout.addWidget(columna)
        self.main_layout.addStretch()

    def clear_layout(self):
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            widget = item.widget()
            if widget: widget.deleteLater()

    def create_list_column(self, lista):
        c = get_theme()
        container = QFrame()
        container.setFixedWidth(330)
        container.setMinimumHeight(500)
        
        container.setStyleSheet(f"""
            QFrame {{
                background: {c["list_bg"]};
                border-radius: 12px;
            }}
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(14, 16, 14, 14)
        layout.setSpacing(12)

        # TÍTULO Y BOTÓN DE ELIMINAR LISTA
        title_layout = QHBoxLayout()
        title = QLabel(lista["nombre"])
        title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {c['text']}; background: transparent;")
        
        btn_delete_list = QPushButton("🗑️") 
        btn_delete_list.setFixedSize(28, 28)
        btn_delete_list.setCursor(Qt.CursorShape.PointingHandCursor)
        # Ahora el botón tiene un fondo gris visible y se pone rojo al hacer hover
        btn_delete_list.setStyleSheet(f"""
            QPushButton {{ 
                background: {c["surface_secondary"]}; 
                border: none; 
                font-size: 14px; 
                border-radius: 6px; 
            }}
            QPushButton:hover {{ 
                background: {c["red"]}; 
            }}
        """)
        btn_delete_list.clicked.connect(lambda checked=False, id_l=lista["id"]: self.list_deleted_requested.emit(id_l))

        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(btn_delete_list)
        layout.addLayout(title_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        drop_area = DropArea(lista["id"])
        drop_area.setStyleSheet(f"""
            QFrame#drop_area {{ background: transparent; border-radius: 12px; }}
            QFrame#drop_area[drag_active="true"] {{
                background: {c["surface_secondary"]};
                border: 2px dashed {c["blue"]};
            }}
        """)

        cards_layout = QVBoxLayout()
        cards_layout.setContentsMargins(4, 4, 4, 4)
        cards_layout.setSpacing(16)
        cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        drop_area.setLayout(cards_layout)

        tarjetas = database.obtener_tarjetas_por_lista(lista["id"])
        for tarjeta in tarjetas:
            card = CardWidget(tarjeta)
            card.clicked.connect(self.card_clicked.emit)
            cards_layout.addWidget(card)

        drop_area.card_dropped.connect(
            lambda id_tarjeta, idx, l_dest=lista["id"]: self.handle_card_drop(id_tarjeta, l_dest, idx)
        )
        scroll.setWidget(drop_area)
        layout.addWidget(scroll, 1)

        add_card = QPushButton("Añadir")
        add_card.setCursor(Qt.CursorShape.PointingHandCursor)
        add_card.clicked.connect(lambda checked=False, id_lista=lista["id"]: self.create_card_requested.emit(id_lista))
        layout.addWidget(add_card)

        container.setLayout(layout)
        return container

    def get_card_list(self, id_tarjeta):
        tarjeta = database.obtener_tarjeta(id_tarjeta)
        if tarjeta is None: return None
        return tarjeta["id_lista"]

    def handle_card_drop(self, id_tarjeta, id_lista_destino, nuevo_indice):
        id_lista_origen = self.get_card_list(id_tarjeta)
        if id_lista_origen is None: return
        try:
            database.mover_tarjeta(id_tarjeta, id_lista_origen, id_lista_destino, nuevo_indice)
            self.reload()
        except Exception as error:
            print("Error moviendo tarjeta:", error)