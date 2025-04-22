# TODO: Add audio support.
# TODO: Support displays of sizes other than 6x6.

from __future__ import annotations

from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QImage, qGray
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from flipflops.display import Display


class VideoPlayer(QWidget):
    def __init__(self, index: int, display: Display) -> None:
        super().__init__()

        self._index: int = index

        self._ready: bool = False
        self._display: Display = display
        self._display.on_ready.connect(self._handle_ready)
        self._display.on_done.connect(self._handle_ready)
        self._display.on_close.connect(self._handle_close)

        self._media: QMediaPlayer | None = None
        self._was_playing: bool = False

        vbox = QVBoxLayout()
        vbox.setSpacing(0)
        vbox.setContentsMargins(0, 0, 0, 0)

        self._video: QVideoWidget = QVideoWidget()
        size_policy = self._video.sizePolicy()
        size_policy.setVerticalStretch(1)
        self._video.setSizePolicy(size_policy)
        vbox.addWidget(self._video)

        hbox = QHBoxLayout()
        hbox.setSpacing(5)

        if self.style().name() == "macos":
            hbox.setContentsMargins(5, 0, 5, 0)
        else:
            hbox.setContentsMargins(5, 5, 5, 5)

        open_file = QPushButton("Open")
        open_file.clicked.connect(self._handle_open)
        hbox.addWidget(open_file)

        self._play_pause: QPushButton = QPushButton("Pause")
        self._play_pause.setFixedWidth(self._play_pause.sizeHint().width())
        self._play_pause.setText("Play")
        self._play_pause.setEnabled(False)
        self._play_pause.clicked.connect(self._handle_play_pause)
        hbox.addWidget(self._play_pause)

        self._seek_slider: QSlider = QSlider(Qt.Orientation.Horizontal)
        self._seek_slider.setEnabled(False)
        self._seek_slider.sliderPressed.connect(self._handle_seek_start)
        self._seek_slider.sliderMoved.connect(self._handle_seek)
        self._seek_slider.sliderReleased.connect(self._handle_seek_end)

        # NOTE: Compensate for uncentered seek slider
        if self.style().name() == "macos":
            wrapper = QVBoxLayout()
            wrapper.setSpacing(0)
            wrapper.setContentsMargins(0, 0, 0, 0)

            wrapper.addSpacing(9)
            wrapper.addWidget(self._seek_slider)

            hbox.addLayout(wrapper)
        else:
            hbox.addWidget(self._seek_slider)

        self._has_hours: bool = False
        self._total_time: str | None = None
        self._seek_label: QLabel = QLabel("--:-- / --:--")
        hbox.addWidget(self._seek_label)

        vbox.addLayout(hbox)

        self.setLayout(vbox)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    @Slot()
    def handle_switch(self, index: int) -> None:
        if index != self._index and self._media is not None:
            self._play_pause.setText("Play")
            self._media.pause()

    def _write_display(self) -> None:
        assert self._media is not None

        frame = self._media.videoSink().videoFrame()

        if not frame.isValid():
            return

        image = frame.toImage()
        image.convertTo(QImage.Format.Format_Mono)

        w = image.width()
        h = image.height()
        s = min(w, h)
        x = (w - s) // 2
        y = (h - s) // 2

        image = image.copy(x, y, s, s).scaled(6, 6)

        # TODO: Clean this up, precalculate all frames for performance
        points = (divmod(i, 6) for i in range(36))
        grays = (qGray(image.pixel(x, y)) for y, x in points)
        dots = [Display.Dot.BLACK if gray == 0 else Display.Dot.WHITE for gray in grays]

        self._display.write_display(dots)

    @Slot()
    def _handle_close(self) -> None:
        self._play_pause.setEnabled(False)

        if self._media is not None:
            self._play_pause.setText("Play")
            self._media.pause()

    @Slot()
    def _handle_ready(self) -> None:
        self._play_pause.setEnabled(True)

        if self._media is not None and self._media.isPlaying():
            self._write_display()
        else:
            self._ready = True

    @Slot()
    def _handle_open(self) -> None:
        # TODO: Properly configure file dialog.
        url, _ = QFileDialog.getOpenFileUrl(
            caption="Open Video", filter="Videos (*.ogv *.mp4 *.mov)"
        )

        if url.isEmpty():
            return

        if self._media is None:
            self._media = QMediaPlayer()
            self._media.setVideoOutput(self._video)
            self._media.playingChanged.connect(self._handle_playing_change)
            self._media.durationChanged.connect(self._handle_duration_change)
            self._media.positionChanged.connect(self._handle_position_change)
            self._media.errorOccurred.connect(self._handle_error)

        self._media.pause()
        self._media.setSource(url)
        self._play_pause.setText("Play")
        self._seek_slider.setEnabled(True)
        self._seek_slider.setValue(0)
        self._seek_label.setMinimumWidth(0)
        self._seek_label.setMaximumWidth((1 << 24) - 1)  # QWIDGETSIZE_MAX

    @Slot()
    def _handle_error(self, error: QMediaPlayer.Error, message: str) -> None:
        assert self._media is not None

        self._media.pause()
        self._media.setSource("")
        self._play_pause.setEnabled(False)
        self._play_pause.setText("Play")
        self._seek_slider.setEnabled(False)
        self._seek_slider.setValue(0)
        self._has_hours = False
        self._total_time = None
        self._seek_label.setText("--:-- / --:--")
        self._seek_label.setMinimumWidth(0)
        self._seek_label.setMaximumWidth((1 << 24) - 1)  # QWIDGETSIZE_MAX

        # TODO: Improve error popup.
        QMessageBox.critical(self, "Video Player", f"{error.name}: {message}.")

    @Slot()
    def _handle_play_pause(self) -> None:
        assert self._media is not None

        if self._media.isPlaying():
            self._media.pause()
        else:
            self._media.play()

    @Slot(bool)
    def _handle_playing_change(self, playing: bool) -> None:
        self._play_pause.setText("Pause" if playing else "Play")

    @Slot(int)
    def _handle_duration_change(self, duration: int) -> None:
        rest = round(duration / 1000)
        rest, seconds = divmod(rest, 60)
        hours, minutes = divmod(rest, 60)

        if hours > 0:
            self._has_hours = True
            self._total_time = f"{hours:02}:{minutes:02}:{seconds:02}"

            self._seek_label.setText("00:00:00 / 00:00:00")
            self._seek_label.setFixedWidth(self._seek_label.sizeHint().width())
            self._seek_label.setText(f"00:00:00 / {self._total_time}")
        else:
            self._has_hours = False
            self._total_time = f"{minutes:02}:{seconds:02}"

            self._seek_label.setText("00:00 / 00:00")
            self._seek_label.setFixedWidth(self._seek_label.sizeHint().width())
            self._seek_label.setText(f"00:00 / {self._total_time}")

        self._seek_slider.setRange(0, duration)

    @Slot(int)
    def _handle_position_change(self, position: int) -> None:
        assert self._media is not None
        assert self._total_time is not None

        if self._ready and self._media.isPlaying():
            self._ready = False
            self._write_display()

        rest = round(position / 1000)
        rest, seconds = divmod(rest, 60)
        hours, minutes = divmod(rest, 60)

        if self._has_hours:
            current = f"{hours:02}:{minutes:02}:{seconds:02}"
        else:
            current = f"{minutes:02}:{seconds:02}"

        self._seek_label.setText(f"{current} / {self._total_time}")

        if not self._seek_slider.isSliderDown():
            self._seek_slider.setSliderPosition(position)

    @Slot()
    def _handle_seek_start(self) -> None:
        assert self._media is not None

        self._was_playing = self._media.isPlaying()
        self._media.pause()
        self._media.setPosition(self._seek_slider.value())

    @Slot(int)
    def _handle_seek(self, value: int) -> None:
        assert self._media is not None
        self._media.setPosition(value)

    @Slot()
    def _handle_seek_end(self) -> None:
        assert self._media is not None

        if self._was_playing:
            self._media.play()
