# TODO: Support displays of sizes other than 6x6.
# TODO: Use QEnum once typing issues are resolved.

from __future__ import annotations

from enum import Enum, auto

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtSerialPort import QSerialPort, QSerialPortInfo


class Display(QObject):
    class RawRow(Enum):
        OFF = auto()
        ON = auto()

        def __bytes__(self) -> bytes:
            match self:
                case Display.RawRow.OFF:
                    return b" "
                case Display.RawRow.ON:
                    return b"1"

    class RawCol(Enum):
        OFF = auto()
        ON_BLACK = auto()
        ON_WHITE = auto()

        def __bytes__(self) -> bytes:
            match self:
                case Display.RawCol.OFF:
                    return b" "
                case Display.RawCol.ON_BLACK:
                    return b"0"
                case Display.RawCol.ON_WHITE:
                    return b"1"

    class Dot(Enum):
        BLACK = auto()
        WHITE = auto()

        def __bytes__(self) -> bytes:
            match self:
                case Display.Dot.BLACK:
                    return b"0"
                case Display.Dot.WHITE:
                    return b"1"

    on_open: Signal = Signal()
    on_close: Signal = Signal()
    on_read: Signal = Signal(bytes)
    on_write: Signal = Signal(bytes)
    on_error: Signal = Signal(QSerialPort.SerialPortError)
    on_ready: Signal = Signal()
    on_done: Signal = Signal()

    def __init__(self) -> None:
        super().__init__()

        self._port: QSerialPort | None = None

    def open(self, info: QSerialPortInfo) -> None:
        assert self._port is None

        self._port = QSerialPort(
            info,
            baudRate=QSerialPort.BaudRate.Baud9600,
            dataBits=QSerialPort.DataBits.Data8,
            flowControl=QSerialPort.FlowControl.NoFlowControl,
            parity=QSerialPort.Parity.NoParity,
            stopBits=QSerialPort.StopBits.OneStop,
        )

        self._port.open(QSerialPort.OpenModeFlag.ReadWrite)
        self._port.readyRead.connect(self._handle_read)
        self._port.errorOccurred.connect(self._handle_error)
        self.on_open.emit()

    def write_abort(self) -> None:
        self.write(b"abort")

    def write_force(self, force: bool) -> None:
        self.write(b"force: " + b"on" if force else b"off")

    def write_display(self, dots: list[Dot]) -> None:
        assert len(dots) == 36
        self.write(b"display: " + b"".join(bytes(dot) for dot in dots))

    def write_raw(self, rows: list[RawRow], cols: list[RawCol]) -> None:
        assert len(rows) == 6
        assert len(cols) == 6

        self.write(
            b"raw: "
            + b"".join(bytes(row) for row in rows)
            + b"".join(bytes(col) for col in cols)
        )

    def write(self, value: bytes) -> None:
        assert self._port is not None

        self._port.write(value + b"\n")
        self.on_write.emit(value)

    def close(self) -> None:
        assert self._port is not None

        self._port.readyRead.disconnect(self._handle_read)
        self._port.errorOccurred.disconnect(self._handle_error)

        if self._port.isOpen():
            self._port.close()

        self._port = None
        self.on_close.emit()

    @Slot()
    def _handle_read(self) -> None:
        assert self._port is not None

        while self._port.canReadLine():
            line = bytes(self._port.readLine().data()).removesuffix(b"\n")
            self.on_read.emit(line)

            if line == b"ready":
                self.on_ready.emit()
            elif line == b"done":
                self.on_done.emit()

    @Slot(QSerialPort.SerialPortError)
    def _handle_error(self, error: QSerialPort.SerialPortError) -> None:
        assert self._port is not None

        self.close()
        self.on_error.emit(error)
