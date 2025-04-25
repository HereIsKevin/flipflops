from __future__ import annotations

from PySide6.QtCore import QFile, Qt
from PySide6.QtWidgets import QDockWidget, QLabel


def _load_instructions() -> str:
    file = QFile(":/resources/instructions.html")

    if not file.open(QFile.OpenModeFlag.ReadOnly):
        raise FileNotFoundError("Failed to read :/resources/instructions.html.")

    return bytes(file.readAll().data()).decode()


_INSTRUCTIONS = _load_instructions()


class Instructions(QDockWidget):
    def __init__(self) -> None:
        super().__init__(
            "Instructions",
            allowedAreas=Qt.DockWidgetArea.RightDockWidgetArea,
            features=QDockWidget.DockWidgetFeature.NoDockWidgetFeatures,
        )

        label = QLabel(_INSTRUCTIONS, textFormat=Qt.TextFormat.RichText)
        label.setContentsMargins(5, 5, 5, 5)
        label.setAlignment(Qt.AlignmentFlag.AlignLeading)
        font = label.font()
        font.setPixelSize(20)
        label.setFont(font)
        self.setWidget(label)
