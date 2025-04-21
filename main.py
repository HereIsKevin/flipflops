import sys

from PySide6.QtCore import Qt, Slot
from PySide6.QtSerialPort import QSerialPort
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QTabWidget

from flipflops.console import Console
from flipflops.display import Display
from flipflops.tool_bar import ToolBar
from flipflops.video_player import VideoPlayer


class FlipFlops(QMainWindow):
    def __init__(self) -> None:
        super().__init__(documentMode=True)

        if self.style().name() == "macos":
            self.setUnifiedTitleAndToolBarOnMac(True)

        self.setWindowTitle("FlipFlops")
        self.setMinimumSize(800, 700)

        display = Display()
        display.on_open.connect(self._handle_open)
        display.on_close.connect(self._handle_close)
        display.on_error.connect(self._handle_display_error)

        console = Console(display)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, console)

        tool_bar = ToolBar(display)
        tool_bar.on_console_toggle.connect(console.setVisible)
        self.addToolBar(tool_bar)

        self._tabs: QTabWidget = QTabWidget(documentMode=True)
        self._tabs.setEnabled(False)

        video_player = VideoPlayer(0, display)
        self._tabs.currentChanged.connect(video_player.handle_switch)
        self._tabs.addTab(video_player, "Video Player")

        self.setCentralWidget(self._tabs)

    @Slot()
    def _handle_open(self) -> None:
        self._tabs.setEnabled(True)

    @Slot()
    def _handle_close(self) -> None:
        self._tabs.setEnabled(False)

    @Slot(QSerialPort.SerialPortError)
    def _handle_display_error(self, error: QSerialPort.SerialPortError) -> None:
        # TODO: Improve error popup.
        QMessageBox.critical(
            self,
            "FlipFlops",
            f"{error.name}: Display serial disconnected unexpectedly.",
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    flip_flops = FlipFlops()
    flip_flops.show()

    sys.exit(app.exec())
