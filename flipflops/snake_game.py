from __future__ import annotations

import random
from collections.abc import Callable
from enum import Enum, auto
from typing import cast

from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from flipflops.display import Display


class _Cell(Enum):
    EMPTY = auto()
    SNAKE = auto()
    APPLE = auto()


class _Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()


class SnakeGame(QWidget):
    def __init__(self, index: int, display: Display) -> None:
        super().__init__()

        self._index: int = index

        self._starting: bool = False
        self._display: Display = display
        self._display.on_ready.connect(self._handle_ready)
        self._display.on_done.connect(self._handle_ready)
        self._display.on_close.connect(self._handle_close)

        self._cells: list[_Cell] = [_Cell.EMPTY for _ in range(36)]
        self._direction: _Direction = _Direction.RIGHT

        self._snake: list[int] = []
        self._eaten: int = 0

        self._timer: QTimer = QTimer(interval=600, timerType=Qt.TimerType.PreciseTimer)
        self._timer.timeout.connect(self._handle_move_snake)

        vbox = QVBoxLayout()
        vbox.setSpacing(5)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

        vbox.addStretch(1)

        self._apples_eaten: QLabel = QLabel("Apples Eaten: 0")
        vbox.addWidget(self._apples_eaten)

        hbox = QHBoxLayout()
        hbox.setSpacing(0)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._start_stop: QPushButton = QPushButton("Start")
        self._start_stop.setEnabled(False)
        self._start_stop.setFixedWidth(self._start_stop.sizeHint().width())
        self._start_stop.clicked.connect(self._handle_start_stop)
        hbox.addWidget(self._start_stop)
        vbox.addLayout(hbox)

        vbox.addStretch(1)

        self.setLayout(vbox)

        up = QShortcut(QKeySequence(Qt.Key.Key_Up), self)
        up.activated.connect(self._direction_handler(_Direction.UP))

        down = QShortcut(QKeySequence(Qt.Key.Key_Down), self)
        down.activated.connect(self._direction_handler(_Direction.DOWN))

        left = QShortcut(QKeySequence(Qt.Key.Key_Left), self)
        left.activated.connect(self._direction_handler(_Direction.LEFT))

        right = QShortcut(QKeySequence(Qt.Key.Key_Right), self)
        right.activated.connect(self._direction_handler(_Direction.RIGHT))

        start = QShortcut(QKeySequence(Qt.Key.Key_Return), self)
        start.activated.connect(self._handle_start)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    @Slot()
    def handle_switch(self, index: int) -> None:
        if index != self._index:
            self._timer.stop()
            self._starting = False
            self._start_stop.setText("Start")

    def _direction_handler(self, direction: _Direction) -> Callable[[], None]:
        @Slot()
        def handle() -> None:
            if not self.hasFocus() or not self._timer.isActive():
                return

            row, col = divmod(self._snake[-1], 6)

            match direction:
                case _Direction.UP:
                    row -= 1
                case _Direction.DOWN:
                    row += 1
                case _Direction.LEFT:
                    col -= 1
                case _Direction.RIGHT:
                    col += 1

            if row < 0 or row > 5 or col < 0 or col > 5:
                self._direction = direction
                return

            if row * 6 + col == self._snake[-2]:
                return

            self._direction = direction

        return cast(Callable[[], None], handle)

    @Slot()
    def _handle_ready(self) -> None:
        if self._starting:
            self._starting = False
            self._timer.start()

        self._start_stop.setEnabled(True)

    @Slot()
    def _handle_close(self) -> None:
        self._timer.stop()
        self._starting = False
        self._start_stop.setText("Start")
        self._start_stop.setEnabled(False)

    @Slot()
    def _handle_start(self) -> None:
        if self.hasFocus():
            self._handle_start_stop()

    @Slot()
    def _handle_start_stop(self) -> None:
        if not self._start_stop.isEnabled():
            return

        if self._timer.isActive():
            self._start_stop.setText("Start")
            self._starting = False
            self._timer.stop()

            QMessageBox.information(
                self,
                "Snake Game",
                f"You Stopped the Game :|\nApples Eaten: {self._eaten}",
            )
        else:
            self._cells = [_Cell.EMPTY for _ in range(36)]
            self._snake = [2 * 6 + 2, 2 * 6 + 3]

            for cell in self._snake:
                self._cells[cell] = _Cell.SNAKE

            empty_cells = [i for i, c in enumerate(self._cells) if c == _Cell.EMPTY]
            apple_index = random.choice(empty_cells)
            self._cells[apple_index] = _Cell.APPLE

            self._direction = _Direction.RIGHT
            self._eaten = 0

            self._apples_eaten.setText("Apples Eaten: 0")
            self._start_stop.setText("Stop")

            dots = [
                Display.Dot.BLACK if cell == _Cell.EMPTY else Display.Dot.WHITE
                for cell in self._cells
            ]

            self._display.write_display(dots)
            self.setFocus()

            self._starting = True

    @Slot()
    def _handle_move_snake(self) -> None:
        row, col = divmod(self._snake[-1], 6)

        match self._direction:
            case _Direction.UP:
                row -= 1
            case _Direction.DOWN:
                row += 1
            case _Direction.LEFT:
                col -= 1
            case _Direction.RIGHT:
                col += 1

        if row < 0 or row > 5 or col < 0 or col > 5:
            self._start_stop.setText("Start")
            self._timer.stop()

            QMessageBox.information(
                self,
                "Snake Game",
                f"You Crashed Into the Wall :(\nApples Eaten: {self._eaten}",
            )

            return

        cell_index = row * 6 + col

        match self._cells[cell_index]:
            case _Cell.EMPTY:
                self._cells[cell_index] = _Cell.SNAKE
                self._snake.append(cell_index)
                self._cells[self._snake.pop(0)] = _Cell.EMPTY
            case _Cell.SNAKE:
                self._start_stop.setText("Start")
                self._timer.stop()

                QMessageBox.information(
                    self,
                    "Snake Game",
                    f"You Rammed Into Yourself :(\nApples Eaten: {self._eaten}",
                )
            case _Cell.APPLE:
                self._cells[cell_index] = _Cell.SNAKE
                self._snake.append(cell_index)

                empty_cells = [i for i, c in enumerate(self._cells) if c == _Cell.EMPTY]

                if len(empty_cells) == 0:
                    self._start_stop.setText("Start")
                    self._timer.stop()

                    QMessageBox.information(
                        self,
                        "Snake Game",
                        f"YOU WON :)\nApples Eaten: {self._eaten}",
                    )

                    return

                apple_index = random.choice(empty_cells)
                self._cells[apple_index] = _Cell.APPLE

                self._eaten += 1
                self._apples_eaten.setText(f"Apples Eaten: {self._eaten}")

        dots = [
            Display.Dot.BLACK if cell == _Cell.EMPTY else Display.Dot.WHITE
            for cell in self._cells
        ]

        self._display.write_display(dots)
