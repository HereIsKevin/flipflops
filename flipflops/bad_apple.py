from __future__ import annotations

import json
import math
import time
from typing import cast

from PySide6.QtCore import QFile, Qt, Slot
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from flipflops.display import Display


def _load_frames() -> list[str]:
    file = QFile(":/resources/bad_apple.json")

    if not file.open(QFile.OpenModeFlag.ReadOnly):
        raise FileNotFoundError("Failed to read :/resources/bad_apple.json.")

    return cast(list[str], json.loads(bytes(file.readAll().data())))


_FRAMES = _load_frames()


class BadApple(QWidget):
    def __init__(self, index: int, display: Display) -> None:
        super().__init__()

        self._index: int = index

        self._display: Display = display
        self._display.on_ready.connect(self._handle_ready)
        self._display.on_done.connect(self._handle_ready)
        self._display.on_close.connect(self._handle_close)

        self._start_time: float = 0
        self._frames_total: int = 0
        self._playing: bool = False
        self._ready: bool = False

        vbox = QVBoxLayout()
        vbox.setSpacing(5)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

        vbox.addStretch(1)

        self._frame_on: QLabel = QLabel("Frame: 0000 of 0000")
        self._frame_on.setFixedWidth(self._frame_on.sizeHint().width())
        self._frame_on.setText(f"Frame: 0 of {len(_FRAMES)}")
        vbox.addWidget(self._frame_on)

        self._frames_played: QLabel = QLabel("Frames Played: 0000")
        self._frames_played.setFixedWidth(self._frames_played.sizeHint().width())
        self._frames_played.setText(f"Frames Played: {self._frames_total}")
        vbox.addWidget(self._frames_played)

        hbox = QHBoxLayout()
        hbox.setSpacing(0)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._start_stop: QPushButton = QPushButton("Start")
        self._start_stop.setFixedWidth(self._start_stop.sizeHint().width())
        self._start_stop.clicked.connect(self._handle_start_stop)
        hbox.addWidget(self._start_stop)
        vbox.addLayout(hbox)

        vbox.addStretch(1)

        self.setLayout(vbox)

    @Slot()
    def handle_switch(self, index: int) -> None:
        if index != self._index:
            self._playing = False
            self._frames_total = 0
            self._start_stop.setText("Start")

    @Slot()
    def _handle_ready(self) -> None:
        if not self._playing:
            self._ready = True
            return

        current_time = time.time()
        index = math.floor((current_time - self._start_time) * 30)

        if index >= len(_FRAMES):
            self._playing = False
            self._frames_total = 0
            self._start_stop.setText("Start")
            return

        self._display.write(b"display: " + _FRAMES[index].encode("ascii"))

        self._frames_total += 1
        self._frame_on.setText(f"Frame: {index + 1} of {len(_FRAMES)}")
        self._frames_played.setText(f"Frames Played: {self._frames_total}")

    @Slot()
    def _handle_close(self) -> None:
        self._playing = False
        self._start_stop.setText("Start")

    @Slot()
    def _handle_start_stop(self) -> None:
        if self._playing:
            self._playing = False
            self._frames_total = 0
            self._start_stop.setText("Start")
        else:
            self._start_time = time.time()
            self._playing = True
            self._start_stop.setText("Stop")

            if self._ready:
                self._ready = False
                self._handle_ready()
