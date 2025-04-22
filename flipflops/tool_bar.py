from __future__ import annotations

from typing import override

from PySide6.QtCore import Signal, Slot
from PySide6.QtSerialPort import QSerialPortInfo
from PySide6.QtWidgets import QComboBox, QPushButton, QToolBar, QWidget

from flipflops.display import Display


class _PortSelect(QComboBox):
    def __init__(self) -> None:
        super().__init__()
        self._add_items()

    @override
    def showPopup(self) -> None:
        current = self.currentText()
        self.clear()
        self._add_items()
        self.setCurrentText(current)
        super().showPopup()

    def _add_items(self) -> None:
        for port in QSerialPortInfo.availablePorts():
            self.addItem(port.systemLocation(), port)


class ToolBar(QToolBar):
    on_console_toggle: Signal = Signal(bool)

    def __init__(self, display: Display) -> None:
        super().__init__(movable=False)

        if self.style().name() == "macos":
            self.setContentsMargins(0, 0, 5, 0)
            self.setStyleSheet("QToolBar { spacing: 0px; }")
        else:
            self.setContentsMargins(0, 0, 0, 0)
            self.setStyleSheet("QToolBar { padding: 5px; spacing: 5px; }")

        self._display: Display = display
        self._display.on_open.connect(self._handle_display_open)
        self._display.on_close.connect(self._handle_display_close)

        self._port_select: _PortSelect = _PortSelect()
        self._port_select.setFixedWidth(300)
        self.addWidget(self._port_select)

        self._display_connected: bool = False
        self._display_toggle: QPushButton = QPushButton("Disconnect")
        self._display_toggle.setFixedWidth(self._display_toggle.sizeHint().width())
        self._display_toggle.setText("Connect")
        self._display_toggle.clicked.connect(self._handle_display_toggle)
        self.addWidget(self._display_toggle)

        spacer = QWidget()
        size_policy = spacer.sizePolicy()
        size_policy.setHorizontalStretch(1)
        spacer.setSizePolicy(size_policy)
        self.addWidget(spacer)

        self._console_toggle: QPushButton = QPushButton("Console")
        self._console_toggle.setCheckable(True)
        self._console_toggle.setChecked(True)
        self._console_toggle.clicked.connect(self._handle_console_toggle)
        self.addWidget(self._console_toggle)

    @Slot()
    def _handle_display_open(self) -> None:
        self._display_toggle.setEnabled(True)
        self._port_select.setEnabled(False)
        self._display_toggle.setText("Disconnect")
        self._display_connected = True

    @Slot()
    def _handle_display_close(self) -> None:
        self._display_toggle.setEnabled(True)
        self._port_select.setEnabled(True)
        self._display_toggle.setText("Connect")
        self._display_connected = False

    @Slot()
    def _handle_display_toggle(self) -> None:
        self._display_toggle.setEnabled(False)
        self._port_select.setEnabled(False)

        if self._display_connected:
            self._display.close()
        else:
            self._display.open(self._port_select.currentData())

    @Slot()
    def _handle_console_toggle(self) -> None:
        self.on_console_toggle.emit(self._console_toggle.isChecked())
