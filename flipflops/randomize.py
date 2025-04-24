from __future__ import annotations

import random

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QSpinBox, QVBoxLayout, QWidget

from flipflops.display import Display


class Randomize(QWidget):
    def __init__(self, index: int, display: Display) -> None:
        super().__init__()

        self._index: int = index

        self._display: Display = display
        self._display.on_ready.connect(self._handle_ready)
        self._display.on_done.connect(self._handle_ready)
        self._display.on_close.connect(self._handle_close)

        self._playing: bool = False
        self._ready: bool = False
        self._dots: list[Display.Dot] = [Display.Dot.BLACK] * 36

        vbox = QVBoxLayout()
        vbox.setSpacing(5)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

        vbox.addStretch(1)

        self._changes: QSpinBox = QSpinBox(
            minimum=1, maximum=36, value=36, suffix=" changes"
        )
        self._changes.setFixedWidth(self._changes.sizeHint().width())
        self._changes.valueChanged.connect(self._handle_value_change)
        self._changes.setValue(1)
        vbox.addWidget(self._changes)

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

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    @Slot()
    def handle_switch(self, index: int) -> None:
        if index != self._index:
            self._playing = False
            self._start_stop.setText("Start")

    @Slot(int)
    def _handle_value_change(self, value: int) -> None:
        if value == 1:
            self._changes.setSuffix(" change")
        else:
            self._changes.setSuffix(" changes")

    @Slot()
    def _handle_ready(self) -> None:
        self._start_stop.setEnabled(True)

        if not self._playing:
            self._ready = True
            return

        for index in random.sample(range(36), self._changes.value()):
            self._dots[index] = (
                Display.Dot.WHITE
                if self._dots[index] == Display.Dot.BLACK
                else Display.Dot.BLACK
            )

        self._display.write_display(self._dots)

    @Slot()
    def _handle_close(self) -> None:
        self._playing = False
        self._start_stop.setEnabled(False)
        self._start_stop.setText("Start")

    @Slot()
    def _handle_start_stop(self) -> None:
        if self._playing:
            self._playing = False
            self._start_stop.setText("Start")
        else:
            self._playing = True
            self._dots = [Display.Dot.BLACK] * 36
            self._start_stop.setText("Stop")

            if self._ready:
                self._ready = False
                self._handle_ready()
