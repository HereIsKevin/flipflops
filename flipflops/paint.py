# TODO: Make game better in general and have better messages.

from __future__ import annotations

from collections.abc import Callable
from typing import cast

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QPushButton, QWidget

from flipflops.display import Display


class Paint(QWidget):
    def __init__(self, display: Display) -> None:
        super().__init__()

        self._display: Display = display
        self._display.on_ready.connect(self._handle_ready)
        self._display.on_done.connect(self._handle_ready)
        self._display.on_close.connect(self._handle_close)

        grid = QGridLayout()
        grid.setSpacing(5)
        self.setContentsMargins(5, 5, 5, 5)
        grid.setRowStretch(0, 1)
        grid.setRowStretch(3, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(2, 1)

        self._canvas: _Canvas = _Canvas()
        self._canvas.on_display.connect(self._handle_display)
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

        self._display_button: QPushButton = QPushButton("Display")
        self._display_button.setEnabled(False)
        self._display_button.clicked.connect(self._handle_display)
        hbox.addWidget(self._display_button)

        grid.addLayout(hbox, 1, 1)

        self.setLayout(grid)

    @Slot()
    def _handle_display(self) -> None:
        if not self._display_button.isEnabled():
            return

        self._display_button.setEnabled(False)
        self._display.write_display(self._canvas.dots())

    @Slot()
    def _handle_ready(self) -> None:
        self._display_button.setEnabled(True)

    @Slot()
    def _handle_close(self) -> None:
        self._display_button.setEnabled(False)


class _Canvas(QWidget):
    on_display: Signal = Signal()

    def __init__(self) -> None:
        super().__init__()

        grid = QGridLayout()

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setContentsMargins(30, 30, 30, 30)
        self.setStyleSheet(
            """
            _Canvas {
                background-color: black;

                border-style: solid;
                border-color: white;
                border-width: 2px;
                border-radius: 5px;
            }

            QPushButton {
                min-width: 76px;
                width: 76px;
                max-width: 76px;

                min-height: 76px;
                height: 76px;
                max-height: 76px;

                border-style: solid;
                border-color: white;
                border-width: 2px;
                border-radius: 40px;

                background-color: black;
            }

            QPushButton:checked {
                background-color: white;
            }
            """
        )

        self._row: int = 0
        self._col: int = 0
        self._buttons: list[QPushButton] = []

        for r in range(6):
            for c in range(6):
                button = QPushButton()
                button.setCheckable(True)
                button.clicked.connect(self._fake_focus_handler(r, c))
                self._buttons.append(button)
                grid.addWidget(button, r, c)

        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(8)

        self.setLayout(grid)
        self.setFixedSize(self.sizeHint())
        self._update_focus()

        up = QShortcut(QKeySequence(Qt.Key.Key_Up), self)
        up.activated.connect(self._handle_up)

        down = QShortcut(QKeySequence(Qt.Key.Key_Down), self)
        down.activated.connect(self._handle_down)

        left = QShortcut(QKeySequence(Qt.Key.Key_Left), self)
        left.activated.connect(self._handle_left)

        right = QShortcut(QKeySequence(Qt.Key.Key_Right), self)
        right.activated.connect(self._handle_right)

        toggle = QShortcut(QKeySequence(Qt.Key.Key_Space), self)
        toggle.activated.connect(self._handle_toggle)

        black = QShortcut(QKeySequence(Qt.Key.Key_B), self)
        black.activated.connect(self.handle_fill_black)

        white = QShortcut(QKeySequence(Qt.Key.Key_W), self)
        white.activated.connect(self.handle_fill_white)

        submit = QShortcut(QKeySequence(Qt.Key.Key_Return), self)
        submit.activated.connect(self._handle_submit)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

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
            Display.Dot.WHITE if button.isChecked() else Display.Dot.BLACK
            for button in self._buttons
        ]

    def _fake_focus_handler(self, row: int, col: int) -> Callable[[], None]:
        @Slot()
        def handle() -> None:
            self._row = row
            self._col = col
            self._update_focus()

        return cast(Callable[[], None], handle)

    def _update_focus(self) -> None:
        for index, button in enumerate(self._buttons):
            if index == self._row * 6 + self._col:
                button.setStyleSheet(
                    """
                    min-width: 68px;
                    width: 68px;
                    max-width: 68px;

                    min-height: 68px;
                    height: 68px;
                    max-height: 68px;

                    border-color: gold;
                    border-width: 6px;
                    """
                )
            else:
                button.setStyleSheet("")

    @Slot()
    def _handle_up(self) -> None:
        if not self.hasFocus():
            return

        if self._row > 0:
            self._row -= 1

        self._update_focus()

    @Slot()
    def _handle_down(self) -> None:
        if not self.hasFocus():
            return

        if self._row < 5:
            self._row += 1

        self._update_focus()

    @Slot()
    def _handle_left(self) -> None:
        if not self.hasFocus():
            return

        if self._col > 0:
            self._col -= 1

        self._update_focus()

    @Slot()
    def _handle_right(self) -> None:
        if not self.hasFocus():
            return

        if self._col < 5:
            self._col += 1

        self._update_focus()

    @Slot()
    def _handle_toggle(self) -> None:
        if not self.hasFocus():
            return

        button = self._buttons[self._row * 6 + self._col]
        button.setChecked(not button.isChecked())

    @Slot()
    def _handle_submit(self) -> None:
        if not self.hasFocus():
            return

        self.on_display.emit()
