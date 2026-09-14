from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QFrame
)

from PySide6.QtCore import (
    Qt,
    Signal
)

from styles.theme import get_theme


class DropArea(QFrame):

    card_dropped = Signal(
        int,
        int
    )

    def __init__(
        self,
        id_lista,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.id_lista = id_lista

        self.setAcceptDrops(
            True
        )

        self.setMinimumHeight(
            80
        )

        self.setObjectName(
            "drop_area"
        )


    # DRAG ENTER

    def dragEnterEvent(
        self,
        event
    ):

        if event.mimeData().hasText():

            event.acceptProposedAction()

            self.setProperty(
                "drag_active",
                True
            )

            self.style().unpolish(
                self
            )

            self.style().polish(
                self
            )


    # DRAG MOVE

    def dragMoveEvent(
        self,
        event
    ):

        if event.mimeData().hasText():

            event.acceptProposedAction()


    # DRAG LEAVE

    def dragLeaveEvent(
        self,
        event
    ):

        self.setProperty(
            "drag_active",
            False
        )

        self.style().unpolish(
            self
        )

        self.style().polish(
            self
        )


    # DROP

    def dropEvent(
        self,
        event
    ):

        try:

            id_tarjeta = int(
                event.mimeData().text()
            )

            # Calculamos la posición vertical
            # donde se soltó.
            nuevo_indice = self.calculate_drop_index(
                event.position().y()
            )

            self.card_dropped.emit(
                id_tarjeta,
                nuevo_indice
            )

            event.acceptProposedAction()

        except Exception as error:

            print(
                "Error en Drop:",
                error
            )

        finally:

            self.setProperty(
                "drag_active",
                False
            )

            self.style().unpolish(
                self
            )

            self.style().polish(
                self
            )


    # CALCULAR POSICIÓN

    def calculate_drop_index(
        self,
        y
    ):

        for indice in range(
            self.layout().count()
        ):

            item = self.layout().itemAt(
                indice
            )

            widget = item.widget()

            if widget is None:
                continue

            centro = (
                widget.geometry().top()
                +
                widget.geometry().height()
                / 2
            )

            if y < centro:

                return indice

        return self.layout().count()
