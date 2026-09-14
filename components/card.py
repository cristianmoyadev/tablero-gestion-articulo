from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, Signal, QMimeData, QUrl
from PySide6.QtGui import QPixmap, QColor, QDrag, QDesktopServices, QPainter, QBrush
from styles.theme import get_theme

# AHORA HEREDA DE QFrame PARA QUE EL FONDO CSS FUNCIONE SIEMPRE
class CardWidget(QFrame):
    clicked = Signal(int)

    def __init__(self, tarjeta):
        super().__init__()
        self.tarjeta = tarjeta
        self.drag_start_position = None
        
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.setMinimumWidth(280)
        self.setMaximumWidth(310)
        self.setObjectName("card")
        self.build_ui()

    def build_ui(self):
        c = get_theme()
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 12)
        layout.setSpacing(10)

        # IMAGEN PERFECTAMENTE REDONDEADA
        image_label = QLabel()
        image_label.setFixedSize(284, 160) 
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setStyleSheet(f"""
            background: {c["surface_secondary"]};
            border-radius: 10px;
            color: {c["secondary_text"]};
        """)

        ruta = self.tarjeta["foto_ruta"]
        if ruta:
            pixmap = QPixmap(ruta)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(284, 160, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                rounded_pixmap = self.round_image_corners(pixmap, 10)
                image_label.setPixmap(rounded_pixmap)
            else:
                image_label.setText("Imagen no disp.")
        else:
            image_label.setText("Sin imagen")
        layout.addWidget(image_label)

        # INFORMACIÓN
        info = QFrame()
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(8, 0, 8, 0)
        info_layout.setSpacing(6)

        title = QLabel(self.tarjeta["titulo"])
        title.setWordWrap(True)
        title.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {c['text']}; background: transparent; border: none;")
        info_layout.addWidget(title)

        # PRECIO Y BOTÓN URL
        bottom_layout = QHBoxLayout()
        precio = self.tarjeta["precio"]
        moneda = self.tarjeta["moneda"]
        texto_precio = ""
        
        if precio is not None:
            if moneda == "CLP": texto_precio = f"${precio:,.0f} CLP"
            elif moneda == "USD": texto_precio = f"${precio:,.2f} USD"
            elif moneda == "EUR": texto_precio = f"€{precio:,.2f} EUR"
            else: texto_precio = str(precio)
            
        price_label = QLabel(texto_precio)
        price_label.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {c['green']}; background: transparent; border: none;")
        bottom_layout.addWidget(price_label)
        bottom_layout.addStretch()

        raw_url = self.tarjeta["url"]
        url_text = raw_url.strip() if raw_url else ""
        if url_text:
            btn_link = QPushButton("Ir")
            btn_link.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_link.setStyleSheet(f"""
                QPushButton {{
                    background-color: {c['blue']};
                    color: #FFFFFF;
                    border-radius: 6px;
                    padding: 4px 10px;
                    font-size: 11px;
                    font-weight: bold;
                    border: none;
                }}
                QPushButton:hover {{ background-color: #1D4ED8; }}
            """)
            btn_link.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(url_text)))
            bottom_layout.addWidget(btn_link)

        info_layout.addLayout(bottom_layout)
        info.setLayout(info_layout)
        layout.addWidget(info)
        self.setLayout(layout)

        # INDICADOR DE ESTADO
        estado = self.tarjeta["estado"]
        color = None
        if estado == "prioridad": color = c["yellow"]
        elif estado == "comprado": color = c["green"]

        if color:
            indicator = QLabel(self)
            indicator.setFixedSize(14, 14)
            indicator.setStyleSheet(f"background: {color}; border-radius: 7px; border: 2px solid {c['card_bg']};")
            indicator.move(275, 18)
            indicator.raise_()

        # ESTILO TARJETA
        self.setStyleSheet(f"""
            QFrame#card {{
                background-color: {c["card_bg"]};
                border: 1px solid {c["border"]};
                border-radius: 14px;
            }}
            QFrame#card:hover {{ border: 1px solid {c["blue"]}; }}
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)

    def round_image_corners(self, pixmap, radius):
        rounded = QPixmap(pixmap.size())
        rounded.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(pixmap))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rounded.rect(), radius, radius)
        painter.end()
        return rounded

    def mousePressEvent(self, event):
        if self.childAt(event.position().toPoint()) and isinstance(self.childAt(event.position().toPoint()), QPushButton):
            super().mousePressEvent(event)
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.position()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton) or self.drag_start_position is None: return
        distancia = (event.position() - self.drag_start_position).manhattanLength()
        if distancia < 10: return
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(str(self.tarjeta["id"]))
        drag.setMimeData(mime_data)
        drag.setPixmap(self.grab())
        drag.setHotSpot(event.position().toPoint())
        self.setWindowOpacity(0.5)
        drag.exec(Qt.DropAction.MoveAction)
        self.setWindowOpacity(1.0)

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.CursorShape.OpenHandCursor)
        if self.drag_start_position is not None:
            distancia = (event.position() - self.drag_start_position).manhattanLength()
            if distancia < 10:
                if not (self.childAt(event.position().toPoint()) and isinstance(self.childAt(event.position().toPoint()), QPushButton)):
                    self.clicked.emit(self.tarjeta["id"])
        self.drag_start_position = None
        super().mouseReleaseEvent(event)