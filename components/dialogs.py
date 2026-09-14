from pathlib import Path
from uuid import uuid4
import shutil

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                               QTextEdit, QComboBox, QPushButton, QMessageBox, QFileDialog, QWidget)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QPixmap, QDesktopServices
import database

class CardDialog(QDialog):
    def __init__(self, parent=None, tarjeta=None):
        super().__init__(parent)
        self.tarjeta = tarjeta
        self.selected_image_path = tarjeta["foto_ruta"] if tarjeta else ""
        self.is_deleted = False
        
        self.setWindowTitle("Editar artículo" if tarjeta else "Nuevo artículo")
        self.setMinimumWidth(500)
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # PREVIEW IMAGEN
        self.image_preview = QLabel()
        self.image_preview.setFixedHeight(220)
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview.setStyleSheet("border-radius: 12px; background: rgba(255,255,255,0.05);")
        self.update_image_preview()
        layout.addWidget(self.image_preview)

        # BOTONES IMAGEN
        image_buttons = QHBoxLayout()
        choose_image_button = QPushButton("Elegir imagen")
        choose_image_button.clicked.connect(self.choose_image)
        remove_image_button = QPushButton("Quitar imagen")
        remove_image_button.clicked.connect(self.remove_image)
        image_buttons.addWidget(choose_image_button)
        image_buttons.addWidget(remove_image_button)
        layout.addLayout(image_buttons)

        # NOMBRE
        layout.addWidget(QLabel("Nombre"))
        self.title_input = QLineEdit()
        if self.tarjeta: self.title_input.setText(self.tarjeta["titulo"])
        layout.addWidget(self.title_input)

        # DESCRIPCIÓN
        layout.addWidget(QLabel("Descripción"))
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(90)
        if self.tarjeta: self.description_input.setPlainText(self.tarjeta["descripcion"])
        layout.addWidget(self.description_input)

        # URL + BOTÓN IR
        layout.addWidget(QLabel("Link de compra"))
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://tienda.com/...")
        if self.tarjeta: self.url_input.setText(self.tarjeta["url"])
        
        btn_go = QPushButton("Ir")
        btn_go.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_go.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(self.url_input.text().strip())))
        
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(btn_go)
        layout.addLayout(url_layout)

        # PRECIO Y MONEDA
        price_layout = QHBoxLayout()
        price_container = QVBoxLayout()
        price_container.addWidget(QLabel("Precio"))
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Ej: 19990")
        if self.tarjeta and self.tarjeta["precio"] is not None:
            self.price_input.setText(str(self.tarjeta["precio"]))
        price_container.addWidget(self.price_input)

        currency_container = QVBoxLayout()
        currency_container.addWidget(QLabel("Moneda"))
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(["", "CLP", "USD", "EUR"])
        if self.tarjeta:
            idx = self.currency_combo.findText(self.tarjeta["moneda"] or "")
            if idx >= 0: self.currency_combo.setCurrentIndex(idx)
        currency_container.addWidget(self.currency_combo)

        price_layout.addLayout(price_container, 2)
        price_layout.addLayout(currency_container, 1)
        layout.addLayout(price_layout)

        # ESTADO
        layout.addWidget(QLabel("Prioridad / Estado"))
        self.status_combo = QComboBox()
        self.status_combo.addItem("Sin estado", "normal")
        self.status_combo.addItem("Prioridad", "prioridad")
        self.status_combo.addItem("Comprado", "comprado")
        if self.tarjeta:
            idx = self.status_combo.findData(self.tarjeta["estado"])
            if idx >= 0: self.status_combo.setCurrentIndex(idx)
        layout.addWidget(self.status_combo)

        # BOTONES INFERIORES
        buttons = QHBoxLayout()
        
        # BOTÓN ELIMINAR
        if self.tarjeta:
            btn_delete = QPushButton("Eliminar")
            btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_delete.setStyleSheet("background-color: #EF4444; color: white; border: none;")
            btn_delete.clicked.connect(self.delete_card)
            buttons.addWidget(btn_delete)
            
        buttons.addStretch()
        cancel = QPushButton("Cancelar")
        cancel.clicked.connect(self.reject)
        save = QPushButton("Guardar")
        save.setObjectName("primary_btn")
        save.clicked.connect(self.validate_and_accept)
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        layout.addLayout(buttons)

        self.setLayout(layout)

    def delete_card(self):
        resp = QMessageBox.question(self, "Eliminar", "¿Seguro que deseas eliminar este artículo permanentemente?", 
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if resp == QMessageBox.StandardButton.Yes:
            self.is_deleted = True
            self.accept()

    def choose_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Elegir imagen", "", "Imágenes (*.png *.jpg *.jpeg *.webp *.bmp)")
        if not file_path: return
        source = Path(file_path)
        unique_name = f"{uuid4().hex}{source.suffix.lower()}"
        destination = database.IMAGES_DIR / unique_name
        try:
            shutil.copy2(source, destination)
            self.selected_image_path = str(destination)
            self.update_image_preview()
        except Exception as error:
            QMessageBox.critical(self, "Error", f"No se pudo copiar:\n{error}")

    def remove_image(self):
        self.selected_image_path = ""
        self.update_image_preview()

    def update_image_preview(self):
        if not self.selected_image_path:
            self.image_preview.setPixmap(QPixmap())
            self.image_preview.setText("Sin imagen")
            return
        pixmap = QPixmap(self.selected_image_path)
        if pixmap.isNull():
            self.image_preview.setText("Error al cargar")
            return
        scaled = pixmap.scaled(self.image_preview.width(), self.image_preview.height(), 
                               Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.image_preview.setPixmap(scaled)
        self.image_preview.setText("")

    def validate_and_accept(self):
        if not self.title_input.text().strip():
            QMessageBox.warning(self, "Error", "El artículo necesita un nombre.")
            return
        if self.price_input.text().strip():
            try: float(self.price_input.text())
            except ValueError:
                QMessageBox.warning(self, "Error", "El precio debe ser un número válido.")
                return
        self.accept()

    def get_data(self):
        precio = float(self.price_input.text()) if self.price_input.text().strip() else None
        return {
            "titulo": self.title_input.text().strip(),
            "descripcion": self.description_input.toPlainText().strip(),
            "url": self.url_input.text().strip(),
            "foto_ruta": self.selected_image_path,
            "precio": precio,
            "moneda": self.currency_combo.currentText() or None,
            "estado": self.status_combo.currentData()
        }

class ListDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva lista")
        self.setMinimumWidth(350)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.addWidget(QLabel("Nombre de la lista"))
        self.input = QLineEdit()
        layout.addWidget(self.input)

        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel = QPushButton("Cancelar")
        cancel.clicked.connect(self.reject)
        create = QPushButton("Crear")
        create.setObjectName("primary_btn")
        create.clicked.connect(self.validate_and_accept)
        buttons.addWidget(cancel)
        buttons.addWidget(create)
        layout.addLayout(buttons)
        self.setLayout(layout)

    def validate_and_accept(self):
        if not self.input.text().strip():
            QMessageBox.warning(self, "Error", "Escribe un nombre.")
            return
        self.accept()

    def get_name(self):
        return self.input.text().strip()