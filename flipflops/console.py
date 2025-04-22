from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDockWidget,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from flipflops.display import Display

_MONOSPACE_FONT = QFont("JetBrains Mono")
_MONOSPACE_FONT.setStyleHint(QFont.StyleHint.Monospace)


class Console(QDockWidget):
    def __init__(self, display: Display) -> None:
        super().__init__(
            "Console",
            allowedAreas=Qt.DockWidgetArea.BottomDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea,
            features=QDockWidget.DockWidgetFeature.NoDockWidgetFeatures
            | QDockWidget.DockWidgetFeature.DockWidgetMovable,
        )

        self._display: Display = display

        root = QWidget()

        vbox = QVBoxLayout()
        vbox.setSpacing(0)
        vbox.setContentsMargins(0, 0, 0, 0)

        self._console: QTextEdit = QTextEdit()
        self._console.setFrameShape(QTextEdit.Shape.NoFrame)
        self._console.setFont(_MONOSPACE_FONT)
        self._console.setReadOnly(True)
        vbox.addWidget(self._console)

        hbox = QHBoxLayout()
        hbox.setSpacing(5)
        hbox.setContentsMargins(5, 5, 5, 5)

        self._input: QLineEdit = QLineEdit(placeholderText="Enter a command...")
        self._input.setEnabled(False)
        self._input.setFont(_MONOSPACE_FONT)
        self._input.returnPressed.connect(self._handle_submit)
        hbox.addWidget(self._input)

        clear = QPushButton("Clear")
        clear.clicked.connect(self._console.clear)
        hbox.addWidget(clear)

        vbox.addLayout(hbox)
        root.setLayout(vbox)
        self.setWidget(root)

        self._display.on_open.connect(self._handle_open)
        self._display.on_close.connect(self._handle_close)
        self._display.on_read.connect(self._handle_read)
        self._display.on_write.connect(self._handle_write)

    def write_comment(self, value: str) -> None:
        self._write("//", value)

    def _write(self, symbol: str, value: str) -> None:
        time = datetime.now().time().isoformat(timespec="microseconds")
        self._console.append(f"{time} {symbol} {value}")

    @Slot()
    def _handle_submit(self) -> None:
        text = self._input.text()

        if len(text) == 0:
            return

        self._display.write(text.encode("ascii"))
        self._input.clear()

    @Slot()
    def _handle_open(self) -> None:
        self._input.setEnabled(True)

    @Slot()
    def _handle_close(self) -> None:
        self._input.setEnabled(False)

    @Slot(bytes)
    def _handle_read(self, value: bytes) -> None:
        self._write("<-", value.decode("ascii"))

    @Slot(bytes)
    def _handle_write(self, value: bytes) -> None:
        self._write("->", value.decode("ascii"))
