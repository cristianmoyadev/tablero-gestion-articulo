DARK = {
    "background": "#000000",        # Fondo general
    "list_bg": "#121212",           # Lista
    "card_bg": "#242427",           # Tarjeta
    "surface_secondary": "#3F3F46", 
    "surface_hover": "#52525B",
    "border": "#3F3F46",            # Borde de la tarjeta
    "text": "#F4F4F5",
    "secondary_text": "#A1A1AA",
    "blue": "#3B82F6",
    "green": "#10B981",
    "yellow": "#F59E0B",
    "red": "#EF4444"
}

def get_theme():
    return DARK

def build_stylesheet():
    c = get_theme()
    return f"""
    QMainWindow, QDialog {{
        background-color: {c["background"]};
    }}

    QWidget#central_widget, QWidget#board_widget {{
        background-color: {c["background"]};
    }}

    QWidget {{
        font-family: "Segoe UI", "SF Pro Display", Arial;
        color: {c["text"]};
    }}

    QLabel#app_title {{
        font-size: 28px;
        font-weight: bold;
        letter-spacing: -0.5px;
    }}

    QLabel#app_subtitle {{
        font-size: 14px;
        color: {c["secondary_text"]};
    }}

    QScrollArea, QScrollArea > QWidget > QWidget {{
        border: none;
        background: transparent;
    }}

    QLineEdit, QTextEdit, QComboBox {{
        background: {c["surface_secondary"]};
        border: 1px solid {c["border"]};
        border-radius: 8px;
        padding: 10px;
        color: {c["text"]};
        font-size: 14px;
    }}

    QLineEdit:focus, QTextEdit:focus, QComboBox:focus {{
        border: 1px solid {c["blue"]};
    }}

    QPushButton {{
        background: {c["surface_secondary"]};
        color: {c["text"]};
        border: 1px solid {c["border"]};
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 600;
        font-size: 13px;
    }}

    QPushButton:hover {{
        background: {c["surface_hover"]};
        border: 1px solid {c["blue"]};
    }}

    QPushButton:pressed {{
        background: {c["surface_secondary"]};
    }}
    
    QPushButton#primary_btn {{
        background: {c["blue"]};
        color: #FFFFFF;
        border: none;
    }}
    QPushButton#primary_btn:hover {{
        background: #1D4ED8;
    }}

    /* BARRA HORIZONTAL */
    QScrollBar:horizontal {{
        border: none;
        background: {c["list_bg"]};
        height: 14px;
        margin: 0px 20px 5px 20px;
        border-radius: 7px;
    }}
    QScrollBar::handle:horizontal {{
        background: {c["surface_secondary"]};
        border-radius: 7px;
        min-width: 40px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {c["surface_hover"]};
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0px; height: 0px;
    }}
    
    /* BARRA VERTICAL */
    QScrollBar:vertical {{
        border: none;
        background: transparent;
        width: 10px;
        margin: 5px;
    }}
    QScrollBar::handle:vertical {{
        background: {c["surface_secondary"]};
        border-radius: 5px;
    }}
    """