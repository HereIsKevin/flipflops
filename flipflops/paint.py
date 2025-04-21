from __future__ import annotations

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from flipflops.display import Display


class Paint(QWidget):
    def __init__(self, display: Display) -> None:
        super().__init__()

        self._display: Display = display

        grid = QGridLayout()
        grid.setSpacing(5)
        self.setContentsMargins(5, 5, 5, 5)
        grid.setRowStretch(0, 1)
        grid.setRowStretch(3, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(2, 1)

        self._canvas: Canvas = Canvas()
        grid.addWidget(self._canvas, 2, 1)

        hbox = QHBoxLayout()
        hbox.setSpacing(5)
        hbox.setContentsMargins(0, 0, 0, 0)

        fill_black = QPushButton("Fill Black")
        fill_black.clicked.connect(self._canvas.handle_fill_black)
        hbox.addWidget(fill_black)

        fill_white = QPushButton("Fill White")
        fill_white.clicked.connect(self._canvas.handle_fill_white)
        hbox.addWidget(fill_white)

        hbox.addStretch(1)

        display_canvas = QPushButton("Display")
        display_canvas.clicked.connect(self._handle_display)
        hbox.addWidget(display_canvas)

        grid.addLayout(hbox, 1, 1)

        self.setLayout(grid)

    @Slot()
    def _handle_display(self) -> None:
        self._display.write_display(self._canvas.dots())


class Canvas(QWidget):
    def __init__(self) -> None:
        super().__init__()

        grid = QGridLayout()

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setContentsMargins(20, 20, 20, 20)
        self.setStyleSheet(
            """
            Canvas {
                background-color: black;

                border-style: solid;
                border-color: white;
                border-width: 1px;
                border-radius: 5px;
            }

            QPushButton {
                min-width: 60px;
                width: 60px;
                max-width: 60px;

                min-height: 60px;
                height: 60px;
                max-height: 60px;

                border-style: solid;
                border-color: white;
                border-width: 1px;
                border-radius: 30px;

                background-color: black;
            }

            QPushButton:checked {
                background-color: white;
            }
        """
        )

        self._buttons: list[QPushButton] = []

        for r in range(6):
            for c in range(6):
                button = QPushButton()
                button.setCheckable(True)
                self._buttons.append(button)
                grid.addWidget(button, r, c)

        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(5)

        self.setLayout(grid)
        self.setFixedSize(self.sizeHint())

    @Slot()
    def handle_fill_black(self) -> None:
        for button in self._buttons:
            button.setChecked(False)

    @Slot()
    def handle_fill_white(self) -> None:
        for button in self._buttons:
            button.setChecked(True)

    def dots(self) -> list[Display.Dot]:
        return [
            Display.Dot.White if button.isChecked() else Display.Dot.Black
            for button in self._buttons
        ]
